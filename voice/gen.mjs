// Озвучка через ElevenLabs. Запускается вручную в GitHub Actions («Озвучка» → Run workflow).
// Делает mp3 только для новых строк из voice/list.json и обновляет voice/index.json.
import fs from 'node:fs'; import crypto from 'node:crypto'; import { execFileSync } from 'node:child_process';
const KEY = process.env.ELEVENLABS_API_KEY;
if(!KEY){ console.log('Секрет ELEVENLABS_API_KEY ещё не добавлен — озвучку пропускаю.'); process.exit(0); }
const cfg = JSON.parse(fs.readFileSync('voice/config.json','utf8'));
const list = JSON.parse(fs.readFileSync('voice/list.json','utf8')).items;
const idxPath = 'voice/index.json';
const index = fs.existsSync(idxPath) ? JSON.parse(fs.readFileSync(idxPath,'utf8')) : {};
const only = (process.env.ONLY||'').trim();
const limit = +(process.env.LIMIT||0) || Infinity;
const stages = (process.env.STAGES||'').split(',').map(x=>x.trim()).filter(Boolean);   // какие этапы озвучивать          // сколько новых файлов сделать за запуск
fs.mkdirSync('voice/files', {recursive:true});
let made=0, skipped=0, failed=0, chars=0;
index.__parts = index.__parts || {};
for(const it of list){ if(it.parts){ index.__parts[it.key] = it.parts; } }
for(const it of list){
  if(it.parts) continue;
  if(stages.length && !stages.includes(it.stage)) continue;
  if(made>=limit) break;
  const voice = cfg.voices[it.lang], model = it.model || cfg.models[it.lang], st = it.settings || cfg.settings[it.lang];
  if(!voice){ skipped++; continue; }
  const h = crypto.createHash('sha1').update([it.lang,voice,model,it.text,JSON.stringify(st),it.keepvowel?'kv2':''].join('|')).digest('hex').slice(0,16);
  const file = `voice/files/${h}.mp3`;
  if(only ? only!==it.key : (fs.existsSync(file) && index[it.key]===file)){ skipped++; continue; }
  const body = { text: it.text, model_id: model, voice_settings: st };
  if(/flash|turbo/.test(model)) body.language_code = it.lang;
  // Последнюю огласовку модель «съедает», как при остановке. Поэтому после слова добавляем ещё одно,
  // а потом по меткам времени обрезаем звук ровно после нашего слова.
  const kv = it.keepvowel;
  if(kv) body.text = it.text + ' وَهُوَ';
  const url = `https://api.elevenlabs.io/v1/text-to-speech/${voice}${kv?'/with-timestamps':''}?output_format=mp3_44100_64`;
  const r = await fetch(url, { method:'POST', headers:{'xi-api-key':KEY,'content-type':'application/json','accept':kv?'application/json':'audio/mpeg'}, body: JSON.stringify(body) });
  if(!r.ok){ const t=(await r.text()).slice(0,300); console.log('Ошибка', r.status, it.key, t); failed++;
    if(r.status===401 || /quota|credit|limit/i.test(t)){ console.log('Стоп: нет доступа или закончились символы.'); break; } continue; }
  const cost = +(r.headers.get('character-cost') || r.headers.get('x-character-count') || 0); chars += cost;
  if(kv){
    const j = await r.json(); const al = j.alignment || j.normalized_alignment;
    const tmp = 'voice/tmp.mp3'; fs.writeFileSync(tmp, Buffer.from(j.audio_base64, 'base64'));
    let end = al && al.character_end_times_seconds ? al.character_end_times_seconds[Math.min(it.text.length-1, al.character_end_times_seconds.length-1)] : null;
    if(end){ end = +end + 0.06;
      execFileSync('ffmpeg', ['-y','-loglevel','error','-i',tmp,'-t',String(end),'-af',`afade=t=out:st=${Math.max(0,end-0.08)}:d=0.08`,'-b:a','64k',file]);
      console.log('обрезано по', end.toFixed(2), 'с');
    } else { fs.copyFileSync(tmp, file); console.log('нет меток времени — без обрезки'); }
    fs.unlinkSync(tmp);
  } else fs.writeFileSync(file, Buffer.from(await r.arrayBuffer()));
  index[it.key] = file; made++;
  console.log('ok', it.lang, cost||'', it.key.slice(0,60), '→', file);
}
fs.writeFileSync(idxPath, JSON.stringify(index));
console.log(`Готово: новых ${made}, пропущено ${skipped}, ошибок ${failed}, списано символов (по ответу сервиса): ${chars||'нет данных'}`);
if(failed && !made) process.exit(1);
