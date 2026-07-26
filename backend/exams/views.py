from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsOquvchi, IsNazoratchi
from courses.access import (MAVZU_OTISH_FOIZI, keyingi_mavzu, mavzu_ochiqmi,
                            oquvchiga_fan_biriktirilganmi)
from .models import Mashq, Savol, Javob, MashqNatija, OquvchiJavob
from .serializers import (
    MashqSerializer, MashqOquvchigaSerializer, MashqNatijaSerializer,
    OquvchiJavobBatafsilSerializer
)


# ==================== ADMIN: MASHQ/SAVOL/JAVOB CRUD ====================

class MashqViewSet(viewsets.ModelViewSet):
    queryset = Mashq.objects.all()
    serializer_class = MashqSerializer
    permission_classes = [IsAdmin]


class SavolViewSet(viewsets.ModelViewSet):
    from .serializers import SavolSerializer
    queryset = Savol.objects.all()
    serializer_class = SavolSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = Savol.objects.all()
        mashq_id = self.request.query_params.get('mashq')
        if mashq_id:
            qs = qs.filter(mashq_id=mashq_id)
        return qs


class JavobViewSet(viewsets.ModelViewSet):
    from .serializers import JavobSerializer
    queryset = Javob.objects.all()
    serializer_class = JavobSerializer
    permission_classes = [IsAdmin]


# ==================== O'QUVCHI: MASHQNI YECHISH ====================

