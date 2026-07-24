from django.db import transaction

from .models import OquvchiCoin, CoinTarix


@transaction.atomic
def coin_qoshish(oquvchi, miqdor, sabab, izoh=''):
    """Balansni atomik yangilaydi va har bir o'zgarishni tarixga yozadi."""
    balans_obj, _ = OquvchiCoin.objects.get_or_create(oquvchi=oquvchi)
    balans_obj = OquvchiCoin.objects.select_for_update().get(pk=balans_obj.pk)
    yangi_balans = balans_obj.balans + int(miqdor)
    if yangi_balans < 0:
        yangi_balans = 0
    haqiqiy_miqdor = yangi_balans - balans_obj.balans
    balans_obj.balans = yangi_balans
    balans_obj.save(update_fields=['balans', 'updated_at'])
    CoinTarix.objects.create(
        oquvchi=oquvchi,
        miqdor=haqiqiy_miqdor,
        sabab=sabab,
        izoh=izoh,
    )
    return balans_obj
