const VERSION = 'alaziz-pwa-v7';
const APP_CACHE = `${VERSION}-app`;
const RUNTIME_CACHE = `${VERSION}-runtime`;
const MEDIA_CACHE = 'alaziz-offline-media-v1';
const APP_SHELL = [
  '/',
  '/login',
  '/manifest.webmanifest',
  '/favicon.svg',
  '/pwa/icon-192.png',
  '/pwa/icon-512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(APP_CACHE)
      .then((cache) => cache.addAll(APP_SHELL))
      .catch(() => undefined),
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys
        .filter((key) => key.startsWith('alaziz-pwa-') && ![APP_CACHE, RUNTIME_CACHE].includes(key))
        .map((key) => caches.delete(key)),
    )),
  );
  self.clients.claim();
});

function isApiRequest(url) {
  return url.pathname.startsWith('/api/') || url.pathname === '/api';
}

function isMediaRequest(request, url) {
  return ['audio', 'video', 'image'].includes(request.destination)
    || /\.(mp3|wav|ogg|m4a|mp4|webm|jpg|jpeg|png|webp|svg|pdf)(\?|$)/i.test(url.pathname);
}

async function navigationResponse(request) {
  try {
    const response = await fetch(request);
    if (response?.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      await cache.put('/', response.clone());
    }
    return response;
  } catch {
    return (
      await caches.match(request)
      || await caches.match('/')
      || await caches.match('/login')
      || new Response(
        '<!doctype html><html lang="uz"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Offline</title><body style="font-family:system-ui;padding:32px;text-align:center"><h1>Internet mavjud emas</h1><p>Oldindan yuklangan darslarni ilova ichidagi Offline bo‘limidan oching.</p></body></html>',
        { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } },
      )
    );
  }
}

async function cacheFirst(request, cacheName = RUNTIME_CACHE) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response && (response.ok || response.type === 'opaque')) {
      const cache = await caches.open(cacheName);
      await cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('', { status: 504, statusText: 'Offline' });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cached = await cache.match(request);
  const network = fetch(request)
    .then((response) => {
      if (response?.ok && response.type === 'basic') cache.put(request, response.clone());
      return response;
    })
    .catch(() => null);
  return cached || await network || new Response('', { status: 504, statusText: 'Offline' });
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);

  // Authenticated API responses are stored in per-user IndexedDB by the app,
  // never in the shared service-worker cache.
  if (isApiRequest(url)) return;

  if (request.mode === 'navigate') {
    event.respondWith(navigationResponse(request));
    return;
  }

  if (isMediaRequest(request, url)) {
    event.respondWith(cacheFirst(request, MEDIA_CACHE));
    return;
  }

  if (url.origin === self.location.origin) {
    event.respondWith(staleWhileRevalidate(request));
  }
});

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});
