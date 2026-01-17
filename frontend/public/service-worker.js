// Pyramyd PWA Service Worker
// Version 1.0.0

const CACHE_NAME = 'pyramyd-v6-fix';
const OFFLINE_QUEUE = 'pyramyd-offline-queue';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/favicon.ico'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS.map(url => new Request(url, { cache: 'reload' })));
      })
      .catch((error) => {
        console.log('[SW] Cache installation failed:', error);
      })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME && cacheName !== OFFLINE_QUEUE)
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
  return self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests differently
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
  } else {
    // Static assets strategy
    event.respondWith(handleStaticRequest(request));
  }
});

<<<<<<< HEAD
// Handle static asset requests (cache-first)
// Handle static asset requests (Network-First with Cache Fallback)
async function handleStaticRequest(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    // Try network first (Always get latest version)
    const response = await fetch(request);

    // If successful, update the cache
    if (response.status === 200) {
      cache.put(request, response.clone());
=======
// Handle static asset requests
// Handle static asset requests
async function handleStaticRequest(request) {
  // Strategy: Network-First for ALL static assets (HTML, CSS, JS, Images)
  // CRITICAL: Prevent SW from handling non-GET requests (e.g. POST uploads) in this fallback
  if (request.method !== 'GET') {
    return fetch(request);
  }

  try {
    // 1. Try Network first
    const networkResponse = await fetch(request);

    // If successful (200 OK), cache it and return
    if (networkResponse.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
>>>>>>> 3c08bac4cdd6f65fe0f1b7cf2bb12556ec177a49
    }

    return networkResponse;
  } catch (error) {
<<<<<<< HEAD
    // Note: 'Only-if-cached' mode error handling?
    // Network failed, try cache
    console.log('[SW] Network failed for static asset, trying cache:', request.url);
    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }

    // Return offline page for navigation requests if both fail
    if (request.destination === 'document') {
=======
    // 2. If Network fails (offline), try Cache
    console.log('[SW] Network failed, checking cache:', request.url);
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    // 3. Fallback for navigation requests
    if (request.mode === 'navigate') {
>>>>>>> 3c08bac4cdd6f65fe0f1b7cf2bb12556ec177a49
      return cache.match('/index.html');
    }

    throw error;
  }
}

// Handle API requests (network-first with cache fallback)
// Handle API requests (network-first with cache fallback)
async function handleApiRequest(request) {
  const url = new URL(request.url);

  // CRITICAL: NEVER cache Auth routes
  if (url.pathname.includes('/auth/')) {
    return fetch(request);
  }

  // CRITICAL: NEVER cache non-GET requests
  if (request.method !== 'GET') {
    return fetch(request);
  }

  const cache = await caches.open(CACHE_NAME);

  try {
    // Try network first
    const response = await fetch(request);

<<<<<<< HEAD
    // Cache successful GET requests
    if (request.method === 'GET' && response.status === 200) {
=======
    // Cache ONLY successful GET requests
    if (response.status === 200) {
>>>>>>> 3c08bac4cdd6f65fe0f1b7cf2bb12556ec177a49
      cache.put(request, response.clone());
    }

    return response;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);

    // If GET request, try cache
    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }

<<<<<<< HEAD
    // If POST/PUT request (like product creation), queue it for later
    if (request.method === 'POST' || request.method === 'PUT') {
      await queueOfflineRequest(request);
      return new Response(
        JSON.stringify({
          queued: true,
          message: 'Request queued for sync when online'
        }),
        {
          status: 202,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

=======
>>>>>>> 3c08bac4cdd6f65fe0f1b7cf2bb12556ec177a49
    // Return error for other cases
    return new Response(
      JSON.stringify({ error: 'No network connection', offline: true }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}


// Queue offline requests
async function queueOfflineRequest(request) {
  const queue = await caches.open(OFFLINE_QUEUE);
  const body = await request.clone().text();

  const queuedRequest = {
    url: request.url,
    method: request.method,
    headers: Array.from(request.headers.entries()),
    body: body,
    timestamp: Date.now()
  };

  // Store as a unique entry
  const queueKey = `offline-${Date.now()}-${Math.random()}`;
  await queue.put(
    new Request(queueKey),
    new Response(JSON.stringify(queuedRequest))
  );

  console.log('[SW] Queued offline request:', queueKey);
}

// Background Sync event - sync queued requests when online
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);

  if (event.tag === 'sync-offline-requests') {
    event.waitUntil(syncOfflineRequests());
  }
});

// Sync all queued offline requests
async function syncOfflineRequests() {
  console.log('[SW] Starting offline requests sync...');
  const queue = await caches.open(OFFLINE_QUEUE);
  const requests = await queue.keys();

  for (const request of requests) {
    try {
      const response = await queue.match(request);
      const queuedRequest = await response.json();

      // Recreate and send the request
      const headers = new Headers(queuedRequest.headers);
      const fetchRequest = new Request(queuedRequest.url, {
        method: queuedRequest.method,
        headers: headers,
        body: queuedRequest.body
      });

      const fetchResponse = await fetch(fetchRequest);

      if (fetchResponse.ok) {
        console.log('[SW] Synced request:', queuedRequest.url);
        await queue.delete(request);

        // Notify clients about successful sync
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
          client.postMessage({
            type: 'SYNC_SUCCESS',
            url: queuedRequest.url,
            timestamp: queuedRequest.timestamp
          });
        });
      }
    } catch (error) {
      console.error('[SW] Failed to sync request:', error);
    }
  }

  console.log('[SW] Offline requests sync completed');
}

// Message event - handle commands from clients
self.addEventListener('message', (event) => {
  console.log('[SW] Received message:', event.data);

  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data.type === 'SYNC_NOW') {
    syncOfflineRequests();
  }

  if (event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
});

console.log('[SW] Service worker loaded');
