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
