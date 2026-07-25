import io
import json
import random
import tempfile
import zipfile
from datetime import timedelta

from django.core.management import call_command
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdmin, IsOquvchi
from courses.models import Fan, Daraja, OquvchiFan

from .coins import coin_qoshish
from .features import (
    check_achievements, client_ip, create_notification, faoliyat_streak,
    log_faoliyat, notifications_for_user, payment_state, record_test_security,
    ensure_default_achievements,
)
from .models import (
    Bildirishnoma, BildirishnomaOqildi, PlacementNatija, GateTestSavol,
    TestXavfsizlikLog, FaoliyatLog, Yutuq, OquvchiYutuq, Tolov,
    SozJuftligi, TezkorOyiniSessiya, OquvchiCoin, PlatformSozlama,
    Sertifikat,
)


def _notification_data(obj, user=None):
    data = {
        'id': obj.id,
        'sarlavha': obj.sarlavha,
        'matn': obj.matn,
        'tur': obj.tur,
        'tur_display': obj.get_tur_display(),
        'target_turi': obj.target_turi,
        'target_display': obj.get_target_turi_display(),
        'target_user': obj.target_user_id,
        'target_user_ism': obj.target_user.full_name if obj.target_user else '',
        'target_fan': obj.target_fan_id,
        'target_fan_nomi': obj.target_fan.nomi if obj.target_fan else '',
        'target_daraja': obj.target_daraja_id,
        'target_daraja_nomi': obj.target_daraja.nomi if obj.target_daraja else '',
        'havola': obj.havola,
        'faol': obj.faol,
        'created_at': obj.created_at,
        'tugash_sana': obj.tugash_sana,
        'oqilganlar_soni': obj.oqilganlar.count() if hasattr(obj, 'oqilganlar') else 0,
    }
    if user:
        data['oqilgan'] = obj.oqilganlar.filter(oquvchi=user).exists()
    return data


class MeningBildirishnomalarimView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        qs = notifications_for_user(request.user).select_related('target_user', 'target_fan', 'target_daraja')[:100]
        data = [_notification_data(item, request.user) for item in qs]
        return Response({'oqilmagan_soni': sum(1 for item in data if not item['oqilgan']), 'natijalar': data})


