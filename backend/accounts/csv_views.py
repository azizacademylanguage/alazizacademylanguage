"""CSV export/import — Admin uchun foydalanuvchilarni yuklab olish/yuklash."""
import csv
import io

from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsAdmin
from exams.audit import log_amal

User = get_user_model()


class FoydalanuvchilarCSVExportView(APIView):
    """GET /api/admin/export/users.csv -> barcha foydalanuvchilar ro'yxati CSV formatda"""
    permission_classes = [IsAdmin]

    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="foydalanuvchilar.csv"'
        response.write('\ufeff')  # Excel uchun UTF-8 BOM

        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Ism', 'Familya', 'Rol', 'Filial', 'Faol', "Yaratilgan sana"])

        for u in User.objects.all().select_related('filial').order_by('id'):
            writer.writerow([
                u.id, u.username, u.ism, u.familya, u.get_role_display(),
                u.filial.nomi if u.filial else '', 'Ha' if u.faol else "Yo'q",
                u.created_at.strftime('%Y-%m-%d %H:%M'),
            ])

        log_amal(request.user, 'csv_export', 'Foydalanuvchilar CSV eksport qilindi')
        return response


class NatijalarCSVExportView(APIView):
    """GET /api/admin/export/natijalar.csv -> barcha mashq natijalari CSV formatda"""
    permission_classes = [IsAdmin]

    def get(self, request):
        from exams.models import MashqNatija

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="natijalar.csv"'
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow(["O'quvchi", 'Mashq', "To'g'ri", 'Jami', 'Foiz', 'Urinish', 'Sana'])

        for n in MashqNatija.objects.select_related('oquvchi', 'mashq').order_by('-boshlangan_vaqt')[:5000]:
            writer.writerow([
                n.oquvchi.full_name, n.mashq.sarlavha, n.togri_soni, n.jami_soni,
                str(n.foiz), n.urinish_raqami, n.boshlangan_vaqt.strftime('%Y-%m-%d %H:%M'),
            ])

        log_amal(request.user, 'csv_export', 'Natijalar CSV eksport qilindi')
        return response


class OquvchilarCSVImportView(APIView):
    """
    POST /api/nazoratchi/oquvchilar/csv-import/  multipart: {file}
    CSV format: username,password,ism,familya  (har qatorda bitta o'quvchi)
    Nazoratchi o'z filialiga ko'plab o'quvchini bir vaqtda import qila oladi.
    """
    permission_classes = [IsAdmin]  # Admin va Nazoratchi versiyalari alohida route bo'lishi mumkin, hozircha admin

    def post(self, request):
        fayl = request.FILES.get('file')
        if not fayl:
            return Response({'detail': "CSV fayl yuborilishi shart."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = fayl.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            return Response({'detail': "Fayl kodировкаси noto'g'ri, UTF-8 formatda saqlang."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(io.StringIO(data))
        yaratilganlar = []
        xatolar = []

        for idx, row in enumerate(reader, start=2):
            username = (row.get('username') or '').strip()
            password = (row.get('password') or '').strip()
            ism = (row.get('ism') or '').strip()
            familya = (row.get('familya') or '').strip()

            if not username or not password:
                xatolar.append(f"Qator {idx}: username yoki password bo'sh")
                continue
            if username.casefold() == password.casefold():
                xatolar.append(f"Qator {idx}: login va parol bir xil bo'lishi mumkin emas")
                continue
            if User.objects.filter(username__iexact=username).exists():
                xatolar.append(f"Qator {idx}: '{username}' allaqachon mavjud")
                continue

            user = User(username=username, role=User.ROLE_OQUVCHI, ism=ism, familya=familya, yaratgan=request.user)
            user.set_password(password)
            user.save()
            yaratilganlar.append(username)

        log_amal(request.user, 'csv_import', f"{len(yaratilganlar)} o'quvchi import qilindi")
        return Response({
            'yaratildi': len(yaratilganlar),
            'yaratilganlar': yaratilganlar,
            'xatolar': xatolar,
        }, status=status.HTTP_201_CREATED)
