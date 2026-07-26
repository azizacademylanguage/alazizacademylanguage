from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin, IsNazoratchi, IsOquvchi
from .models import Fan, Daraja, Mavzu, Dars, OquvchiFan, DarsProgress
from .access import daraja_ochiqmi, mavzu_ochiqmi, oquvchiga_fan_biriktirilganmi
from .serializers import (
    FanSerializer, FanQisqaSerializer, FanRoyxatSerializer, DarajaSerializer, DarajaQisqaSerializer,
    MavzuSerializer, MavzuQisqaSerializer, DarsSerializer,
    OquvchiFanSerializer, DarsProgressSerializer
)


# ==================== ADMIN: FAN/DARAJA/MAVZU/DARS CRUD ====================

class FanViewSet(viewsets.ModelViewSet):
    """GET ochiq hammaga (o'quvchi ham ko'rishi kerak bo'lishi mumkin), lekin
    yozish faqat Admin uchun."""
    queryset = Fan.objects.prefetch_related('darajalar').all().order_by('tartib')
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return FanRoyxatSerializer
        return FanSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class DarajaViewSet(viewsets.ModelViewSet):
    serializer_class = DarajaQisqaSerializer
    queryset = Daraja.objects.all().order_by('tartib')

    def get_queryset(self):
        qs = Daraja.objects.all().order_by('tartib')
        fan_id = self.request.query_params.get('fan')
        if fan_id:
            qs = qs.filter(fan_id=fan_id)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class MavzuViewSet(viewsets.ModelViewSet):
    serializer_class = MavzuSerializer
    queryset = Mavzu.objects.all().order_by('tartib')

    def get_queryset(self):
        qs = Mavzu.objects.all().order_by('tartib')
        daraja_id = self.request.query_params.get('daraja')
        if daraja_id:
            qs = qs.filter(daraja_id=daraja_id)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


class DarsViewSet(viewsets.ModelViewSet):
    serializer_class = DarsSerializer
    queryset = Dars.objects.all().order_by('tartib')

    def get_queryset(self):
        qs = Dars.objects.all().order_by('tartib')
        mavzu_id = self.request.query_params.get('mavzu')
        if mavzu_id:
            qs = qs.filter(mavzu_id=mavzu_id)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]


# ==================== NAZORATCHI: FAN BIRIKTIRISH ====================

