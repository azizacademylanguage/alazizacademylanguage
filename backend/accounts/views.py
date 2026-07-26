import logging

from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.db.models import Avg, Count, Q, Sum

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
        # select_related filial so'rovini kamaytiradi; annotation esa har bir
        # nazoratchi uchun alohida COUNT so'rovi yuborilishining oldini oladi.
        return User.objects.filter(role=User.ROLE_NAZORATCHI).select_related('filial').annotate(
            _oquvchilar_soni=Count(
                'yaratganlari',
                filter=Q(yaratganlari__role=User.ROLE_OQUVCHI),
                distinct=True,
            )
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except DatabaseError as exc:
            # Migration hali relationship indeksini tiklayotgan paytda ham admin
            # sahifasi butunlay qulab tushmasin. Minimal ro'yxat qaytariladi va
            # Railway logida aniq diagnostika qoladi.
            logger.exception('ADMIN_NAZORATCHILAR_LIST_FAILED error=%s', exc.__class__.__name__)
            try:
                rows = list(User.objects.filter(role=User.ROLE_NAZORATCHI).values(
                    'id', 'username', 'ism', 'familya', 'filial_id', 'faol', 'created_at'
                ).order_by('-created_at'))
                filial_ids = [row['filial_id'] for row in rows if row.get('filial_id')]
                filial_map = dict(Filial.objects.filter(id__in=filial_ids).values_list('id', 'nomi'))
                data = [
                    {
                        **row,
                        'filial': row.get('filial_id'),
                        'filial_nomi': filial_map.get(row.get('filial_id'), ''),
                        'oquvchilar_soni': 0,
                    }
                    for row in rows
                ]
                return Response(data)
            except DatabaseError as fallback_exc:
                logger.exception(
                    'ADMIN_NAZORATCHILAR_FALLBACK_FAILED error=%s',
                    fallback_exc.__class__.__name__,
                )
                return Response(
                    {"detail": "Baza migratsiyasi yakunlanmoqda. Bir necha soniyadan keyin qayta urinib ko'ring."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

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


class KengaytirilganStatistikaView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        from exams.models import MashqNatija, ListeningNatija, SpeakingNatija, WritingNatija, Sertifikat, CoinTarix
        students = User.objects.filter(role=User.ROLE_OQUVCHI)
        today = timezone.localdate()
        week = timezone.now() - timedelta(days=7)
        inactive = students.exclude(last_login__gte=week)
        expiring = students.filter(obuna_tugashi__range=(today, today + timedelta(days=5)))
        by_level = list(students.values('biriktirilgan_fanlar__daraja__nomi').annotate(soni=Count('id')).order_by('-soni')[:15])
        return Response({
            'faol_7_kun': students.filter(last_login__gte=week).count(),
            'faol_emas_7_kun': inactive.count(),
            'muddati_5_kunda_tugaydi': expiring.count(),
            'qarzdorlar': students.filter(tolov_holati='qarzdor').count(),
            'mashq_ortacha': round(float(MashqNatija.objects.aggregate(v=Avg('foiz'))['v'] or 0),2),
            'listening_ortacha': round(float(ListeningNatija.objects.aggregate(v=Avg('foiz'))['v'] or 0),2),
            'speaking_ortacha': round(float(SpeakingNatija.objects.aggregate(v=Avg('ai_foiz'))['v'] or 0),2),
            'writing_ortacha': round(float(WritingNatija.objects.aggregate(v=Avg('ai_foiz'))['v'] or 0),2),
            'sertifikatlar': Sertifikat.objects.count(),
            'coin_aylanmasi': CoinTarix.objects.aggregate(v=Sum('miqdor'))['v'] or 0,
            'darajalar_kesimida': by_level,
            'etibor_talab_qiladi': [{'id':u.id,'ism':u.full_name,'login':u.username,'oxirgi_kirish':u.last_login} for u in inactive[:20]],
        })

class ReytingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        from django.db.models import Sum, Max
        from exams.models import MashqNatija, ListeningNatija, SpeakingNatija, WritingNatija, CoinTarix
        qs=User.objects.filter(role=User.ROLE_OQUVCHI, faol=True)
        if request.user.role == User.ROLE_NAZORATCHI:
            qs=qs.filter(filial=request.user.filial)
        rows=[]
        for u in qs.select_related('filial'):
            test=float(MashqNatija.objects.filter(oquvchi=u).aggregate(v=Max('foiz'))['v'] or 0)
            listen=float(ListeningNatija.objects.filter(oquvchi=u).aggregate(v=Max('foiz'))['v'] or 0)
            speak=float(SpeakingNatija.objects.filter(oquvchi=u).aggregate(v=Max('ai_foiz'))['v'] or 0)
            write=float(WritingNatija.objects.filter(oquvchi=u).aggregate(v=Max('ai_foiz'))['v'] or 0)
            coin=CoinTarix.objects.filter(oquvchi=u).aggregate(v=Sum('miqdor'))['v'] or 0
            ball=round(test+listen+speak+write+max(0,coin),2)
            rows.append({'id':u.id,'ism':u.full_name,'filial':u.filial.nomi if u.filial else '—','ball':ball,'test':test,'listening':listen,'speaking':speak,'writing':write,'coin':coin})
        rows=sorted(rows,key=lambda x:x['ball'],reverse=True)
        for i,row in enumerate(rows,1): row['orin']=i
        return Response(rows[:100])
