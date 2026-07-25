"""
Gate Test, Final Test, Sertifikat, Writing, Speaking, Coin/Shop, Admin audit log
uchun view'lar. Asosiy exams/views.py faylini ortiqcha kattalashtirmaslik uchun
alohida fayl.
"""
import random
import secrets
import string

from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
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
    """Yakuniy testdan 80%+ olsa sertifikat yaratiladi va keyingi daraja ochiladi."""
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
        savollar = {s.id: s for s in final_test.savollar.all()}

        togri_soni = 0
        for item in javoblar_data:
            savol = savollar.get(item.get('savol'))
            if not savol:
                continue
            tanlangan_ids = set(item.get('tanlangan_javoblar', []))
            togri_ids = set(savol.javoblar.filter(togri=True).values_list('id', flat=True))
            if tanlangan_ids == togri_ids and tanlangan_ids:
                togri_soni += 1

        jami = len(savollar) or 1
        foiz = round((togri_soni / jami) * 100, 2)
        otish_bali = max(80, int(final_test.otish_bali_foiz or 80))
        otdi = foiz >= otish_bali

        urinish_raqami = FinalTestNatija.objects.filter(
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

        next_level = keyingi_daraja(daraja)
        if otdi:
            sertifikat, created = Sertifikat.objects.get_or_create(
                oquvchi=request.user,
                daraja=daraja,
                defaults={'kod': _sertifikat_kod_yaratish(), 'foiz': foiz},
            )
            if not created and float(foiz) > float(sertifikat.foiz):
                sertifikat.foiz = foiz
                sertifikat.save(update_fields=['foiz'])
            natija.sertifikat = sertifikat
            natija.save(update_fields=['sertifikat'])
            from .models import PlatformSozlama
            coin_qoshish(request.user, PlatformSozlama.load().final_test_coin, 'final_test', f"{daraja} yakuniy testidan o'tildi")
            log_amal(
                request.user,
                'daraja_tugatildi',
                f"{daraja.fan.nomi} - {daraja.nomi}: {foiz}% bilan tugatildi",
                nishon_user=request.user,
            )

        data = FinalTestNatijaSerializer(natija).data
        data['keyingi_daraja'] = (
            {
                'id': next_level.id,
                'nomi': next_level.nomi,
                'ochildi': bool(otdi),
            }
            if next_level else None
        )
        data['xabar'] = (
            f"Tabriklaymiz! {next_level.nomi} darajasi avtomatik ochildi."
            if otdi and next_level
            else "Tabriklaymiz! Kursning oxirgi darajasini tugatdingiz."
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
            natija.baholanmoqda = False
            natija.save()
            if natija.ai_foiz and natija.ai_foiz >= 60:
                from .models import PlatformSozlama
                coin_qoshish(request.user, PlatformSozlama.load().mashq_coin, 'mashq', 'Writing topshiriq muvaffaqiyatli bajarildi')
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


class SpeakingTopshirishView(APIView):
    """POST /api/oquvchi/speaking/{topshiriq_id}/topshirish/  multipart: {audio_yozuv}
    Hozircha audio saqlanadi; AI orqali transkripsiya/baholash uchun tashqi nutqni-matnga
    aylantiruvchi xizmat ulanishi kerak (hozircha ai_izoh'da izoh qoldiriladi)."""
    permission_classes = [IsOquvchi]

    def post(self, request, topshiriq_id):
        try:
            topshiriq = SpeakingTopshiriq.objects.get(id=topshiriq_id)
        except SpeakingTopshiriq.DoesNotExist:
            return Response({'detail': 'Topshiriq topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        audio_fayl = request.FILES.get('audio_yozuv')
        if not audio_fayl:
            return Response({'detail': "Audio fayl yuborilishi shart."}, status=status.HTTP_400_BAD_REQUEST)
        from .models import PlatformSozlama
        max_mb = PlatformSozlama.load().max_fayl_mb
        if audio_fayl.size > max_mb * 1024 * 1024:
            return Response(
                {'detail': f"Audio fayl {max_mb} MB dan oshmasligi kerak."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        natija = SpeakingNatija.objects.create(
            oquvchi=request.user, topshiriq=topshiriq, audio_yozuv=audio_fayl, baholanmoqda=True,
        )
        # Eslatma: audio-dan-matnga aylantirish (Speech-to-Text) tashqi xizmat talab qiladi
        # (masalan Whisper API). Hozircha qo'lda/keyinroq baholash uchun navbatda qoladi.
        natija.ai_izoh = "Audio qabul qilindi, o'qituvchi tomonidan tekshiriladi."
        natija.baholanmoqda = True
        natija.save()

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

# ==================== AI YORDAMCHI ====================

def _oquvchi_ai_konteksti(oquvchi):
    from django.db.models import Avg, Count
    from .models import MashqNatija

    assignment = OquvchiFan.objects.select_related('daraja__fan').filter(oquvchi=oquvchi).order_by('created_at').first()
    natijalar = MashqNatija.objects.filter(oquvchi=oquvchi).select_related(
        'mashq__dars__mavzu__daraja__fan'
    ).order_by('-boshlangan_vaqt')
    ortacha = natijalar.aggregate(v=Avg('foiz'))['v'] or 0
    zaif_qs = natijalar.values('mashq__dars__mavzu__nomi').annotate(
        foiz=Avg('foiz'), urinishlar=Count('id')
    ).order_by('foiz')[:5]
    zaif = [
        {'mavzu': x['mashq__dars__mavzu__nomi'] or 'Noma’lum', 'foiz': float(x['foiz'] or 0), 'urinishlar': x['urinishlar']}
        for x in zaif_qs
    ]
    oxirgi = [
        {
            'mavzu': n.mashq.dars.mavzu.nomi,
            'dars': n.mashq.dars.sarlavha,
            'foiz': float(n.foiz),
            'sana': n.boshlangan_vaqt.isoformat(),
        }
        for n in natijalar[:5]
    ]
    return {
        'ism': oquvchi.full_name,
        'fan': assignment.daraja.fan.nomi if assignment else '',
        'daraja': assignment.daraja.nomi if assignment else '',
        'ortacha_foiz': float(ortacha),
        'jami_urinishlar': natijalar.count(),
        'zaif_mavzular': zaif,
        'oxirgi_natijalar': oxirgi,
    }


class AIYordamchiView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        from .models import AIYordamchiXabar, PlatformSozlama
        from .serializers_extra import AIYordamchiXabarSerializer
        sozlama = PlatformSozlama.load()
        xabarlar = AIYordamchiXabar.objects.filter(oquvchi=request.user).order_by('-created_at')[:60]
        data = list(reversed(AIYordamchiXabarSerializer(xabarlar, many=True).data))
        return Response({
            'faol': sozlama.ai_yordamchi_faol,
            'kunlik_limit': sozlama.ai_kunlik_limit,
            'xabarlar': data,
            'kontekst': _oquvchi_ai_konteksti(request.user),
            'tezkor_savollar': [
                'Natijamni tahlil qilib ber',
                'Bugungi o‘quv rejamni tuzib ber',
                'Qaysi mavzularni ko‘proq takrorlashim kerak?',
                'Testdagi xatolarimni qanday kamaytiraman?',
            ],
        })

    def post(self, request):
        from .models import AIYordamchiXabar, PlatformSozlama
        from .serializers_extra import AIYordamchiXabarSerializer
        from .ai_baholash import ai_yordamchi_javob

        sozlama = PlatformSozlama.load()
        if not sozlama.ai_yordamchi_faol:
            return Response({'detail': 'AI yordamchi admin tomonidan vaqtincha o‘chirilgan.'}, status=status.HTTP_403_FORBIDDEN)
        savol = str(request.data.get('savol', '')).strip()
        if len(savol) < 2:
            return Response({'detail': 'Savolingizni yozing.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(savol) > 2000:
            return Response({'detail': 'Savol 2000 belgidan oshmasin.'}, status=status.HTTP_400_BAD_REQUEST)
        bugungi = AIYordamchiXabar.objects.filter(
            oquvchi=request.user, role=AIYordamchiXabar.ROLE_USER, created_at__date=timezone.localdate()
        ).count()
        if bugungi >= sozlama.ai_kunlik_limit:
            return Response({'detail': f'Bugungi {sozlama.ai_kunlik_limit} ta savol limiti tugadi.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        AIYordamchiXabar.objects.create(oquvchi=request.user, role='user', matn=savol)
        tarix = list(AIYordamchiXabar.objects.filter(oquvchi=request.user).order_by('-created_at').values('role', 'matn')[:10])
        tarix.reverse()
        kontekst = _oquvchi_ai_konteksti(request.user)
        javob, manba = ai_yordamchi_javob(savol, kontekst, tarix)
        ai_xabar = AIYordamchiXabar.objects.create(
            oquvchi=request.user,
            role='assistant',
            matn=javob,
            meta={'manba': manba, 'kontekst_ortacha': kontekst.get('ortacha_foiz', 0)},
        )
        return Response({
            'xabar': AIYordamchiXabarSerializer(ai_xabar).data,
            'qolgan_limit': max(0, sozlama.ai_kunlik_limit - bugungi - 1),
        }, status=status.HTTP_201_CREATED)

    def delete(self, request):
        from .models import AIYordamchiXabar
        AIYordamchiXabar.objects.filter(oquvchi=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== MUROJAATLAR ====================

class MeningMurojaatlarimView(APIView):
    permission_classes = [IsOquvchi]

    def get(self, request):
        from .models import Murojaat
        from .serializers_extra import MurojaatSerializer
        qs = Murojaat.objects.filter(foydalanuvchi=request.user).prefetch_related('javoblar__muallif')
        return Response(MurojaatSerializer(qs, many=True).data)

    def post(self, request):
        from .models import Murojaat, PlatformSozlama
        from .serializers_extra import MurojaatSerializer
        if not PlatformSozlama.load().murojaatlar_faol:
            return Response({'detail': 'Murojaatlar bo‘limi vaqtincha yopilgan.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MurojaatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        murojaat = Murojaat.objects.create(
            foydalanuvchi=request.user,
            kategoriya=serializer.validated_data.get('kategoriya', 'boshqa'),
            sarlavha=serializer.validated_data['sarlavha'],
            matn=serializer.validated_data['matn'],
        )
        return Response(MurojaatSerializer(murojaat).data, status=status.HTTP_201_CREATED)


class MeningMurojaatimDetailView(APIView):
    permission_classes = [IsOquvchi]

    def _get(self, request, murojaat_id):
        from .models import Murojaat
        try:
            return Murojaat.objects.prefetch_related('javoblar__muallif').get(id=murojaat_id, foydalanuvchi=request.user)
        except Murojaat.DoesNotExist:
            return None

    def get(self, request, murojaat_id):
        from .serializers_extra import MurojaatSerializer
        obj = self._get(request, murojaat_id)
        if not obj:
            return Response({'detail': 'Murojaat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MurojaatSerializer(obj).data)

    def post(self, request, murojaat_id):
        from .models import MurojaatJavob
        from .serializers_extra import MurojaatSerializer
        obj = self._get(request, murojaat_id)
        if not obj:
            return Response({'detail': 'Murojaat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        if obj.status == 'yopildi':
            return Response({'detail': 'Yopilgan murojaatga javob yozib bo‘lmaydi.'}, status=status.HTTP_400_BAD_REQUEST)
        matn = str(request.data.get('matn', '')).strip()
        if not matn:
            return Response({'detail': 'Javob matnini yozing.'}, status=status.HTTP_400_BAD_REQUEST)
        MurojaatJavob.objects.create(murojaat=obj, muallif=request.user, matn=matn)
        obj.status = 'korilmoqda'
        obj.oxirgi_javob_adminniki = False
        obj.save(update_fields=['status', 'oxirgi_javob_adminniki', 'updated_at'])
        return Response(MurojaatSerializer(obj).data)


class AdminMurojaatlarView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from .models import Murojaat
        from .serializers_extra import MurojaatSerializer
        qs = Murojaat.objects.select_related('foydalanuvchi__filial').prefetch_related('javoblar__muallif')
        status_filter = request.query_params.get('status', '').strip()
        kategoriya = request.query_params.get('kategoriya', '').strip()
        q = request.query_params.get('q', '').strip()
        if status_filter:
            qs = qs.filter(status=status_filter)
        if kategoriya:
            qs = qs.filter(kategoriya=kategoriya)
        if q:
            qs = qs.filter(Q(kod__icontains=q) | Q(sarlavha__icontains=q) | Q(foydalanuvchi__username__icontains=q) | Q(foydalanuvchi__ism__icontains=q))
        return Response(MurojaatSerializer(qs[:300], many=True).data)


class AdminMurojaatDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get(self, murojaat_id):
        from .models import Murojaat
        try:
            return Murojaat.objects.select_related('foydalanuvchi__filial').prefetch_related('javoblar__muallif').get(id=murojaat_id)
        except Murojaat.DoesNotExist:
            return None

    def get(self, request, murojaat_id):
        from .serializers_extra import MurojaatSerializer
        obj = self._get(murojaat_id)
        if not obj:
            return Response({'detail': 'Murojaat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MurojaatSerializer(obj).data)

    def patch(self, request, murojaat_id):
        from .models import Murojaat
        from .serializers_extra import MurojaatSerializer
        obj = self._get(murojaat_id)
        if not obj:
            return Response({'detail': 'Murojaat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        yangi_status = request.data.get('status', obj.status)
        ustuvorlik = request.data.get('ustuvorlik', obj.ustuvorlik)
        if yangi_status not in dict(Murojaat.STATUS_CHOICES):
            return Response({'detail': 'Noto‘g‘ri status.'}, status=status.HTTP_400_BAD_REQUEST)
        if ustuvorlik not in dict(Murojaat.USTUVORLIK_CHOICES):
            return Response({'detail': 'Noto‘g‘ri ustuvorlik.'}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = yangi_status
        obj.ustuvorlik = ustuvorlik
        obj.closed_at = timezone.now() if yangi_status == 'yopildi' else None
        obj.save(update_fields=['status', 'ustuvorlik', 'closed_at', 'updated_at'])
        log_amal(request.user, 'murojaat_holati', f'{obj.kod}: {obj.get_status_display()}', nishon_user=obj.foydalanuvchi)
        return Response(MurojaatSerializer(obj).data)

    def post(self, request, murojaat_id):
        from .models import MurojaatJavob
        from .serializers_extra import MurojaatSerializer
        obj = self._get(murojaat_id)
        if not obj:
            return Response({'detail': 'Murojaat topilmadi.'}, status=status.HTTP_404_NOT_FOUND)
        matn = str(request.data.get('matn', '')).strip()
        if not matn:
            return Response({'detail': 'Javob matnini yozing.'}, status=status.HTTP_400_BAD_REQUEST)
        MurojaatJavob.objects.create(murojaat=obj, muallif=request.user, matn=matn)
        obj.status = 'javob_berildi'
        obj.oxirgi_javob_adminniki = True
        obj.closed_at = None
        obj.save(update_fields=['status', 'oxirgi_javob_adminniki', 'closed_at', 'updated_at'])
        log_amal(request.user, 'murojaatga_javob', f'{obj.kod} murojaatiga javob berildi', nishon_user=obj.foydalanuvchi)
        return Response(MurojaatSerializer(obj).data)


# ==================== KUCHLI ANALITIKA ====================

class KuchliAnalitikaView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from datetime import timedelta
        from django.contrib.auth import get_user_model
        from django.db.models import Avg, Count, Max
        from django.db.models.functions import TruncDate
        from accounts.models import Filial, KirishTarixi
        from .models import (
            MashqNatija, OquvchiJavob, WritingNatija, SpeakingNatija,
            Sertifikat, Murojaat,
        )
        User = get_user_model()
        try:
            kunlar = max(7, min(365, int(request.query_params.get('kunlar', 30))))
        except ValueError:
            kunlar = 30
        since = timezone.now() - timedelta(days=kunlar)
        oquvchilar = User.objects.filter(role=User.ROLE_OQUVCHI)
        filial_id = request.query_params.get('filial')
        if filial_id:
            oquvchilar = oquvchilar.filter(filial_id=filial_id)
        ids = list(oquvchilar.values_list('id', flat=True))
        natijalar = MashqNatija.objects.filter(oquvchi_id__in=ids, boshlangan_vaqt__gte=since)
        avg = natijalar.aggregate(v=Avg('foiz'))['v'] or 0

        qiyin_mavzular = list(
            natijalar.values('mashq__dars__mavzu__nomi', 'mashq__dars__mavzu__daraja__fan__nomi')
            .annotate(ortacha=Avg('foiz'), urinishlar=Count('id'))
            .filter(urinishlar__gte=1)
            .order_by('ortacha')[:10]
        )
        qiyin_savollar = list(
            OquvchiJavob.objects.filter(natija__oquvchi_id__in=ids, natija__boshlangan_vaqt__gte=since, togri_berilgan=False)
            .values('savol__matn', 'savol__mashq__dars__sarlavha')
            .annotate(xatolar=Count('id'))
            .order_by('-xatolar')[:10]
        )
        kunlik = list(
            natijalar.annotate(sana=TruncDate('boshlangan_vaqt')).values('sana')
            .annotate(urinishlar=Count('id'), ortacha=Avg('foiz'))
            .order_by('sana')
        )

        latest_results = {
            x['oquvchi_id']: x for x in MashqNatija.objects.filter(oquvchi_id__in=ids)
            .values('oquvchi_id').annotate(last=Max('boshlangan_vaqt'), avg=Avg('foiz'), attempts=Count('id'))
        }
        latest_logins = {
            x['user_id']: x['last'] for x in KirishTarixi.objects.filter(user_id__in=ids, muvaffaqiyatli=True)
            .values('user_id').annotate(last=Max('created_at'))
        }
        risk = []
        seven_days = timezone.now() - timedelta(days=7)
        last_activity_map = {}
        for uid in ids:
            r = latest_results.get(uid, {})
            candidates = [d for d in [r.get('last'), latest_logins.get(uid)] if d]
            last_activity_map[uid] = max(candidates) if candidates else None
        faol_7_kun = sum(1 for value in last_activity_map.values() if value and value >= seven_days)

        for user in oquvchilar.select_related('filial')[:1000]:
            r = latest_results.get(user.id, {})
            last_activity = last_activity_map.get(user.id)
            reasons = []
            if not last_activity or last_activity < seven_days:
                reasons.append('7 kundan beri faol emas')
            if r and float(r.get('avg') or 0) < 60:
                reasons.append('o‘rtacha natija 60% dan past')
            if int(r.get('attempts') or 0) >= 5 and float(r.get('avg') or 0) < 70:
                reasons.append('ko‘p urinish, natija past')
            if reasons:
                risk.append({
                    'id': user.id,
                    'full_name': user.full_name,
                    'username': user.username,
                    'filial': user.filial.nomi if user.filial else '',
                    'ortacha': round(float(r.get('avg') or 0), 2),
                    'urinishlar': int(r.get('attempts') or 0),
                    'oxirgi_faollik': last_activity,
                    'sabablar': reasons,
                    'xavf_darajasi': 'yuqori' if len(reasons) >= 2 else 'orta',
                })
        risk.sort(key=lambda x: (0 if x['xavf_darajasi'] == 'yuqori' else 1, x['ortacha']))

        filiallar = []
        filial_qs = Filial.objects.all().order_by('nomi')
        if filial_id:
            filial_qs = filial_qs.filter(id=filial_id)
        for f in filial_qs:
            fids = list(oquvchilar.filter(filial=f).values_list('id', flat=True))
            fqs = MashqNatija.objects.filter(oquvchi_id__in=fids, boshlangan_vaqt__gte=since)
            filiallar.append({
                'id': f.id,
                'nomi': f.nomi,
                'oquvchilar': len(fids),
                'urinishlar': fqs.count(),
                'ortacha': round(float(fqs.aggregate(v=Avg('foiz'))['v'] or 0), 2),
                'sertifikatlar': Sertifikat.objects.filter(oquvchi_id__in=fids, berilgan_sana__gte=since).count(),
            })

        return Response({
            'davr_kunlari': kunlar,
            'umumiy': {
                'oquvchilar': len(ids),
                'faol_7_kun': faol_7_kun,
                'urinishlar': natijalar.count(),
                'ortacha_foiz': round(float(avg), 2),
                'sertifikatlar': Sertifikat.objects.filter(oquvchi_id__in=ids, berilgan_sana__gte=since).count(),
                'writing_ortacha': round(float(WritingNatija.objects.filter(oquvchi_id__in=ids, created_at__gte=since).aggregate(v=Avg('ai_foiz'))['v'] or 0), 2),
                'speaking_ortacha': round(float(SpeakingNatija.objects.filter(oquvchi_id__in=ids, created_at__gte=since).aggregate(v=Avg('ai_foiz'))['v'] or 0), 2),
                'ochiq_murojaatlar': Murojaat.objects.filter(foydalanuvchi_id__in=ids).exclude(status='yopildi').count(),
                'xavf_guruhi': len(risk),
            },
            'qiyin_mavzular': [
                {'mavzu': x['mashq__dars__mavzu__nomi'], 'fan': x['mashq__dars__mavzu__daraja__fan__nomi'], 'ortacha': round(float(x['ortacha'] or 0), 2), 'urinishlar': x['urinishlar']}
                for x in qiyin_mavzular
            ],
            'kop_xato_savollar': [
                {'savol': x['savol__matn'], 'dars': x['savol__mashq__dars__sarlavha'], 'xatolar': x['xatolar']}
                for x in qiyin_savollar
            ],
            'kunlik_faollik': [
                {'sana': x['sana'], 'urinishlar': x['urinishlar'], 'ortacha': round(float(x['ortacha'] or 0), 2)}
                for x in kunlik
            ],
            'xavf_guruhi': risk[:100],
            'filiallar': filiallar,
        })


# ==================== PLATFORMA SOZLAMALARI ====================

class PlatformSozlamaView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from .models import PlatformSozlama
        from .serializers_extra import PlatformSozlamaSerializer
        return Response(PlatformSozlamaSerializer(PlatformSozlama.load()).data)

    def patch(self, request):
        from .models import PlatformSozlama
        from .serializers_extra import PlatformSozlamaSerializer
        obj = PlatformSozlama.load()
        serializer = PlatformSozlamaSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        log_amal(request.user, 'platform_sozlamasi', 'Platforma sozlamalari yangilandi')
        return Response(serializer.data)


class PlatformHolatiView(APIView):
    def get(self, request):
        from .models import PlatformSozlama
        from .serializers_extra import PlatformSozlamaSerializer
        return Response(PlatformSozlamaSerializer(PlatformSozlama.load()).data)