class FanBiriktirishView(APIView):
    """POST /api/nazoratchi/oquvchilar/{id}/fan-biriktirish/  body: {daraja: id}"""
    permission_classes = [IsNazoratchi]

    def post(self, request, oquvchi_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            oquvchi = User.objects.get(id=oquvchi_id, role=User.ROLE_OQUVCHI, yaratgan=request.user)
        except User.DoesNotExist:
            return Response({'detail': "O'quvchi topilmadi yoki sizga tegishli emas."}, status=status.HTTP_404_NOT_FOUND)

        daraja_id = request.data.get('daraja')
        if not daraja_id:
            return Response({'detail': "'daraja' maydoni majburiy."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            daraja = Daraja.objects.get(id=daraja_id)
        except Daraja.DoesNotExist:
            return Response({'detail': "Daraja topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        # O'quvchiga faqat bitta fan va boshlang'ich daraja tanlanadi.
        OquvchiFan.objects.filter(oquvchi=oquvchi).delete()
        obj, created = OquvchiFan.objects.get_or_create(
            oquvchi=oquvchi,
            daraja=daraja,
            defaults={'biriktirgan': request.user, 'qolda_ochilgan': True},
        )
        if not created and not obj.qolda_ochilgan:
            obj.qolda_ochilgan = True
            obj.biriktirgan = request.user
            obj.save(update_fields=['qolda_ochilgan', 'biriktirgan'])
        from exams.audit import log_amal
        log_amal(
            request.user, 'fan_biriktirildi',
            f"{daraja} biriktirildi", nishon_user=oquvchi
        )
        serializer = OquvchiFanSerializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, oquvchi_id):
        """Fan biriktirishni bekor qilish: body: {daraja: id}"""
        daraja_id = request.data.get('daraja')
        OquvchiFan.objects.filter(oquvchi_id=oquvchi_id, daraja_id=daraja_id, biriktirgan=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== O'QUVCHI: FANLARIM / MAVZULAR / DARS ====================

class FanlarimView(APIView):
    """GET /api/oquvchi/fanlarim/ -> menga biriktirilgan fan+daraja ro'yxati"""
    permission_classes = [IsOquvchi]

    def get(self, request):
        # Har bir o'quvchiga faqat admin tanlagan bitta fan ko'rsatiladi.
        biriktirilgan = OquvchiFan.objects.filter(oquvchi=request.user).select_related(
            'daraja__fan'
        ).prefetch_related('daraja__fan__darajalar').order_by(
            '-created_at', '-id'
        )[:1]
        serializer = OquvchiFanSerializer(biriktirilgan, many=True)
        return Response(serializer.data)


class MavzularView(APIView):
    """GET /api/oquvchi/mavzular/{daraja_id}/ -> mavzular + har dars progress bilan"""
    permission_classes = [IsOquvchi]

    def get(self, request, daraja_id):
        try:
            daraja = Daraja.objects.select_related('fan').get(id=daraja_id)
        except Daraja.DoesNotExist:
            return Response({'detail': 'Daraja topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if not oquvchiga_fan_biriktirilganmi(request.user, daraja.fan):
            return Response({'detail': "Sizga bu fan biriktirilmagan."}, status=status.HTTP_403_FORBIDDEN)

        if not daraja_ochiqmi(request.user, daraja):
            return Response({
                'detail': "Bu daraja hali qulflangan. Avval oldingi darajaning yakuniy testidan kamida 80% oling.",
                'qulflangan': True,
            }, status=status.HTTP_403_FORBIDDEN)

        mavzular = Mavzu.objects.filter(daraja_id=daraja_id).prefetch_related(
            'darslar__progresslar', 'darslar__mashq__natijalar'
        ).order_by('tartib', 'id')
        serializer = MavzuQisqaSerializer(mavzular, many=True, context={'oquvchi': request.user})
        return Response(serializer.data)


class DarsBatafsilView(APIView):
    """GET /api/oquvchi/dars/{id}/ -> dars tafsilotlari (ruxsat tekshirilgan holda)"""
    permission_classes = [IsOquvchi]

    def get(self, request, dars_id):
        try:
            dars = Dars.objects.select_related('mavzu__daraja').get(id=dars_id)
        except Dars.DoesNotExist:
            return Response({'detail': 'Dars topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        daraja = dars.mavzu.daraja
        if not oquvchiga_fan_biriktirilganmi(request.user, daraja.fan):
            return Response({'detail': "Sizga bu darsning fani biriktirilmagan."}, status=status.HTTP_403_FORBIDDEN)
        if not mavzu_ochiqmi(request.user, dars.mavzu):
            return Response({
                'detail': "Bu mavzu qulflangan. Avval oldingi mavzu testidan kamida 80% oling.",
                'qulflangan': True,
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = DarsSerializer(dars)
        progress, _ = DarsProgress.objects.get_or_create(oquvchi=request.user, dars=dars)
        data = serializer.data
        data['progress'] = DarsProgressSerializer(progress).data
        data['mashq_bor'] = hasattr(dars, 'mashq')
        if hasattr(dars, 'mashq'):
            data['mashq_id'] = dars.mashq.id
        return Response(data)


class DarsProgressSaqlashView(APIView):
    """POST /api/oquvchi/dars/{id}/progress/  body: {video_pozitsiya_soniya, video_tugatilgan}"""
    permission_classes = [IsOquvchi]

    def post(self, request, dars_id):
        try:
            dars = Dars.objects.get(id=dars_id)
        except Dars.DoesNotExist:
            return Response({'detail': 'Dars topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        daraja = dars.mavzu.daraja
        if not oquvchiga_fan_biriktirilganmi(request.user, daraja.fan):
            return Response({'detail': "Sizga bu darsning fani biriktirilmagan."}, status=status.HTTP_403_FORBIDDEN)
        if not mavzu_ochiqmi(request.user, dars.mavzu):
            return Response({'detail': "Bu mavzu hali qulflangan."}, status=status.HTTP_403_FORBIDDEN)

        progress, _ = DarsProgress.objects.get_or_create(oquvchi=request.user, dars=dars)
        if 'video_pozitsiya_soniya' in request.data:
            progress.video_pozitsiya_soniya = request.data['video_pozitsiya_soniya']
        if 'video_tugatilgan' in request.data:
            progress.video_tugatilgan = request.data['video_tugatilgan']
        progress.save()
        return Response(DarsProgressSerializer(progress).data)
