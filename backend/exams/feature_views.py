from collections import defaultdict
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Filial
from accounts.permissions import IsAdmin
from courses.models import OquvchiFan
from .audit import log_amal
from .coins import coin_qoshish
from .models import (
    FinalTestNatija, KunlikFaollik, ListeningNatija, MashqNatija, Musobaqa,
    Sertifikat, ShopBuyurtma, SpeakingNatija, WritingNatija,
)

User = get_user_model()


def _points_map(start, end, fan_id=None, filial_id=None):
    users = User.objects.filter(role=User.ROLE_OQUVCHI, faol=True)
    if filial_id:
        users = users.filter(filial_id=filial_id)
    if fan_id:
        users = users.filter(biriktirilgan_fanlar__daraja__fan_id=fan_id).distinct()
    user_ids = list(users.values_list('id', flat=True))
    points = defaultdict(float)
    details = defaultdict(lambda: {'test': 0, 'final': 0, 'listening': 0, 'writing': 0, 'faollik': 0, 'sertifikat': 0})

    def add_rows(qs, date_field, score_field, divisor, key):
        rows = qs.filter(oquvchi_id__in=user_ids, **{f'{date_field}__date__gte': start, f'{date_field}__date__lte': end}) \
            .values('oquvchi_id').annotate(total=Sum(score_field))
        for row in rows:
            value = float(row['total'] or 0) / divisor
            points[row['oquvchi_id']] += value
            details[row['oquvchi_id']][key] = round(value, 1)

    add_rows(MashqNatija.objects.all(), 'boshlangan_vaqt', 'foiz', 10, 'test')
    add_rows(FinalTestNatija.objects.all(), 'created_at', 'foiz', 5, 'final')
    add_rows(ListeningNatija.objects.all(), 'created_at', 'foiz', 10, 'listening')
    add_rows(WritingNatija.objects.exclude(ai_foiz=None), 'created_at', 'ai_foiz', 10, 'writing')

    activity_rows = KunlikFaollik.objects.filter(oquvchi_id__in=user_ids, sana__range=(start, end)).values('oquvchi_id').annotate(total=Sum('faollik_soni'))
    for row in activity_rows:
        value = int(row['total'] or 0) * 2
        points[row['oquvchi_id']] += value
        details[row['oquvchi_id']]['faollik'] = value

    certificate_rows = Sertifikat.objects.filter(oquvchi_id__in=user_ids, berilgan_sana__date__range=(start, end)).values('oquvchi_id').annotate(total=Count('id'))
    for row in certificate_rows:
        value = int(row['total'] or 0) * 50
        points[row['oquvchi_id']] += value
        details[row['oquvchi_id']]['sertifikat'] = value

    user_map = {u.id: u for u in users.select_related('filial')}
    ranking = []
    for uid in user_ids:
        user = user_map[uid]
        ranking.append({
            'oquvchi_id': uid,
            'ism': user.full_name,
            'username': user.username,
            'filial': user.filial.nomi if user.filial else '',
            'ball': round(points[uid], 1),
            'tafsilot': details[uid],
        })
    ranking.sort(key=lambda item: (-item['ball'], item['ism'].casefold()))
    for index, item in enumerate(ranking, 1):
        item['orin'] = index
    return ranking


