import client from './client';

export const getReyting = (period = 'hafta') => client.get('/reyting/', { params: { period } }).then(r => r.data);
export const getMusobaqalar = () => client.get('/musobaqalar/').then(r => r.data);
