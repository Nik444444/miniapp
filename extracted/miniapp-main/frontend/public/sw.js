const CACHE_NAME = 'german-letter-ai-v2';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/mobile.css'
];

// Telegram Web App specific cache
const TELEGRAM_CACHE = 'telegram-web-app-v1';
const telegramUrlsToCache = [
  'https://telegram.org/js/telegram-web-app.js'
];

// Установка Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    Promise.all([
      caches.open(CACHE_NAME)
        .then(cache => {
          console.log('Opened main cache');
          return cache.addAll(urlsToCache);
        }),
      caches.open(TELEGRAM_CACHE)
        .then(cache => {
          console.log('Opened Telegram cache');
          return cache.addAll(telegramUrlsToCache);
        })
    ])
  );
});

// Обработка запросов
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Handle Telegram Web App requests
  if (url.hostname === 'telegram.org') {
    event.respondWith(
      caches.match(request, { cacheName: TELEGRAM_CACHE })
        .then(response => {
          return response || fetch(request);
        })
    );
    return;
  }
  
  // Handle API requests - always fetch from network
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Don't cache API responses
          return response;
        })
        .catch(error => {
          console.error('API request failed:', error);
          // Return cached offline response if available
          if (request.method === 'GET') {
            return caches.match('/offline.html');
          }
          throw error;
        })
    );
    return;
  }
  
  // Handle other requests
  event.respondWith(
    caches.match(request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(request);
      })
      .catch(error => {
        console.error('Fetch failed:', error);
        // Return fallback page for navigation requests
        if (request.mode === 'navigate') {
          return caches.match('/');
        }
        throw error;
      })
  );
});

// Активация Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME && cacheName !== TELEGRAM_CACHE) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push уведомления
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: data.primaryKey,
        telegramUserId: data.telegramUserId,
        url: data.url || '/'
      },
      actions: [
        {
          action: 'open',
          title: 'Открыть',
          icon: '/icons/icon-192x192.png'
        },
        {
          action: 'close',
          title: 'Закрыть',
          icon: '/icons/icon-192x192.png'
        }
      ],
      requireInteraction: true,
      silent: false
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Обработка нажатий на уведомления
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  const notificationData = event.notification.data;
  let targetUrl = '/';
  
  if (notificationData && notificationData.url) {
    targetUrl = notificationData.url;
  }
  
  if (event.action === 'open') {
    event.waitUntil(
      self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      }).then(clientList => {
        // Try to focus existing window
        for (const client of clientList) {
          if (client.url === targetUrl && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Open new window
        if (self.clients.openWindow) {
          return self.clients.openWindow(targetUrl);
        }
      })
    );
  } else if (event.action === 'close') {
    // Just close the notification
    event.notification.close();
  } else {
    // Default action
    event.waitUntil(
      self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      }).then(clientList => {
        if (clientList.length > 0) {
          return clientList[0].focus();
        }
        
        if (self.clients.openWindow) {
          return self.clients.openWindow(targetUrl);
        }
      })
    );
  }
});

// Обработка фоновой синхронизации
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  } else if (event.tag === 'telegram-sync') {
    event.waitUntil(doTelegramSync());
  }
});

function doBackgroundSync() {
  return new Promise((resolve, reject) => {
    // Sync offline data when connection is restored
    console.log('Background sync triggered');
    
    // Check if we have any pending analysis requests
    caches.open('offline-data').then(cache => {
      cache.keys().then(keys => {
        keys.forEach(key => {
          if (key.url.includes('/api/analyze-file')) {
            // Retry failed analysis requests
            fetch(key.url, {
              method: 'POST',
              body: key.body
            }).then(response => {
              if (response.ok) {
                cache.delete(key);
              }
            });
          }
        });
      });
    });
    
    resolve();
  });
}

function doTelegramSync() {
  return new Promise((resolve, reject) => {
    // Sync Telegram-specific data
    console.log('Telegram sync triggered');
    
    // Send any pending Telegram notifications
    resolve();
  });
}

// Обработка обновлений Service Worker
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      type: 'VERSION',
      version: CACHE_NAME
    });
  } else if (event.data && event.data.type === 'TELEGRAM_READY') {
    // Handle Telegram Web App ready event
    console.log('Telegram Web App is ready');
    
    // Update cache with Telegram-specific resources
    caches.open(TELEGRAM_CACHE).then(cache => {
      cache.addAll(telegramUrlsToCache);
    });
  }
});

// Periodic background sync for Telegram
self.addEventListener('periodicsync', event => {
  if (event.tag === 'telegram-news-sync') {
    event.waitUntil(
      fetch('/api/telegram-news')
        .then(response => response.json())
        .then(data => {
          // Cache latest news
          caches.open('telegram-news').then(cache => {
            cache.put('/api/telegram-news', new Response(JSON.stringify(data)));
          });
        })
        .catch(error => {
          console.error('Failed to sync Telegram news:', error);
        })
    );
  }
});

// Handle online/offline events
self.addEventListener('online', event => {
  console.log('App is online');
  // Trigger background sync
  self.registration.sync.register('background-sync');
});

self.addEventListener('offline', event => {
  console.log('App is offline');
  // Store offline status
  caches.open('app-status').then(cache => {
    cache.put('/status', new Response(JSON.stringify({ offline: true })));
  });
});

// Telegram Web App specific event handlers
self.addEventListener('telegramwebapp', event => {
  console.log('Telegram Web App event:', event);
  
  if (event.type === 'ready') {
    // App is ready in Telegram
    self.registration.showNotification('German Letter AI', {
      body: 'Приложение готово к работе в Telegram!',
      icon: '/icons/icon-192x192.png',
      badge: '/icons/icon-72x72.png',
      silent: true
    });
  }
});

// Handle viewport changes in Telegram
self.addEventListener('viewportchange', event => {
  console.log('Viewport changed:', event);
  
  // Adjust cached resources based on viewport
  if (event.isExpanded) {
    // Load more resources for expanded view
    caches.open(CACHE_NAME).then(cache => {
      cache.addAll([
        '/static/css/expanded.css',
        '/static/js/expanded.js'
      ]);
    });
  }
});

// Error handling
self.addEventListener('error', event => {
  console.error('Service Worker error:', event.error);
  
  // Send error to analytics or logging service
  if (event.error.message.includes('telegram')) {
    console.error('Telegram-related error:', event.error);
  }
});

// Unhandled promise rejection
self.addEventListener('unhandledrejection', event => {
  console.error('Unhandled promise rejection:', event.reason);
  event.preventDefault();
});