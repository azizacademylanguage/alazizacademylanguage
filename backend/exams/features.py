from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from .models import (
    Bildirishnoma, BildirishnomaOqildi, FaoliyatLog, OquvchiKunlikFaollik,
    TestXavfsizlikLog, Yutuq, OquvchiYutuq, Tolov, PlatformSozlama,
    MashqNatija, Sertifikat,
)
from .coins import coin_qoshish


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')


def log_faoliyat(request, amal, tavsif='', obyekt_turi='', obyekt_id=None, meta=None):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return None
    row = FaoliyatLog.objects.create(
        user=request.user,
        amal=amal,
        tavsif=tavsif[:300],
        obyekt_turi=obyekt_turi[:60],
        obyekt_id=obyekt_id,
        meta=meta or {},
        ip_manzil=client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )
    if request.user.role == 'oquvchi':
        OquvchiKunlikFaollik.objects.get_or_create(oquvchi=request.user, sana=timezone.localdate())
    return row


def faoliyat_streak(user):
    dates = list(OquvchiKunlikFaollik.objects.filter(oquvchi=user).values_list('sana', flat=True)[:366])
    if not dates:
        return 0
    dates = set(dates)
    day = timezone.localdate()
    if day not in dates and day - timedelta(days=1) in dates:
        day -= timedelta(days=1)
    count = 0
    while day in dates:
        count += 1
        day -= timedelta(days=1)
    return count


def record_test_security(request, test_turi, obyekt_id, xavfsizlik=None):
    xavfsizlik = xavfsizlik if isinstance(xavfsizlik, dict) else {}
    duration = max(0, int(xavfsizlik.get('davomiylik_soniya') or 0))
    focus = max(0, int(xavfsizlik.get('sahifadan_chiqish_soni') or 0))
    reasons = []
    if duration and duration < 15:
        reasons.append('Test juda tez yakunlangan')
    if focus >= 3:
        reasons.append('Test vaqtida sahifadan ko‘p chiqilgan')
    if xavfsizlik.get('vaqt_tugadi'):
        reasons.append('Vaqt chegarasi tugagan')
    row = TestXavfsizlikLog.objects.create(
        oquvchi=request.user,
        test_turi=test_turi,
        obyekt_id=obyekt_id,
        davomiylik_soniya=duration,
        sahifadan_chiqish_soni=focus,
        shubhali=bool(reasons),
        sabablar=reasons,
        ip_manzil=client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )
    return row


def create_notification(title, body, user=None, tur='info', link='', created_by=None):
    if not PlatformSozlama.load().bildirishnomalar_faol:
        return None
    return Bildirishnoma.objects.create(
        sarlavha=title,
        matn=body,
        tur=tur,
        target_turi=Bildirishnoma.TARGET_USER if user else Bildirishnoma.TARGET_ALL,
        target_user=user,
        havola=link,
        created_by=created_by,
    )


def notifications_for_user(user):
    now = timezone.now()
    daraja_ids = list(user.biriktirilgan_fanlar.values_list('daraja_id', flat=True))
    fan_ids = list(user.biriktirilgan_fanlar.values_list('daraja__fan_id', flat=True))
    return Bildirishnoma.objects.filter(
        faol=True,
    ).filter(
        Q(tugash_sana__isnull=True) | Q(tugash_sana__gte=now)
    ).filter(
        Q(target_turi=Bildirishnoma.TARGET_ALL)
        | Q(target_turi=Bildirishnoma.TARGET_USER, target_user=user)
        | Q(target_turi=Bildirishnoma.TARGET_FAN, target_fan_id__in=fan_ids)
        | Q(target_turi=Bildirishnoma.TARGET_DARAJA, target_daraja_id__in=daraja_ids)
    ).distinct()


