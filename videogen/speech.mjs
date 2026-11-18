// Озвучка реплик через OpenRouter (openai/gpt-audio). Поток pcm16 24 кГц → wav.
import fs from 'node:fs'; import { execFileSync } from 'node:child_process';
const job = JSON.parse(fs.readFileSync('videogen/job.json','utf8')); const out=`videogen/out/run${job.run}`; fs.mkdirSync(out,{recursive:true});
const H={'Authorization':`Bearer ${process.env.OPENROUTER_API_KEY}`,'Content-Type':'application/json'};
const log=[]; const say=(...a)=>{const s=a.join(' ');console.log(s);log.push(s);};
const sp = job.speech;
async function speak(text, who, file){
  const c = sp.cast[who];
  const body = { model: sp.model, modalities:['text','audio'], audio:{voice:c.voice, format:'pcm16'}, stream:true,
    messages:[{role:'system', content: sp.system + ' VOICE: ' + c.style},{role:'user', content: 'Read this aloud exactly, nothing else:\n«' + text + '»'}] };
  const r = await fetch('https://openrouter.ai/api/v1/chat/completions',{method:'POST',headers:H,body:JSON.stringify(body),signal:AbortSignal.timeout(180000)});
  if(!r.ok){ say('ошибка', who, r.status, (await r.text()).slice(0,300)); return false; }
  const txt = await r.text(); const chunks=[]; let tr=''; let usage=null;
  for(const line of txt.split('\n')){ if(!line.startsWith('data: ')||line.includes('[DONE]')) continue;
    try{ const j=JSON.parse(line.slice(6)); const a=j.choices?.[0]?.delta?.audio; if(a?.data) chunks.push(Buffer.from(a.data,'base64')); if(a?.transcript) tr+=a.transcript; if(j.usage) usage=j.usage; }catch{} }
  if(!chunks.length){ say('нет звука', who, txt.slice(0,300)); return false; }
  const norm = x=>x.replace(/[\u064B-\u0652\u0670«»!?؟.,،:\s]/g,'').replace(/[أإآ]/g,'ا');
  const good = norm(tr)===norm(text);
  say(good?'ok':'НЕ ТО', file, who, '| прочитано:', tr.slice(0,120), '| cost', usage?.cost ?? '?');
  if(good) fs.writeFileSync(file, Buffer.concat(chunks)); return good;
}
for(const [i,l] of sp.lines.entries()){
  if(sp.only && !sp.only.includes(i)) continue;
  const f=`${out}/line${String(i).padStart(2,'0')}-${l.who}.pcm`;
  for(let k=0;k<4;k++){ if(await speak(l.text, l.who, f)) break; }
}
fs.writeFileSync(`${out}/log.txt`, log.join('\n'));
