const DB_NAME = 'alaziz-offline-v2';
const DB_VERSION = 2;
const API_STORE = 'api-cache';
const QUEUE_STORE = 'request-queue';
const META_STORE = 'meta';

function openDatabase() {
  return new Promise((resolve, reject) => {
    if (!('indexedDB' in window)) {
      reject(new Error('IndexedDB mavjud emas'));
      return;
    }
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(API_STORE)) db.createObjectStore(API_STORE, { keyPath: 'key' });
      if (!db.objectStoreNames.contains(QUEUE_STORE)) db.createObjectStore(QUEUE_STORE, { keyPath: 'id', autoIncrement: true });
      if (!db.objectStoreNames.contains(META_STORE)) db.createObjectStore(META_STORE, { keyPath: 'key' });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function transaction(storeName, mode, action) {
  return openDatabase().then((db) => new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, mode);
    const store = tx.objectStore(storeName);
    let result;
    try {
      result = action(store);
    } catch (error) {
      reject(error);
      return;
    }
    tx.oncomplete = () => resolve(result?.result ?? result);
    tx.onerror = () => reject(tx.error || result?.error);
    tx.onabort = () => reject(tx.error || new Error('IndexedDB transaction aborted'));
  }));
}

export function currentOfflineUserKey() {
  try {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    return String(user?.id || user?.username || 'guest');
  } catch {
    return 'guest';
  }
}

export function buildOfflineCacheKey(url) {
  return `${currentOfflineUserKey()}::${url}`;
}

export async function saveApiCache(url, data) {
  const key = buildOfflineCacheKey(url);
  const record = { key, url, userKey: currentOfflineUserKey(), data, savedAt: Date.now() };
  await transaction(API_STORE, 'readwrite', (store) => store.put(record));
  window.dispatchEvent(new CustomEvent('offline-cache-updated'));
  return record;
}

export async function getApiCache(url) {
  const key = buildOfflineCacheKey(url);
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const request = db.transaction(API_STORE, 'readonly').objectStore(API_STORE).get(key);
    request.onsuccess = () => resolve(request.result || null);
    request.onerror = () => reject(request.error);
  });
}

export async function listApiCache() {
  const userKey = currentOfflineUserKey();
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const request = db.transaction(API_STORE, 'readonly').objectStore(API_STORE).getAll();
    request.onsuccess = () => resolve((request.result || []).filter((item) => item.userKey === userKey));
    request.onerror = () => reject(request.error);
  });
}

export async function enqueueOfflineRequest(requestData) {
  const record = {
    ...requestData,
    userKey: currentOfflineUserKey(),
    createdAt: Date.now(),
    attempts: 0,
  };
  await transaction(QUEUE_STORE, 'readwrite', (store) => store.add(record));
  window.dispatchEvent(new CustomEvent('offline-queue-updated'));
  return record;
}

export async function listOfflineQueue() {
  const userKey = currentOfflineUserKey();
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const request = db.transaction(QUEUE_STORE, 'readonly').objectStore(QUEUE_STORE).getAll();
    request.onsuccess = () => resolve((request.result || []).filter((item) => item.userKey === userKey));
    request.onerror = () => reject(request.error);
  });
}

export async function deleteOfflineQueueItem(id) {
  await transaction(QUEUE_STORE, 'readwrite', (store) => store.delete(id));
  window.dispatchEvent(new CustomEvent('offline-queue-updated'));
}

export async function updateOfflineQueueItem(item) {
  await transaction(QUEUE_STORE, 'readwrite', (store) => store.put(item));
  window.dispatchEvent(new CustomEvent('offline-queue-updated'));
}

export async function setOfflineMeta(key, value) {
  await transaction(META_STORE, 'readwrite', (store) => store.put({ key: `${currentOfflineUserKey()}::${key}`, value }));
  window.dispatchEvent(new CustomEvent('offline-meta-updated'));
}

export async function getOfflineMeta(key) {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const request = db.transaction(META_STORE, 'readonly').objectStore(META_STORE).get(`${currentOfflineUserKey()}::${key}`);
    request.onsuccess = () => resolve(request.result?.value ?? null);
    request.onerror = () => reject(request.error);
  });
}

export async function clearCurrentUserOfflineData({ includeQueue = true } = {}) {
  const userKey = currentOfflineUserKey();
  const db = await openDatabase();
  const stores = includeQueue ? [API_STORE, QUEUE_STORE, META_STORE] : [API_STORE, META_STORE];
  await Promise.all(stores.map((storeName) => new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, 'readwrite');
    const store = tx.objectStore(storeName);
    const request = store.openCursor();
    request.onsuccess = () => {
      const cursor = request.result;
      if (!cursor) return;
      const value = cursor.value;
      const belongs = storeName === META_STORE
        ? String(value.key || '').startsWith(`${userKey}::`)
        : value.userKey === userKey || String(value.key || '').startsWith(`${userKey}::`);
      if (belongs) cursor.delete();
      cursor.continue();
    };
    tx.oncomplete = resolve;
    tx.onerror = () => reject(tx.error);
  })));
  if ('caches' in window) {
    const names = await caches.keys();
    await Promise.all(names.filter((name) => name.startsWith('alaziz-offline-media-')).map((name) => caches.delete(name)));
  }
  window.dispatchEvent(new CustomEvent('offline-cache-updated'));
  window.dispatchEvent(new CustomEvent('offline-queue-updated'));
}

export async function getOfflineStats() {
  const [cache, queue, lastDownload] = await Promise.all([
    listApiCache().catch(() => []),
    listOfflineQueue().catch(() => []),
    getOfflineMeta('last-download').catch(() => null),
  ]);
  const lessonCount = cache.filter((item) => /\/oquvchi\/dars\/\d+\/?(?:\?|$)/.test(item.url)).length;
  const approxBytes = cache.reduce((sum, item) => sum + JSON.stringify(item.data ?? null).length, 0);
  return { cacheCount: cache.length, lessonCount, queueCount: queue.length, lastDownload, approxBytes };
}
