"""
Gate Test, Final Test, Sertifikat, Writing, Speaking, Coin/Shop, Admin audit log
uchun view'lar. Asosiy exams/views.py faylini ortiqcha kattalashtirmaslik uchun
alohida fayl.
"""
import logging
import random
import secrets
import string
import re
import unicodedata
from difflib import SequenceMatcher

from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction, IntegrityError
from django.db.models import Avg, Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission

from accounts.permissions import IsAdmin, IsNazoratchi, IsOquvchi
from courses.models import Daraja, OquvchiFan
from courses.access import (
    daraja_ochiqmi, daraja_mavzulari_tugaganmi, keyingi_daraja,
    oquvchiga_fan_biriktirilganmi,
)

from .models import (
    GateTest, GateTestSavol, GateTestJavob, GateTestNatija,
    FinalTest, FinalTestSavol, FinalTestJavob, FinalTestNatija, Sertifikat,
    WritingTopshiriq, WritingNatija, SpeakingTopshiriq, SpeakingNatija,
    OquvchiCoin, CoinTarix, ShopMahsulot, ShopBuyurtma, SozJuftligi, SozOyiniSessiya, AdminAmalLog,
)
from .serializers_extra import (
    GateTestSerializer, GateTestOquvchigaSerializer, GateTestNatijaSerializer,
    FinalTestSerializer, FinalTestOquvchigaSerializer, FinalTestNatijaSerializer, SertifikatSerializer,
    WritingTopshiriqSerializer, WritingNatijaSerializer,
    SpeakingTopshiriqSerializer, SpeakingNatijaSerializer,
    OquvchiCoinSerializer, CoinTarixSerializer, ShopMahsulotSerializer, ShopBuyurtmaSerializer,
    AdminAmalLogSerializer,
)
from .coins import coin_qoshish
from .audit import log_amal
from .engagement import bildirishnoma_yarat, faollik_qayd_et


logger = logging.getLogger(__name__)


def _xavfsiz_qoshimcha(nomi, callback):
    """Qo‘shimcha bonus/bildirishnoma xatosi asosiy test natijasini buzmasin."""
    try:
        return callback()
    except Exception:
        logger.exception("FINAL_TEST_AUX_FAILED step=%s", nomi)
        return None


def _sertifikatni_ol_yoki_yarat(oquvchi, daraja, foiz):
    """Legacy bazadagi dublikatlar va kod kolliziyalariga chidamli sertifikat yaratish."""
    sertifikat = (
        Sertifikat.objects.select_for_update()
        .filter(oquvchi=oquvchi, daraja=daraja)
        .order_by('id')
        .first()
    )
    created = False
    if sertifikat is None:
        for _ in range(8):
            try:
                # Ichki savepoint IntegrityError'dan keyin tashqi transactionni sog‘lom saqlaydi.
                with transaction.atomic():
                    sertifikat = Sertifikat.objects.create(
                        oquvchi=oquvchi,
                        daraja=daraja,
                        kod=_sertifikat_kod_yaratish(),
                        foiz=foiz,
                    )
                created = True
                break
            except IntegrityError:
                # Juda kam uchraydigan kod kolliziyasida yangi kod bilan qayta urinadi.
                continue
        if sertifikat is None:
            raise IntegrityError('Sertifikat uchun noyob kod yaratib bo‘lmadi.')

    if float(foiz) > float(sertifikat.foiz or 0):
        sertifikat.foiz = foiz
        sertifikat.save(update_fields=['foiz'])
    return sertifikat, created


# ==================== ADMIN CRUD: WRITING / SPEAKING TOPSHIRIQLAR ====================

class WritingTopshiriqViewSet(viewsets.ModelViewSet):
    serializer_class = WritingTopshiriqSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = WritingTopshiriq.objects.all()
        dars_id = self.request.query_params.get('dars')
        if dars_id:
            qs = qs.filter(dars_id=dars_id)
        return qs


class SpeakingTopshiriqViewSet(viewsets.ModelViewSet):
    serializer_class = SpeakingTopshiriqSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = SpeakingTopshiriq.objects.all()
        dars_id = self.request.query_params.get('dars')
        if dars_id:
            qs = qs.filter(dars_id=dars_id)
        return qs


# ==================== ADMIN CRUD: GATE TEST ====================

class GateTestViewSet(viewsets.ModelViewSet):
    queryset = GateTest.objects.all()
    serializer_class = GateTestSerializer
    permission_classes = [IsAdmin]


class GateTestSavolViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = GateTestSavol.objects.all()
        gate_test_id = self.request.query_params.get('gate_test')
        if gate_test_id:
            qs = qs.filter(gate_test_id=gate_test_id)
        return qs

    def get_serializer_class(self):
        from .serializers_extra import GateTestSavolSerializer
        return GateTestSavolSerializer


class GateTestJavobViewSet(viewsets.ModelViewSet):
    from .serializers_extra import GateTestJavobSerializer
    queryset = GateTestJavob.objects.all()
    serializer_class = GateTestJavobSerializer
    permission_classes = [IsAdmin]


