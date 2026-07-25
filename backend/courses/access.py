"""Fan, daraja va mavzularni ochish/qulflash qoidalari."""
from courses.models import Daraja, Mavzu, OquvchiFan

MAVZU_OTISH_FOIZI = 80
DARAJA_OTISH_FOIZI = 80


def oquvchi_fan_biriktirishi(oquvchi, fan):
    """O'quvchining ushbu fan bo'yicha boshlang'ich biriktirishini qaytaradi."""
    return (
        OquvchiFan.objects.filter(oquvchi=oquvchi, daraja__fan=fan)
        .select_related('daraja__fan')
        .order_by('created_at', 'id')
        .first()
    )


def oquvchiga_fan_biriktirilganmi(oquvchi, fan) -> bool:
    return OquvchiFan.objects.filter(oquvchi=oquvchi, daraja__fan=fan).exists()


def daraja_ochiqmi(oquvchi, daraja: Daraja) -> bool:
    """
    Admin tanlagan boshlang'ich daraja ochiq bo'ladi.

    Keyingi darajalar joriy va oradagi barcha darajalarning yakuniy testidan
    kamida 80% olingandan keyin avtomatik ochiladi. Admin tanlagan darajadan
    oldingi darajalar esa yopiq qoladi.
    """
    assignment = oquvchi_fan_biriktirishi(oquvchi, daraja.fan)
    if not assignment:
        return False

    boshlangich = assignment.daraja
    if daraja.tartib < boshlangich.tartib:
        return False
    if daraja.id == boshlangich.id:
        return bool(assignment.qolda_ochilgan)

    from exams.models import FinalTestNatija

    oldingi_darajalar = Daraja.objects.filter(
        fan=daraja.fan,
        tartib__gte=boshlangich.tartib,
        tartib__lt=daraja.tartib,
    ).order_by('tartib', 'id')

    for oldingi in oldingi_darajalar:
        otilgan = FinalTestNatija.objects.filter(
            oquvchi=oquvchi,
            final_test__daraja=oldingi,
            otdi=True,
            foiz__gte=DARAJA_OTISH_FOIZI,
        ).exists()
        if not otilgan:
            return False
    return True


def daraja_qulf_sababi(oquvchi, daraja: Daraja) -> str:
    assignment = oquvchi_fan_biriktirishi(oquvchi, daraja.fan)
    if not assignment:
        return "Bu fan sizga biriktirilmagan. Admin bilan bog'laning."
    if daraja.tartib < assignment.daraja.tartib:
        return "Bu daraja admin tomonidan ochilmagan. Admin bilan bog'laning."
    if daraja.id == assignment.daraja_id and not assignment.qolda_ochilgan:
        return "Bu daraja admin tomonidan yopilgan. Admin bilan bog'laning."
    oldingi = Daraja.objects.filter(
        fan=daraja.fan,
        tartib__lt=daraja.tartib,
        tartib__gte=assignment.daraja.tartib,
    ).order_by('-tartib', '-id').first()
    if oldingi:
        return f"Avval {oldingi.nomi} yakuniy testidan kamida 80% oling."
    return "Daraja hali ochilmagan. Admin bilan bog'laning."


def mavzu_testdan_otilganmi(oquvchi, mavzu: Mavzu) -> bool:
    """Mavzudagi barcha testli darslar kamida 80% bilan bajarilgan bo'lsa True."""
    from exams.models import MashqNatija

    darslar = list(mavzu.darslar.all())
    mashqlar = [dars.mashq for dars in darslar if hasattr(dars, 'mashq')]
    if not mashqlar:
        return False

    for mashq in mashqlar:
        passed = MashqNatija.objects.filter(
            oquvchi=oquvchi,
            mashq=mashq,
            foiz__gte=int(mashq.otish_bali_foiz or MAVZU_OTISH_FOIZI),
        ).exists()
        if not passed:
            return False
    return True


def daraja_mavzulari_tugaganmi(oquvchi, daraja: Daraja) -> bool:
    """Darajadagi barcha mavzular 80%+ bilan tugatilganligini tekshiradi."""
    mavzular = list(Mavzu.objects.filter(daraja=daraja).prefetch_related('darslar__mashq'))
    return bool(mavzular) and all(mavzu_testdan_otilganmi(oquvchi, mavzu) for mavzu in mavzular)


def mavzu_ochiqmi(oquvchi, mavzu: Mavzu) -> bool:
    """Birinchi mavzu ochiq; keyingilari oldingi mavzular 80% bilan o'tilganda ochiladi."""
    if not daraja_ochiqmi(oquvchi, mavzu.daraja):
        return False

    tartiblangan = list(Mavzu.objects.filter(daraja=mavzu.daraja).order_by('tartib', 'id'))
    try:
        index = next(i for i, item in enumerate(tartiblangan) if item.id == mavzu.id)
    except StopIteration:
        return False

    if index == 0:
        return True

    return all(mavzu_testdan_otilganmi(oquvchi, oldingi) for oldingi in tartiblangan[:index])


def keyingi_mavzu(mavzu: Mavzu):
    tartiblangan = list(Mavzu.objects.filter(daraja=mavzu.daraja).order_by('tartib', 'id'))
    for index, item in enumerate(tartiblangan):
        if item.id == mavzu.id and index + 1 < len(tartiblangan):
            return tartiblangan[index + 1]
    return None


def keyingi_daraja(daraja: Daraja):
    return Daraja.objects.filter(
        fan=daraja.fan,
        tartib__gt=daraja.tartib,
    ).order_by('tartib', 'id').first()


def mavzu_holati(oquvchi, mavzu: Mavzu) -> dict:
    from exams.models import MashqNatija

    ochiq = mavzu_ochiqmi(oquvchi, mavzu)
    mashqlar = [dars.mashq for dars in mavzu.darslar.all() if hasattr(dars, 'mashq')]

    eng_yaxshi_foiz = 0.0
    if mashqlar:
        best = MashqNatija.objects.filter(
            oquvchi=oquvchi,
            mashq__in=mashqlar,
        ).order_by('-foiz').values_list('foiz', flat=True).first()
        eng_yaxshi_foiz = float(best or 0)

    return {
        'ochiq': ochiq,
        'otilgan': mavzu_testdan_otilganmi(oquvchi, mavzu),
        'eng_yaxshi_foiz': eng_yaxshi_foiz,
        'otish_foizi': max([int(m.otish_bali_foiz or MAVZU_OTISH_FOIZI) for m in mashqlar], default=MAVZU_OTISH_FOIZI),
        'qulf_sababi': '' if ochiq else "Avval oldingi mavzu testidan kamida 80% oling.",
    }


def oquvchi_fanlari_access_bilan(oquvchi):
    biriktirilganlar = OquvchiFan.objects.filter(oquvchi=oquvchi).select_related('daraja__fan')
    return [
        {'oquvchi_fan': of, 'ochiq': daraja_ochiqmi(oquvchi, of.daraja)}
        for of in biriktirilganlar
    ]
