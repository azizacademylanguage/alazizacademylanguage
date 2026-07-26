# Qo‘shilgan modullar

## 4. Kuchli admin statistikasi

Admin menyusidagi **Kuchli statistika** bo‘limida:

- bugun va oxirgi 7 kunda faol o‘quvchilar;
- 7 kun faol bo‘lmaganlar;
- muddati tugagan va 5 kun ichida tugaydiganlar;
- qarzdorlar;
- test, listening, speaking va writing o‘rtacha natijalari;
- filiallar taqqoslanishi;
- oylik yangi o‘quvchilar;
- top reyting va e’tibor talab qiladiganlar ko‘rsatiladi.

## 5. To‘lov va foydalanish muddati

O‘quvchi yaratishda tarif, boshlanish/tugash sanasi, to‘lov holati va muddat tugaganda bloklash tanlanadi. Admin kartadagi kalendar tugmasi orqali muddatni 30 kunga uzaytiradi. Muddat tugasa ta’lim API’lari qulflanadi va o‘quvchiga admin bilan bog‘lanish xabari chiqadi.

## 7. Writing avtomatik tekshirish

ANTHROPIC_API_KEY bo‘lmasa ham mahalliy tekshiruvchi ishlaydi. U so‘z soni, grammatika, lug‘at boyligi, tuzilish, tinish belgilari, takroriy so‘zlar va tavsiyalarni chiqaradi. API kaliti berilsa AI baholash ishlaydi.

## 9. Reyting va musobaqa

Ball test, final test, listening, writing, kunlik faollik va sertifikatlar asosida hisoblanadi. Admin fan yoki filial bo‘yicha musobaqa yaratadi. Musobaqani yakunlashda 1–3 o‘rinlarga avtomatik coin beriladi.

## 11. Excel kontent boshqaruvi

**Hisobotlar** sahifasidan XLSX eksport va import ishlaydi. Varaqlar:

- Mavzular
- TestSavollar
- Listening
- Writing
- Speaking

Import xatolari qator raqami bilan qaytariladi.

## 12. Audit va backup

Audit logda amal, obyekt turi/ID, IP, eski va yangi holat saqlanadi. **Hisobotlar** sahifasidan ZIP backup yuklanadi va shu formatdagi backup bazaga xavfsiz birlashtirib tiklanadi. Railway Volume ulangan bo‘lsa avtomatik backup uchun Cron service buyrug‘i:

```bash
python manage.py create_backup --keep 7
```

Backup fayllari `MEDIA_ROOT/backups` ichida saqlanadi.
