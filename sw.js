// LOM TV Service Worker — minimāls, lai iespējotu PWA instalāciju
const CACHE_NAME = 'lom-tv-v2';

// Install — kešo galveno lapu
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll([
      './',
      './index.html',
      './manifest.json'
    ]))
  );
  self.skipWaiting();
});

// Activate — notīra vecās keša versijas
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch — network-first stratēģija (vienmēr mēģina tīklu, ja nav — keša)
self.addEventListener('fetch', (e) => {
  // Nepārtver YouTube, Google Sheets, Google Fonts pieprasījumus
  if (e.request.url.includes('youtube.com') ||
      e.request.url.includes('ytimg.com') ||
      e.request.url.includes('googlevideo.com') ||
      e.request.url.includes('googleapis.com') ||
      e.request.url.includes('google.com') ||
      e.request.url.includes('gstatic.com')) {
    return;
  }
  e.respondWith(
    fetch(e.request).then(res => {
      // Kešo veiksmīgus GET pieprasījumus
      if (res.ok && e.request.method === 'GET') {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
      }
      return res;
    }).catch(() => caches.match(e.request))
  );
});
