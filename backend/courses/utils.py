import re


def toza_daraja_nomi(value: str) -> str:
    """Daraja nomidan raqam va foiz oralig'i kabi eski qo'shimchalarni olib tashlaydi."""
    value = (value or '').strip()
    value = re.sub(r'^\s*\d+[.)-]?\s*', '', value)
    value = re.sub(r'\s*[—–-]\s*\d+\s*%?\s*[—–-]\s*\d+\s*%?\s*$', '', value)
    value = re.sub(r'\s+\d+\s*%\s*$', '', value)
    return value.strip(' —–-')
