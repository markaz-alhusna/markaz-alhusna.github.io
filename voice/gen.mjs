// Озвучка через ElevenLabs. Запускается в GitHub Actions (ключ — в секретах репозитория).
// Делает mp3 только для новых строк из voice/list.json и обновляет voice/index.json.
import fs from 'node:fs'; import crypto from 'node:crypto';
const KEY = process.env.ELEVENLABS_API_KEY;
if(!KEY){ console.log('Секрет ELEVENLABS_API_KEY ещё не добавлен — озвучку пропускаю.'); process.exit(0); }
const cfg = JSON.parse(fs.readFileSync('voice/config.json','utf8'));
const list = JSON.parse(fs.readFileSync('voice/list.json','utf8')).items;
const idxPath = 'voice/index.json';
const index = fs.existsSync(idxPath) ? JSON.parse(fs.readFileSync(idxPath,'utf8')) : {};
const only = (process.env.ONLY||'').trim();          // можно переозвучить одну строку
fs.mkdirSync('voice/files', {recursive:true});
let made = 0, skipped = 0, failed = 0;
for(const it of list){
  const voice = cfg.voices[it.lang];
  if(!voice){ console.log('Нет голоса для языка', it.lang, '— пропускаю', it.key); skipped++; continue; }
  const h = crypto.createHash('sha1').update(it.lang+'|'+voice+'|'+it.text+'|'+JSON.stringify(cfg.settings)).digest('hex').slice(0,16);
  const file = `voice/files/${h}.mp3`;
  if(fs.existsSync(file) && index[it.key]===file && only!==it.key){ skipped++; continue; }
  if(only && only!==it.key){ skipped++; continue; }
  const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voice}?output_format=mp3_44100_64`, {
    method:'POST', headers:{'xi-api-key':KEY,'content-type':'application/json','accept':'audio/mpeg'},
    body: JSON.stringify({ text: it.text, model_id: cfg.model, language_code: it.lang, voice_settings: cfg.settings }) });
  if(!r.ok){ console.log('Ошибка', r.status, it.key, (await r.text()).slice(0,200)); failed++; if(r.status===401) break; continue; }
  fs.writeFileSync(file, Buffer.from(await r.arrayBuffer()));
  index[it.key] = file; made++;
  console.log('ok', it.key, '→', file);
}
fs.writeFileSync(idxPath, JSON.stringify(index, null, 0));
console.log(`Готово: новых ${made}, пропущено ${skipped}, ошибок ${failed}`);
if(failed && !made) process.exit(1);
