import client from './client';

export const getFanlarim = () => client.get('/oquvchi/fanlarim/').then(r => r.data);
export const getMavzular = (darajaId) => client.get(`/oquvchi/mavzular/${darajaId}/`).then(r => r.data);
export const getDars = (darsId) => client.get(`/oquvchi/dars/${darsId}/`).then(r => r.data);
export const saveDarsProgress = (darsId, data) => client.post(`/oquvchi/dars/${darsId}/progress/`, data).then(r => r.data);

export const getMashq = (mashqId) => client.get(`/oquvchi/mashq/${mashqId}/`).then(r => r.data);
export const topshirMashq = (mashqId, javoblar, xavfsizlik = {}) =>
  client.post(`/oquvchi/mashq/${mashqId}/topshirish/`, { javoblar, xavfsizlik }).then(r => r.data);

export const getNatijalarim = () => client.get('/oquvchi/natijalarim/').then(r => r.data);
export const getXatolarim = (mashqId) => client.get(`/oquvchi/xatolarim/${mashqId}/`).then(r => r.data);
