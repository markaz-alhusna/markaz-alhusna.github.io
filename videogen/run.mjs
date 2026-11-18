// Генерация видео через OpenRouter. Запускается в GitHub Actions при пуше в ветку video-work.
// Ключ только в GitHub Secrets (OPENROUTER_API_KEY). Результаты — в ветке video-out.
import fs from 'node:fs';
const KEY = process.env.OPENROUTER_API_KEY;
if(!KEY){ console.log('Нет секрета OPENROUTER_API_KEY — стоп.'); process.exit(1); }
const API = 'https://openrouter.ai/api/v1';
const H = { 'Authorization': `Bearer ${KEY}`, 'Content-Type': 'application/json', 'HTTP-Referer': 'https://markaz-alhusna.github.io', 'X-Title': 'AL-HUSNA' };
const job = JSON.parse(fs.readFileSync('videogen/job.json','utf8'));
const out = `videogen/out/run${job.run}`; fs.mkdirSync(out, {recursive:true});
const log = []; const say = (...a)=>{ const s=a.join(' '); console.log(s); log.push(s); };
const balance = async (label)=>{ try{ const r=await fetch(`${API}/key`,{headers:H}); const j=await r.json(); const d=j.data||{}; say(`[${label}] израсходовано всего: $${(+d.usage||0).toFixed(4)}; лимит ключа: ${d.limit??'нет'}; осталось по лимиту: ${d.limit_remaining??'—'}`); return +d.usage||0; }catch(e){ say('баланс не прочитан', e.message); return 0; } };
const u0 = await balance('до');

// Список моделей (бесплатно) — чтобы видеть, что доступно и почём
try{
  const r = await fetch(`${API}/models?output_modalities=image`,{headers:H}); const j = await r.json();
  fs.writeFileSync(`${out}/image-models.json`, JSON.stringify((j.data||[]).map(m=>({id:m.id, pricing:m.pricing})),null,1));
  const v = await fetch(`${API}/videos/models`,{headers:H}); fs.writeFileSync(`${out}/video-models.json`, await v.text());
}catch(e){ say('список моделей не получен', e.message); }

const dataUrl = p => `data:image/${p.endsWith('.png')?'png':'jpeg'};base64,${fs.readFileSync(p).toString('base64')}`;

async function genImage(model, text, refs){
  const content = [{type:'text', text}, ...refs.map(p=>({type:'image_url', image_url:{url:dataUrl(p)}}))];
  const r = await fetch(`${API}/chat/completions`, { method:'POST', headers:H, body: JSON.stringify({
    model, modalities:['image','text'], image_config:{aspect_ratio:'16:9'},
    messages:[{role:'user', content}] }) });
  const t = await r.text(); if(!r.ok) throw new Error(`${r.status} ${t.slice(0,300)}`);
  const j = JSON.parse(t); const img = j.choices?.[0]?.message?.images?.[0]?.image_url?.url;
  if(!img) throw new Error('нет картинки в ответе: '+t.slice(0,300));
  return Buffer.from(img.split(',')[1], 'base64');
}

if(job.stage==='images'){
  let model = null;
  const tryGen = async (id, text, refs)=>{
    for(const m of (model ? [model] : job.image_models)){
      try{ const buf = await genImage(m, text, refs); fs.writeFileSync(`${out}/${id}.png`, buf); model = m; say('ok', id, m); return true; }
      catch(e){ say('ошибка', id, m, e.message); }
    }
    return false;
  };
  const base = `STYLE: ${job.style}\nCHARACTERS (keep exactly the same clothes in every image): ${job.characters}\n`;
  if(job.sheet) await tryGen('sheet', `Create one image.\n${base}IMAGE: ${job.sheet}`, []);
  for(const s of job.scenes){
    const refs = fs.existsSync(`${out}/sheet.png`) ? [`${out}/sheet.png`] : [];
    const text = `Create one image.\n${base}SCENE: ${s.prompt}\n` + (refs.length ? 'The attached image is the character reference sheet: keep the boys and clothes identical, but use the camera angle and composition described in SCENE.' : '');
    await tryGen(s.id, text, refs);
  }
}

if(job.stage==='video'){
  const src = job.video.from;  // папка с картинками (например videogen/out/run2)
  for(const c of job.video.clips){
    const img = `${src}/${c.image}.png`;
    for(const v of job.video.models){
      const body = { model: v.model, prompt: c.prompt + ' ' + (job.video.common||''), resolution: v.resolution, aspect_ratio: '16:9', duration: v.duration, generate_audio: false,
        frame_images: [{ type:'image_url', image_url:{ url: dataUrl(img) }, frame_type:'first_frame' }] };
      if(v.provider) body.provider = v.provider;
      const r = await fetch(`${API}/videos`, { method:'POST', headers:H, body: JSON.stringify(body) });
      const t = await r.text(); if(!r.ok){ say('ошибка запуска', c.id, v.model, r.status, t.slice(0,300)); continue; }
      const jid = JSON.parse(t).id; say('запущено', c.id, v.model, jid);
      let st = null;
      for(let i=0;i<60;i++){ await new Promise(z=>setTimeout(z, 20000));
        const p = await fetch(`${API}/videos/${jid}`, {headers:H}); st = await p.json();
        if(['completed','failed','cancelled','expired'].includes(st.status)) break; }
      if(st?.status!=='completed'){ say('не получилось', c.id, v.model, st?.status, JSON.stringify(st?.error||'').slice(0,300)); continue; }
      const d = await fetch(`${API}/videos/${jid}/content?index=0`, {headers:H});
      fs.writeFileSync(`${out}/${c.id}.mp4`, Buffer.from(await d.arrayBuffer()));
      say('ok', c.id, v.model, 'стоимость', st.usage?.cost ?? '?'); break;
    }
  }
}

const u1 = await balance('после');
say(`Этот запуск стоил примерно: $${(u1-u0).toFixed(4)}`);
fs.writeFileSync(`${out}/log.txt`, log.join('\n'));