class MashqOlishView(APIView):
    """GET /api/oquvchi/mashq/{id}/ -> savollarni to'g'ri javobsiz qaytaradi"""
    permission_classes = [IsOquvchi]

    def get(self, request, mashq_id):
        try:
            mashq = Mashq.objects.select_related('dars__mavzu__daraja').get(id=mashq_id)
        except Mashq.DoesNotExist:
            return Response({'detail': 'Mashq topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        daraja = mashq.dars.mavzu.daraja
        if not oquvchiga_fan_biriktirilganmi(request.user, daraja.fan):
            return Response({'detail': 'Sizga bu mashqning fani biriktirilmagan.'}, status=status.HTTP_403_FORBIDDEN)
        if not mavzu_ochiqmi(request.user, mashq.dars.mavzu):
            return Response({
                'detail': "Bu mavzu qulflangan. Avval oldingi mavzu testidan kamida 80% oling.",
                'qulflangan': True,
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = MashqOquvchigaSerializer(mashq)
        return Response(serializer.data)


class MashqTopshirishView(APIView):
    """
    POST /api/oquvchi/mashq/{id}/topshirish/
    body: { javoblar: [ {savol: id, tanlangan_javoblar: [id,...]} yoki {savol: id, matn_javob: "..."} , ... ] }
    -> avtomatik baholaydi, foiz hisoblaydi, natijani saqlaydi
    """
    permission_classes = [IsOquvchi]

    def post(self, request, mashq_id):
        try:
            mashq = Mashq.objects.select_related('dars__mavzu__daraja').get(id=mashq_id)
        except Mashq.DoesNotExist:
            return Response({'detail': 'Mashq topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        daraja = mashq.dars.mavzu.daraja
        if not oquvchiga_fan_biriktirilganmi(request.user, daraja.fan):
            return Response({'detail': 'Sizga bu mashqning fani biriktirilmagan.'}, status=status.HTTP_403_FORBIDDEN)
        if not mavzu_ochiqmi(request.user, mashq.dars.mavzu):
            return Response({
                'detail': "Bu mavzu qulflangan. Avval oldingi mavzu testidan kamida 80% oling.",
                'qulflangan': True,
            }, status=status.HTTP_403_FORBIDDEN)

        javoblar_data = request.data.get('javoblar', [])
        savollar = {s.id: s for s in mashq.savollar.all()}

        urinish_raqami = MashqNatija.objects.filter(oquvchi=request.user, mashq=mashq).count() + 1

        natija = MashqNatija.objects.create(
            oquvchi=request.user,
            mashq=mashq,
            jami_soni=len(savollar),
            urinish_raqami=urinish_raqami,
        )

        togri_soni = 0
        for item in javoblar_data:
            savol_id = item.get('savol')
            savol = savollar.get(savol_id)
            if not savol:
                continue

            togri_berilgan = False
            oquvchi_javob = OquvchiJavob.objects.create(
                natija=natija,
                savol=savol,
                matn_javob=item.get('matn_javob', ''),
            )

            if savol.tur == Savol.TUR_TEXT:
                berilgan_matn = (item.get('matn_javob') or '').strip().lower()
                togri_matn = (savol.togri_matn_javob or '').strip().lower()
                togri_berilgan = bool(berilgan_matn) and berilgan_matn == togri_matn
            else:
                tanlangan_ids = set(item.get('tanlangan_javoblar', []))
                togri_ids = set(savol.javoblar.filter(togri=True).values_list('id', flat=True))
                togri_berilgan = tanlangan_ids == togri_ids and len(tanlangan_ids) > 0
                if tanlangan_ids:
                    oquvchi_javob.tanlangan_javoblar.set(tanlangan_ids)

            oquvchi_javob.togri_berilgan = togri_berilgan
            oquvchi_javob.save()

            if togri_berilgan:
                togri_soni += 1

        jami = len(savollar) or 1
        foiz = round((togri_soni / jami) * 100, 2)

        natija.togri_soni = togri_soni
        natija.foiz = foiz
        natija.tugagan_vaqt = timezone.now()
        natija.save()

        if foiz >= MAVZU_OTISH_FOIZI:
            from .coins import coin_qoshish
            coin_qoshish(request.user, 5, 'mashq', f"{mashq.sarlavha} mashqi {foiz}% bilan tugatildi")

        data = MashqNatijaSerializer(natija).data
        data['otdi'] = foiz >= MAVZU_OTISH_FOIZI
        data['otish_foizi'] = MAVZU_OTISH_FOIZI
        data['daraja_id'] = mashq.dars.mavzu.daraja_id
        navbatdagi = keyingi_mavzu(mashq.dars.mavzu)
        data['keyingi_mavzu_id'] = navbatdagi.id if navbatdagi else None
        data['keyingi_mavzu_ochildi'] = bool(navbatdagi and mavzu_ochiqmi(request.user, navbatdagi))
        data['xabar'] = (
            "Tabriklaymiz! Keyingi mavzu ochildi."
            if data['keyingi_mavzu_ochildi']
            else ("Testdan o'tdingiz." if data['otdi'] else "Keyingi mavzu ochilishi uchun kamida 80% oling.")
        )
        return Response(data, status=status.HTTP_201_CREATED)


class NatijalarimView(APIView):
    """GET /api/oquvchi/natijalarim/ -> o'zining barcha natijalari"""
    permission_classes = [IsOquvchi]

    def get(self, request):
        natijalar = MashqNatija.objects.filter(oquvchi=request.user).order_by('-boshlangan_vaqt')
        return Response(MashqNatijaSerializer(natijalar, many=True).data)


class XatolarimView(APIView):
    """GET /api/oquvchi/xatolarim/{mashq_id}/ -> so'nggi urinishdagi xato javoblar"""
    permission_classes = [IsOquvchi]

    def get(self, request, mashq_id):
        oxirgi_natija = MashqNatija.objects.filter(
            oquvchi=request.user, mashq_id=mashq_id
        ).order_by('-boshlangan_vaqt').first()

        if not oxirgi_natija:
            return Response({'detail': 'Natija topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        xato_javoblar = oxirgi_natija.berilgan_javoblar.filter(togri_berilgan=False)
        return Response(OquvchiJavobBatafsilSerializer(xato_javoblar, many=True).data)


# ==================== NAZORATCHI: O'QUVCHI STATISTIKASI ====================

class OquvchiStatistikaView(APIView):
    """GET /api/nazoratchi/oquvchilar/{id}/statistika/"""
    permission_classes = [IsNazoratchi]

    def get(self, request, oquvchi_id):
        from django.contrib.auth import get_user_model
        from django.db.models import Avg
        User = get_user_model()
        try:
            oquvchi = User.objects.get(id=oquvchi_id, role=User.ROLE_OQUVCHI, yaratgan=request.user)
        except User.DoesNotExist:
            return Response({'detail': "O'quvchi topilmadi yoki sizga tegishli emas."}, status=status.HTTP_404_NOT_FOUND)

        natijalar = MashqNatija.objects.filter(oquvchi=oquvchi).order_by('-boshlangan_vaqt')
        ortacha = natijalar.aggregate(a=Avg('foiz'))['a'] or 0

        return Response({
            'oquvchi': oquvchi.full_name,
            'jami_urinishlar': natijalar.count(),
            'ortacha_foiz': round(float(ortacha), 2),
            'natijalar': MashqNatijaSerializer(natijalar, many=True).data,
        })
