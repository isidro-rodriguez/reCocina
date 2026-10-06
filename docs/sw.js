const CACHE = "recocina-v1"; // la genera build_precache.py (ver precache.json)

self.addEventListener("install", (e) => {
    e.waitUntil(caches.open(CACHE).then((c) => c.addAll(["/"])));
    self.skipWaiting();
});

self.addEventListener("activate", (e) => {
    e.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Stale-while-revalidate: sirve de caché y actualiza en segundo plano
self.addEventListener("fetch", (e) => {
    const url = new URL(e.request.url);
    if (e.request.method !== "GET" || url.origin !== location.origin) return;
    e.respondWith(
        caches.open(CACHE).then(async (cache) => {
            const cached = await cache.match(e.request);
            const network = fetch(e.request)
                .then((r) => {
                    if (r.ok) cache.put(e.request, r.clone());
                    return r;
                })
                .catch(() => cached);
            return cached || network;
        })
    );
});

self.addEventListener("message", async (e) => {
    if (e.data?.type !== "PRECACHE") return;
    const { urls, version } = await (await fetch("/precache.json")).json();
    const cache = await caches.open(version);
    await cache.addAll(urls);
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== version).map((k) => caches.delete(k)));
});
