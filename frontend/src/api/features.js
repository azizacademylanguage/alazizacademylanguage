import client from './client';

// Bildirishnomalar
export const getBildirishnomalarim = () => client.get('/oquvchi/bildirishnomalar/').then(r => r.data);
export const bildirishnomaOqish = (id) => client.post(`/oquvchi/bildirishnomalar/${id}/oqish/`).then(r => r.data);
export const barchaBildirishnomalarniOqish = () => client.post('/oquvchi/bildirishnomalar/barchasini-oqish/').then(r => r.data);
export const getAdminBildirishnomalar = () => client.get('/admin/bildirishnomalar/').then(r => r.data);
export const createBildirishnoma = (data) => client.post('/admin/bildirishnomalar/', data).then(r => r.data);
export const updateBildirishnoma = (id, data) => client.patch(`/admin/bildirishnomalar/${id}/`, data).then(r => r.data);
export const deleteBildirishnoma = (id) => client.delete(`/admin/bildirishnomalar/${id}/`);

// Placement test
export const getPlacementTest = (fan) => client.get('/oquvchi/placement-test/', { params: fan ? { fan } : {} }).then(r => r.data);
export const submitPlacementTest = (fan, javoblar, xavfsizlik) => client.post('/oquvchi/placement-test/', { fan, javoblar, xavfsizlik }).then(r => r.data);
export const getPlacementNatijalar = () => client.get('/admin/placement-natijalari/').then(r => r.data);
export const confirmPlacementNatija = (id) => client.post(`/admin/placement-natijalari/${id}/tasdiqlash/`).then(r => r.data);

// Faoliyat va xavfsizlik
export const getFaoliyatim = () => client.get('/oquvchi/faoliyatim/').then(r => r.data);
export const getAdminFaoliyat = (params = {}) => client.get('/admin/faoliyat/', { params }).then(r => r.data);
export const getTestXavfsizligi = (shubhali = false) => client.get('/admin/test-xavfsizligi/', { params: shubhali ? { shubhali: 1 } : {} }).then(r => r.data);

// Yutuqlar
export const getYutuqlarim = () => client.get('/oquvchi/yutuqlarim/').then(r => r.data);

// To'lov
export const getTolovim = () => client.get('/oquvchi/tolovim/').then(r => r.data);
export const getAdminTolovlar = (q = '') => client.get('/admin/tolovlar/', { params: q ? { q } : {} }).then(r => r.data);
export const createTolov = (data) => client.post('/admin/tolovlar/', data).then(r => r.data);
export const updateTolov = (id, data) => client.patch(`/admin/tolovlar/${id}/`, data).then(r => r.data);
export const deleteTolov = (id) => client.delete(`/admin/tolovlar/${id}/`);

// Yangi tezkor tarjima o'yini
export const startTezkorOyin = () => client.get('/oquvchi/tezkor-oyin/').then(r => r.data);
export const finishTezkorOyin = (token, javoblar) => client.post(`/oquvchi/tezkor-oyin/${token}/yakunlash/`, { javoblar }).then(r => r.data);

// Sertifikat holati
export const updateSertifikatStatus = (id, data) => client.patch(`/admin/sertifikatlar/${id}/status/`, data).then(r => r.data);

// Backup
export const downloadBackup = async () => {
  const response = await client.get('/admin/backup/yuklash/', { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.download = `alaziz_backup_${new Date().toISOString().slice(0, 10)}.zip`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
export const restoreBackup = (file, tasdiq) => {
  const form = new FormData();
  form.append('file', file);
  form.append('tasdiq', tasdiq);
  return client.post('/admin/backup/tiklash/', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data);
};
