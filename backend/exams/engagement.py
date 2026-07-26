from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import User
from .models import Bildirishnoma, CoinTarix, KunlikFaollik


def bildirishnoma_yarat(oquvchi, sarlavha, matn='', tur='info', havola=''):
    if not oquvchi or oquvchi.role != User.ROLE_OQUVCHI:
        return None
    return Bildirishnoma.objects.create(
        oquvchi=oquvchi,
        sarlavha=sarlavha,
        matn=matn,
        tur=tur,
        havola=havola,
    )


def streak_hisobla(oquvchi):
    dates = list(
        KunlikFaollik.objects.filter(oquvchi=oquvchi)
        .order_by('-sana')
        .values_list('sana', flat=True)
    )
    if not dates:
        return {'joriy': 0, 'eng_yaxshi': 0, 'bugun_faol': False}

    date_set = set(dates)
    today = timezone.localdate()
    cursor = today if today in date_set else today - timedelta(days=1)
    current = 0
    while cursor in date_set:
        current += 1
        cursor -= timedelta(days=1)

    best = 0
    run = 0
    previous = None
    for day in sorted(date_set):
        if previous and day == previous + timedelta(days=1):
            run += 1
        else:
            run = 1
        best = max(best, run)
        previous = day

    return {'joriy': current, 'eng_yaxshi': best, 'bugun_faol': today in date_set}


@transaction.atomic
def faollik_qayd_et(oquvchi, tur='kirish'):
    if not oquvchi or oquvchi.role != User.ROLE_OQUVCHI:
        return {'joriy': 0, 'eng_yaxshi': 0, 'bugun_faol': False, 'bonus': 0}

    today = timezone.localdate()
    row, _ = KunlikFaollik.objects.select_for_update().get_or_create(
        oquvchi=oquvchi,
        sana=today,
        defaults={'faollik_soni': 0, 'turlar': []},
    )
    types = list(row.turlar or [])
    if tur not in types:
        types.append(tur)
        row.faollik_soni += 1
    row.turlar = types
    row.save(update_fields=['faollik_soni', 'turlar', 'updated_at'])

    stats = streak_hisobla(oquvchi)
    bonus = 0
    current = stats['joriy']
    if current >= 7 and current % 7 == 0:
        bonus_key = f"{current} kunlik streak bonusi - {today.isoformat()}"
        already = CoinTarix.objects.filter(oquvchi=oquvchi, sabab='streak', izoh=bonus_key).exists()
        if not already:
            from .coins import coin_qoshish
            coin_qoshish(oquvchi, 10, 'streak', bonus_key)
            bonus = 10
            bildirishnoma_yarat(
                oquvchi,
                f'🔥 {current} kunlik faollik!',
                'Ketma-ket o‘qiganingiz uchun 10 coin bonus berildi.',
                tur='success',
                havola='/oquvchi',
            )
    stats['bonus'] = bonus
    return stats
