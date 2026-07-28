from collections import defaultdict
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
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
    Bildirishnoma, FinalTestNatija, KunlikFaollik, ListeningNatija, MashqNatija, Musobaqa,
    MusobaqaUrinish, Savol, Sertifikat, ShopBuyurtma, SpeakingNatija, WritingNatija,
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


def _eligible_students(competition):
    users = User.objects.filter(role=User.ROLE_OQUVCHI, faol=True)
    if competition.filial_id:
        users = users.filter(filial_id=competition.filial_id)
    if competition.fan_id:
        users = users.filter(biriktirilgan_fanlar__daraja__fan_id=competition.fan_id)
    return users.distinct()


def _is_eligible(competition, user):
    if not user or user.role != User.ROLE_OQUVCHI or not user.faol:
        return False
    return _eligible_students(competition).filter(pk=user.pk).exists()


def _competition_ranking(competition, limit=100):
    attempts = competition.urinishlar.filter(status=MusobaqaUrinish.STATUS_YAKUN).select_related('oquvchi__filial')
    result = []
    for index, attempt in enumerate(attempts.order_by('-foiz', 'sarflangan_soniya', 'tugagan_vaqt')[:limit], 1):
        result.append({
            'orin': index,
            'oquvchi_id': attempt.oquvchi_id,
            'ism': attempt.oquvchi.full_name,
            'username': attempt.oquvchi.username,
            'filial': attempt.oquvchi.filial.nomi if attempt.oquvchi.filial else '',
            'ball': float(attempt.foiz),
            'foiz': float(attempt.foiz),
            'togri_soni': attempt.togri_soni,
            'jami_soni': attempt.jami_soni,
            'sarflangan_soniya': attempt.sarflangan_soniya,
        })
    return result


def _competition_question_pool(competition, user):
    qs = Savol.objects.select_related('mashq__dars__mavzu__daraja__fan').prefetch_related('javoblar')
    if competition.fan_id:
        qs = qs.filter(mashq__dars__mavzu__daraja__fan_id=competition.fan_id)
    else:
        fan_ids = OquvchiFan.objects.filter(oquvchi=user).values_list('daraja__fan_id', flat=True)
        qs = qs.filter(mashq__dars__mavzu__daraja__fan_id__in=fan_ids)
    return list(qs.filter(javoblar__isnull=False).distinct())


def _serialize_competition_questions(question_ids):
    questions = Savol.objects.filter(id__in=question_ids).prefetch_related('javoblar')
    question_map = {item.id: item for item in questions}
    output = []
    for qid in question_ids:
        question = question_map.get(qid)
        if not question:
            continue
        answers = [{'id': item.id, 'matn': item.matn} for item in question.javoblar.all()]
        random.shuffle(answers)
        output.append({
            'id': question.id,
            'matn': question.matn,
            'rasm': question.rasm.url if question.rasm else None,
            'tur': question.tur,
            'javoblar': answers,
        })
    return output


