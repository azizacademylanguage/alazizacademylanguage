import client from './client';

export const getDarsBatafsil = (id) => client.get(`/admin/darslar/${id}/`).then(r => r.data);
export const uploadDarsMedia = (id, formData) =>
  client.patch(`/admin/darslar/${id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data);
export const getMashqBatafsil = (id) => client.get(`/admin/mashqlar/${id}/`).then(r => r.data);
export const createSavolTo = (data) => client.post('/admin/savollar/', data).then(r => r.data);
export const createJavobTo = (data) => client.post('/admin/javoblar/', data).then(r => r.data);
export const deleteSavolTo = (id) => client.delete(`/admin/savollar/${id}/`);
