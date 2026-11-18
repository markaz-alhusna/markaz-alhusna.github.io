// Восстанавливает уже озвученные файлы из истории ElevenLabs (бесплатно), если сохранение в GitHub не прошло.
import fs from 'node:fs'; import crypto from 'node:crypto';
const KEY = process.env.ELEVENLABS_API_KEY; const stages = (process.env.STAGES||'').split(',').map(x=>x.trim()).filter(Boolean);
const cfg = JSON.parse(fs.readFileSync('voice/config.json','utf8'));
const list = JSON.parse(fs.readFileSync('voice/list.json','utf8')).items;
const idxPath='voice/index.json'; const index = JSON.parse(fs.readFileSync(idxPath,'utf8'));
const norm = t => String(t||'').replace(/\[[^\]]*\]/g,'').replace(/\u0301/g,'').replace(/\s+/g,' ').trim();
const want = new Map();
for(const it of list){ if(it.parts || it.keepvowel) continue; if(stages.length && !stages.includes(it.stage)) continue;
  const voice=cfg.voices[it.lang], model=it.model||cfg.models[it.lang], st=it.settings||cfg.settings[it.lang];
  const h = crypto.createHash('sha1').update([it.lang,voice,model,it.text,JSON.stringify(st),it.keepvowel?'kv2':''].join('|')).digest('hex').slice(0,16);
  const file=`voice/files/${h}.mp3`; if(fs.existsSync(file)){ index[it.key]=file; continue; }
  want.set(voice+'|'+norm(it.text), {it,file}); }
console.log('нужно восстановить:', want.size);
let after=null, got=0, pages=0;
while(want.size && pages<40){ pages++;
  const u='https://api.elevenlabs.io/v1/history?page_size=1000'+(after?'&start_after_history_item_id='+after:'');
  const r=await fetch(u,{headers:{'xi-api-key':KEY}}); if(!r.ok){ console.log('history', r.status, (await r.text()).slice(0,200)); break; }
  const j=await r.json(); const hs=j.history||[]; if(pages===1) hs.slice(0,3).forEach(h=>console.log('пример истории:', h.voice_id, h.model_id, JSON.stringify(h.text).slice(0,80)));
  for(const h of hs){ const k=h.voice_id+'|'+norm(h.text); const w=want.get(k); if(!w) continue;
    const a=await fetch(`https://api.elevenlabs.io/v1/history/${h.history_item_id}/audio`,{headers:{'xi-api-key':KEY}});
    if(!a.ok){ console.log('audio', a.status); continue; }
    fs.writeFileSync(w.file, Buffer.from(await a.arrayBuffer())); index[w.it.key]=w.file; want.delete(k); got++; }
  if(!j.has_more || !hs.length) break; after=j.last_history_item_id; }
fs.writeFileSync(idxPath, JSON.stringify(index));
console.log('восстановлено', got, '— не найдено', want.size);
for(const [k] of want) console.log('  нет:', k.slice(0,80));
