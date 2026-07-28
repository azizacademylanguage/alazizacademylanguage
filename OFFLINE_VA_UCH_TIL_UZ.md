# Offline rejim va uch tilli interfeys

## Interfeys tillari

Platformaning asosiy interfeysi quyidagi tillarda ishlaydi:

- O‘zbekcha
- Русский
- English

Til tanlash tugmasi login sahifasi, desktop sidebar, mobil topbar va asosiy panellarda mavjud. Tanlangan til brauzerda saqlanadi va qayta kirganda ham o‘zgarmaydi.

## Offline rejim

O‘quvchi menyusida **Offline** bo‘limi mavjud. Internet bor paytda **Darslarni yuklash** tugmasi bosilganda:

- biriktirilgan fandagi ochiq darajalar;
- mavzular va dars matnlari;
- test, listening, writing va speaking topshiriqlari;
- mavjud audio, video va rasmlar

qurilmaga saqlanadi.

Internet uzilganda oldindan yuklangan darslar ochiladi. Offline bajarilgan qo‘llab-quvvatlanadigan test va progress natijalari navbatga qo‘yiladi. Internet qaytganda ular avtomatik yuboriladi. **Sinxronlash** tugmasi orqali qo‘lda ham yuborish mumkin.

> Mikrofon audio fayli kabi katta FormData yuborish talab qiladigan speaking topshiriqlari internet bilan topshiriladi. Matn asosidagi speaking natijasi offline navbatga qo‘yilishi mumkin.

## Ma’lumot xavfsizligi

- API javoblari umumiy Service Worker cache’iga saqlanmaydi.
- O‘quvchi ma’lumotlari IndexedDB’da foydalanuvchi bo‘yicha alohida saqlanadi.
- Chiqib, boshqa login bilan kirilganda boshqa foydalanuvchining offline darslari ko‘rsatilmaydi.
- Offline bo‘limidagi **Tozalash** tugmasi joriy foydalanuvchining saqlangan ma’lumotlarini o‘chiradi.

## Netlify deploy

Service Worker yangilangani uchun GitHub pushdan keyin Netlify’da:

1. **Deploys** bo‘limiga kiring.
2. **Trigger deploy** ni bosing.
3. **Clear cache and deploy site** ni tanlang.

Brauzer eski versiyani ko‘rsatsa, `Ctrl + Shift + R` bosing. iPhone’da Safari’ni yopib qayta oching yoki bosh ekrandagi eski PWA’ni o‘chirib qayta o‘rnating.
