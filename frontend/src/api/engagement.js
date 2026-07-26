import client from './client';

export const getListening = (darsId) => client.get(`/oquvchi/listening/${darsId}/`).then((r) => r.data);
export const submitListening = (darsId, javoblar) =>
  client.post(`/oquvchi/listening/${darsId}/topshirish/`, { javoblar }).then((r) => r.data);

export const getOqishRejasi = () => client.get('/oquvchi/oqish-rejasi/').then((r) => r.data);
export const getStreak = () => client.get('/oquvchi/streak/').then((r) => r.data);

export const getBildirishnomalar = () => client.get('/oquvchi/bildirishnomalar/').then((r) => r.data);
export const markBildirishnomaRead = (id) =>
  client.patch(`/oquvchi/bildirishnomalar/${id}/oqildi/`).then((r) => r.data);
export const markAllBildirishnomalarRead = () =>
  client.post('/oquvchi/bildirishnomalar/barchasi-oqildi/').then((r) => r.data);
