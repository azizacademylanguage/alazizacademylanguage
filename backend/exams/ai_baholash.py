"""Writing javoblarini AI yoki mahalliy qoidalar bilan avtomatik baholash."""
import json
import os
import re
from collections import Counter


def _sentences(text):
    return [s.strip() for s in re.split(r'[.!?]+', text or '') if s.strip()]


def _language_hint(task_text):
    text = (task_text or '').casefold()
    if any(ch in text for ch in 'ёъыэ') or 'рус' in text:
        return 'ru'
    if re.search(r'[가-힣]', text) or 'kore' in text:
        return 'ko'
    return 'en'


def _local_baholash(topshiriq_matni, javob_matni, minimal_soz_soni):
    words = re.findall(r"[\w'’-]+", javob_matni, flags=re.UNICODE)
    lower = [w.casefold() for w in words]
    word_count = len(words)
    sentences = _sentences(javob_matni)
    unique_ratio = len(set(lower)) / max(word_count, 1)
    errors = []
    suggestions = []

    if word_count < minimal_soz_soni:
        errors.append(f"So'zlar soni kam: {word_count}/{minimal_soz_soni}.")
        suggestions.append(f"Yana kamida {minimal_soz_soni - word_count} ta so'z qo'shing.")
    if javob_matni and javob_matni[0].isalpha() and not javob_matni[0].isupper():
        errors.append("Matn bosh harf bilan boshlanmagan.")
        suggestions.append("Birinchi gapni bosh harf bilan boshlang.")
    if javob_matni.strip() and javob_matni.strip()[-1] not in '.!?':
        errors.append("Matn oxirida tinish belgisi yo'q.")
        suggestions.append("Matn oxiriga nuqta, savol yoki undov belgisi qo'ying.")

    repeated = [w for w, count in Counter(lower).items() if len(w) > 3 and count >= 4]
    if repeated:
        errors.append("Ayrim so'zlar juda ko'p takrorlangan: " + ', '.join(repeated[:4]))
        suggestions.append("Takrorlangan so'zlar o'rniga sinonimlardan foydalaning.")

    bad_spacing = re.findall(r'\s+[,.!?;:]', javob_matni)
    if bad_spacing:
        errors.append("Tinish belgisidan oldin ortiqcha bo'sh joy bor.")
    if re.search(r'([!?.,])\1{1,}', javob_matni):
        errors.append("Tinish belgisi keragidan ortiq takrorlangan.")

    language = _language_hint(topshiriq_matni)
    language_rules = {
        'en': [
            (r'\bi am agree\b', "'I am agree' o'rniga 'I agree' yozing."),
            (r'\bhe go\b', "'He go' o'rniga 'He goes' yozing."),
            (r'\bshe go\b', "'She go' o'rniga 'She goes' yozing."),
            (r'\bdid\s+\w+ed\b', "'did' dan keyin fe'lning asosiy shaklini ishlating."),
        ],
        'ru': [
            (r'\bя есть\b', "Rus tilida oddiy hozirgi gaplarda 'есть' ko'pincha ishlatilmaydi."),
        ],
        'ko': [],
    }
    for pattern, message in language_rules.get(language, []):
        if re.search(pattern, javob_matni.casefold()):
            errors.append(message)

    length_score = min(100, round(word_count / max(minimal_soz_soni, 1) * 100))
    structure_score = min(100, 45 + min(len(sentences), 5) * 10 + (10 if javob_matni.strip()[-1:] in '.!?' else 0))
    vocabulary_score = min(100, round(unique_ratio * 125))
    grammar_score = max(20, 100 - len(errors) * 12)
    score = round(length_score * .30 + grammar_score * .35 + vocabulary_score * .20 + structure_score * .15, 2)

    if score >= 85:
        summary = "Juda yaxshi yozilgan. Fikrlar aniq va lug'at boyligi yaxshi."
    elif score >= 70:
        summary = "Yaxshi natija. Ko'rsatilgan kichik xatolarni tuzatsangiz matn yanada ravon bo'ladi."
    elif score >= 60:
        summary = "Qoniqarli natija. Gap tuzilishi va grammatika ustida yana ishlang."
    else:
        summary = "Matnni qayta ko'rib chiqing: hajm, grammatika va gap tuzilishini yaxshilang."

    details = {
        'til': language,
        'soz_soni': word_count,
        'gap_soni': len(sentences),
        'grammatika': grammar_score,
        'lugat_boyligi': vocabulary_score,
        'tuzilish': structure_score,
        'hajm': length_score,
        'tavsiyalar': suggestions,
    }
    return {'foiz': score, 'izoh': summary, 'xatolar': errors, 'tafsilot': details}


def writing_baholash(topshiriq_matni, javob_matni, minimal_soz_soni=30):
    """Claude mavjud bo'lsa AI, bo'lmasa kuchli mahalliy tekshiruv ishlaydi."""
    local = _local_baholash(topshiriq_matni, javob_matni, minimal_soz_soni)
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return local
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Til o'qituvchisi sifatida yozma ishni bahola.
Topshiriq: {topshiriq_matni}
Minimal so'z: {minimal_soz_soni}
Javob: {javob_matni}
Faqat JSON qaytar: {{"foiz":0-100,"izoh":"o'zbekcha 2 gap","xatolar":["..."],"tafsilot":{{"grammatika":0-100,"lugat_boyligi":0-100,"tuzilish":0-100,"hajm":0-100,"tavsiyalar":["..."]}}}}"""
        response = client.messages.create(model=os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6'), max_tokens=700, messages=[{'role': 'user', 'content': prompt}])
        text = ''.join(block.text for block in response.content if hasattr(block, 'text'))
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            return local
        data = json.loads(match.group(0))
        return {
            'foiz': max(0, min(100, float(data.get('foiz', local['foiz'])))),
            'izoh': data.get('izoh') or local['izoh'],
            'xatolar': data.get('xatolar') or local['xatolar'],
            'tafsilot': data.get('tafsilot') or local['tafsilot'],
        }
    except Exception:
        return local
