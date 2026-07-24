import client, { API_BASE } from './client';

// CSV export/import — token talab qilingani uchun blob orqali yuklab, keyin fayl sifatida saqlaymiz
async function yuklabOlishCSV(url, filename) {
  const response = await client.get(url, { responseType: 'blob' });
  const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = blobUrl;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(blobUrl);
}

export const eksportUsersCSV = () => yuklabOlishCSV('/admin/export/users.csv', 'foydalanuvchilar.csv');
export const eksportNatijalarCSV = () => yuklabOlishCSV('/admin/export/natijalar.csv', 'natijalar.csv');

export const importUsersCSV = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return client.post('/admin/import/users-csv/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);
};

// Audit log
export const getAmalLoglari = () => client.get('/admin/amal-loglari/').then(r => r.data);

// Gate Test / Final Test CRUD (admin)
export const getGateTestlar = () => client.get('/admin/gate-testlar/').then(r => r.data);
export const createGateTest = (data) => client.post('/admin/gate-testlar/', data).then(r => r.data);
export const getGateTestBatafsil = (id) => client.get(`/admin/gate-testlar/${id}/`).then(r => r.data);
export const createGateTestSavol = (data) => client.post('/admin/gate-test-savollari/', data).then(r => r.data);
export const createGateTestJavob = (data) => client.post('/admin/gate-test-javoblari/', data).then(r => r.data);
export const deleteGateTestSavol = (id) => client.delete(`/admin/gate-test-savollari/${id}/`);

export const getFinalTestlar = () => client.get('/admin/final-testlar/').then(r => r.data);
export const createFinalTest = (data) => client.post('/admin/final-testlar/', data).then(r => r.data);
export const getFinalTestBatafsil = (id) => client.get(`/admin/final-testlar/${id}/`).then(r => r.data);
export const createFinalTestSavol = (data) => client.post('/admin/final-test-savollari/', data).then(r => r.data);
export const createFinalTestJavob = (data) => client.post('/admin/final-test-javoblari/', data).then(r => r.data);
export const deleteFinalTestSavol = (id) => client.delete(`/admin/final-test-savollari/${id}/`);
