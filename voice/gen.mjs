// Озвучка через ElevenLabs. Запускается вручную в GitHub Actions («Озвучка» → Run workflow).
// Делает mp3 только для новых строк из voice/list.json и обновляет voice/index.json.
import fs from 'node:fs'; import crypto from 'node:crypto';
const KEY = process.env.ELEVENLABS_API_KEY;
if(!KEY){ console.log('Секрет ELEVENLABS_API_KEY ещё не добавлен — озвучку пропускаю.'); process.exit(0); }
const cfg = JSON.parse(fs.readFileSync('voice/config.json','utf8'));
const list = JSON.parse(fs.readFileSync('voice/list.json','utf8')).items;
const idxPath = 'voice/index.json';
const index = fs.existsSync(idxPath) ? JSON.parse(fs.readFileSync(idxPath,'utf8')) : {};
const only = (process.env.ONLY||'').trim();
const limit = +(process.env.LIMIT||0) || Infinity;          // сколько новых файлов сделать за запуск
fs.mkdirSync('voice/files', {recursive:true});
let made=0, skipped=0, failed=0, chars=0;
index.__parts = index.__parts || {};
for(const it of list){ if(it.parts){ index.__parts[it.key] = it.parts; } }
for(const it of list){
  if(it.parts) continue;
  if(made>=limit) break;
  const voice = cfg.voices[it.lang], model = it.model || cfg.models[it.lang], st = it.settings || cfg.settings[it.lang];
  if(!voice){ skipped++; continue; }
  const h = crypto.createHash('sha1').update([it.lang,voice,model,it.text,JSON.stringify(st)].join('|')).digest('hex').slice(0,16);
  const file = `voice/files/${h}.mp3`;
  if(only ? only!==it.key : (fs.existsSync(file) && index[it.key]===file)){ skipped++; continue; }
  const body = { text: it.text, model_id: model, voice_settings: st };
  if(/flash|turbo/.test(model)) body.language_code = it.lang;
  const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}?output_format=mp3_44100_64`, {
    method:'POST', headers:{'xi-api-key':KEY,'content-type':'application/json','accept':'audio/mpeg'}, body: JSON.stringify(body) });
  if(!r.ok){ const t=(await r.text()).slice(0,300); console.log('Ошибка', r.status, it.key, t); failed++;
    if(r.status===401 || /quota|credit|limit/i.test(t)){ console.log('Стоп: нет доступа или закончились символы.'); break; } continue; }
  fs.writeFileSync(file, Buffer.from(await r.arrayBuffer()));
  const cost = +(r.headers.get('character-cost') || r.headers.get('x-character-count') || 0); chars += cost;
  index[it.key] = file; made++;
  console.log('ok', it.lang, cost||'', it.key.slice(0,60), '→', file);
}
fs.writeFileSync(idxPath, JSON.stringify(index));
console.log(`Готово: новых ${made}, пропущено ${skipped}, ошибок ${failed}, списано символов (по ответу сервиса): ${chars||'нет данных'}`);
if(failed && !made) process.exit(1);
