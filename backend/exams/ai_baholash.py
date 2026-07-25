"""
Writing (yozma) javoblarni AI (Claude) orqali avtomatik baholash.

Ishlatish uchun ANTHROPIC_API_KEY muhit o'zgaruvchisi o'rnatilgan bo'lishi kerak.
API kaliti bo'lmasa, funksiya oddiy (so'z sonini hisoblovchi) fallback bilan ishlaydi,
shunda tizim umuman ishlamay qolmaydi.
"""
import os
import json
import re


def _fallback_baholash(topshiriq_matni, javob_matni, minimal_soz_soni):
    """AI mavjud bo'lmasa ishlatiladigan oddiy baholash — faqat so'z sonini tekshiradi."""
    soz_soni = len(javob_matni.split())
    foiz = 100 if soz_soni >= minimal_soz_soni else round((soz_soni / max(minimal_soz_soni, 1)) * 70, 2)
    izoh = (
        f"(Avtomatik tekshiruv: {soz_soni} so'z yozilgan, kamida {minimal_soz_soni} so'z kerak.) "
        "AI baholash xizmati sozlanmagan — o'qituvchi tomonidan qo'lda ko'rib chiqilishi tavsiya etiladi."
    )
    return {'foiz': foiz, 'izoh': izoh, 'xatolar': []}


def writing_baholash(topshiriq_matni, javob_matni, minimal_soz_soni=30):
    """
    Claude API orqali yozma javobni baholaydi.
    Qaytaradi: {'foiz': float, 'izoh': str, 'xatolar': list[str]}
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return _fallback_baholash(topshiriq_matni, javob_matni, minimal_soz_soni)

    try:
        import anthropic
    except ImportError:
        return _fallback_baholash(topshiriq_matni, javob_matni, minimal_soz_soni)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Sen ingliz tili o'qituvchisisan. O'quvchining yozma ishini baholashing kerak.

Topshiriq: {topshiriq_matni}
Minimal so'z soni: {minimal_soz_soni}

O'quvchi javobi:
\"\"\"{javob_matni}\"\"\"

Quyidagi JSON formatda javob ber (boshqa hech narsa yozma, faqat JSON):
{{
  "foiz": <0 dan 100 gacha butun son, umumiy baho>,
  "izoh": "<o'zbek tilida qisqa, ijobiy va rag'batlantiruvchi fikr-mulohaza, 2-3 gap>",
  "xatolar": ["<grammatik xato 1>", "<grammatik xato 2>", ...]
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, 'text'))
        # Modelning JSON atrofidagi ortiqcha matnini tozalash
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            raise ValueError("AI javobida JSON topilmadi")
        data = json.loads(match.group(0))
        return {
            'foiz': float(data.get('foiz', 0)),
            'izoh': data.get('izoh', ''),
            'xatolar': data.get('xatolar', []),
        }
    except Exception:
        return _fallback_baholash(topshiriq_matni, javob_matni, minimal_soz_soni)


def _ai_yordamchi_fallback(savol, kontekst):
    """API kaliti bo'lmaganda ham real o'quvchi natijalariga tayangan javob."""
    text = (savol or '').lower()
    ism = kontekst.get('ism', "O'quvchi")
    fan = kontekst.get('fan', 'tanlangan fan')
    daraja = kontekst.get('daraja', '')
    ortacha = kontekst.get('ortacha_foiz', 0)
    zaif = kontekst.get('zaif_mavzular', [])
    oxirgi = kontekst.get('oxirgi_natijalar', [])

    if any(k in text for k in ['natija', 'foiz', 'qanday o‘qiyap', 'qanday oqiyap', 'progress']):
        zaif_matn = ', '.join(x.get('mavzu', '') for x in zaif[:3]) or "hozircha aniqlanmadi"
        return (
            f"{ism}, sizning {fan} {daraja} bo‘yicha o‘rtacha natijangiz {ortacha:.1f}%. "
            f"Ko‘proq takrorlash kerak bo‘lgan mavzular: {zaif_matn}. "
            "Avval eng past natijali mavzuni qayta o‘qing, keyin testdagi xatolarni tahlil qilib yana urinib ko‘ring."
        )
    if any(k in text for k in ['reja', 'qanday o‘rgan', 'qanday organ', 'maslahat']):
        mavzu = zaif[0].get('mavzu') if zaif else (oxirgi[0].get('mavzu') if oxirgi else fan)
        return (
            f"Bugungi qisqa reja: 1) {mavzu} mavzusini 15 daqiqa qayta o‘qing; "
            "2) 10 ta muhim so‘zni ovoz chiqarib takrorlang; 3) bitta kichik test ishlang; "
            "4) xato javoblar bo‘yicha 3 ta misol gap tuzing. Shu tartibda ishlasangiz natija tezroq oshadi."
        )
    if any(k in text for k in ['xato', 'noto‘g‘ri', 'notogri']):
        zaif_matn = ', '.join(f"{x.get('mavzu')} ({x.get('foiz', 0):.0f}%)" for x in zaif[:3])
        return (
            f"Sizda ko‘proq xato kuzatilgan joylar: {zaif_matn or 'hali yetarli natija mavjud emas'}. "
            "Har bir xato uchun to‘g‘ri javob sababini yozib chiqing va o‘sha qoida bilan yangi misol tuzing."
        )
    if any(k in text for k in ['salom', 'assalom']):
        return f"Salom, {ism}! Men sizning {fan} bo‘yicha AI yordamchingizman. Mavzuni tushuntirish, natijani tahlil qilish yoki o‘quv reja tuzishda yordam beraman."

    return (
        f"Savolingizni tushundim. Siz hozir {fan} {daraja} darajasida o‘qiyapsiz va o‘rtacha natijangiz {ortacha:.1f}%. "
        "Savolni aniq mavzu yoki misol bilan yozsangiz, men uni bosqichma-bosqich tushuntiraman. "
        "Masalan: “Present Perfect qachon ishlatiladi?” yoki “Natijamni qanday oshiraman?”"
    )


def ai_yordamchi_javob(savol, kontekst, tarix=None):
    """O'quvchining shaxsiy konteksti bilan AI yordamchi javobini yaratadi."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return _ai_yordamchi_fallback(savol, kontekst), 'ichki-yordamchi'
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        history_text = ''
        for item in (tarix or [])[-8:]:
            history_text += f"\n{item.get('role')}: {item.get('matn')}"
        prompt = f"""Sen Al-Aziz Academy platformasidagi mehribon va aniq AI o'qituvchisan.
O'quvchiga faqat o'zbek tilida, sodda va amaliy javob ber. Javob 5-10 gapdan oshmasin.
O'quvchi konteksti:
{json.dumps(kontekst, ensure_ascii=False, default=str)}

Oldingi qisqa suhbat:{history_text or ' yo‘q'}

O'quvchi savoli: {savol}

Natijalardan kelib chiqib shaxsiy tavsiya ber. Javobni markdownsiz oddiy matnda yoz."""
        response = client.messages.create(
            model=os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-4-6'),
            max_tokens=700,
            messages=[{'role': 'user', 'content': prompt}],
        )
        text = ''.join(block.text for block in response.content if hasattr(block, 'text')).strip()
        if not text:
            raise ValueError('AI bo‘sh javob qaytardi')
        return text, 'anthropic'
    except Exception:
        return _ai_yordamchi_fallback(savol, kontekst), 'ichki-yordamchi'
