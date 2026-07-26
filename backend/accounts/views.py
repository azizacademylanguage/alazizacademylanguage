import logging

from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Avg

from .models import Filial
from .serializers import (
    MyTokenObtainPairSerializer, UserMeSerializer, FilialSerializer,
    NazoratchiSerializer, OquvchiSerializer, AdminOquvchiSerializer
)
from .permissions import IsAdmin, IsNazoratchi

User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ -> {access, refresh, user: {...}}"""
    serializer_class = MyTokenObtainPairSerializer


class MeView(APIView):
    """GET /api/auth/me/ -> joriy foydalanuvchi ma'lumotlari"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)


# ==================== ADMIN: FILIALLAR ====================

class FilialViewSet(viewsets.ModelViewSet):
    """
    GET/POST /api/admin/filiallar/
    GET/PUT/DELETE /api/admin/filiallar/{id}/
    """
    queryset = Filial.objects.all().order_by('nomi')
    serializer_class = FilialSerializer
    permission_classes = [IsAdmin]


# ==================== ADMIN: NAZORATCHILAR ====================

class NazoratchiViewSet(viewsets.ModelViewSet):
    """
    GET/POST /api/admin/nazoratchilar/
    GET/PUT/DELETE /api/admin/nazoratchilar/{id}/
    """
    serializer_class = NazoratchiSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(role=User.ROLE_NAZORATCHI).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()


# ==================== ADMIN: O'QUVCHILAR ====================

class AdminOquvchiViewSet(viewsets.ModelViewSet):
    """
    GET/POST /api/admin/oquvchilar/
    GET/PUT/PATCH/DELETE /api/admin/oquvchilar/{id}/

    Admin o'quvchini login, parol, fan va daraja bilan birga yaratadi.
    """
    serializer_class = AdminOquvchiSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.filter(role=User.ROLE_OQUVCHI).prefetch_related(
            'biriktirilgan_fanlar__daraja__fan'
        ).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as exc:
            # Password is never written to logs. Unexpected production errors
            # become visible in Railway logs with a stable error code.
            logger.exception(
                "ADMIN_STUDENT_CREATE_FAILED username=%s daraja=%s error=%s",
                request.data.get('username', ''),
                request.data.get('daraja', ''),
                exc.__class__.__name__,
            )
            raise


class AdminStatistikaView(APIView):
    """GET /api/admin/statistika/ -> umumiy tizim statistikasi"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from exams.models import MashqNatija
        filiallar = Filial.objects.all()
        data = []
        for f in filiallar:
            oquvchilar = User.objects.filter(role=User.ROLE_OQUVCHI, filial=f)
            natijalar = MashqNatija.objects.filter(oquvchi__in=oquvchilar)
            ortacha_foiz = natijalar.aggregate(a=Avg('foiz'))['a'] or 0
            data.append({
                'filial_id': f.id,
                'filial_nomi': f.nomi,
                'nazoratchilar_soni': User.objects.filter(role=User.ROLE_NAZORATCHI, filial=f).count(),
                'oquvchilar_soni': oquvchilar.count(),
                'ortacha_foiz': round(float(ortacha_foiz), 2),
            })
        return Response({
            'jami_filiallar': filiallar.count(),
            'jami_nazoratchilar': User.objects.filter(role=User.ROLE_NAZORATCHI).count(),
            'jami_oquvchilar': User.objects.filter(role=User.ROLE_OQUVCHI).count(),
            'filiallar_kesimida': data,
        })


# ==================== NAZORATCHI: O'QUVCHILAR ====================

class OquvchiViewSet(viewsets.ModelViewSet):
    """
    GET/POST /api/nazoratchi/oquvchilar/
    GET/PUT/DELETE /api/nazoratchi/oquvchilar/{id}/
    Nazoratchi faqat o'zi yaratgan o'quvchilarni ko'radi va boshqaradi.
    """
    serializer_class = OquvchiSerializer
    permission_classes = [IsNazoratchi]

    def get_queryset(self):
        return User.objects.filter(role=User.ROLE_OQUVCHI, yaratgan=self.request.user).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class NazoratchiStatistikaView(APIView):
    """GET /api/nazoratchi/statistika/ -> filial bo'yicha statistika"""
    permission_classes = [IsNazoratchi]

    def get(self, request):
        from exams.models import MashqNatija
        from django.db.models import Avg
        oquvchilar = User.objects.filter(role=User.ROLE_OQUVCHI, yaratgan=request.user)
        natijalar = MashqNatija.objects.filter(oquvchi__in=oquvchilar)
        ortacha = natijalar.aggregate(a=Avg('foiz'))['a'] or 0
        return Response({
            'oquvchilar_soni': oquvchilar.count(),
            'jami_urinishlar': natijalar.count(),
            'ortacha_foiz': round(float(ortacha), 2),
        })
