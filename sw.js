/* AL-HUSNA: приложение на телефоне. Страницу всегда берём свежую из сети
   (чтобы правки появлялись сразу), картинки и озвучку — из памяти телефона. */
const CACHE = 'alh-v1';
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil((async()=>{
  for(const k of await caches.keys()) if(k!==CACHE) await caches.delete(k);
  await self.clients.claim(); })()); });
self.addEventListener('fetch', e => {
  const req = e.request; const url = new URL(req.url);
  if(req.method!=='GET' || url.origin!==location.origin) return;          // Supabase и прочее — мимо
  const asset = /\.(webp|png|mp3|woff2?)$/i.test(url.pathname);
  if(asset){
    e.respondWith(caches.open(CACHE).then(async c => { const hit = await c.match(req); if(hit) return hit;
      const r = await fetch(req); if(r.ok) c.put(req, r.clone()); return r; }));
  } else {
    e.respondWith(fetch(req).then(r => { if(r.ok && (req.mode==='navigate')){ const cp=r.clone(); caches.open(CACHE).then(c=>c.put('./', cp)); } return r; })
      .catch(async () => (await caches.match(req)) || (req.mode==='navigate' ? caches.match('./') : Response.error())));
  }
});
