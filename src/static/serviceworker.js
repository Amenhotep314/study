const OFFLINE_VERSION = 1;
const CACHE_NAME = "fluxstudy_offline";
const OFFLINE_URLS = [
    "static/stylesheet.css",
    "static/greensboro_winter.css",
    "static/serenity_now.css",
    "home",
    "my_account",
    "todos",
    "semesters",
    "courses",
    "static/favicon.png",
    "static/icon.png",
    "static/app.webmanifest",
    "offline"
]

self.addEventListener("install", (event) => {
    event.waitUntil(
        (async () => {
            const cache = await caches.open(CACHE_NAME);
            // Setting {cache: 'reload'} in the new request ensures that the
            // response isn't fulfilled from the HTTP cache; i.e., it will be
            // from the network.
            await cache.addAll(OFFLINE_URLS);
        })()
    );
    // Force the waiting service worker to become the active service worker.
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        (async () => {
            if ("navigationPreload" in self.registration) {
                await self.registration.navigationPreload.enable();
            }
        })()
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        (async () => {
            cache = await caches.open(CACHE_NAME);
            try {

                // Try to respond from navigation preload
                console.log("Trying to respond from navigation preload")
                const preloadResponse = await event.preloadResponse;
                if (preloadResponse) {
                    clone = preloadResponse.clone();
                    cache.put(event.request, clone);
                    return preloadResponse;
                }

                // Try to respond from network
                console.log("Trying to respond from network")
                const networkResponse = await fetch(event.request);
                clone = networkResponse.clone();
                cache.put(event.request, clone);
                return networkResponse;

            } catch (error) {
                // Try to respond from the cache
                console.log("Trying to respond from cache")
                let cachedResponse = await cache.match(event.request);
                if(!cachedResponse){
                    console.log("Trying to show offline page");
                    cachedResponse = await cache.match("offline");
                }
                return cachedResponse;
            }
        })()
    );
});