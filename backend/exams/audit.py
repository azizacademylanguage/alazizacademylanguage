from .models import AdminAmalLog


def log_amal(foydalanuvchi, amal, tavsif='', nishon_user=None):
    """Admin/Nazoratchi amalini audit logga yozadi. Xato bo'lsa jim o'tkazib yuboradi
    (log yozish asosiy amalni to'xtatmasligi kerak)."""
    try:
        AdminAmalLog.objects.create(
            foydalanuvchi=foydalanuvchi, amal=amal, tavsif=tavsif, nishon_user=nishon_user
        )
    except Exception:
        pass
