# Yangi o‘quvchi funksiyalari

Ushbu versiyaga Listening, Speaking, shaxsiy o‘qish rejasi, kunlik streak, bildirishnomalar va PWA o‘rnatish imkoniyati qo‘shilgan.

## 1. Listening

- Har bir darsda 10 ta listening savoli bor.
- Brauzer chet tilidagi so‘z yoki gapni ovoz chiqarib o‘qiydi.
- O‘quvchi o‘zbekcha tarjimani variantlardan tanlaydi.
- Javoblar backend tomonidan tekshiriladi.
- Natija va eng yaxshi foiz saqlanadi.
- Kamida 80% olish talab qilinadi.

## 2. Speaking va talaffuz

- O‘quvchi namunani tinglaydi va mikrofon orqali takrorlaydi.
- Brauzer nutqni matnga aylantiradi.
- Backend tanilgan matnni namuna bilan solishtirib foiz beradi.
- English, Rus tili va Koreys tili uchun mos nutq tili avtomatik tanlanadi.
- Mikrofon funksiyasi HTTPS domenida Chrome yoki Edge brauzerida eng yaxshi ishlaydi.

## 3. Shaxsiy o‘qish rejasi

O‘quvchi bosh sahifasida quyidagilar ko‘rinadi:

- bugungi tavsiya qilingan dars yoki yakuniy test;
- hozirgi daraja va tugallangan mavzular;
- qaytarish uchun 5 ta so‘z;
- haftalik maqsad;
- shaxsiy tavsiyalar;
- joriy streak.

## 4. Kunlik streak

- Har kuni kirish va bajarilgan o‘quv faoliyatlari qayd etiladi.
- Ketma-ket kunlar soni ko‘rsatiladi.
- Har 7 kunlik streak uchun 10 coin bir marta beriladi.
- Bonus takroran olinmaydi.

## 5. Bildirishnomalar

O‘quvchi quyidagi holatlarda ichki bildirishnoma oladi:

- daraja yoki yakuniy test natijasi;
- yangi daraja ochilishi;
- sertifikat berilishi;
- do‘kon xaridi va buyurtma holati;
- streak bonusi.

Mobil va desktop headerda o‘qilmagan bildirishnomalar soni chiqadi. Alohida bildirishnomalar sahifasi ham mavjud.

## 6. PWA ilova

- Saytni telefon yoki kompyuter bosh ekraniga ilova sifatida o‘rnatish mumkin.
- Manifest, 192×192 va 512×512 ikonlar hamda service worker tayyor.
- Netlify kabi HTTPS domenida o‘rnatish tugmasi ishlaydi.
- Asosiy ilova qobig‘i keshga olinadi; API va Railway so‘rovlari keshga yozilmaydi.

## Productionga chiqarish

### Railway

Backend service uchun root directory:

```text
/backend
```

Deployda `start.sh` avtomatik ravishda migration, katalog seed va admin tayyorlashni bajaradi. Yangi `0006` migration ham shu jarayonda qo‘llanadi.

### Netlify

```text
Base directory: frontend
Build command: npm run build
Publish directory: dist
```

Environment variable:

```env
VITE_API_BASE_URL=https://SIZNING-RAILWAY-DOMENINGIZ.up.railway.app
```

PWA va yangi frontend fayllari chiqishi uchun eski keshni tozalab qayta deploy qilish tavsiya etiladi:

```text
Deploys → Trigger deploy → Clear cache and deploy site
```
