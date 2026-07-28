import client from './client';

export const login = async (username, password) => {
  const { data } = await client.post('/auth/login/', { username, password });
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  localStorage.setItem('user', JSON.stringify(data.user));
  window.dispatchEvent(new CustomEvent('offline-user-changed'));
  return data.user;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  window.dispatchEvent(new CustomEvent('offline-user-changed'));
};

export const getMe = async () => {
  const { data } = await client.get('/auth/me/');
  return data;
};

export const getStoredUser = () => {
  const raw = localStorage.getItem('user');
  return raw ? JSON.parse(raw) : null;
};
