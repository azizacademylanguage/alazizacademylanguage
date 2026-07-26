# Railway database tuzatishi

Ushbu versiya ikki production sxema xatosini tuzatadi:

1. `users.token_version` ustuni `NOT NULL` bo'lib, yangi foydalanuvchi yaratishda qiymat yuborilmagan.
2. `exams.0004` bajarilgan deb yozilgan bo'lsa-da, `soz_oyini_sessiyalari` jadvali fizik bazada yo'q bo'lgan.

Deployda quyidagi migrationlar bajariladi:

```text
Applying accounts.0005_user_token_version... OK
Applying exams.0008_repair_word_game_schema... OK
DB_REPAIR_READY sequences=...
```

Shundan so'ng admin paneldan yangi o'quvchi yaratish va so'z o'yini ishlaydi.
