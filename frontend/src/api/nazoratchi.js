import client from './client';

export const getOquvchilar = () => client.get('/nazoratchi/oquvchilar/').then(r => r.data);
export const createOquvchi = (data) => client.post('/nazoratchi/oquvchilar/', data).then(r => r.data);
export const updateOquvchi = (id, data) => client.put(`/nazoratchi/oquvchilar/${id}/`, data).then(r => r.data);
export const deleteOquvchi = (id) => client.delete(`/nazoratchi/oquvchilar/${id}/`);

export const biriktirFan = (oquvchiId, darajaId) =>
  client.post(`/nazoratchi/oquvchilar/${oquvchiId}/fan-biriktirish/`, { daraja: darajaId }).then(r => r.data);

export const olibTashlaFan = (oquvchiId, darajaId) =>
  client.delete(`/nazoratchi/oquvchilar/${oquvchiId}/fan-biriktirish/`, { data: { daraja: darajaId } });

export const getOquvchiStatistika = (id) => client.get(`/nazoratchi/oquvchilar/${id}/statistika/`).then(r => r.data);
export const getNazoratchiStatistika = () => client.get('/nazoratchi/statistika/').then(r => r.data);

export const getFanlarRoyxati = () => client.get('/admin/fanlar/').then(r => r.data);

export const coinBerish = (oquvchiId, miqdor, izoh) =>
  client.post(`/admin/oquvchilar/${oquvchiId}/coin-berish/`, { miqdor, izoh }).then(r => r.data);
