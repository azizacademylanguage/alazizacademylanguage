import client from './client';

export const getFiliallar = () => client.get('/admin/filiallar/').then(r => r.data);
export const createFilial = (data) => client.post('/admin/filiallar/', data).then(r => r.data);
export const deleteFilial = (id) => client.delete(`/admin/filiallar/${id}/`);

export const getNazoratchilar = () => client.get('/admin/nazoratchilar/').then(r => r.data);
export const createNazoratchi = (data) => client.post('/admin/nazoratchilar/', data).then(r => r.data);
export const updateNazoratchi = (id, data) => client.put(`/admin/nazoratchilar/${id}/`, data).then(r => r.data);
export const deleteNazoratchi = (id) => client.delete(`/admin/nazoratchilar/${id}/`);

export const getAdminStatistika = () => client.get('/admin/statistika/').then(r => r.data);

export const getFanlar = () => client.get('/admin/fanlar/').then(r => r.data);
export const createFan = (data) => client.post('/admin/fanlar/', data).then(r => r.data);
export const getFan = (id) => client.get(`/admin/fanlar/${id}/`).then(r => r.data);
export const deleteFan = (id) => client.delete(`/admin/fanlar/${id}/`);

export const createDaraja = (data) => client.post('/admin/darajalar/', data).then(r => r.data);
export const deleteDaraja = (id) => client.delete(`/admin/darajalar/${id}/`);

export const createMavzu = (data) => client.post('/admin/mavzular/', data).then(r => r.data);
export const deleteMavzu = (id) => client.delete(`/admin/mavzular/${id}/`);

export const createDars = (data) => client.post('/admin/darslar/', data).then(r => r.data);
export const updateDars = (id, data) => client.patch(`/admin/darslar/${id}/`, data).then(r => r.data);
export const deleteDars = (id) => client.delete(`/admin/darslar/${id}/`);

export const createMashq = (data) => client.post('/admin/mashqlar/', data).then(r => r.data);
export const createSavol = (data) => client.post('/admin/savollar/', data).then(r => r.data);
export const createJavob = (data) => client.post('/admin/javoblar/', data).then(r => r.data);

export const getAdminOquvchilar = () => client.get('/admin/oquvchilar/').then(r => r.data);
export const getAdminOquvchiProgress = (id) => client.get(`/admin/oquvchilar/${id}/progress/`).then(r => r.data);
export const createAdminOquvchi = (data) => client.post('/admin/oquvchilar/', data).then(r => r.data);
export const updateAdminOquvchi = (id, data) => client.patch(`/admin/oquvchilar/${id}/`, data).then(r => r.data);
export const deleteAdminOquvchi = (id) => client.delete(`/admin/oquvchilar/${id}/`);

export const getAdminSertifikatlar = (q = '') => client.get('/admin/sertifikatlar/', { params: q ? { q } : {} }).then(r => r.data);
