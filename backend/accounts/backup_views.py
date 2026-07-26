import csv
import io
import json
import zipfile
from datetime import datetime

from django.apps import apps
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.db import models, transaction
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdmin
from exams.audit import log_amal

BACKUP_MODELS = [
    'accounts.Filial', 'accounts.User', 'courses.Fan', 'courses.Daraja', 'courses.Mavzu', 'courses.Dars',
    'courses.OquvchiFan', 'courses.DarsProgress', 'exams.Mashq', 'exams.Savol', 'exams.Javob',
    'exams.MashqNatija', 'exams.GateTestNatija', 'exams.FinalTestNatija', 'exams.Sertifikat',
    'exams.WritingNatija', 'exams.SpeakingNatija', 'exams.ListeningNatija', 'exams.OquvchiCoin',
    'exams.CoinTarix', 'exams.ShopBuyurtma', 'exams.AdminAmalLog', 'exams.Musobaqa',
]


def _json_default(value):
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)


def build_backup_bytes():
    memory = io.BytesIO()
    manifest = {'created_at': timezone.now().isoformat(), 'format': 1, 'models': {}}
    with zipfile.ZipFile(memory, 'w', zipfile.ZIP_DEFLATED) as archive:
        for label in BACKUP_MODELS:
            model = apps.get_model(label)
            rows = list(model.objects.all().values())
            manifest['models'][label] = len(rows)
            archive.writestr(f"data/{label.replace('.', '_')}.json", json.dumps(rows, ensure_ascii=False, default=_json_default, indent=2))
        archive.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Model', 'Qatorlar soni'])
        for name, count in manifest['models'].items():
            writer.writerow([name, count])
        archive.writestr('summary.csv', output.getvalue())
    return memory.getvalue(), manifest


class BackupDownloadView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        payload, manifest = build_backup_bytes()
        log_amal(request.user, 'backup_yuklandi', f"{sum(manifest['models'].values())} qator", request=request)
        filename = f"alaziz_backup_{datetime.now():%Y%m%d_%H%M}.zip"
        response = HttpResponse(payload, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class BackupRestoreView(APIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request):
        if request.headers.get('X-Restore-Confirm') != 'RESTORE':
            return Response({'detail': "Tiklash uchun X-Restore-Confirm: RESTORE sarlavhasi kerak."}, status=status.HTTP_400_BAD_REQUEST)
        upload = request.FILES.get('file')
        if not upload or not upload.name.lower().endswith('.zip'):
            return Response({'detail': 'Faqat platforma yaratgan .zip backup faylini yuboring.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            archive = zipfile.ZipFile(upload)
            manifest = json.loads(archive.read('manifest.json'))
        except Exception:
            return Response({'detail': "Backup fayli noto'g'ri yoki manifest topilmadi."}, status=status.HTTP_400_BAD_REQUEST)
        if manifest.get('format') != 1:
            return Response({'detail': "Backup formati qo'llab-quvvatlanmaydi."}, status=status.HTTP_400_BAD_REQUEST)

        restored = {}
        model_classes = []
        try:
            with transaction.atomic():
                for label in BACKUP_MODELS:
                    filename = f"data/{label.replace('.', '_')}.json"
                    if filename not in archive.namelist():
                        continue
                    model = apps.get_model(label)
                    model_classes.append(model)
                    rows = json.loads(archive.read(filename))
                    allowed = {field.attname: field for field in model._meta.concrete_fields}
                    count = 0
                    for row in rows:
                        pk_name = model._meta.pk.attname
                        pk = row.get(pk_name)
                        if pk is None:
                            continue
                        defaults = {}
                        for key, value in row.items():
                            if key == pk_name or key not in allowed:
                                continue
                            field = allowed[key]
                            if value not in (None, ''):
                                if isinstance(field, models.DateTimeField) and isinstance(value, str):
                                    value = parse_datetime(value) or value
                                elif isinstance(field, models.DateField) and not isinstance(field, models.DateTimeField) and isinstance(value, str):
                                    value = parse_date(value) or value
                            defaults[key] = value
                        model.objects.update_or_create(**{pk_name: pk}, defaults=defaults)
                        count += 1
                    restored[label] = count
                from .db_utils import reset_model_sequences
                reset_model_sequences(model_classes)
        except Exception as exc:
            return Response({'detail': f"Tiklash bekor qilindi: {exc.__class__.__name__}: {exc}"}, status=status.HTTP_400_BAD_REQUEST)
        log_amal(request.user, 'backup_tiklandi', str(restored), yangi_holat=restored, request=request)
        return Response({'tiklandi': restored, 'jami': sum(restored.values())})
