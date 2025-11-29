/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS — Service Worker                                      ║
 * ║   Sprint 008: PWA + Offline Support                              ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

const CACHE_NAME = 'aurora-v1.0';
const OFFLINE_URL = '/offline.html';

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
  console.log('[AuroraOS SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[AuroraOS SW] Caching core assets');
      return cache.addAll(PRECACHE_ASSETS);
    })
  );
  // Activate immediately
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  console.log('[AuroraOS SW] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[AuroraOS SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    })
  );
  // Take control of all pages immediately
  self.clients.claim();
});

// Fetch event - network first, cache fallback
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip API requests (let them go to network)
  if (event.request.url.includes('/v1/')) return;
  
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clone the response before caching
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });
        return response;
      })
      .catch(() => {
        // Network failed, try cache
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          // No cache, return offline page for navigation
          if (event.request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
          }
          return new Response('Offline', { status: 503 });
        });
      })
  );
});

// Background sync for logging events
self.addEventListener('sync', (event) => {
  if (event.tag === 'aurora-sync') {
    console.log('[AuroraOS SW] Background sync triggered');
    // Future: sync pending logs when back online
  }
});

// Push notification handling (future)
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const title = data.title || 'AuroraOS';
  const options = {
    body: data.body || 'Aurora seni bekliyor.',
    icon: '/icons/aurora-192.png',
    badge: '/icons/aurora-192.png',
    tag: 'aurora-notification',
    data: data.url || '/',
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data || '/')
  );
});

console.log('[AuroraOS SW] Service Worker loaded — v1.0');

