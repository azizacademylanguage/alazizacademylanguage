AL-AZIZ TIL PLATFORMASI — ISHGA TUSHIRISH

1) BACKEND (PowerShell):
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed_languages
py manage.py runserver

2) FRONTEND (yangi PowerShell):
cd frontend
npm install
npm run dev

Sayt: http://localhost:5173
Backend: http://127.0.0.1:8000

LOGINLAR:
Admin: admin / admin12345
Filial rahbari: nazoratchi1 / naz12345
O'quvchi: oquvchi1 / stud12345

YANGI IMKONIYATLAR:
- Har bir daraja yakuniy testidan 80%+ olganda PDF va QR kodli sertifikat.
- QR kod sertifikatni ochiq tekshirish sahifasida topadi.
- Sertifikatlar admin panelida ko'rinadi va PDF yuklab olinadi.
- O'quvchi biriktirilgan fan bo'yicha 10 juftlik so'z xotira o'yinini o'ynaydi.
- Har bir to'g'ri juft uchun 1 coin, jami 10 coin.
- Coin do'konida tayyor mahsulotlar mavjud.
- Xarid admin va o'quvchining filial rahbari panelida ko'rinadi.
- Xarid holati: Yangi / Tayyorlanmoqda / Berildi.

QR KOD DEPLOY SOZLAMASI:
Backend hostingda FRONTEND_PUBLIC_URL ni frontend saytingiz manziliga qo'ying.
Masalan: FRONTEND_PUBLIC_URL=https://saytingiz.netlify.app