class BildirishnomaOqishView(APIView):
    permission_classes = [IsOquvchi]

    def post(self, request, bildirishnoma_id):
        try:
            obj = notifications_for_user(request.user).get(id=bildirishnoma_id)
        except Bildirishnoma.DoesNotExist:
            return Response({'detail': 'Bildirishnoma topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        BildirishnomaOqildi.objects.get_or_create(bildirishnoma=obj, oquvchi=request.user)
        log_faoliyat(request, 'bildirishnoma_oqildi', obj.sarlavha, 'bildirishnoma', obj.id)
        return Response({'detail': 'O‘qildi deb belgilandi.'})


class BarchaBildirishnomalarniOqishView(APIView):
    permission_classes = [IsOquvchi]

    def post(self, request):
        for obj in notifications_for_user(request.user):
            BildirishnomaOqildi.objects.get_or_create(bildirishnoma=obj, oquvchi=request.user)
        return Response({'detail': 'Barcha bildirishnomalar o‘qildi deb belgilandi.'})


class AdminBildirishnomalarView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = Bildirishnoma.objects.select_related('target_user', 'target_fan', 'target_daraja', 'created_by')[:200]
        return Response([_notification_data(item) for item in qs])

    def post(self, request):
        title = (request.data.get('sarlavha') or '').strip()
        body = (request.data.get('matn') or '').strip()
        target_type = request.data.get('target_turi') or 'all'
        if not title or not body:
            return Response({'detail': 'Sarlavha va matn majburiy.'}, status=status.HTTP_400_BAD_REQUEST)
        if target_type not in dict(Bildirishnoma.TARGET_CHOICES):
            return Response({'detail': 'Noto‘g‘ri qabul qiluvchi turi.'}, status=status.HTTP_400_BAD_REQUEST)
        target_user = request.data.get('target_user') or None
        target_fan = request.data.get('target_fan') or None
        target_daraja = request.data.get('target_daraja') or None
        if target_type == Bildirishnoma.TARGET_USER and not User.objects.filter(id=target_user, role=User.ROLE_OQUVCHI).exists():
            return Response({'detail': 'Qabul qiluvchi o‘quvchini tanlang.'}, status=status.HTTP_400_BAD_REQUEST)
        if target_type == Bildirishnoma.TARGET_FAN and not Fan.objects.filter(id=target_fan).exists():
            return Response({'detail': 'Qabul qiluvchi fanni tanlang.'}, status=status.HTTP_400_BAD_REQUEST)
        if target_type == Bildirishnoma.TARGET_DARAJA and not Daraja.objects.filter(id=target_daraja).exists():
            return Response({'detail': 'Qabul qiluvchi darajani tanlang.'}, status=status.HTTP_400_BAD_REQUEST)
        obj = Bildirishnoma.objects.create(
            sarlavha=title,
            matn=body,
            tur=request.data.get('tur') or 'info',
            target_turi=target_type,
            target_user_id=target_user if target_type == Bildirishnoma.TARGET_USER else None,
            target_fan_id=target_fan if target_type == Bildirishnoma.TARGET_FAN else None,
            target_daraja_id=target_daraja if target_type == Bildirishnoma.TARGET_DARAJA else None,
            havola=(request.data.get('havola') or '').strip(),
            tugash_sana=request.data.get('tugash_sana') or None,
            created_by=request.user,
        )
        log_faoliyat(request, 'bildirishnoma_yaratildi', title, 'bildirishnoma', obj.id)
        return Response(_notification_data(obj), status=status.HTTP_201_CREATED)


class AdminBildirishnomaDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, bildirishnoma_id):
        try:
            obj = Bildirishnoma.objects.get(id=bildirishnoma_id)
        except Bildirishnoma.DoesNotExist:
            return Response({'detail': 'Bildirishnoma topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        for key in ['sarlavha', 'matn', 'tur', 'target_turi', 'havola', 'faol', 'tugash_sana']:
            if key in request.data:
                setattr(obj, key, request.data[key])
        for key in ['target_user', 'target_fan', 'target_daraja']:
            if key in request.data:
                setattr(obj, f'{key}_id', request.data[key] or None)
        obj.save()
        return Response(_notification_data(obj))

    def delete(self, request, bildirishnoma_id):
        deleted, _ = Bildirishnoma.objects.filter(id=bildirishnoma_id).delete()
        if not deleted:
            return Response({'detail': 'Bildirishnoma topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- PLACEMENT TEST --------------------

def _placement_questions(fan):
    questions = list(
        GateTestSavol.objects.filter(gate_test__daraja__fan=fan)
        .select_related('gate_test__daraja')
        .prefetch_related('javoblar')
        .order_by('gate_test__daraja__tartib', 'tartib')
    )
    if not questions:
        return []
    levels = {}
    for question in questions:
        levels.setdefault(question.gate_test.daraja_id, []).append(question)
    selected = []
    while len(selected) < min(20, len(questions)):
        changed = False
        for items in levels.values():
            if items and len(selected) < 20:
                selected.append(items.pop(0))
                changed = True
        if not changed:
            break
    random.shuffle(selected)
    result = []
    for question in selected:
        variants = list(question.javoblar.all())
        random.shuffle(variants)
        result.append({
            'id': question.id,
            'matn': question.matn,
            'daraja_id': question.gate_test.daraja_id,
            'javoblar': [{'id': answer.id, 'matn': answer.matn} for answer in variants],
        })
    return result


def _recommended_level(fan, percent):
    levels = list(Daraja.objects.filter(fan=fan).order_by('tartib', 'id'))
    if not levels:
        return None
    if len(levels) == 1:
        return levels[0]
    ratio = min(max(float(percent) / 100, 0), 0.9999)
    index = min(int(ratio * len(levels)), len(levels) - 1)
    return levels[index]


class PlacementTestView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        fan_id = request.query_params.get('fan')
        assigned_fans = Fan.objects.filter(
            darajalar__biriktirilgan_oquvchilar__oquvchi=request.user,
        ).distinct()
        if fan_id:
            try:
                fan = assigned_fans.get(id=fan_id)
            except (Fan.DoesNotExist, ValueError, TypeError):
                return Response({'detail': 'Bu fan sizga biriktirilmagan.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            fan = assigned_fans.first()
        if not fan:
            return Response({'detail': 'Placement test uchun sizga biriktirilgan fan topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        questions = _placement_questions(fan)
        if len(questions) < 5:
            return Response({'detail': 'Bu fan uchun kamida 5 ta Gate Test savoli kerak.'}, status=status.HTTP_400_BAD_REQUEST)
        log_faoliyat(request, 'placement_boshlandi', fan.nomi, 'fan', fan.id)
        return Response({'fan': {'id': fan.id, 'nomi': fan.nomi}, 'vaqt_chegarasi_daq': 25, 'savollar': questions})

    def post(self, request):
        try:
            fan = Fan.objects.filter(
                darajalar__biriktirilgan_oquvchilar__oquvchi=request.user,
            ).distinct().get(id=request.data.get('fan'))
        except (Fan.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Bu fan sizga biriktirilmagan.'}, status=status.HTTP_403_FORBIDDEN)
        answers = request.data.get('javoblar') or []
        question_ids = list({item.get('savol') for item in answers if isinstance(item, dict) and item.get('savol')})
        if len(question_ids) < 5:
            return Response({'detail': 'Placement testda kamida 5 ta savolga javob berish kerak.'}, status=status.HTTP_400_BAD_REQUEST)
        questions = {q.id: q for q in GateTestSavol.objects.filter(id__in=question_ids, gate_test__daraja__fan=fan).prefetch_related('javoblar')}
        correct = 0
        saved_answers = []
        for item in answers:
            question = questions.get(item.get('savol'))
            if not question:
                continue
            selected = set(item.get('tanlangan_javoblar') or [])
            right = set(question.javoblar.filter(togri=True).values_list('id', flat=True))
            is_right = bool(selected) and selected == right
            correct += int(is_right)
            saved_answers.append({'savol': question.id, 'tanlangan': list(selected), 'togri': is_right})
        total = len(questions) or 1
        percent = round(correct / total * 100, 2)
        recommended = _recommended_level(fan, percent)
        security = request.data.get('xavfsizlik') or {}
        result = PlacementNatija.objects.create(
            oquvchi=request.user, fan=fan, togri_soni=correct, jami_soni=total,
            foiz=percent, tavsiya_daraja=recommended, javoblar=saved_answers, xavfsizlik=security,
        )
        record_test_security(request, 'placement', fan.id, security)
        log_faoliyat(request, 'placement_yakunlandi', f'{fan.nomi}: {percent}%', 'placement', result.id, {'foiz': percent})
        return Response({
            'id': result.id, 'togri_soni': correct, 'jami_soni': total, 'foiz': percent,
            'tavsiya_daraja': {'id': recommended.id, 'nomi': recommended.nomi} if recommended else None,
            'xabar': f'Sizga {recommended.nomi} darajasi tavsiya qilinadi.' if recommended else 'Daraja topilmadi.',
        }, status=status.HTTP_201_CREATED)


class AdminPlacementNatijalarView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = PlacementNatija.objects.select_related('oquvchi', 'fan', 'tavsiya_daraja')[:200]
        return Response([{
            'id': item.id, 'oquvchi_id': item.oquvchi_id, 'oquvchi_ism': item.oquvchi.full_name,
            'username': item.oquvchi.username, 'fan': item.fan.nomi, 'foiz': item.foiz,
            'tavsiya_daraja': item.tavsiya_daraja.nomi if item.tavsiya_daraja else '',
            'tavsiya_daraja_id': item.tavsiya_daraja_id,
            'tasdiqlangan': item.tasdiqlangan,
            'tasdiqlangan_at': item.tasdiqlangan_at,
            'created_at': item.created_at,
        } for item in qs])


class AdminPlacementTasdiqlashView(APIView):
    permission_classes = [IsAdmin]

    @transaction.atomic
    def post(self, request, natija_id):
        try:
            item = PlacementNatija.objects.select_for_update().select_related('oquvchi', 'tavsiya_daraja', 'fan').get(id=natija_id)
        except PlacementNatija.DoesNotExist:
            return Response({'detail': 'Placement natijasi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        if not item.tavsiya_daraja:
            return Response({'detail': 'Tavsiya qilingan daraja topilmadi.'}, status=status.HTTP_400_BAD_REQUEST)
        OquvchiFan.objects.filter(oquvchi=item.oquvchi).delete()
        OquvchiFan.objects.create(
            oquvchi=item.oquvchi,
            daraja=item.tavsiya_daraja,
            biriktirgan=request.user,
            qolda_ochilgan=True,
        )
        item.tasdiqlangan = True
        item.tasdiqlagan = request.user
        item.tasdiqlangan_at = timezone.now()
        item.save(update_fields=['tasdiqlangan', 'tasdiqlagan', 'tasdiqlangan_at'])
        create_notification(
            'Darajangiz tasdiqlandi',
            f'{item.fan.nomi} fanidan {item.tavsiya_daraja.nomi} darajasi sizga biriktirildi.',
            user=item.oquvchi,
            tur='success',
            link='/oquvchi/fanlarim',
            created_by=request.user,
        )
        log_faoliyat(request, 'placement_tasdiqlandi', f'{item.oquvchi.full_name}: {item.tavsiya_daraja.nomi}', 'placement', item.id)
        return Response({'detail': 'Tavsiya qilingan daraja o‘quvchiga biriktirildi.', 'tasdiqlangan': True})


# -------------------- SECURITY / ACTIVITY --------------------

class MeningFaoliyatimView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        qs = FaoliyatLog.objects.filter(user=request.user)[:100]
        return Response({'streak': faoliyat_streak(request.user), 'natijalar': [
            {'id': x.id, 'amal': x.amal, 'tavsif': x.tavsif, 'meta': x.meta, 'created_at': x.created_at}
            for x in qs
        ]})


class AdminFaoliyatView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = FaoliyatLog.objects.select_related('user').all()
        user_id = request.query_params.get('user')
        action = request.query_params.get('amal')
        if user_id:
            qs = qs.filter(user_id=user_id)
        if action:
            qs = qs.filter(amal=action)
        qs = qs[:300]
        return Response([{
            'id': x.id, 'user_id': x.user_id, 'full_name': x.user.full_name,
            'username': x.user.username, 'role': x.user.role, 'amal': x.amal,
            'tavsif': x.tavsif, 'ip_manzil': x.ip_manzil, 'qurilma': x.user_agent,
            'meta': x.meta, 'created_at': x.created_at,
        } for x in qs])


class AdminTestXavfsizligiView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = TestXavfsizlikLog.objects.select_related('oquvchi').all()
        only_suspicious = request.query_params.get('shubhali') == '1'
        if only_suspicious:
            qs = qs.filter(shubhali=True)
        qs = qs[:300]
        return Response({
            'jami': TestXavfsizlikLog.objects.count(),
            'shubhali_soni': TestXavfsizlikLog.objects.filter(shubhali=True).count(),
            'natijalar': [{
                'id': x.id, 'oquvchi_id': x.oquvchi_id, 'oquvchi_ism': x.oquvchi.full_name,
                'username': x.oquvchi.username, 'test_turi': x.test_turi,
                'obyekt_id': x.obyekt_id, 'davomiylik_soniya': x.davomiylik_soniya,
                'sahifadan_chiqish_soni': x.sahifadan_chiqish_soni,
                'shubhali': x.shubhali, 'sabablar': x.sabablar, 'ip_manzil': x.ip_manzil,
                'created_at': x.created_at,
            } for x in qs],
        })


# -------------------- ACHIEVEMENTS --------------------

class MeningYutuqlarimView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        ensure_default_achievements()
        check_achievements(request.user)
        owned = {x.yutuq_id: x for x in OquvchiYutuq.objects.filter(oquvchi=request.user).select_related('yutuq')}
        achievements = []
        for item in Yutuq.objects.filter(faol=True):
            got = owned.get(item.id)
            achievements.append({
                'id': item.id, 'kod': item.kod, 'nomi': item.nomi, 'tavsif': item.tavsif,
                'icon': item.icon, 'coin_mukofot': item.coin_mukofot,
                'olingan': bool(got), 'olingan_at': got.olingan_at if got else None,
            })
        return Response({'streak': faoliyat_streak(request.user), 'yutuqlar': achievements})


# -------------------- PAYMENTS --------------------

class MeningTolovimView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        state = payment_state(request.user)
        settings = PlatformSozlama.load()
        if (
            state.get('tolov')
            and state.get('qolgan_kun') is not None
            and 0 <= state['qolgan_kun'] <= settings.tolov_ogohlantirish_kun
        ):
            title = 'To‘lov muddati yaqinlashdi'
            body = (
                f'Platformadan foydalanish muddati {state["tolov"]["tugash_sana"]} kuni tugaydi. '
                f'Qolgan vaqt: {state["qolgan_kun"]} kun.'
            )
            already_sent_today = Bildirishnoma.objects.filter(
                target_turi=Bildirishnoma.TARGET_USER,
                target_user=request.user,
                sarlavha=title,
                matn=body,
                created_at__date=timezone.localdate(),
            ).exists()
            if not already_sent_today:
                create_notification(
                    title,
                    body,
                    user=request.user,
                    tur='warning',
                    link='/oquvchi/tolovim',
                )
        history = Tolov.objects.filter(oquvchi=request.user)[:30]
        state['tarix'] = [{
            'id': x.id, 'summa': x.summa, 'tolangan_summa': x.tolangan_summa,
            'qolgan_summa': x.qolgan_summa, 'chegirma_foiz': x.chegirma_foiz,
            'boshlanish_sana': x.boshlanish_sana, 'tugash_sana': x.tugash_sana,
            'status': x.status, 'status_display': x.get_status_display(), 'izoh': x.izoh,
        } for x in history]
        return Response(state)


class AdminTolovlarView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = Tolov.objects.select_related('oquvchi', 'oquvchi__filial').all()
        q = (request.query_params.get('q') or '').strip()
        if q:
            qs = qs.filter(Q(oquvchi__ism__icontains=q) | Q(oquvchi__familya__icontains=q) | Q(oquvchi__username__icontains=q))
        return Response([self._data(x) for x in qs[:300]])

    def post(self, request):
        try:
            student = User.objects.get(id=request.data.get('oquvchi'), role=User.ROLE_OQUVCHI)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'O‘quvchi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        required = ['boshlanish_sana', 'tugash_sana']
        if any(not request.data.get(x) for x in required):
            return Response({'detail': 'Boshlanish va tugash sanasi majburiy.'}, status=status.HTTP_400_BAD_REQUEST)
        obj = Tolov.objects.create(
            oquvchi=student,
            summa=request.data.get('summa') or 0,
            tolangan_summa=request.data.get('tolangan_summa') or 0,
            chegirma_foiz=request.data.get('chegirma_foiz') or 0,
            boshlanish_sana=request.data['boshlanish_sana'],
            tugash_sana=request.data['tugash_sana'],
            status=request.data.get('status') or 'qarzdor',
            izoh=request.data.get('izoh') or '',
            created_by=request.user,
        )
        create_notification('To‘lov ma’lumoti yangilandi', f'Foydalanish muddati: {obj.boshlanish_sana} — {obj.tugash_sana}. Holat: {obj.get_status_display()}.', user=student, tur='info', link='/oquvchi/tolovim', created_by=request.user)
        log_faoliyat(request, 'tolov_kiritildi', student.full_name, 'tolov', obj.id)
        return Response(self._data(obj), status=status.HTTP_201_CREATED)

    @staticmethod
    def _data(x):
        return {
            'id': x.id, 'oquvchi': x.oquvchi_id, 'oquvchi_ism': x.oquvchi.full_name,
            'username': x.oquvchi.username, 'filial_nomi': x.oquvchi.filial.nomi if x.oquvchi.filial else '',
            'summa': x.summa, 'tolangan_summa': x.tolangan_summa, 'qolgan_summa': x.qolgan_summa,
            'chegirma_foiz': x.chegirma_foiz, 'boshlanish_sana': x.boshlanish_sana,
            'tugash_sana': x.tugash_sana, 'status': x.status, 'status_display': x.get_status_display(),
            'izoh': x.izoh, 'created_at': x.created_at,
        }


class AdminTolovDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, tolov_id):
        try:
            obj = Tolov.objects.select_related('oquvchi', 'oquvchi__filial').get(id=tolov_id)
        except Tolov.DoesNotExist:
            return Response({'detail': 'To‘lov topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        for key in ['summa', 'tolangan_summa', 'chegirma_foiz', 'boshlanish_sana', 'tugash_sana', 'status', 'izoh']:
            if key in request.data:
                setattr(obj, key, request.data[key])
        obj.save()
        create_notification('To‘lov holati o‘zgardi', f'Yangi holat: {obj.get_status_display()}. Muddati: {obj.tugash_sana}.', user=obj.oquvchi, tur='warning', link='/oquvchi/tolovim', created_by=request.user)
        return Response(AdminTolovlarView._data(obj))

    def delete(self, request, tolov_id):
        deleted, _ = Tolov.objects.filter(id=tolov_id).delete()
        if not deleted:
            return Response({'detail': 'To‘lov topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------- NEW QUICK TRANSLATION GAME --------------------

class TezkorOyiniBoshlashView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        today = timezone.localdate()
        today_completed = TezkorOyiniSessiya.objects.filter(oquvchi=request.user, tugallangan=True, completed_at__date=today).count()
        if today_completed >= 3:
            return Response({'detail': 'Bugungi 3 ta mukofotli o‘yin limitingiz tugadi. Ertaga yana o‘ynang.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        fan = Fan.objects.filter(darajalar__biriktirilgan_oquvchilar__oquvchi=request.user).distinct().first()
        if not fan:
            return Response({'detail': 'Avval sizga fan biriktirilishi kerak.'}, status=status.HTTP_400_BAD_REQUEST)
        pairs = list(SozJuftligi.objects.filter(fan=fan, faol=True))
        if len(pairs) < 10:
            return Response({'detail': 'O‘yin uchun kamida 10 ta so‘z juftligi kerak.'}, status=status.HTTP_400_BAD_REQUEST)
        selected = random.sample(pairs, 10)
        all_options = [x.uzbek_soz for x in pairs]
        questions = []
        for idx, pair in enumerate(selected, 1):
            direction = random.choice(['chet_uz', 'uz_chet'])
            if direction == 'chet_uz':
                prompt, correct = pair.chet_soz, pair.uzbek_soz
                pool = all_options
            else:
                prompt, correct = pair.uzbek_soz, pair.chet_soz
                pool = [x.chet_soz for x in pairs]
            wrong = random.sample([x for x in pool if x != correct], min(3, len(pool) - 1))
            options = wrong + [correct]
            random.shuffle(options)
            questions.append({'id': idx, 'savol': prompt, 'togri': correct, 'variantlar': options, 'yonalish': direction})
        session = TezkorOyiniSessiya.objects.create(oquvchi=request.user, fan=fan, savollar=questions, jami_soni=len(questions))
        log_faoliyat(request, 'tezkor_oyin_boshlandi', fan.nomi, 'tezkor_oyin', session.id)
        public = [{k: v for k, v in item.items() if k != 'togri'} for item in questions]
        return Response({'token': session.token, 'fan': fan.nomi, 'vaqt_soniya': 90, 'qolgan_oyin': 3 - today_completed, 'savollar': public})


class TezkorOyiniYakunlashView(APIView):
    permission_classes = [IsOquvchi]

    @transaction.atomic
    def post(self, request, token):
        try:
            session = TezkorOyiniSessiya.objects.select_for_update().get(token=token, oquvchi=request.user)
        except TezkorOyiniSessiya.DoesNotExist:
            return Response({'detail': 'O‘yin sessiyasi topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        balance, _ = OquvchiCoin.objects.get_or_create(oquvchi=request.user)
        if session.tugallangan:
            return Response({'togri_soni': session.togri_soni, 'berilgan_coin': session.berilgan_coin, 'balans': balance.balans, 'allaqachon_yakunlangan': True})
        answers = request.data.get('javoblar') or []
        answer_map = {}
        for item in answers:
            if not isinstance(item, dict):
                continue
            try:
                question_id = int(item.get('savol'))
            except (TypeError, ValueError):
                continue
            answer_map[question_id] = str(item.get('javob') or '')
        correct = sum(1 for question in session.savollar if answer_map.get(int(question['id'])) == question['togri'])
        settings = PlatformSozlama.load()
        coins = correct * settings.tezkor_oyin_har_javob_coin
        if correct == session.jami_soni:
            coins += settings.tezkor_oyin_mukammal_bonus
        session.togri_soni = correct
        session.berilgan_coin = coins
        session.tugallangan = True
        session.completed_at = timezone.now()
        session.save(update_fields=['togri_soni', 'berilgan_coin', 'tugallangan', 'completed_at'])
        balance = coin_qoshish(request.user, coins, 'tezkor_oyin', f'{session.fan.nomi}: {correct}/{session.jami_soni}')
        check_achievements(request.user, game_score=correct)
        balance.refresh_from_db(fields=['balans'])
        log_faoliyat(request, 'tezkor_oyin_yakunlandi', f'{correct}/{session.jami_soni}', 'tezkor_oyin', session.id, {'coin': coins})
        return Response({'togri_soni': correct, 'jami_soni': session.jami_soni, 'foiz': round(correct / session.jami_soni * 100), 'berilgan_coin': coins, 'balans': balance.balans, 'xabar': f'{correct} ta to‘g‘ri javob va {coins} coin!'})


# -------------------- CERTIFICATE STATUS --------------------

class AdminSertifikatStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, sertifikat_id):
        try:
            obj = Sertifikat.objects.select_related('oquvchi').get(id=sertifikat_id)
        except Sertifikat.DoesNotExist:
            return Response({'detail': 'Sertifikat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        obj.faol = bool(request.data.get('faol', True))
        obj.bekor_sabab = request.data.get('bekor_sabab') or ''
        obj.bekor_qilingan_sana = None if obj.faol else timezone.now()
        obj.save(update_fields=['faol', 'bekor_sabab', 'bekor_qilingan_sana'])
        create_notification('Sertifikat holati yangilandi', f'{obj.kod} sertifikati holati: {"faol" if obj.faol else "bekor qilingan"}.', user=obj.oquvchi, tur='warning', link='/oquvchi/sertifikatlarim', created_by=request.user)
        return Response({'id': obj.id, 'faol': obj.faol, 'bekor_sabab': obj.bekor_sabab, 'bekor_qilingan_sana': obj.bekor_qilingan_sana})


# -------------------- BACKUP / RESTORE --------------------

class AdminBackupDownloadView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        out = io.StringIO()
        call_command(
            'dumpdata',
            exclude=['contenttypes', 'auth.permission', 'admin.logentry', 'sessions.session'],
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
            indent=2,
            stdout=out,
        )
        raw = out.getvalue().encode('utf-8')
        zip_buffer = io.BytesIO()
        stamp = timezone.localtime().strftime('%Y%m%d_%H%M%S')
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(f'alaziz_backup_{stamp}.json', raw)
            archive.writestr('README.txt', 'Tiklash uchun admin Backup bo‘limidan ushbu ZIP ichidagi JSON faylni yuklang.\n')
        log_faoliyat(request, 'backup_yuklandi', stamp)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="alaziz_backup_{stamp}.zip"'
        return response


class AdminBackupRestoreView(APIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded = request.FILES.get('file')
        confirmation = request.data.get('tasdiq')
        if confirmation != 'TIKLASH':
            return Response({'detail': 'Tasdiq maydoniga TIKLASH deb yozing.'}, status=status.HTTP_400_BAD_REQUEST)
        if not uploaded or not uploaded.name.lower().endswith('.json'):
            return Response({'detail': 'ZIP ichidan olingan .json backup faylini yuklang.'}, status=status.HTTP_400_BAD_REQUEST)
        max_bytes = PlatformSozlama.load().max_fayl_mb * 1024 * 1024
        if uploaded.size > max_bytes:
            return Response({'detail': 'Backup fayli ruxsat etilgan hajmdan katta.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            json.loads(uploaded.read().decode('utf-8'))
            uploaded.seek(0)
        except Exception:
            return Response({'detail': 'JSON backup fayli yaroqsiz.'}, status=status.HTTP_400_BAD_REQUEST)
        with tempfile.NamedTemporaryFile(suffix='.json') as tmp:
            for chunk in uploaded.chunks():
                tmp.write(chunk)
            tmp.flush()
            try:
                call_command('loaddata', tmp.name, verbosity=0)
            except Exception as exc:
                return Response({'detail': f'Tiklashda xato: {exc}'}, status=status.HTTP_400_BAD_REQUEST)
        log_faoliyat(request, 'backup_tiklandi', uploaded.name)
        return Response({'detail': 'Backup muvaffaqiyatli tiklandi.'})
