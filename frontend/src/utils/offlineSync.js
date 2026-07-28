import axios from 'axios';
import { API_BASE } from '../api/client';
import { deleteOfflineQueueItem, listOfflineQueue, updateOfflineQueueItem } from './offlineDb';

function normalizePayload(data) {
  if (data == null || data === '') return undefined;
  if (typeof data === 'string') {
    try { return JSON.parse(data); } catch { return data; }
  }
  return data;
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return null;
  try {
    const { data } = await axios.post(`${API_BASE}/auth/refresh/`, { refresh }, { timeout: 30000 });
    localStorage.setItem('access_token', data.access);
    return data.access;
  } catch {
    return null;
  }
}

async function sendItem(item, token) {
  return axios({
    method: item.method,
    url: item.url.startsWith('http') ? item.url : `${API_BASE}${item.url.startsWith('/') ? item.url : `/${item.url}`}`,
    data: normalizePayload(item.data),
    params: item.params,
    timeout: 30000,
    headers: {
      'Content-Type': item.contentType || 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'X-Offline-Replay': String(item.id),
    },
  });
}

export async function syncOfflineQueue({ onProgress } = {}) {
  if (!navigator.onLine) return { synced: 0, failed: 0, remaining: (await listOfflineQueue()).length };
  const queue = await listOfflineQueue();
  let synced = 0;
  let failed = 0;

  for (const item of queue) {
    try {
      let token = localStorage.getItem('access_token');
      try {
        await sendItem(item, token);
      } catch (error) {
        if (error.response?.status !== 401) throw error;
        token = await refreshAccessToken();
        if (!token) throw error;
        await sendItem(item, token);
      }
      await deleteOfflineQueueItem(item.id);
      synced += 1;
    } catch (error) {
      const status = error.response?.status;
      if (status && status >= 400 && status < 500 && ![401, 408, 429].includes(status)) {
        await deleteOfflineQueueItem(item.id);
      } else {
        await updateOfflineQueueItem({ ...item, attempts: (item.attempts || 0) + 1, lastError: error.message, lastAttemptAt: Date.now() });
        failed += 1;
      }
    }
    onProgress?.({ synced, failed, total: queue.length });
  }

  const remaining = (await listOfflineQueue()).length;
  window.dispatchEvent(new CustomEvent('offline-sync-complete', { detail: { synced, failed, remaining } }));
  return { synced, failed, remaining };
}
