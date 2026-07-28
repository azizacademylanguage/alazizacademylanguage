import client from './client';

export const getWritingTopshiriqlar = (darsId) => client.get(`/oquvchi/writing/${darsId}/`).then(r => r.data);
export const topshirWriting = (topshiriqId, matnJavob) =>
  client.post(`/oquvchi/writing-topshirish/${topshiriqId}/`, { matn_javob: matnJavob }, { offlineQueue: true, offlineQueueKind: 'writing-result' }).then(r => r.data);

export const getSpeakingTopshiriqlar = (darsId) => client.get(`/oquvchi/speaking/${darsId}/`).then(r => r.data);
export const topshirSpeaking = (topshiriqId, transkripsiya, audioBlob = null) => {
  if (!audioBlob) {
    return client.post(`/oquvchi/speaking-topshirish/${topshiriqId}/`, { transkripsiya }, { offlineQueue: true, offlineQueueKind: 'speaking-result' }).then(r => r.data);
  }
  const formData = new FormData();
  formData.append('transkripsiya', transkripsiya || '');
  formData.append('audio_yozuv', audioBlob, 'yozuv.webm');
  return client.post(`/oquvchi/speaking-topshirish/${topshiriqId}/`, formData).then(r => r.data);
};

export const createWritingTopshiriq = (data) => client.post('/admin/writing-topshiriqlari/', data).then(r => r.data);
export const createSpeakingTopshiriq = (data) => client.post('/admin/speaking-topshiriqlari/', data).then(r => r.data);
