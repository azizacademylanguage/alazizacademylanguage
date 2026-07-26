from .models import AdminAmalLog


def _client_ip(request):
    if not request:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return (forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')) or None


def log_amal(foydalanuvchi, amal, tavsif='', nishon_user=None, *, obyekt_turi='', obyekt_id='', oldingi_holat=None, yangi_holat=None, request=None):
    """Muhim boshqaruv amallarini yozadi; audit xatosi asosiy amalni to'xtatmaydi."""
    try:
        AdminAmalLog.objects.create(
            foydalanuvchi=foydalanuvchi,
            amal=amal,
            tavsif=tavsif,
            nishon_user=nishon_user,
            obyekt_turi=obyekt_turi,
            obyekt_id=str(obyekt_id or ''),
            ip_manzil=_client_ip(request),
            oldingi_holat=oldingi_holat or {},
            yangi_holat=yangi_holat or {},
        )
    except Exception:
        pass
