# Jonli musobaqa va til tanlash dizayni

## Musobaqa oqimi

1. Admin `Musobaqalar` bo‘limida musobaqa yaratadi.
2. Fan, filial, savollar soni, vaqt va sovrin coinlarini belgilaydi.
3. `Boshlash` tugmasi bosilganda musobaqa `Jonli` holatiga o‘tadi.
4. Mos fan/filialdagi o‘quvchilarda 5 soniya ichida katta animatsiyali bildirishnoma chiqadi.
5. O‘quvchi `Musobaqaga kirish`ni bosadi va `3–2–1` sanog‘idan keyin test boshlanadi.
6. Savollar tegishli fan testlari bankidan tasodifiy olinadi, variantlar aralashtiriladi.
7. Vaqt tugasa javoblar avtomatik topshiriladi. Sahifa yangilansa vaqt davom etadi.
8. Har bir o‘quvchi bir marta qatnashadi. Natija foiz, to‘g‘ri javoblar va tezlik bo‘yicha reytingga tushadi.
9. Admin musobaqani yakunlaganda 1–3-o‘rinlarga coin beriladi.

## Til tanlash

- Oddiy select o‘rniga bayroqli, animatsiyali dropdown qo‘shildi.
- O‘zbekcha, Русский va English variantlari mavjud.
- Desktop, sidebar, login va mobil topbar ko‘rinishlariga mos.
- Tanlangan til `localStorage`da saqlanadi.

## Deploy

Backendda yangi migration:

```text
exams.0010_live_competition
```

Railway deploy vaqtida `python manage.py migrate` avtomatik bajariladi.
Service Worker `alaziz-pwa-v8`ga yangilandi. Netlify’da eski cache qolsa:

```text
Deploys → Trigger deploy → Clear cache and deploy site
```
