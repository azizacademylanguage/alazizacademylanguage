import client from './client';

export const getCoinlarim = () => client.get('/oquvchi/coinlarim/').then((r) => r.data);

// So'z xotira o'yini
export const startSozOyini = () => client.get('/oquvchi/soz-oyini/').then((r) => r.data);
export const checkSozOyiniPair = (token, birinchi, ikkinchi) =>
  client.post(`/oquvchi/soz-oyini/${token}/tekshirish/`, { birinchi, ikkinchi }).then((r) => r.data);
export const finishSozOyini = (token, juftliklar) =>
  client.post(`/oquvchi/soz-oyini/${token}/yakunlash/`, { juftliklar }).then((r) => r.data);

// O'quvchi do'koni
export const getShopMahsulotlari = () => client.get('/oquvchi/shop/').then((r) => r.data);
export const getShopBuyurtmalarim = () => client.get('/oquvchi/shop-buyurtmalarim/').then((r) => r.data);
export const shopXarid = (mahsulotId) => client.post(`/oquvchi/shop/${mahsulotId}/xarid/`).then((r) => r.data);

// Admin / filial rahbari
export const getShopBuyurtmalar = (status = '') =>
  client.get('/boshqaruv/shop-buyurtmalar/', { params: status ? { status } : {} }).then((r) => r.data);
export const updateShopBuyurtmaStatus = (buyurtmaId, status) =>
  client.patch(`/boshqaruv/shop-buyurtmalar/${buyurtmaId}/status/`, { status }).then((r) => r.data);

export const adminCoinBerish = (oquvchiId, miqdor, izoh) =>
  client.post(`/admin/oquvchilar/${oquvchiId}/coin-berish/`, { miqdor, izoh }).then((r) => r.data);

export const getAdminShopMahsulotlari = () => client.get('/admin/shop-mahsulotlari/').then((r) => r.data);
export const createShopMahsulot = (data) => client.post('/admin/shop-mahsulotlari/', data).then((r) => r.data);
export const deleteShopMahsulot = (id) => client.delete(`/admin/shop-mahsulotlari/${id}/`);
