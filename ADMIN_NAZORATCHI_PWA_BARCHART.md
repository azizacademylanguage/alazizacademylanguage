# Admin va filial rahbari PWA + filiallar bar chart

## Qo‘shilganlar

- Admin panelida telefon/kompyuterga ilova sifatida o‘rnatish kartasi.
- Filial rahbari panelida telefon/kompyuterga ilova sifatida o‘rnatish kartasi.
- Barcha rollarda mobil topbar va desktop yuqori qismida PWA install tugmasi.
- iPhone ruscha menyu uchun ko‘rsatma: «Поделиться» → «На экран “Домой”» → «Добавить».
- Admin bosh sahifasidagi filiallar taqqoslash diagrammasi yangi responsiv gorizontal bar chartga o‘tkazildi.
- Eng yuqori natija, eng ko‘p o‘quvchi va umumiy filial/o‘quvchi ko‘rsatkichlari qo‘shildi.
- Kuchli statistika sahifasidagi filial diagrammasi ham bir xil yangi dizaynga o‘tkazildi.
- Service worker kesh versiyasi `v4` ga yangilandi.

## Deploy

GitHub repository ichidagi fayllarni yangilang:

```powershell
git add .
git commit -m "Admin nazoratchi PWA va filial bar chart qo'shildi"
git push origin main
```

Netlify avtomatik deploy qilmasa:

`Deploys → Trigger deploy → Clear cache and deploy site`