class AdminKengaytirilganStatistikaView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.localdate()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        students = User.objects.filter(role=User.ROLE_OQUVCHI)
        active_7_ids = KunlikFaollik.objects.filter(sana__gte=week_ago).values_list('oquvchi_id', flat=True).distinct()
        active_today = KunlikFaollik.objects.filter(sana=today).values('oquvchi_id').distinct().count()
        expiring = students.filter(tugash_sana__gte=today, tugash_sana__lte=today + timedelta(days=5)).count()

        level_distribution = list(OquvchiFan.objects.values('daraja__nomi').annotate(soni=Count('oquvchi_id', distinct=True)).order_by('daraja__tartib'))
        branch_rows = []
        for branch in Filial.objects.all().order_by('nomi'):
            branch_students = students.filter(filial=branch)
            avg = MashqNatija.objects.filter(oquvchi__in=branch_students).aggregate(v=Avg('foiz'))['v'] or 0
            branch_rows.append({'filial': branch.nomi, 'oquvchilar': branch_students.count(), 'ortacha': round(float(avg), 1)})

        monthly = []
        for offset in range(5, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=offset * 31)).replace(day=1)
            if month_start.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            monthly.append({'oy': month_start.strftime('%m.%Y'), 'yangi': students.filter(created_at__date__gte=month_start, created_at__date__lt=next_month).count()})

        return Response({
            'kpi': {
                'jami_oquvchi': students.count(),
                'bugun_faol': active_today,
                '7_kun_faol': students.filter(id__in=active_7_ids).count(),
                '7_kun_faol_emas': students.exclude(id__in=active_7_ids).count(),
                'muddati_tugagan': students.filter(tugash_sana__lt=today, muddat_bloklash=True).count(),
                '5_kunda_tugaydi': expiring,
                'tolanmagan': students.filter(tolov_holati=User.TOLOV_TOLANMAGAN).count(),
                'sertifikatlar': Sertifikat.objects.count(),
                'yangi_xaridlar': ShopBuyurtma.objects.filter(status='yangi').count(),
            },
            'ortachalar': {
                'test': round(float(MashqNatija.objects.aggregate(v=Avg('foiz'))['v'] or 0), 1),
                'listening': round(float(ListeningNatija.objects.aggregate(v=Avg('foiz'))['v'] or 0), 1),
                'speaking': round(float(SpeakingNatija.objects.aggregate(v=Avg('ai_foiz'))['v'] or 0), 1),
                'writing': round(float(WritingNatija.objects.aggregate(v=Avg('ai_foiz'))['v'] or 0), 1),
            },
            'darajalar': level_distribution,
            'filiallar': branch_rows,
            'oylik_qoshilish': monthly,
            'ehtibor_talab': list(students.exclude(id__in=active_7_ids).select_related('filial').values('id', 'username', 'ism', 'familya', 'filial__nomi', 'tugash_sana')[:20]),
            'top_reyting': _points_map(month_ago, today)[:10],
        })


class ReytingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        period = request.query_params.get('period', 'hafta')
        start = today - timedelta(days=30 if period == 'oy' else 7)
        fan_id = request.query_params.get('fan')
        filial_id = request.query_params.get('filial')
        ranking = _points_map(start, today, fan_id, filial_id)
        mine = next((item for item in ranking if item['oquvchi_id'] == request.user.id), None)
        return Response({'boshlanish': start, 'tugash': today, 'reyting': ranking[:100], 'mening_orinim': mine})


class MusobaqaSerializer(serializers.ModelSerializer):
    fan_nomi = serializers.CharField(source='fan.nomi', read_only=True)
    filial_nomi = serializers.CharField(source='filial.nomi', read_only=True)
    reyting = serializers.SerializerMethodField()

    class Meta:
        model = Musobaqa
        fields = ['id', 'nomi', 'tavsif', 'boshlanish_sana', 'tugash_sana', 'fan', 'fan_nomi', 'filial', 'filial_nomi', 'status', 'birinchi_coin', 'ikkinchi_coin', 'uchinchi_coin', 'goliblar', 'reyting', 'created_at']
        read_only_fields = ['goliblar', 'created_at']

    def get_reyting(self, obj):
        return _points_map(obj.boshlanish_sana, obj.tugash_sana, obj.fan_id, obj.filial_id)[:20]


class MusobaqaViewSet(viewsets.ModelViewSet):
    queryset = Musobaqa.objects.select_related('fan', 'filial').all()
    serializer_class = MusobaqaSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        obj = serializer.save(yaratgan=self.request.user)
        log_amal(self.request.user, 'musobaqa_yaratildi', obj.nomi, obyekt_turi='Musobaqa', obyekt_id=obj.pk, request=self.request)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def yakunlash(self, request, pk=None):
        obj = self.get_object()
        if obj.status == Musobaqa.STATUS_YAKUN:
            return Response({'detail': 'Bu musobaqa avval yakunlangan.'}, status=status.HTTP_400_BAD_REQUEST)
        ranking = _points_map(obj.boshlanish_sana, obj.tugash_sana, obj.fan_id, obj.filial_id)[:3]
        prizes = [obj.birinchi_coin, obj.ikkinchi_coin, obj.uchinchi_coin]
        winners = []
        for index, item in enumerate(ranking):
            user = User.objects.get(pk=item['oquvchi_id'])
            coin_qoshish(user, prizes[index], 'admin', f"{obj.nomi}: {index + 1}-o'rin")
            winners.append({**item, 'bonus_coin': prizes[index]})
        obj.goliblar = winners
        obj.status = Musobaqa.STATUS_YAKUN
        obj.save(update_fields=['goliblar', 'status'])
        log_amal(request.user, 'musobaqa_yakunlandi', obj.nomi, obyekt_turi='Musobaqa', obyekt_id=obj.pk, yangi_holat={'goliblar': winners}, request=request)
        return Response(MusobaqaSerializer(obj).data)
