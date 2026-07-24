import client from './client';

export const getWritingTopshiriqlar = (darsId) => client.get(`/oquvchi/writing/${darsId}/`).then(r => r.data);
export const topshirWriting = (topshiriqId, matnJavob) =>
  client.post(`/oquvchi/writing-topshirish/${topshiriqId}/`, { matn_javob: matnJavob }).then(r => r.data);

export const getSpeakingTopshiriqlar = (darsId) => client.get(`/oquvchi/speaking/${darsId}/`).then(r => r.data);
export const topshirSpeaking = (topshiriqId, audioBlob) => {
  const formData = new FormData();
  formData.append('audio_yozuv', audioBlob, 'yozuv.webm');
  return client.post(`/oquvchi/speaking-topshirish/${topshiriqId}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);
};

// Admin uchun
export const createWritingTopshiriq = (data) => client.post('/admin/writing-topshiriqlari/', data).then(r => r.data);
export const createSpeakingTopshiriq = (data) => client.post('/admin/speaking-topshiriqlari/', data).then(r => r.data);
