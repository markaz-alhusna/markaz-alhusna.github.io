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
  for(const s of job.scenes){
    const refs = ['videogen/ref/style1.jpg'];
    if(fs.existsSync(`${out}/s1.png`) && s.id!=='s1') refs.push(`${out}/s1.png`);
    const text = `Create one image.\nSTYLE: ${job.style}\nCHARACTERS (keep exactly the same clothes in every scene): ${job.characters}\nSCENE: ${s.prompt}\n` +
      `The first attached image is ONLY a style reference (look, light, faceless shadow faces) — do not copy its scene or people.` +
      (refs.length>1 ? ` The second attached image shows the same two boys in this film — keep their clothes and look identical.` : '');
    const tries = model ? [model] : job.image_models;
    for(const m of tries){
      try{ const buf = await genImage(m, text, refs); fs.writeFileSync(`${out}/${s.id}.png`, buf); model = m; say('ok', s.id, m); break; }
      catch(e){ say('ошибка', s.id, m, e.message); }
    }
  }
}
const u1 = await balance('после');
say(`Этот запуск стоил примерно: $${(u1-u0).toFixed(4)}`);
fs.writeFileSync(`${out}/log.txt`, log.join('\n'));