# ==================== ADMIN CRUD: FINAL TEST ====================

class FinalTestViewSet(viewsets.ModelViewSet):
    queryset = FinalTest.objects.all()
    serializer_class = FinalTestSerializer
    permission_classes = [IsAdmin]


class FinalTestSavolViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = FinalTestSavol.objects.all()
        final_test_id = self.request.query_params.get('final_test')
        if final_test_id:
            qs = qs.filter(final_test_id=final_test_id)
        return qs

    def get_serializer_class(self):
        from .serializers_extra import FinalTestSavolSerializer
        return FinalTestSavolSerializer


class FinalTestJavobViewSet(viewsets.ModelViewSet):
    from .serializers_extra import FinalTestJavobSerializer
    queryset = FinalTestJavob.objects.all()
    serializer_class = FinalTestJavobSerializer
    permission_classes = [IsAdmin]


# ==================== O'QUVCHI: GATE TEST TOPSHIRISH ====================

class GateTestOlishView(APIView):
    """GET /api/oquvchi/gate-test/{daraja_id}/ -> shu darajaning Gate Test savollari
    (javoblarsiz, chunki bu — keyingi darajaga o'tish uchun ochish testi)"""
    permission_classes = [IsOquvchi]

    def get(self, request, daraja_id):
        try:
            daraja = Daraja.objects.get(id=daraja_id)
        except Daraja.DoesNotExist:
            return Response({'detail': 'Daraja topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(daraja, 'gate_test'):
            return Response({'detail': "Bu daraja uchun Gate Test mavjud emas."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GateTestOquvchigaSerializer(daraja.gate_test)
        return Response(serializer.data)


class GateTestTopshirishView(APIView):
    """
    POST /api/oquvchi/gate-test/{daraja_id}/topshirish/
    body: { javoblar: [{savol: id, tanlangan_javoblar: [id,...]}] }
    Agar o'tish balidan yuqori ball olsa — keyingi daraja avtomatik ochiladi.
    """
    permission_classes = [IsOquvchi]

    def post(self, request, daraja_id):
        try:
            daraja = Daraja.objects.get(id=daraja_id)
        except Daraja.DoesNotExist:
            return Response({'detail': 'Daraja topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(daraja, 'gate_test'):
            return Response({'detail': "Bu daraja uchun Gate Test mavjud emas."}, status=status.HTTP_404_NOT_FOUND)

        gate_test = daraja.gate_test
        javoblar_data = request.data.get('javoblar', [])
        savollar = {s.id: s for s in gate_test.savollar.all()}

        togri_soni = 0
        for item in javoblar_data:
            savol = savollar.get(item.get('savol'))
            if not savol:
                continue
            tanlangan_ids = set(item.get('tanlangan_javoblar', []))
            togri_ids = set(savol.javoblar.filter(togri=True).values_list('id', flat=True))
            if tanlangan_ids == togri_ids and len(tanlangan_ids) > 0:
                togri_soni += 1

        jami = len(savollar) or 1
        foiz = round((togri_soni / jami) * 100, 2)
        otdi = foiz >= daraja.ochish_uchun_foiz

        urinish_raqami = GateTestNatija.objects.filter(oquvchi=request.user, gate_test=gate_test).count() + 1
        natija = GateTestNatija.objects.create(
            oquvchi=request.user, gate_test=gate_test,
            togri_soni=togri_soni, jami_soni=jami, foiz=foiz, otdi=otdi,
            urinish_raqami=urinish_raqami,
        )

        if otdi:
            coin_qoshish(request.user, 20, 'gate_test', f"{daraja} Gate Test'dan o'tildi")
            # Keyingi daraja bo'yicha OquvchiFan yozuvi mavjud bo'lsa, uni "ochiq" deb belgilash shart emas —
            # daraja_ochiqmi() funksiyasi GateTestNatija orqali avtomatik tekshiradi.

        return Response(GateTestNatijaSerializer(natija).data, status=status.HTTP_201_CREATED)


# ==================== O'QUVCHI: FINAL TEST TOPSHIRISH ====================

class FinalTestOlishView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request, daraja_id):
        try:
            daraja = Daraja.objects.select_related('fan').get(id=daraja_id)
        except Daraja.DoesNotExist:
            return Response({'detail': 'Daraja topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if not oquvchiga_fan_biriktirilganmi(request.user, daraja.fan):
            return Response({'detail': "Sizga bu fan biriktirilmagan."}, status=status.HTTP_403_FORBIDDEN)
        if not daraja_ochiqmi(request.user, daraja):
            return Response({'detail': "Bu daraja hali sizga ochilmagan."}, status=status.HTTP_403_FORBIDDEN)
        if not daraja_mavzulari_tugaganmi(request.user, daraja):
            return Response({
                'detail': "Yakuniy test ochilishi uchun darajadagi barcha mavzu testlaridan kamida 80% oling.",
                'mavzular_tugamagan': True,
            }, status=status.HTTP_403_FORBIDDEN)
        if not hasattr(daraja, 'final_test'):
            return Response({'detail': "Bu daraja uchun yakuniy test mavjud emas."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FinalTestOquvchigaSerializer(daraja.final_test)
        return Response(serializer.data)


def _sertifikat_kod_yaratish():
    while True:
        kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        if not Sertifikat.objects.filter(kod=kod).exists():
            return kod


class FinalTestTopshirishView(APIView):
    """Yakuniy testdan 80%+ olsa QR-kodli sertifikat yaratiladi."""
    permission_classes = [IsOquvchi]

    def post(self, request, daraja_id):
        try:
            daraja = Daraja.objects.select_related('fan').get(id=daraja_id)
        except Daraja.DoesNotExist:
            return Response({'detail': 'Daraja topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if not oquvchiga_fan_biriktirilganmi(request.user, daraja.fan):
            return Response({'detail': "Sizga bu fan biriktirilmagan."}, status=status.HTTP_403_FORBIDDEN)
        if not daraja_ochiqmi(request.user, daraja):
            return Response({'detail': "Bu daraja hali sizga ochilmagan."}, status=status.HTTP_403_FORBIDDEN)
        if not daraja_mavzulari_tugaganmi(request.user, daraja):
            return Response({'detail': "Avval barcha mavzularni 80%+ bilan tugating."}, status=status.HTTP_403_FORBIDDEN)
        if not hasattr(daraja, 'final_test'):
            return Response({'detail': "Bu daraja uchun yakuniy test mavjud emas."}, status=status.HTTP_404_NOT_FOUND)

        final_test = daraja.final_test
        javoblar_data = request.data.get('javoblar', [])
        if not isinstance(javoblar_data, list):
            return Response({'detail': "Javoblar formati noto‘g‘ri."}, status=status.HTTP_400_BAD_REQUEST)

        savollar = {s.id: s for s in final_test.savollar.prefetch_related('javoblar').all()}
        if not savollar:
            return Response({'detail': "Yakuniy testda savollar mavjud emas."}, status=status.HTTP_400_BAD_REQUEST)

        togri_soni = 0
        for item in javoblar_data:
            if not isinstance(item, dict):
                continue
            savol = savollar.get(item.get('savol'))
            if not savol:
                continue
            tanlangan_ids = {int(v) for v in (item.get('tanlangan_javoblar') or []) if str(v).isdigit()}
            togri_ids = {j.id for j in savol.javoblar.all() if j.togri}
            if tanlangan_ids == togri_ids and tanlangan_ids:
                togri_soni += 1

        jami = len(savollar)
        foiz = round((togri_soni / jami) * 100, 2)
        otish_bali = max(80, int(final_test.otish_bali_foiz or 80))
        otdi = foiz >= otish_bali
        next_level = keyingi_daraja(daraja)

        try:
            with transaction.atomic():
                urinish_raqami = FinalTestNatija.objects.select_for_update().filter(
                    oquvchi=request.user, final_test=final_test
                ).count() + 1
                natija = FinalTestNatija.objects.create(
                    oquvchi=request.user,
                    final_test=final_test,
                    togri_soni=togri_soni,
                    jami_soni=jami,
                    foiz=foiz,
                    otdi=otdi,
                    urinish_raqami=urinish_raqami,
                )

                sertifikat = None
                sertifikat_yangi = False
                if otdi:
                    sertifikat, sertifikat_yangi = _sertifikatni_ol_yoki_yarat(
                        request.user, daraja, foiz
                    )
                    natija.sertifikat = sertifikat
                    natija.save(update_fields=['sertifikat'])
        except Exception as exc:
            logger.exception(
                "FINAL_TEST_CORE_FAILED user=%s daraja=%s",
                request.user.pk,
                daraja.pk,
            )
            return Response(
                {
                    'detail': "Yakuniy test natijasini saqlashda baza xatosi yuz berdi. Railway migratsiyasini deploy qiling.",
                    'error_code': 'FINAL_TEST_SAVE_FAILED',
                    'technical_detail': str(exc)[:240],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Quyidagi imkoniyatlar qo‘shimcha: ulardan biri xato qilsa natija va sertifikat bekor bo‘lmaydi.
        if otdi:
            # Bir daraja uchun bonus faqat sertifikat birinchi marta yaratilganda beriladi.
            if sertifikat_yangi:
                _xavfsiz_qoshimcha(
                    'coin',
                    lambda: coin_qoshish(request.user, 50, 'final_test', f"{daraja} yakuniy testidan o'tildi"),
                )
            _xavfsiz_qoshimcha(
                'audit',
                lambda: log_amal(
                    request.user,
                    'daraja_tugatildi',
                    f"{daraja.fan.nomi} - {daraja.nomi}: {foiz}% bilan tugatildi",
                    nishon_user=request.user,
                ),
            )
            _xavfsiz_qoshimcha(
                'certificate_notification',
                lambda: bildirishnoma_yarat(
                    request.user,
                    'Sertifikatingiz tayyor!',
                    f'{daraja.fan.nomi} — {daraja.nomi} darajasini {foiz}% bilan tugatdingiz.',
                    tur='certificate',
                    havola='/oquvchi/sertifikatlarim',
                ),
            )
            if next_level:
                _xavfsiz_qoshimcha(
                    'next_level_notification',
                    lambda: bildirishnoma_yarat(
                        request.user,
                        f'{next_level.nomi} darajasi ochildi',
                        'Keyingi darajadagi mavzularni boshlashingiz mumkin.',
                        tur='success',
                        havola='/oquvchi',
                    ),
                )
        else:
            _xavfsiz_qoshimcha(
                'failed_notification',
                lambda: bildirishnoma_yarat(
                    request.user,
                    'Yakuniy testdan o‘tilmadi',
                    f'{daraja.nomi} darajasida {foiz}% oldingiz. Keyingi daraja uchun kamida 80% kerak.',
                    tur='warning',
                    havola=f'/oquvchi/final-test/{daraja.id}',
                ),
            )

        _xavfsiz_qoshimcha('activity', lambda: faollik_qayd_et(request.user, 'final_test'))

        # select_related serializerning legacy bazada ortiqcha query xatolarini kamaytiradi.
        natija = FinalTestNatija.objects.select_related(
            'sertifikat__oquvchi', 'sertifikat__daraja__fan'
        ).get(pk=natija.pk)
        data = FinalTestNatijaSerializer(natija, context={'request': request}).data
        data['keyingi_daraja'] = (
            {'id': next_level.id, 'nomi': next_level.nomi, 'ochildi': bool(otdi)}
            if next_level else None
        )
        data['xabar'] = (
            f"Tabriklaymiz! QR kodli sertifikat berildi va {next_level.nomi} darajasi avtomatik ochildi."
            if otdi and next_level
            else "Tabriklaymiz! QR kodli sertifikat berildi va kursning oxirgi darajasini tugatdingiz."
            if otdi
            else "Keyingi daraja ochilmadi. Kamida 80% natija kerak."
        )
        return Response(data, status=status.HTTP_201_CREATED)


# ==================== SERTIFIKATLAR ====================

class MeningSertifikatlarimView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        sertifikatlar = Sertifikat.objects.filter(oquvchi=request.user).select_related('oquvchi', 'daraja__fan')
        return Response(SertifikatSerializer(sertifikatlar, many=True, context={'request': request}).data)


class AdminSertifikatlarView(APIView):
    """Admin uchun darajadan o'tgan o'quvchilar va sertifikatlar ro'yxati."""
    permission_classes = [IsAdmin]

    def get(self, request):
        sertifikatlar = Sertifikat.objects.select_related('oquvchi', 'daraja__fan').all()
        q = request.query_params.get('q', '').strip()
        if q:
            from django.db.models import Q
            sertifikatlar = sertifikatlar.filter(
                Q(oquvchi__ism__icontains=q)
                | Q(oquvchi__familya__icontains=q)
                | Q(oquvchi__username__icontains=q)
                | Q(daraja__nomi__icontains=q)
                | Q(daraja__fan__nomi__icontains=q)
                | Q(kod__icontains=q)
            )
        return Response(SertifikatSerializer(sertifikatlar, many=True, context={'request': request}).data)


class SertifikatTekshirishView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, kod):
        try:
            sert = Sertifikat.objects.select_related('oquvchi', 'daraja__fan').get(kod=kod)
        except Sertifikat.DoesNotExist:
            return Response({'detail': 'Sertifikat topilmadi.', 'haqiqiy': False}, status=status.HTTP_404_NOT_FOUND)
        data = SertifikatSerializer(sert, context={'request': request}).data
        data['haqiqiy'] = True
        return Response(data)


class SertifikatPDFView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, kod):
        try:
            sert = Sertifikat.objects.select_related('oquvchi', 'daraja__fan').get(kod=kod)
        except Sertifikat.DoesNotExist:
            return Response({'detail': 'Sertifikat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        from .certificate_pdf import certificate_pdf_bytes
        response = HttpResponse(certificate_pdf_bytes(sert), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sertifikat-{sert.kod}.pdf"'
        return response


class SertifikatQRView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request, kod):
        try:
            sert = Sertifikat.objects.select_related('oquvchi', 'daraja__fan').get(kod=kod)
        except Sertifikat.DoesNotExist:
            return Response({'detail': 'Sertifikat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        from .certificate_pdf import certificate_qr_bytes
        return HttpResponse(certificate_qr_bytes(sert), content_type='image/png')


# ==================== WRITING ====================

class WritingTopshiriqlarView(APIView):
    """GET /api/oquvchi/writing/{dars_id}/ -> shu darsga tegishli yozma topshiriqlar"""
    permission_classes = [IsOquvchi]

    def get(self, request, dars_id):
        topshiriqlar = WritingTopshiriq.objects.filter(dars_id=dars_id)
        return Response(WritingTopshiriqSerializer(topshiriqlar, many=True).data)


class WritingTopshirishView(APIView):
    """POST /api/oquvchi/writing/{topshiriq_id}/topshirish/  body: {matn_javob}
    AI baholash sinxron chaqiriladi (Claude API orqali)."""
    permission_classes = [IsOquvchi]

    def post(self, request, topshiriq_id):
        try:
            topshiriq = WritingTopshiriq.objects.get(id=topshiriq_id)
        except WritingTopshiriq.DoesNotExist:
            return Response({'detail': 'Topshiriq topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        matn_javob = request.data.get('matn_javob', '').strip()
        if not matn_javob:
            return Response({'detail': "Javob matni bo'sh bo'lishi mumkin emas."}, status=status.HTTP_400_BAD_REQUEST)

        natija = WritingNatija.objects.create(
            oquvchi=request.user, topshiriq=topshiriq, matn_javob=matn_javob, baholanmoqda=True,
        )

        from .ai_baholash import writing_baholash
        try:
            baho = writing_baholash(topshiriq.matn, matn_javob, topshiriq.minimal_soz_soni)
            natija.ai_foiz = baho['foiz']
            natija.ai_izoh = baho['izoh']
            natija.ai_xatolar = baho['xatolar']
            natija.baholash_tafsiloti = baho.get('tafsilot', {})
            natija.baholanmoqda = False
            natija.save()
            if natija.ai_foiz and natija.ai_foiz >= 60:
                coin_qoshish(request.user, 10, 'mashq', 'Writing topshiriq muvaffaqiyatli bajarildi')
        except Exception as e:
            natija.ai_izoh = f"AI baholashda xatolik yuz berdi: {str(e)}"
            natija.baholanmoqda = False
            natija.save()

        return Response(WritingNatijaSerializer(natija).data, status=status.HTTP_201_CREATED)


# ==================== SPEAKING ====================

class SpeakingTopshiriqlarView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request, dars_id):
        topshiriqlar = SpeakingTopshiriq.objects.filter(dars_id=dars_id)
        return Response(SpeakingTopshiriqSerializer(topshiriqlar, many=True).data)


def _nutqni_tozalash(text):
    text = unicodedata.normalize('NFKC', text or '').casefold()
    text = re.sub(r"[^\w\s'’-]", ' ', text, flags=re.UNICODE)
    return ' '.join(text.split())


def _talaffuz_foizi(target, transcript):
    target_clean = _nutqni_tozalash(target)
    transcript_clean = _nutqni_tozalash(transcript)
    if not target_clean or not transcript_clean:
        return 0
    sequence = SequenceMatcher(None, target_clean, transcript_clean).ratio()
    target_words = target_clean.split()
    transcript_words = transcript_clean.split()
    common = sum(1 for word in target_words if word in transcript_words)
    word_score = common / max(1, len(target_words))
    return round(min(100, (sequence * 70 + word_score * 30) * 100), 2)


class SpeakingTopshirishView(APIView):
    """Brauzer Speech Recognition transkripsiyasini maqsad matn bilan solishtiradi."""
    permission_classes = [IsOquvchi]

    def post(self, request, topshiriq_id):
        try:
            topshiriq = SpeakingTopshiriq.objects.select_related('dars__mavzu__daraja__fan').get(id=topshiriq_id)
        except SpeakingTopshiriq.DoesNotExist:
            return Response({'detail': 'Topshiriq topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        transcript = str(request.data.get('transkripsiya', '')).strip()
        audio_fayl = request.FILES.get('audio_yozuv')
        if not transcript and not audio_fayl:
            return Response({'detail': "Ovozli natija yoki transkripsiya yuborilishi shart."}, status=status.HTTP_400_BAD_REQUEST)

        percentage = _talaffuz_foizi(topshiriq.matn, transcript) if transcript else 0
        if transcript:
            if percentage >= 85:
                comment = "Ajoyib talaffuz! Gap aniq va to‘liq aytildi."
            elif percentage >= 70:
                comment = "Yaxshi natija. Ayrim so‘zlarni sekinroq va aniqroq takrorlang."
            elif percentage >= 50:
                comment = "O‘rtacha natija. Namunani tinglab, gapni bo‘lib-bo‘lib qayta ayting."
            else:
                comment = "Yana mashq qiling: avval namunani tinglang, keyin sekin takrorlang."
        else:
            comment = "Audio qabul qilindi. Brauzer transkripsiya bermagani uchun foiz hisoblanmadi."

        natija = SpeakingNatija.objects.create(
            oquvchi=request.user,
            topshiriq=topshiriq,
            audio_yozuv=audio_fayl,
            transkripsiya=transcript,
            ai_foiz=percentage,
            ai_izoh=comment,
            baholanmoqda=False,
        )
        faollik_qayd_et(request.user, 'speaking')
        return Response(SpeakingNatijaSerializer(natija).data, status=status.HTTP_201_CREATED)


# ==================== SO'Z O'YINI / COIN / SHOP ====================

def _oquvchining_fani(oquvchi):
    """O'quvchiga eng oxirgi biriktirilgan fan. UI ham aynan shu fanni ko'rsatadi."""
    assignment = (
        OquvchiFan.objects.filter(oquvchi=oquvchi)
        .select_related('daraja__fan')
        .order_by('-created_at', '-id')
        .first()
    )
    return assignment.daraja.fan if assignment else None


class SozOyiniBoshlashView(APIView):
    """Biriktirilgan fan uchun 10 juftdan iborat 20 ta yopiq karta yaratadi."""
    permission_classes = [IsOquvchi]

    def get(self, request):
        fan = _oquvchining_fani(request.user)
        if not fan:
            return Response(
                {'detail': "Avval admin sizga fan biriktirishi kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        juftliklar = list(SozJuftligi.objects.filter(fan=fan, faol=True).order_by('tartib', 'id')[:10])
        if len(juftliklar) < 10:
            return Response(
                {'detail': "Bu fan uchun 10 ta so'z juftligi hali tayyor emas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cardlar = []
        for juftlik in juftliklar:
            cardlar.extend([
                {
                    'id': secrets.token_urlsafe(10),
                    'matn': juftlik.chet_soz,
                    'juftlik_id': juftlik.id,
                    'tomon': 'chet',
                },
                {
                    'id': secrets.token_urlsafe(10),
                    'matn': juftlik.uzbek_soz,
                    'juftlik_id': juftlik.id,
                    'tomon': 'uzbek',
                },
            ])
        random.shuffle(cardlar)
        sessiya = SozOyiniSessiya.objects.create(
            oquvchi=request.user,
            fan=fan,
            cardlar=cardlar,
        )
        # Frontendga juftlik identifikatori va tomoni berilmaydi: o'yinchi tarjimani o'zi topadi.
        public_cards = [{'id': item['id'], 'matn': item['matn']} for item in cardlar]
        return Response({
            'token': str(sessiya.token),
            'fan': fan.nomi,
            'jami_juftlik': 10,
            'har_bir_juftlik_coin': 1,
            'cardlar': public_cards,
        })


class SozOyiniJuftTekshirishView(APIView):
    """Ikki karta haqiqiy tarjima jufti ekanini tekshiradi; javoblarni oshkor qilmaydi."""
    permission_classes = [IsOquvchi]

    def post(self, request, token):
        try:
            sessiya = SozOyiniSessiya.objects.get(token=token, oquvchi=request.user, tugallangan=False)
        except SozOyiniSessiya.DoesNotExist:
            return Response({'detail': "Faol o'yin sessiyasi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        birinchi_id = request.data.get('birinchi')
        ikkinchi_id = request.data.get('ikkinchi')
        if not birinchi_id or not ikkinchi_id or birinchi_id == ikkinchi_id:
            return Response({'detail': 'Ikki xil karta yuboring.'}, status=status.HTTP_400_BAD_REQUEST)
        kartalar = {item['id']: item for item in sessiya.cardlar}
        birinchi = kartalar.get(birinchi_id)
        ikkinchi = kartalar.get(ikkinchi_id)
        if not birinchi or not ikkinchi:
            return Response({'detail': 'Karta topilmadi.'}, status=status.HTTP_400_BAD_REQUEST)
        togri = birinchi['juftlik_id'] == ikkinchi['juftlik_id'] and birinchi['tomon'] != ikkinchi['tomon']
        return Response({'togri': togri})


class SozOyiniYakunlashView(APIView):
    """Topilgan 10 juftni serverda tekshiradi va har bir to'g'ri juft uchun 1 coin beradi."""
    permission_classes = [IsOquvchi]

    @transaction.atomic
    def post(self, request, token):
        try:
            sessiya = SozOyiniSessiya.objects.select_for_update().get(token=token, oquvchi=request.user)
        except SozOyiniSessiya.DoesNotExist:
            return Response({'detail': "O'yin sessiyasi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if sessiya.tugallangan:
            balans_obj, _ = OquvchiCoin.objects.get_or_create(oquvchi=request.user)
            return Response({
                'topilgan_soni': sessiya.topilgan_soni,
                'berilgan_coin': sessiya.berilgan_coin,
                'balans': balans_obj.balans,
                'allaqachon_yakunlangan': True,
            })

        yuborilgan = request.data.get('juftliklar', [])
        if not isinstance(yuborilgan, list):
            return Response({'detail': "'juftliklar' ro'yxat bo'lishi kerak."}, status=status.HTTP_400_BAD_REQUEST)

        kartalar = {item['id']: item for item in sessiya.cardlar}
        ishlatilgan_cardlar = set()
        topilgan_pairlar = set()

        for item in yuborilgan:
            if not isinstance(item, dict):
                continue
            birinchi_id = item.get('birinchi')
            ikkinchi_id = item.get('ikkinchi')
            if not birinchi_id or not ikkinchi_id:
                continue
            if birinchi_id in ishlatilgan_cardlar or ikkinchi_id in ishlatilgan_cardlar:
                continue
            birinchi = kartalar.get(birinchi_id)
            ikkinchi = kartalar.get(ikkinchi_id)
            if not birinchi or not ikkinchi:
                continue
            if birinchi['juftlik_id'] == ikkinchi['juftlik_id'] and birinchi['tomon'] != ikkinchi['tomon']:
                ishlatilgan_cardlar.update([birinchi_id, ikkinchi_id])
                topilgan_pairlar.add(birinchi['juftlik_id'])

        topilgan_soni = min(len(topilgan_pairlar), 10)
        if topilgan_soni < 10:
            return Response({
                'detail': "O'yinni yakunlash uchun barcha 10 ta tarjima juftini toping.",
                'topilgan_soni': topilgan_soni,
            }, status=status.HTTP_400_BAD_REQUEST)

        berilgan_coin = topilgan_soni
        sessiya.tugallangan = True
        sessiya.topilgan_soni = topilgan_soni
        sessiya.berilgan_coin = berilgan_coin
        sessiya.completed_at = timezone.now()
        sessiya.save(update_fields=['tugallangan', 'topilgan_soni', 'berilgan_coin', 'completed_at'])
        balans_obj = coin_qoshish(
            request.user,
            berilgan_coin,
            'soz_oyini',
            f"{sessiya.fan.nomi}: {topilgan_soni} ta so'z jufti topildi",
        )
        faollik_qayd_et(request.user, 'soz_oyini')
        return Response({
            'topilgan_soni': topilgan_soni,
            'berilgan_coin': berilgan_coin,
            'balans': balans_obj.balans,
            'xabar': f"Ajoyib! {topilgan_soni} ta juft topdingiz va {berilgan_coin} coin oldingiz.",
        })


class MeningCoinlarimView(APIView):
    """GET /api/oquvchi/coinlarim/ -> balans + so'nggi tarix"""
    permission_classes = [IsOquvchi]

    def get(self, request):
        balans_obj, _ = OquvchiCoin.objects.get_or_create(oquvchi=request.user)
        tarix = CoinTarix.objects.filter(oquvchi=request.user)[:20]
        return Response({
            'balans': balans_obj.balans,
            'tarix': CoinTarixSerializer(tarix, many=True).data,
        })


class ShopMahsulotlarView(APIView):
    """GET /api/oquvchi/shop/ -> faol mahsulotlar ro'yxati"""
    permission_classes = [IsOquvchi]

    def get(self, request):
        mahsulotlar = ShopMahsulot.objects.filter(faol=True)
        return Response(ShopMahsulotSerializer(mahsulotlar, many=True, context={'request': request}).data)


class MeningShopBuyurtmalarimView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        buyurtmalar = ShopBuyurtma.objects.filter(oquvchi=request.user).select_related('mahsulot', 'oquvchi__filial')
        return Response(ShopBuyurtmaSerializer(buyurtmalar, many=True).data)


class ShopXaridView(APIView):
    """Coin yetarli bo'lsa mahsulotni sotib oladi va admin/filial rahbari uchun buyurtma yaratadi."""
    permission_classes = [IsOquvchi]

    @transaction.atomic
    def post(self, request, mahsulot_id):
        try:
            mahsulot = ShopMahsulot.objects.get(id=mahsulot_id, faol=True)
        except ShopMahsulot.DoesNotExist:
            return Response({'detail': 'Mahsulot topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        balans_obj, _ = OquvchiCoin.objects.get_or_create(oquvchi=request.user)
        balans_obj = OquvchiCoin.objects.select_for_update().get(pk=balans_obj.pk)
        if balans_obj.balans < mahsulot.narx_coin:
            return Response({'detail': "Coin balansingiz yetarli emas."}, status=status.HTTP_400_BAD_REQUEST)

        balans_obj.balans -= mahsulot.narx_coin
        balans_obj.save(update_fields=['balans', 'updated_at'])
        CoinTarix.objects.create(
            oquvchi=request.user,
            miqdor=-mahsulot.narx_coin,
            sabab='shop',
            izoh=f"{mahsulot.nomi} sotib olindi",
        )
        buyurtma = ShopBuyurtma.objects.create(
            oquvchi=request.user,
            mahsulot=mahsulot,
            narx_coin=mahsulot.narx_coin,
        )
        log_amal(
            request.user,
            'shop_xarid',
            f"{mahsulot.nomi} {mahsulot.narx_coin} coinga sotib olindi",
            nishon_user=request.user,
        )
        bildirishnoma_yarat(
            request.user,
            "Do‘kon buyurtmasi qabul qilindi",
            f'{mahsulot.nomi} uchun {mahsulot.narx_coin} coin sarflandi.',
            tur='shop',
            havola='/oquvchi/shop',
        )
        faollik_qayd_et(request.user, 'shop')
        data = ShopBuyurtmaSerializer(buyurtma).data
        data['qolgan_balans'] = balans_obj.balans
        return Response(data, status=status.HTTP_201_CREATED)


class AdminShopMahsulotViewSet(viewsets.ModelViewSet):
    """Admin uchun do'kon mahsulotlarini boshqarish"""
    queryset = ShopMahsulot.objects.all()
    serializer_class = ShopMahsulotSerializer
    permission_classes = [IsAdmin]


class AdminYokiNazoratchi(BasePermission):
    """Admin yoki filial rahbari (ichki roli: nazoratchi)."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ('admin', 'nazoratchi'))


class ShopBuyurtmalarBoshqaruvView(APIView):
    """Admin barcha, filial rahbari esa o'z filialidagi xaridlarni ko'radi."""
    permission_classes = [AdminYokiNazoratchi]

    def get(self, request):
        buyurtmalar = ShopBuyurtma.objects.select_related('oquvchi__filial', 'mahsulot')
        if request.user.role == 'nazoratchi':
            if request.user.filial_id:
                buyurtmalar = buyurtmalar.filter(oquvchi__filial_id=request.user.filial_id)
            else:
                buyurtmalar = buyurtmalar.filter(oquvchi__yaratgan=request.user)
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            buyurtmalar = buyurtmalar.filter(status=status_filter)
        return Response(ShopBuyurtmaSerializer(buyurtmalar, many=True).data)


class ShopBuyurtmaStatusView(APIView):
    permission_classes = [AdminYokiNazoratchi]

    def patch(self, request, buyurtma_id):
        try:
            buyurtma = ShopBuyurtma.objects.select_related('oquvchi__filial', 'mahsulot').get(id=buyurtma_id)
        except ShopBuyurtma.DoesNotExist:
            return Response({'detail': 'Buyurtma topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'nazoratchi':
            permitted = (
                request.user.filial_id and buyurtma.oquvchi.filial_id == request.user.filial_id
            ) or buyurtma.oquvchi.yaratgan_id == request.user.id
            if not permitted:
                return Response({'detail': "Bu buyurtma sizning filialingizga tegishli emas."}, status=status.HTTP_403_FORBIDDEN)

        yangi_status = request.data.get('status')
        valid_statuses = {choice[0] for choice in ShopBuyurtma.STATUS_CHOICES}
        if yangi_status not in valid_statuses:
            return Response({'detail': "Noto'g'ri status."}, status=status.HTTP_400_BAD_REQUEST)
        buyurtma.status = yangi_status
        buyurtma.save(update_fields=['status'])
        bildirishnoma_yarat(
            buyurtma.oquvchi,
            "Do‘kon buyurtmasi yangilandi",
            f'{buyurtma.mahsulot.nomi}: {buyurtma.get_status_display()}.',
            tur='shop',
            havola='/oquvchi/shop',
        )
        log_amal(
            request.user,
            'shop_status_ozgardi',
            f"{buyurtma.mahsulot.nomi}: {buyurtma.get_status_display()}",
            nishon_user=buyurtma.oquvchi,
        )
        return Response(ShopBuyurtmaSerializer(buyurtma).data)


class AdminCoinBerishView(APIView):
    """Admin istalgan, filial rahbari esa o'z filialidagi o'quvchiga coin beradi."""
    permission_classes = [AdminYokiNazoratchi]

    def post(self, request, oquvchi_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            oquvchi = User.objects.get(id=oquvchi_id, role=User.ROLE_OQUVCHI)
        except User.DoesNotExist:
            return Response({'detail': "O'quvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role == 'nazoratchi':
            permitted = (
                request.user.filial_id and oquvchi.filial_id == request.user.filial_id
            ) or oquvchi.yaratgan_id == request.user.id
            if not permitted:
                return Response({'detail': "Siz faqat o'z filialingizdagi o'quvchilarga coin bera olasiz."}, status=status.HTTP_403_FORBIDDEN)

        try:
            miqdor = int(request.data.get('miqdor', 0))
        except (TypeError, ValueError):
            return Response({'detail': "Coin miqdori son bo'lishi kerak."}, status=status.HTTP_400_BAD_REQUEST)
        izoh = request.data.get('izoh', '')
        balans_obj = coin_qoshish(oquvchi, miqdor, 'admin', izoh)
        log_amal(request.user, 'coin_berildi', f"{miqdor} coin: {izoh}", nishon_user=oquvchi)
        return Response(OquvchiCoinSerializer(balans_obj).data)


# ==================== ADMIN AUDIT LOG ====================

class AdminAmalLoglariView(APIView):
    """GET /api/admin/amal-loglari/ -> so'nggi 100 ta admin amali"""
    permission_classes = [IsAdmin]

    def get(self, request):
        loglar = AdminAmalLog.objects.all()[:100]
        return Response(AdminAmalLogSerializer(loglar, many=True).data)
