/**
 * NexusAI Service Worker
 * =====================
 *
 * Provides offline functionality, caching, and background sync
 */

const CACHE_NAME = "nexusai-v1.0.0";
const STATIC_CACHE = "nexusai-static-v1.0.0";
const DYNAMIC_CACHE = "nexusai-dynamic-v1.0.0";

// Files to cache for offline use
const STATIC_FILES = [
  "/",
  "/index.html",
  "/static/css/clean-ui.css",
  "/static/js/clean-app.js",
  "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
  "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
];

// API endpoints that can work offline
const OFFLINE_FALLBACKS = {
  "/api/conversations": { conversations: [], status: "offline" },
  "/api/templates": { templates: [], status: "offline" },
  "/api/models": {
    models: { available: [], default: "offline-mode" },
    status: "offline",
  },
};

// Install event - cache static files
self.addEventListener("install", (event) => {
  console.log("Service Worker: Installing...");

  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log("Service Worker: Caching static files");
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log("Service Worker: Static files cached");
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error("Service Worker: Error caching static files", error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("Service Worker: Activating...");

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log("Service Worker: Deleting old cache", cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log("Service Worker: Activated");
        return self.clients.claim();
      })
  );
});

// Fetch event - serve cached content when offline
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle different types of requests
  if (request.method === "GET") {
    if (isStaticFile(request.url)) {
      // Static files - cache first strategy
      event.respondWith(cacheFirst(request));
    } else if (isAPIRequest(request.url)) {
      // API requests - network first with offline fallback
      event.respondWith(networkFirstWithFallback(request));
    } else {
      // Other requests - network first with cache fallback
      event.respondWith(networkFirst(request));
    }
  } else if (request.method === "POST") {
    // Handle POST requests (chat, etc.)
    event.respondWith(handlePostRequest(request));
  }
});

// Message event - handle messages from main thread
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

// Background sync event
self.addEventListener("sync", (event) => {
  if (event.tag === "background-sync") {
    event.waitUntil(doBackgroundSync());
  }
});

// Push notification event
self.addEventListener("push", (event) => {
  const options = {
    body: event.data ? event.data.text() : "New message from NexusAI",
    icon: "/static/icons/icon-192x192.png",
    badge: "/static/icons/badge-72x72.png",
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1,
    },
    actions: [
      {
        action: "explore",
        title: "Open NexusAI",
        icon: "/static/icons/checkmark.png",
      },
      {
        action: "close",
        title: "Close",
        icon: "/static/icons/xmark.png",
      },
    ],
  };

  event.waitUntil(self.registration.showNotification("NexusAI", options));
});

// Notification click event
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  if (event.action === "explore") {
    event.waitUntil(clients.openWindow("/"));
  }
});

// Helper functions
function isStaticFile(url) {
  return (
    url.includes("/static/") ||
    url.includes("cdnjs.cloudflare.com") ||
    url.endsWith(".css") ||
    url.endsWith(".js") ||
    url.endsWith(".png") ||
    url.endsWith(".jpg") ||
    url.endsWith(".svg")
  );
}

function isAPIRequest(url) {
  return url.includes("/api/");
}

async function cacheFirst(request) {
  try {
    const cache = await caches.open(STATIC_CACHE);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.error("Cache first strategy failed:", error);
    return new Response("Offline", { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    return new Response("Offline", { status: 503 });
  }
}

async function networkFirstWithFallback(request) {
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Try cache first
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline fallback
    const url = new URL(request.url);
    const fallback = OFFLINE_FALLBACKS[url.pathname];

    if (fallback) {
      return new Response(JSON.stringify(fallback), {
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response(
      JSON.stringify({
        error: "Offline",
        status: "offline",
      }),
      {
        status: 503,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

async function handlePostRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    // Store for background sync
    const requestData = await request.clone().json();
    await storeForSync(request.url, requestData);

    // Return offline response
    return new Response(
      JSON.stringify({
        status: "queued",
        message: "Request queued for when you're back online",
      }),
      {
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

async function storeForSync(url, data) {
  // Store requests for background sync
  const syncStore = await getObjectStore("sync-requests", "readwrite");
  await syncStore.add({
    url,
    data,
    timestamp: Date.now(),
  });
}

async function doBackgroundSync() {
  try {
    const syncStore = await getObjectStore("sync-requests", "readonly");
    const requests = await syncStore.getAll();

    for (const request of requests) {
      try {
        await fetch(request.url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(request.data),
        });

        // Remove from sync store after successful sync
        const deleteStore = await getObjectStore("sync-requests", "readwrite");
        await deleteStore.delete(request.id);
      } catch (error) {
        console.error("Background sync failed for request:", request, error);
      }
    }
  } catch (error) {
    console.error("Background sync failed:", error);
  }
}

async function getObjectStore(storeName, mode) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("nexusai-db", 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction([storeName], mode);
      const store = transaction.objectStore(storeName);
      resolve(store);
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(storeName)) {
        const store = db.createObjectStore(storeName, {
          keyPath: "id",
          autoIncrement: true,
        });
        store.createIndex("timestamp", "timestamp", { unique: false });
      }
    };
  });
}
