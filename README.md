# AL-AZIZ til o‘rganish platformasi

Django REST backend va React/Vite frontend asosidagi til o‘rganish tizimi.

## Tayyor funksiyalar

- Admin o‘quvchi yaratishda ism, familya, login, parol, fan va boshlang‘ich darajani tanlaydi.
- O‘quvchiga faqat admin tanlagan bitta fan ko‘rinadi: **English**, **Rus tili** yoki **Koreys tili**.
- Daraja nomlarida raqamlar va foiz oralig‘i ko‘rsatilmaydi.
- Boshlang‘ich daraja ochiq, qolganlari qulf holatida turadi.
- Qulflangan daraja bosilganda sabab va admin bilan bog‘lanish xabari chiqadi.
- Har bir darajada 3 ta mavzu, har bir mavzuda tushuntirish va 10 savollik test bor.
- Mavzu testidan kamida 80% olinsa keyingi mavzu ochiladi.
- Darajadagi barcha mavzular 80%+ bajarilgach 10 savollik yakuniy test ochiladi.
- Yakuniy testdan 80%+ olinsa keyingi daraja avtomatik ochiladi.
- 80% dan past natijada keyingi daraja ochilmaydi.
- O‘tgan o‘quvchiga QR kodli PDF sertifikat avtomatik beriladi.
- QR kod skanerlanganda sertifikatning ochiq tekshirish sahifasi chiqadi.
- Admin panelida sertifikatlar, o‘quvchi ism-familyasi, fan, daraja, natija va PDF yuklab olish tugmasi mavjud.
- Dizaynda `#3C1642`, `#086375`, `#082900`, `#3B6402`, `#117E68` ranglari, soyalar, hover, transition va animatsiyalar ishlatilgan.
- Har bir darsda 10 savollik Listening mashqi mavjud.
- Speaking bo‘limida namuna tinglash, mikrofonda aytish va talaffuz aniqligi foizi mavjud.
- O‘quvchi bosh sahifasida shaxsiy o‘qish rejasi, bugungi dars, haftalik maqsad va qaytarish so‘zlari chiqadi.
- Kunlik streak yuritiladi; har 7 kunlik faollik uchun 10 coin bonus beriladi.
- Sertifikat, daraja, test, streak va do‘kon holatlari uchun ichki bildirishnomalar mavjud.
- Sayt PWA sifatida telefon yoki kompyuter bosh ekraniga o‘rnatiladi.

## Windows PowerShell orqali ishga tushirish

`start.bat` kerak emas. Backend va frontendni ikki terminalda alohida ishga tushiring.

### 1-terminal: backend

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed_languages
py manage.py runserver
```

Backend: `http://127.0.0.1:8000`

Django admin: `http://127.0.0.1:8000/admin/`

> `seed_languages` buyrug‘ini qayta ishlatish mumkin. U uchta til, 21 ta daraja, 63 ta mavzu va testlarni tayyorlaydi.

### 2-terminal: frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Tayyor loginlar

| Rol | Login | Parol |
|---|---|---|
| Admin | `admin` | `admin12345` |
| Nazoratchi | `nazoratchi1` | `naz12345` |
| O‘quvchi | `oquvchi1` | `stud12345` |

Demo o‘quvchiga **English — Beginner** tanlangan.

## QR kod uchun deploy sozlamasi

QR kod sertifikatning frontend sahifasiga olib boradi. Domen bilan joylashtirganda backend muhitiga quyidagini kiriting:

```env
FRONTEND_PUBLIC_URL=https://sizning-saytingiz.uz
```

Frontend API manzilini o‘zgartirish uchun:

```env
VITE_API_BASE_URL=https://backend-domeningiz.uz
```

## Tekshiruv buyruqlari

Backend:

```powershell
py manage.py check
py manage.py test courses exams
```

Frontend:

```powershell
npm run build
```

## Railway + Netlify production

Tayyor production sozlamalari va qadamlar: `DEPLOY_RAILWAY_NETLIFY_UZ.md`.

Yangi Listening, Speaking, reja, streak, bildirishnoma va PWA bo‘yicha qo‘llanma: `YANGI_FUNKSiyalar_3_4_5_6_9_10.md`.

## 2026-07 yangi modullar

Kengaytirilgan statistika, o‘quvchi to‘lov/muddat nazorati, writing avtomatik tekshiruv, reyting-musobaqa, Excel kontent import/eksport va audit/backup qo‘shildi. Batafsil: `YANGI_MODULLAR_4_5_7_9_11_12.md`.

Railway deploy yangi migratsiyalarni avtomatik bajaradi. Avtomatik backup uchun alohida Railway Cron service’da `python manage.py create_backup --keep 7` buyrug‘idan foydalaning va backend Volume’ni `/app/media` ga ulang.


## So'nggi yangilanish

- Standard, Premium va VIP o'rniga bitta **Yagona tarif** qoldirildi.
- Qarzdor va Kutilmoqda holatlari **To'lanmagan** holatiga birlashtirildi.
- Matematika, Ona tili, Tarix, Huquq, IT, Kompyuter, Arab tili va Turk tili qo'shildi.
- Har bir yangi fanga 5 tadan tayyor mavzu joylandi.

Batafsil: `YAGONA_TARIF_VA_YANGI_FANLAR.md`.
