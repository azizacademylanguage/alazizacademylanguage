import client from './client';
export const getFaolMusobaqalar = () => client.get('/musobaqalar/faol/').then(r => r.data);
export const getMusobaqa = (id) => client.get(`/musobaqalar/${id}/`).then(r => r.data);
export const boshlashUrinish = (id) => client.post(`/musobaqalar/${id}/urinish-boshlash/`).then(r => r.data);
export const topshirishMusobaqa = (id, javoblar) => client.post(`/musobaqalar/${id}/topshirish/`, { javoblar }).then(r => r.data);
