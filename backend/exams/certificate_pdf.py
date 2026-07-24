"""Sertifikat PDF va QR kodini yaratish yordamchilari."""
from io import BytesIO

import qrcode
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


PALETTE = {
    'amethyst': '#3C1642',
    'teal': '#086375',
    'forest': '#082900',
    'olive': '#3B6402',
    'jungle': '#117E68',
    'paper': '#FFFFFF',
    'muted': '#5A665F',
}


def certificate_public_url(sertifikat) -> str:
    base = getattr(settings, 'FRONTEND_PUBLIC_URL', 'http://localhost:5173').rstrip('/')
    return f"{base}/sertifikat/{sertifikat.kod}"


def certificate_qr_bytes(sertifikat) -> bytes:
    qr = qrcode.QRCode(version=None, box_size=8, border=3)
    qr.add_data(certificate_public_url(sertifikat))
    qr.make(fit=True)
    image = qr.make_image(fill_color=PALETTE['forest'], back_color='white')
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def _ascii_text(value) -> str:
    """ReportLab standart shriftlarida xavfsiz ko'rinishi uchun tinish belgilarini soddalashtiradi."""
    return str(value or '').replace('’', "'").replace('‘', "'").replace('—', '-').replace('–', '-')


def certificate_pdf_bytes(sertifikat) -> bytes:
    buffer = BytesIO()
    width, height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=(width, height))
    pdf.setTitle(f"Sertifikat {sertifikat.kod}")
    pdf.setAuthor("AL-AZIZ ACADEMY")

    # Oq asos va rangli ramkalar.
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, width, height, stroke=0, fill=1)
    pdf.setStrokeColor(colors.HexColor(PALETTE['forest']))
    pdf.setLineWidth(10)
    pdf.rect(18, 18, width - 36, height - 36, stroke=1, fill=0)
    pdf.setStrokeColor(colors.HexColor(PALETTE['teal']))
    pdf.setLineWidth(2)
    pdf.rect(31, 31, width - 62, height - 62, stroke=1, fill=0)

    # Dekorativ shakllar.
    pdf.setFillColor(colors.HexColor(PALETTE['amethyst']))
    pdf.circle(44, height - 44, 70, stroke=0, fill=1)
    pdf.setFillColor(colors.HexColor(PALETTE['jungle']))
    pdf.circle(width - 38, height - 30, 92, stroke=0, fill=1)
    pdf.setFillColor(colors.HexColor(PALETTE['olive']))
    pdf.circle(width - 15, 5, 115, stroke=0, fill=1)

    # Sarlavha.
    pdf.setFillColor(colors.HexColor(PALETTE['forest']))
    pdf.setFont('Helvetica-Bold', 17)
    pdf.drawCentredString(width / 2, height - 72, 'AL-AZIZ ACADEMY')
    pdf.setFillColor(colors.HexColor(PALETTE['teal']))
    pdf.setFont('Helvetica-Bold', 37)
    pdf.drawCentredString(width / 2, height - 125, 'SERTIFIKAT')
    pdf.setFillColor(colors.HexColor(PALETTE['muted']))
    pdf.setFont('Helvetica', 12)
    pdf.drawCentredString(width / 2, height - 151, "Ushbu sertifikat quyidagi o'quvchiga taqdim etiladi")

    # O'quvchi va kurs ma'lumotlari.
    full_name = _ascii_text(sertifikat.oquvchi.full_name)
    pdf.setFillColor(colors.HexColor(PALETTE['amethyst']))
    pdf.setFont('Helvetica-Bold', 29 if len(full_name) < 30 else 23)
    pdf.drawCentredString(width / 2, height - 205, full_name)

    pdf.setStrokeColor(colors.HexColor(PALETTE['teal']))
    pdf.setLineWidth(1.2)
    pdf.line(width * 0.23, height - 218, width * 0.77, height - 218)

    fan = _ascii_text(sertifikat.daraja.fan.nomi)
    daraja = _ascii_text(sertifikat.daraja.nomi)
    pdf.setFillColor(colors.HexColor(PALETTE['forest']))
    pdf.setFont('Helvetica-Bold', 17)
    pdf.drawCentredString(width / 2, height - 259, f"{fan} - {daraja} darajasi")
    pdf.setFillColor(colors.HexColor(PALETTE['muted']))
    pdf.setFont('Helvetica', 12)
    pdf.drawCentredString(width / 2, height - 285, "muvaffaqiyatli yakunlangani va yakuniy test topshirilgani uchun")

    # Natija bloki.
    box_w, box_h = 210, 72
    box_x, box_y = width / 2 - box_w / 2, height - 385
    pdf.setFillColor(colors.HexColor('#F2F8F6'))
    pdf.setStrokeColor(colors.HexColor(PALETTE['jungle']))
    pdf.roundRect(box_x, box_y, box_w, box_h, 14, stroke=1, fill=1)
    pdf.setFillColor(colors.HexColor(PALETTE['jungle']))
    pdf.setFont('Helvetica-Bold', 24)
    pdf.drawCentredString(width / 2, box_y + 37, f"Natija: {float(sertifikat.foiz):.0f}%")
    pdf.setFillColor(colors.HexColor(PALETTE['muted']))
    pdf.setFont('Helvetica', 9)
    pdf.drawCentredString(width / 2, box_y + 16, 'Minimal talab: 80%')

    # QR va tekshirish ma'lumotlari.
    qr_data = certificate_qr_bytes(sertifikat)
    qr_reader = ImageReader(BytesIO(qr_data))
    qr_size = 92
    qr_x, qr_y = width - 150, 56
    pdf.drawImage(qr_reader, qr_x, qr_y, qr_size, qr_size, preserveAspectRatio=True, mask='auto')
    pdf.setFillColor(colors.HexColor(PALETTE['forest']))
    pdf.setFont('Helvetica-Bold', 8)
    pdf.drawCentredString(qr_x + qr_size / 2, qr_y - 11, 'QR kodni skanerlang')

    date_text = sertifikat.berilgan_sana.astimezone().strftime('%d.%m.%Y')
    pdf.setFillColor(colors.HexColor(PALETTE['muted']))
    pdf.setFont('Helvetica', 10)
    pdf.drawString(68, 112, f"Berilgan sana: {date_text}")
    pdf.drawString(68, 91, f"Sertifikat kodi: {_ascii_text(sertifikat.kod)}")
    pdf.setFillColor(colors.HexColor(PALETTE['forest']))
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(68, 66, "Direktor: ____________________")

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
