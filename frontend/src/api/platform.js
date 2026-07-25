import client from './client';

// AI yordamchi
export const getAIYordamchi = () => client.get('/oquvchi/ai-yordamchi/').then(r => r.data);
export const sendAIYordamchi = (savol) => client.post('/oquvchi/ai-yordamchi/', { savol }).then(r => r.data);
export const clearAIYordamchi = () => client.delete('/oquvchi/ai-yordamchi/');

// O'quvchi murojaatlari
export const getMeningMurojaatlarim = () => client.get('/oquvchi/murojaatlar/').then(r => r.data);
export const createMurojaat = (data) => client.post('/oquvchi/murojaatlar/', data).then(r => r.data);
export const getMeningMurojaatim = (id) => client.get(`/oquvchi/murojaatlar/${id}/`).then(r => r.data);
export const replyMeningMurojaatim = (id, matn) => client.post(`/oquvchi/murojaatlar/${id}/`, { matn }).then(r => r.data);

// Admin murojaatlar
export const getAdminMurojaatlar = (params = {}) => client.get('/admin/murojaatlar/', { params }).then(r => r.data);
export const getAdminMurojaat = (id) => client.get(`/admin/murojaatlar/${id}/`).then(r => r.data);
export const updateAdminMurojaat = (id, data) => client.patch(`/admin/murojaatlar/${id}/`, data).then(r => r.data);
export const replyAdminMurojaat = (id, matn) => client.post(`/admin/murojaatlar/${id}/`, { matn }).then(r => r.data);

// Analitika
export const getKuchliAnalitika = (params = {}) => client.get('/admin/kuchli-analitika/', { params }).then(r => r.data);

// Platforma sozlamalari
export const getPlatformHolati = () => client.get('/platform-holati/').then(r => r.data);
export const getPlatformSozlamalari = () => client.get('/admin/platform-sozlamalari/').then(r => r.data);
export const updatePlatformSozlamalari = (data) => client.patch('/admin/platform-sozlamalari/', data).then(r => r.data);

// Xavfsizlik
export const getMeningXavfsizligim = () => client.get('/auth/xavfsizlik/').then(r => r.data);
export const parolAlmashtirish = (data) => client.post('/auth/parol-almashtirish/', data).then(r => r.data);
export const barchaQurilmalardanChiqish = () => client.post('/auth/barcha-qurilmalardan-chiqish/').then(r => r.data);
export const getAdminXavfsizlik = () => client.get('/admin/xavfsizlik/').then(r => r.data);
export const adminSessiyalarniBekorQilish = (userId) => client.post(`/admin/xavfsizlik/${userId}/sessiyalarni-bekor-qilish/`).then(r => r.data);