def default_achievements():
    return [
        ('birinchi_test', 'Birinchi qadam', 'Birinchi testni yakunlang.', '🚀', 5, 1),
        ('mukammal_test', 'Mukammal natija', 'Testdan 100% natija oling.', '💯', 10, 2),
        ('10_test', 'Tinimsiz o‘quvchi', '10 ta test urinishini yakunlang.', '📚', 15, 3),
        ('birinchi_sertifikat', 'Birinchi sertifikat', 'Birinchi sertifikatingizni oling.', '🎓', 20, 4),
        ('7_kun', '7 kunlik seriya', '7 kun ketma-ket platformada faol bo‘ling.', '🔥', 15, 5),
        ('oyin_10', 'Tezkor tarjimon', 'Tezkor tarjima o‘yinida 10/10 natija oling.', '⚡', 10, 6),
    ]


def ensure_default_achievements():
    for code, name, desc, icon, reward, order in default_achievements():
        Yutuq.objects.get_or_create(
            kod=code,
            defaults={'nomi': name, 'tavsif': desc, 'icon': icon, 'coin_mukofot': reward, 'tartib': order},
        )


def award_achievement(user, code, meta=None):
    ensure_default_achievements()
    try:
        achievement = Yutuq.objects.get(kod=code, faol=True)
    except Yutuq.DoesNotExist:
        return None
    obj, created = OquvchiYutuq.objects.get_or_create(oquvchi=user, yutuq=achievement, defaults={'meta': meta or {}})
    if created:
        if achievement.coin_mukofot:
            coin_qoshish(user, achievement.coin_mukofot, 'yutuq', achievement.nomi)
        create_notification(
            f'Yangi yutuq: {achievement.nomi}',
            f'{achievement.tavsif} Mukofot: {achievement.coin_mukofot} coin.',
            user=user,
            tur='success',
            link='/oquvchi/yutuqlarim',
        )
    return obj if created else None


def check_achievements(user, foiz=None, game_score=None):
    if MashqNatija.objects.filter(oquvchi=user).exists():
        award_achievement(user, 'birinchi_test')
    if foiz is not None and float(foiz) >= 100:
        award_achievement(user, 'mukammal_test', {'foiz': float(foiz)})
    if MashqNatija.objects.filter(oquvchi=user).count() >= 10:
        award_achievement(user, '10_test')
    if Sertifikat.objects.filter(oquvchi=user, faol=True).exists():
        award_achievement(user, 'birinchi_sertifikat')
    if faoliyat_streak(user) >= 7:
        award_achievement(user, '7_kun')
    if game_score is not None and int(game_score) >= 10:
        award_achievement(user, 'oyin_10')


def payment_state(user):
    settings = PlatformSozlama.load()
    today = timezone.localdate()
    latest = Tolov.objects.filter(oquvchi=user).exclude(status='bekor').order_by('-tugash_sana').first()
    if not latest:
        return {
            'nazorat_faol': settings.tolov_nazorati_faol,
            'ruxsat': not settings.tolov_nazorati_faol,
            'holat': 'kiritilmagan',
            'xabar': 'To‘lov muddati kiritilmagan.',
            'tolov': None,
            'qolgan_kun': None,
        }
    valid_status = latest.status in {'tolangan', 'imtiyozli', 'qisman'}
    active = latest.boshlanish_sana <= today <= latest.tugash_sana and valid_status
    days = (latest.tugash_sana - today).days
    return {
        'nazorat_faol': settings.tolov_nazorati_faol,
        'ruxsat': active or not settings.tolov_nazorati_faol,
        'holat': 'faol' if active else ('muddati_tugagan' if days < 0 else latest.status),
        'xabar': 'Foydalanish muddati faol.' if active else 'Foydalanish muddati faol emas.',
        'qolgan_kun': days,
        'tolov': {
            'id': latest.id,
            'summa': float(latest.summa),
            'tolangan_summa': float(latest.tolangan_summa),
            'qolgan_summa': float(latest.qolgan_summa),
            'boshlanish_sana': latest.boshlanish_sana,
            'tugash_sana': latest.tugash_sana,
            'status': latest.status,
            'status_display': latest.get_status_display(),
            'izoh': latest.izoh,
        },
    }


def require_payment_or_none(user):
    state = payment_state(user)
    return None if state['ruxsat'] else state
