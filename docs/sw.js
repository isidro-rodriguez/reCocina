// Dos cachés: RUNTIME (fija) guarda lo visitado; la de precarga se llama como el
// `version` de precache.json (lo genera build_precache.py, prefijo "recocina-").
const PREFIX = "recocina-";
const RUNTIME = `${PREFIX}runtime`;
// Clave interna en RUNTIME con la precarga vigente: activate no puede pedirla a la red
const PRECACHE_KEY = "/__precache-version";

const removeStale = (keep) =>
    caches.keys().then((keys) =>
        Promise.all(
            keys
                .filter((k) => k.startsWith(PREFIX) && k !== RUNTIME && k !== keep)
                .map((k) => caches.delete(k))
        )
    );

self.addEventListener("install", (e) => {
    e.waitUntil(caches.open(RUNTIME).then((c) => c.addAll(["/", "/404.html"])));
    self.skipWaiting();
});

self.addEventListener("activate", (e) => {
    e.waitUntil(
        caches
            .open(RUNTIME)
            .then((c) => c.match(PRECACHE_KEY))
            .then((r) => (r ? r.text() : null))
            .then(removeStale)
    );
    self.clients.claim();
});

// Sin red ni copia hay que responder algo: respondWith(undefined) da error de red
const offline = async () =>
    (await caches.match("/404.html")) ||
    new Response("Sin conexión", {
        status: 503,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
    });

// Stale-while-revalidate: sirve de caché y actualiza en segundo plano
self.addEventListener("fetch", (e) => {
    const url = new URL(e.request.url);
    if (e.request.method !== "GET" || url.origin !== location.origin) return;
    e.respondWith(
        (async () => {
            const cached = await caches.match(e.request);
            const network = fetch(e.request)
                .then(async (r) => {
                    if (r.ok) {
                        const runtime = await caches.open(RUNTIME);
                        await runtime.put(e.request, r.clone());
                    }
                    return r;
                })
                .catch(() => cached || offline());
            return cached || network;
        })()
    );
});

self.addEventListener("message", (e) => {
    if (e.data?.type !== "PRECACHE") return;
    e.waitUntil(
        (async () => {
            const { urls, version } = await (await fetch("/precache.json")).json();
            const cache = await caches.open(version);
            await cache.addAll(urls);
            const runtime = await caches.open(RUNTIME);
            await runtime.put(PRECACHE_KEY, new Response(version));
            await removeStale(version);
        })()
    );
});
