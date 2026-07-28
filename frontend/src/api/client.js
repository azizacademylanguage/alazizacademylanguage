import axios from 'axios';
import { enqueueOfflineRequest, getApiCache, saveApiCache } from '../utils/offlineDb';

const rawApiBase = (
  import.meta.env.VITE_API_BASE_URL
  || import.meta.env.VITE_API_BASE
  || 'http://localhost:8000/api'
).trim();

const normalizedBase = rawApiBase.replace(/\/+$/, '');
export const API_BASE = /\/api$/i.test(normalizedBase)
  ? normalizedBase
  : `${normalizedBase}/api`;
export const API_ORIGIN = API_BASE.replace(/\/api\/?$/i, '');

export const apiAssetUrl = (path = '') => {
  if (!path) return '';
  if (/^https?:\/\//i.test(path)) return path;
  return `${API_ORIGIN}${path.startsWith('/') ? path : `/${path}`}`;
};

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

function absoluteRequestUrl(config = {}) {
  const base = config.baseURL || API_BASE;
  const rawUrl = /^https?:\/\//i.test(config.url || '')
    ? config.url
    : `${String(base).replace(/\/+$/, '')}/${String(config.url || '').replace(/^\/+/, '')}`;
  try {
    const url = new URL(rawUrl);
    Object.entries(config.params || {}).forEach(([key, value]) => {
      if (Array.isArray(value)) value.forEach((entry) => url.searchParams.append(key, entry));
      else if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value);
    });
    return url.toString();
  } catch {
    return rawUrl;
  }
}

function queuedResponse(config) {
  return {
    data: {
      offline_queued: true,
      queued: true,
      detail: "Internet qaytganda ma'lumot avtomatik yuboriladi.",
      created_at: new Date().toISOString(),
    },
    status: 202,
    statusText: 'Accepted Offline',
    headers: { 'x-alaziz-offline': 'queued' },
    config,
    request: null,
  };
}

async function queueConfig(config) {
  await enqueueOfflineRequest({
    method: String(config.method || 'post').toLowerCase(),
    url: absoluteRequestUrl(config),
    data: config.data,
    params: config.params,
    contentType: config.headers?.['Content-Type'] || config.headers?.['content-type'] || 'application/json',
    kind: config.offlineQueueKind || 'student-result',
  });
  return queuedResponse(config);
}

client.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;

  const method = String(config.method || 'get').toLowerCase();
  if (!navigator.onLine && method === 'get') {
    const cached = await getApiCache(absoluteRequestUrl(config)).catch(() => null);
    if (cached) {
      config.adapter = async () => ({
        data: cached.data,
        status: 200,
        statusText: 'OK (Offline cache)',
        headers: { 'x-alaziz-offline': 'cache', 'x-alaziz-cache-time': String(cached.savedAt) },
        config,
        request: null,
      });
    }
  } else if (!navigator.onLine && config.offlineQueue === true && method !== 'get') {
    config.adapter = async () => queueConfig(config);
  }

  return config;
});

client.interceptors.response.use(
  async (res) => {
    const method = String(res.config?.method || 'get').toLowerCase();
    if (method === 'get' && res.status >= 200 && res.status < 300 && res.headers?.['x-alaziz-offline'] !== 'cache') {
      saveApiCache(absoluteRequestUrl(res.config), res.data).catch(() => {});
    }
    return res;
  },
  async (error) => {
    const original = error.config || {};
    const method = String(original.method || 'get').toLowerCase();
    const networkFailure = !error.response || error.code === 'ERR_NETWORK' || error.code === 'ECONNABORTED';

    if (method === 'get' && networkFailure) {
      const cached = await getApiCache(absoluteRequestUrl(original)).catch(() => null);
      if (cached) {
        return {
          data: cached.data,
          status: 200,
          statusText: 'OK (Offline cache)',
          headers: { 'x-alaziz-offline': 'cache', 'x-alaziz-cache-time': String(cached.savedAt) },
          config: original,
          request: null,
        };
      }
    }

    if (networkFailure && original.offlineQueue === true && method !== 'get' && !original._offlineQueued) {
      original._offlineQueued = true;
      return queueConfig(original);
    }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_BASE}/auth/refresh/`, { refresh }, { timeout: 30000 });
          localStorage.setItem('access_token', data.access);
          original.headers = original.headers || {};
          original.headers.Authorization = `Bearer ${data.access}`;
          return client(original);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default client;