class MusobaqaSerializer(serializers.ModelSerializer):
    fan_nomi = serializers.CharField(source='fan.nomi', read_only=True)
    filial_nomi = serializers.CharField(source='filial.nomi', read_only=True)
    reyting = serializers.SerializerMethodField()
    mening_urinishim = serializers.SerializerMethodField()
    qatnashishi_mumkin = serializers.SerializerMethodField()
    qatnashuvchilar_soni = serializers.SerializerMethodField()

    class Meta:
        model = Musobaqa
        fields = [
            'id', 'nomi', 'tavsif', 'boshlanish_sana', 'tugash_sana', 'fan', 'fan_nomi',
            'filial', 'filial_nomi', 'status', 'davomiyligi_daq', 'savollar_soni',
            'boshlangan_vaqt', 'yakunlangan_vaqt', 'birinchi_coin', 'ikkinchi_coin',
            'uchinchi_coin', 'goliblar', 'reyting', 'mening_urinishim',
            'qatnashishi_mumkin', 'qatnashuvchilar_soni', 'created_at',
        ]
        read_only_fields = ['goliblar', 'boshlangan_vaqt', 'yakunlangan_vaqt', 'created_at']

    def get_reyting(self, obj):
        return _competition_ranking(obj, 20)

    def get_mening_urinishim(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user.role != User.ROLE_OQUVCHI:
            return None
        attempt = obj.urinishlar.filter(oquvchi=request.user).first()
        if not attempt:
            return None
        return {
            'id': attempt.id,
            'status': attempt.status,
            'foiz': float(attempt.foiz),
            'togri_soni': attempt.togri_soni,
            'jami_soni': attempt.jami_soni,
            'sarflangan_soniya': attempt.sarflangan_soniya,
            'boshlangan_vaqt': attempt.boshlangan_vaqt,
            'tugagan_vaqt': attempt.tugagan_vaqt,
        }

    def get_qatnashishi_mumkin(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and _is_eligible(obj, request.user))

    def get_qatnashuvchilar_soni(self, obj):
        return obj.urinishlar.filter(status=MusobaqaUrinish.STATUS_YAKUN).count()


class MusobaqaViewSet(viewsets.ModelViewSet):
    queryset = Musobaqa.objects.select_related('fan', 'filial').prefetch_related('urinishlar').all()
    serializer_class = MusobaqaSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'faol', 'urinish_boshlash', 'topshirish'):
            return [IsAuthenticated()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role == User.ROLE_OQUVCHI:
            from django.db.models import Q
            assigned_fans = OquvchiFan.objects.filter(oquvchi=user).values_list('daraja__fan_id', flat=True)
            qs = qs.filter(Q(fan_id__in=assigned_fans) | Q(fan__isnull=True))
            qs = qs.filter(Q(filial=user.filial) | Q(filial__isnull=True)).distinct()
        return qs

    def perform_create(self, serializer):
        obj = serializer.save(yaratgan=self.request.user, status=Musobaqa.STATUS_REJA)
        log_amal(self.request.user, 'musobaqa_yaratildi', obj.nomi, obyekt_turi='Musobaqa', obyekt_id=obj.pk, request=self.request)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def faol(self, request):
        qs = self.get_queryset().filter(status=Musobaqa.STATUS_FAOL)
        if request.user.role == User.ROLE_OQUVCHI:
            qs = qs.exclude(urinishlar__oquvchi=request.user, urinishlar__status=MusobaqaUrinish.STATUS_YAKUN)
        return Response(MusobaqaSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def boshlash(self, request, pk=None):
        obj = self.get_object()
        if obj.status == Musobaqa.STATUS_YAKUN:
            return Response({'detail': 'Yakunlangan musobaqani qayta boshlash mumkin emas.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = Musobaqa.STATUS_FAOL
        obj.boshlangan_vaqt = timezone.now()
        obj.yakunlangan_vaqt = None
        obj.save(update_fields=['status', 'boshlangan_vaqt', 'yakunlangan_vaqt'])
        students = list(_eligible_students(obj).only('id'))
        student_ids = [item.id for item in students]
        existing_ids = set(Bildirishnoma.objects.filter(
            oquvchi_id__in=student_ids,
            havola=f'/oquvchi/musobaqalar/{obj.id}',
        ).values_list('oquvchi_id', flat=True))
        notifications = [
            Bildirishnoma(
                oquvchi=student,
                sarlavha='🏆 Yangi musobaqa boshlandi!',
                matn=f'{obj.nomi} musobaqasi boshlandi. {obj.savollar_soni} ta savol, {obj.davomiyligi_daq} daqiqa.',
                tur=Bildirishnoma.TUR_WARNING,
                havola=f'/oquvchi/musobaqalar/{obj.id}',
            )
            for student in students if student.id not in existing_ids
        ]
        if notifications:
            Bildirishnoma.objects.bulk_create(notifications)
        log_amal(request.user, 'musobaqa_boshlandi', obj.nomi, obyekt_turi='Musobaqa', obyekt_id=obj.pk, yangi_holat={'oquvchilar': len(students)}, request=request)
        return Response(MusobaqaSerializer(obj, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='urinish-boshlash', permission_classes=[IsAuthenticated])
    def urinish_boshlash(self, request, pk=None):
        obj = self.get_object()
        if request.user.role != User.ROLE_OQUVCHI or not _is_eligible(obj, request.user):
            return Response({'detail': 'Siz bu musobaqaga biriktirilmagansiz.'}, status=status.HTTP_403_FORBIDDEN)
        if obj.status != Musobaqa.STATUS_FAOL:
            return Response({'detail': 'Musobaqa hozir faol emas.'}, status=status.HTTP_400_BAD_REQUEST)
        attempt = MusobaqaUrinish.objects.filter(musobaqa=obj, oquvchi=request.user).first()
        if attempt and attempt.status == MusobaqaUrinish.STATUS_YAKUN:
            return Response({'detail': 'Siz bu musobaqada allaqachon qatnashgansiz.', 'yakunlangan': True}, status=status.HTTP_400_BAD_REQUEST)
        if not attempt:
            pool = _competition_question_pool(obj, request.user)
            if not pool:
                return Response({'detail': 'Bu fan uchun test savollari topilmadi.'}, status=status.HTTP_400_BAD_REQUEST)
            random.shuffle(pool)
            selected = pool[:min(obj.savollar_soni, len(pool))]
            attempt = MusobaqaUrinish.objects.create(
                musobaqa=obj,
                oquvchi=request.user,
                savol_idlari=[item.id for item in selected],
                jami_soni=len(selected),
            )
        elapsed = max(0, int((timezone.now() - attempt.boshlangan_vaqt).total_seconds()))
        total_seconds = obj.davomiyligi_daq * 60
        return Response({
            'musobaqa': MusobaqaSerializer(obj, context={'request': request}).data,
            'urinish_id': attempt.id,
            'savollar': _serialize_competition_questions(attempt.savol_idlari),
            'qolgan_soniya': max(0, total_seconds - elapsed),
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def topshirish(self, request, pk=None):
        obj = self.get_object()
        if request.user.role != User.ROLE_OQUVCHI:
            return Response({'detail': 'Faqat o‘quvchi topshira oladi.'}, status=status.HTTP_403_FORBIDDEN)
        answers_data = request.data.get('javoblar', [])
        answer_map = {int(item.get('savol')): item for item in answers_data if item.get('savol')}
        with transaction.atomic():
            try:
                attempt = MusobaqaUrinish.objects.select_for_update().get(musobaqa=obj, oquvchi=request.user)
            except MusobaqaUrinish.DoesNotExist:
                return Response({'detail': 'Avval musobaqani boshlang.'}, status=status.HTTP_400_BAD_REQUEST)
            if attempt.status == MusobaqaUrinish.STATUS_YAKUN:
                return Response({'detail': 'Natija avval saqlangan.', 'foiz': float(attempt.foiz)}, status=status.HTTP_400_BAD_REQUEST)
            questions = Savol.objects.filter(id__in=attempt.savol_idlari).prefetch_related('javoblar')
            correct_count = 0
            saved_answers = []
            for question in questions:
                item = answer_map.get(question.id, {})
                if question.tur == Savol.TUR_TEXT:
                    text_answer = str(item.get('matn_javob') or '').strip().casefold()
                    correct = bool(text_answer) and text_answer == (question.togri_matn_javob or '').strip().casefold()
                    saved_answers.append({'savol': question.id, 'matn_javob': item.get('matn_javob', ''), 'togri': correct})
                else:
                    selected_ids = {int(value) for value in item.get('tanlangan_javoblar', [])}
                    correct_ids = set(question.javoblar.filter(togri=True).values_list('id', flat=True))
                    correct = bool(selected_ids) and selected_ids == correct_ids
                    saved_answers.append({'savol': question.id, 'tanlangan_javoblar': list(selected_ids), 'togri': correct})
                if correct:
                    correct_count += 1
            now = timezone.now()
            elapsed = max(1, int((now - attempt.boshlangan_vaqt).total_seconds()))
            total = len(attempt.savol_idlari) or 1
            percentage = round((correct_count / total) * 100, 2)
            attempt.togri_soni = correct_count
            attempt.jami_soni = total
            attempt.foiz = percentage
            attempt.sarflangan_soniya = min(elapsed, obj.davomiyligi_daq * 60)
            attempt.javoblar = saved_answers
            attempt.status = MusobaqaUrinish.STATUS_YAKUN
            attempt.tugagan_vaqt = now
            attempt.save()
        return Response({
            'detail': 'Musobaqa yakunlandi.',
            'foiz': percentage,
            'togri_soni': correct_count,
            'jami_soni': total,
            'sarflangan_soniya': attempt.sarflangan_soniya,
            'reyting': _competition_ranking(obj, 20),
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def yakunlash(self, request, pk=None):
        obj = self.get_object()
        if obj.status == Musobaqa.STATUS_YAKUN:
            return Response({'detail': 'Bu musobaqa avval yakunlangan.'}, status=status.HTTP_400_BAD_REQUEST)
        ranking = _competition_ranking(obj, 3)
        prizes = [obj.birinchi_coin, obj.ikkinchi_coin, obj.uchinchi_coin]
        winners = []
        for index, item in enumerate(ranking):
            user = User.objects.get(pk=item['oquvchi_id'])
            coin_qoshish(user, prizes[index], 'admin', f"{obj.nomi}: {index + 1}-o'rin")
            winners.append({**item, 'bonus_coin': prizes[index]})
        obj.goliblar = winners
        obj.status = Musobaqa.STATUS_YAKUN
        obj.yakunlangan_vaqt = timezone.now()
        obj.save(update_fields=['goliblar', 'status', 'yakunlangan_vaqt'])
        log_amal(request.user, 'musobaqa_yakunlandi', obj.nomi, obyekt_turi='Musobaqa', obyekt_id=obj.pk, yangi_holat={'goliblar': winners}, request=request)
        return Response(MusobaqaSerializer(obj, context={'request': request}).data)

