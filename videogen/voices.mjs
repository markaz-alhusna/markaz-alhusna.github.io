// Голоса ElevenLabs для диалога. stage voices-search: ищем детские мужские голоса и делаем короткие пробы.
// stage voices: озвучиваем все реплики выбранными голосами.
import fs from 'node:fs';
const KEY = process.env.ELEVENLABS_API_KEY; if(!KEY){ console.log('нет ELEVENLABS_API_KEY'); process.exit(1); }
const job = JSON.parse(fs.readFileSync('videogen/job.json','utf8'));
const out = `videogen/out/run${job.run}`; fs.mkdirSync(out,{recursive:true});
const _f=globalThis.fetch; const fetch=async (u,o={})=>{ for(let k=0;k<2;k++){ try{ return await _f(u,{...o, signal:AbortSignal.timeout(120000)}); }catch(e){ console.log('сеть:', String(u).slice(0,60), e.cause?.code||e.name); } } return {ok:false,status:0,text:async()=>'timeout',json:async()=>({})}; };
const H = {'xi-api-key':KEY,'content-type':'application/json'}; const E='https://api.elevenlabs.io/v1';
const log=[]; const say=(...a)=>{const s=a.join(' ');console.log(s);log.push(s);};
async function tts(voice, text, file){
  const r = await fetch(`${E}/text-to-speech/${voice}?output_format=mp3_44100_128`,{method:'POST',headers:H,body:JSON.stringify({text, model_id: job.voices?.model||'eleven_v3', voice_settings:{stability:0.5, similarity_boost:0.8}})});
  if(!r.ok){ say('tts ошибка', r.status, (await r.text()).slice(0,300)); return false; }
  fs.writeFileSync(file, Buffer.from(await r.arrayBuffer())); return true;
}
if(job.stage==='voices-try'){
  for(const [n,v] of job.voices.try.entries()){
    const add = await fetch(`${E}/voices/add/${v.owner}/${v.id}`,{method:'POST',headers:H,body:JSON.stringify({new_name:'kid-'+v.name})});
    const at = await add.text(); let vid=v.id; try{ vid = JSON.parse(at).voice_id||vid; }catch{}
    say('добавлен', v.name, add.status, vid);
    if(await tts(vid, job.voices.sample, `${out}/try-${n}-${v.name}.mp3`)) say('проба', n, vid, v.name);
  }
}
if(job.stage==='voices-search'){
  const seen = new Map();
  for(const q of ['boy','kid']){
    for(const extra of ['']){
      let r; try{ r = await fetch(`${E}/shared-voices?page_size=30&gender=male&search=${encodeURIComponent(q)}${extra}`,{headers:H}); }catch(e){ say('поиск таймаут', q, extra); continue; }
      if(!r.ok){ say('поиск', q, r.status, (await r.text()).slice(0,200)); continue; }
      const j = await r.json();
      for(const v of j.voices||[]){ const d=(v.name+' '+(v.description||'')+' '+(v.descriptive||'')+' '+(v.use_case||'')).toLowerCase();
        if(/boy|kid|child|young/.test(d) && !seen.has(v.voice_id)) seen.set(v.voice_id, v); }
    }
  }
  const list=[...seen.values()].sort((a,b)=>(b.usage_character_count_1y||0)-(a.usage_character_count_1y||0));
  fs.writeFileSync(`${out}/candidates.json`, JSON.stringify(list.map(v=>({id:v.voice_id, owner:v.public_owner_id, name:v.name, age:v.age, lang:v.language, accent:v.accent, desc:(v.description||'').slice(0,200), use:v.usage_character_count_1y, verified:v.verified_languages?.map(x=>x.language)})),null,1));
  say('кандидатов', list.length);
  // пробуем добавить и озвучить пробу первых N
  let n=0;
  for(const v of list){ if(n>=job.voices.samples) break;
    const add = await fetch(`${E}/voices/add/${v.public_owner_id}/${v.voice_id}`,{method:'POST',headers:H,body:JSON.stringify({new_name:'kid-'+v.name.slice(0,30)})});
    const at = await add.text(); let vid=v.voice_id; try{ vid = JSON.parse(at).voice_id||vid; }catch{}
    if(!add.ok) say('добавить не вышло', v.name, add.status, at.slice(0,200));
    if(await tts(vid, job.voices.sample, `${out}/cand-${n}.mp3`)){ say('проба', n, vid, v.name); fs.appendFileSync(`${out}/samples.txt`, `${n}\t${vid}\t${v.name}\t${v.age}\t${v.language}\n`); n++; }
  }
}
if(job.stage==='voices'){
  for(const [i,l] of job.voices.lines.entries()){
    const f = `${out}/line${String(i).padStart(2,'0')}.mp3`;
    if(await tts(job.voices.ids[l.who], l.text, f)) say('ok', i, l.who);
  }
}
try{ const r=await fetch(`${E}/user/subscription`,{headers:H}); const j=await r.json(); say(`символов использовано ${j.character_count} из ${j.character_limit}`);}catch{}
fs.writeFileSync(`${out}/log.txt`, log.join('\n'));
process.on('exit',()=>fs.writeFileSync(`${out}/log.txt`, log.join('\n')));
