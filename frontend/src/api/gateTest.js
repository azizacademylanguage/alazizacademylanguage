import client from './client';

export const getGateTest = (darajaId) => client.get(`/oquvchi/gate-test/${darajaId}/`).then(r => r.data);
export const topshirGateTest = (darajaId, javoblar) =>
  client.post(`/oquvchi/gate-test/${darajaId}/topshirish/`, { javoblar }, { offlineQueue: true, offlineQueueKind: 'gate-test-result' }).then(r => r.data);

export const getFinalTest = (darajaId) => client.get(`/oquvchi/final-test/${darajaId}/`).then(r => r.data);
export const topshirFinalTest = (darajaId, javoblar) =>
  client.post(`/oquvchi/final-test/${darajaId}/topshirish/`, { javoblar }, { offlineQueue: true, offlineQueueKind: 'final-test-result' }).then(r => r.data);

export const getSertifikatlarim = () => client.get('/oquvchi/sertifikatlarim/').then(r => r.data);
export const tekshirSertifikat = (kod) => client.get(`/sertifikat-tekshirish/${kod}/`).then(r => r.data);
