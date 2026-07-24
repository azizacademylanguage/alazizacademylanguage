# AL-AZIZ platformasini Railway + Netlify'ga joylash

## Tuzilma

- `backend/` — Django REST API, Railway'ga joylanadi.
- `frontend/` — React/Vite, Netlify'ga joylanadi.
- `railway.json` va `netlify.toml` tayyor qo'shilgan.

## 1. GitHub'ga yuklash

Loyiha ildizida:

```powershell
git init
git add .
git commit -m "Railway va Netlify production sozlamalari"
git branch -M main
git remote add origin GITHUB_REPOSITORY_URL

git push -u origin main
```

## 2. Railway backend

1. Railway'da **New Project → Deploy from GitHub repo** ni tanlang.
2. Shu repositoryni tanlang. Root Directory'ni bo'sh qoldirish mumkin — ildizdagi `railway.json` ishlaydi.
3. Project ichiga **PostgreSQL** service qo'shing.
4. Backend service Variables bo'limiga quyidagilarni kiriting:

```env
DJANGO_SECRET_KEY=JUDA_UZUN_TASODIFIY_SECRET
DJANGO_DEBUG=False
FRONTEND_PUBLIC_URL=https://SIZNING-SAYTINGIZ.netlify.app
CORS_ALLOWED_ORIGINS=https://SIZNING-SAYTINGIZ.netlify.app
CSRF_TRUSTED_ORIGINS=https://SIZNING-SAYTINGIZ.netlify.app
ADMIN_USERNAME=admin
ADMIN_PASSWORD=KUCHLI_ADMIN_PAROL
ADMIN_EMAIL=admin@example.com
SERVE_MEDIA=True
```

PostgreSQL service qo'shilganda `DATABASE_URL` backend service'ga reference sifatida berilishi kerak:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

5. Backend service **Settings → Networking → Generate Domain** ni bosing.
6. Hosil bo'lgan domenni yozib oling, masalan:

```text
https://alaziz-api-production.up.railway.app
```

7. `DJANGO_ALLOWED_HOSTS` o'zgaruvchisiga domenning faqat host qismini kiriting:

```env
DJANGO_ALLOWED_HOSTS=alaziz-api-production.up.railway.app
```

8. Redeploy qiling. `/health/` manzili `status: ok` qaytarishi kerak.

### Media fayllar doimiy saqlanishi

Railway service'ga Volume qo'shib, mount path sifatida `/app/media` bering va:

```env
MEDIA_ROOT=/app/media
```

qiymatini kiriting. Volume bo'lmasa yuklangan rasm/audio fayllar redeploydan keyin o'chishi mumkin. QR va PDF sertifikatlar bazadagi ma'lumotdan real vaqtda yaratiladi.

## 3. Netlify frontend

1. Netlify'da **Add new site → Import an existing project** ni tanlang.
2. Shu GitHub repositoryni tanlang.
3. Ildizdagi `netlify.toml` avtomatik:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
   ni qo'llaydi.
4. **Environment variables** bo'limiga Railway backend domenini kiriting:

```env
VITE_API_BASE_URL=https://alaziz-api-production.up.railway.app
```

`/api` yozish shart emas; frontend avtomatik qo'shadi.
5. Deploy qiling.

## 4. Netlify domenini Railway'ga qayta yozish

Netlify sayti domeni aniq bo'lgach Railway Variables'da quyidagilarni shu domen bilan yangilang:

```env
FRONTEND_PUBLIC_URL=https://SIZNING-SAYTINGIZ.netlify.app
CORS_ALLOWED_ORIGINS=https://SIZNING-SAYTINGIZ.netlify.app
CSRF_TRUSTED_ORIGINS=https://SIZNING-SAYTINGIZ.netlify.app
```

So'ng Railway backendni Redeploy qiling. Bu login so'rovlari va sertifikat QR kodlari to'g'ri ishlashi uchun muhim.

## 5. Production login

Railway'dagi quyidagi env qiymatlari birinchi adminni yaratadi:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=KUCHLI_ADMIN_PAROL
```

Admin parolini keyinchalik o'zgartirganingizda deploy uni qayta eski holatga tushirmaydi. Env orqali majburan yangilash uchun vaqtincha:

```env
RESET_ADMIN_PASSWORD=True
```

qilib redeploy qiling, keyin yana `False` qiling.

## 6. Tekshirish

- Railway health: `https://BACKEND-DOMEN/health/`
- Django admin: `https://BACKEND-DOMEN/admin/`
- API login frontend orqali ishlaydi.
- Netlify'da sahifani yangilaganda 404 chiqmaydi (`_redirects` qo'shilgan).
- Sertifikat QR kodi Netlify'dagi `/sertifikat/KOD` sahifasini ochadi.

## Railway service rootini `backend` qilib deploy qilish varianti

Root Directory'ni `backend` deb belgilasangiz, `backend/railway.json` avtomatik ishlaydi. Netlify'da Base Directory'ni `frontend` qilib qo'ysangiz, `frontend/netlify.toml` ishlaydi.
