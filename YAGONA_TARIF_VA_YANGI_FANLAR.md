# Yagona tarif va yangi fanlar

## Tarif va to'lov holati

Platformada endi bitta tarif mavjud: **Yagona tarif**.

To'lov holatlari:

- `To'langan`
- `To'lanmagan`

Eski `Standart`, `Premium`, `VIP` tariflari migration vaqtida `Yagona` qiymatiga o'tkaziladi. Eski `Qarzdor` va `Kutilmoqda` holatlari `To'lanmagan` holatiga birlashtiriladi.

## Tayyor fanlar

Avvalgi English, Rus tili va Koreys tiliga qo'shimcha ravishda quyidagi fanlar avtomatik yaratiladi:

1. Matematika
2. Ona tili
3. Tarix
4. Huquq
5. IT
6. Kompyuter
7. Arab tili
8. Turk tili

Har bir yangi fanda `Boshlang'ich` darajasi va 5 ta mavzu mavjud. Har bir mavzuga tushuntirish, bitta dars, 10 savollik test, listening va speaking topshirig'i tayyorlanadi.

Railway deploy vaqtida `python manage.py seed_languages --catalog-only` avtomatik ishlaydi.
