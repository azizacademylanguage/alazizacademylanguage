from datetime import timedelta

from django.db.models import Max
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsOquvchi
from courses.access import daraja_ochiqmi, mavzu_ochiqmi, mavzu_testdan_otilganmi
from courses.models import Dars, OquvchiFan
from courses.utils import toza_daraja_nomi

from .engagement import faollik_qayd_et, streak_hisobla
from .models import (
    Bildirishnoma,
    FinalTestNatija,
    KunlikFaollik,
    ListeningNatija,
    ListeningSavol,
    MashqNatija,
    SozJuftligi,
)
from .serializers_extra import (
    BildirishnomaSerializer,
    ListeningNatijaSerializer,
    ListeningSavolOquvchigaSerializer,
)


def _darsga_ruxsat(oquvchi, dars):
    return (
        OquvchiFan.objects.filter(oquvchi=oquvchi, daraja__fan=dars.mavzu.daraja.fan).exists()
        and daraja_ochiqmi(oquvchi, dars.mavzu.daraja)
        and mavzu_ochiqmi(oquvchi, dars.mavzu)
    )


class ListeningSavollarView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request, dars_id):
        try:
            dars = Dars.objects.select_related('mavzu__daraja__fan').get(id=dars_id)
        except Dars.DoesNotExist:
            return Response({'detail': 'Dars topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        if not _darsga_ruxsat(request.user, dars):
            return Response({'detail': "Bu listening mashqi sizga hali ochilmagan."}, status=status.HTTP_403_FORBIDDEN)

        savollar = ListeningSavol.objects.filter(dars=dars)
        best = ListeningNatija.objects.filter(oquvchi=request.user, dars=dars).aggregate(v=Max('foiz'))['v'] or 0
        return Response({
            'dars': dars.id,
            'sarlavha': f'{dars.sarlavha} — Listening',
            'savollar': ListeningSavolOquvchigaSerializer(savollar, many=True).data,
            'eng_yaxshi_foiz': float(best),
            'otish_foizi': 80,
        })


class ListeningTopshirishView(APIView):
    permission_classes = [IsOquvchi]

    def post(self, request, dars_id):
        try:
            dars = Dars.objects.select_related('mavzu__daraja__fan').get(id=dars_id)
        except Dars.DoesNotExist:
            return Response({'detail': 'Dars topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        if not _darsga_ruxsat(request.user, dars):
            return Response({'detail': "Bu listening mashqi sizga hali ochilmagan."}, status=status.HTTP_403_FORBIDDEN)

        savollar = {q.id: q for q in ListeningSavol.objects.filter(dars=dars)}
        if not savollar:
            return Response({'detail': 'Listening savollari tayyor emas.'}, status=status.HTTP_404_NOT_FOUND)

        answer_rows = request.data.get('javoblar', [])
        answers = {int(row.get('savol')): str(row.get('javob', '')).strip() for row in answer_rows if row.get('savol')}
        correct = sum(1 for qid, question in savollar.items() if answers.get(qid, '').casefold() == question.togri_javob.strip().casefold())
        total = len(savollar)
        percentage = round(correct * 100 / total, 2)
        result = ListeningNatija.objects.create(
            oquvchi=request.user,
            dars=dars,
            togri_soni=correct,
            jami_soni=total,
            foiz=percentage,
            javoblar=answer_rows,
        )
        faollik_qayd_et(request.user, 'listening')
        data = ListeningNatijaSerializer(result).data
        data['otdi'] = percentage >= 80
        data['xabar'] = (
            "Listening mashqidan muvaffaqiyatli o'tdingiz."
            if percentage >= 80
            else "Kamida 80% olish uchun yana bir marta tinglab ko‘ring."
        )
        return Response(data, status=status.HTTP_201_CREATED)


class OqishRejasiView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        streak = faollik_qayd_et(request.user, 'panel')
        assignment = (
            OquvchiFan.objects.filter(oquvchi=request.user)
            .select_related('daraja__fan')
            .order_by('-created_at', '-id')
            .first()
        )
        if not assignment:
            return Response({
                'fan': None,
                'bugungi_dars': None,
                'qaytarish_sozlari': [],
                'haftalik_maqsad': {'maqsad': 5, 'bajarildi': 0, 'foiz': 0},
                'streak': streak,
                'tavsiyalar': ["Admin sizga fan va boshlang‘ich darajani biriktirishi kerak."],
            })

        fan = assignment.daraja.fan
        levels = list(fan.darajalar.all().order_by('tartib', 'id'))
        open_levels = [level for level in levels if daraja_ochiqmi(request.user, level)]
        current_level = open_levels[-1] if open_levels else assignment.daraja

        today_lesson = None
        topics = list(current_level.mavzular.prefetch_related('darslar__mashq').all().order_by('tartib', 'id'))
        completed_topics = 0
        for topic in topics:
            if mavzu_testdan_otilganmi(request.user, topic):
                completed_topics += 1
                continue
            if mavzu_ochiqmi(request.user, topic):
                lesson = topic.darslar.order_by('tartib', 'id').first()
                if lesson:
                    best = 0
                    if hasattr(lesson, 'mashq'):
                        best = MashqNatija.objects.filter(
                            oquvchi=request.user,
                            mashq=lesson.mashq,
                        ).aggregate(v=Max('foiz'))['v'] or 0
                    today_lesson = {
                        'dars_id': lesson.id,
                        'mavzu_id': topic.id,
                        'mavzu_nomi': topic.nomi,
                        'dars_nomi': lesson.sarlavha,
                        'daraja_id': current_level.id,
                        'daraja_nomi': toza_daraja_nomi(current_level.nomi),
                        'eng_yaxshi_foiz': float(best),
                    }
                break

        if not today_lesson and topics:
            final_passed = FinalTestNatija.objects.filter(
                oquvchi=request.user,
                final_test__daraja=current_level,
                otdi=True,
                foiz__gte=80,
            ).exists()
            today_lesson = {
                'yakuniy_test': not final_passed,
                'daraja_id': current_level.id,
                'daraja_nomi': toza_daraja_nomi(current_level.nomi),
                'mavzu_nomi': 'Daraja yakuniy testi' if not final_passed else 'Daraja tugatilgan',
                'dars_nomi': '10 savollik yakuniy test' if not final_passed else 'Keyingi darajaga o‘ting',
                'eng_yaxshi_foiz': 100 if final_passed else 0,
            }

        words = list(SozJuftligi.objects.filter(fan=fan, faol=True).order_by('tartib', 'id'))
        if words:
            offset = timezone.localdate().toordinal() % len(words)
            rotated = words[offset:] + words[:offset]
            review_words = [{'chet_soz': w.chet_soz, 'uzbek_soz': w.uzbek_soz} for w in rotated[:5]]
        else:
            review_words = []

        week_start = timezone.localdate() - timedelta(days=6)
        weekly_actions = sum(
            KunlikFaollik.objects.filter(oquvchi=request.user, sana__gte=week_start)
            .values_list('faollik_soni', flat=True)
        )
        goal = 5
        goal_completed = min(goal, weekly_actions)

        recommendations = []
        if today_lesson:
            recommendations.append("Bugungi tavsiya qilingan darsni yakunlang.")
        recommendations.append("5 ta so‘zni ovoz chiqarib uch marta takrorlang.")
        if streak.get('joriy', 0) < 7:
            recommendations.append("7 kunlik streak uchun har kuni kamida bitta mashq bajaring.")
        else:
            recommendations.append("Faollik seriyangizni davom ettiring — har 7 kunda bonus coin bor.")

        return Response({
            'fan': {'id': fan.id, 'nomi': fan.nomi, 'icon': fan.icon},
            'joriy_daraja': {
                'id': current_level.id,
                'nomi': toza_daraja_nomi(current_level.nomi),
                'mavzular_soni': len(topics),
                'tugatilgan_mavzular': completed_topics,
            },
            'bugungi_dars': today_lesson,
            'qaytarish_sozlari': review_words,
            'haftalik_maqsad': {
                'maqsad': goal,
                'bajarildi': goal_completed,
                'foiz': round(goal_completed * 100 / goal),
            },
            'streak': streak,
            'tavsiyalar': recommendations,
        })


class StreakView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        stats = streak_hisobla(request.user)
        last_14 = list(
            KunlikFaollik.objects.filter(
                oquvchi=request.user,
                sana__gte=timezone.localdate() - timedelta(days=13),
            ).values('sana', 'faollik_soni', 'turlar')
        )
        stats['kunlar'] = last_14
        stats['keyingi_bonus'] = 7 - (stats['joriy'] % 7) if stats['joriy'] % 7 else 7
        return Response(stats)


class BildirishnomalarView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        notifications = Bildirishnoma.objects.filter(oquvchi=request.user)[:50]
        unread = Bildirishnoma.objects.filter(oquvchi=request.user, oqilgan=False).count()
        return Response({
            'oqilmagan_soni': unread,
            'natijalar': BildirishnomaSerializer(notifications, many=True).data,
        })


class BildirishnomaOqildiView(APIView):
    permission_classes = [IsOquvchi]

    def patch(self, request, notification_id):
        try:
            notification = Bildirishnoma.objects.get(id=notification_id, oquvchi=request.user)
        except Bildirishnoma.DoesNotExist:
            return Response({'detail': 'Bildirishnoma topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        notification.oqilgan = True
        notification.save(update_fields=['oqilgan'])
        return Response(BildirishnomaSerializer(notification).data)


class BarchaBildirishnomalarOqildiView(APIView):
    permission_classes = [IsOquvchi]

    def post(self, request):
        updated = Bildirishnoma.objects.filter(oquvchi=request.user, oqilgan=False).update(oqilgan=True)
        return Response({'yangilandi': updated})
