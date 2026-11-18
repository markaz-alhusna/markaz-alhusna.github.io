import fs from 'node:fs';
const job = JSON.parse(fs.readFileSync('videogen/job.json','utf8')); const out=`videogen/out/run${job.run}`; fs.mkdirSync(out,{recursive:true});
const log=[]; const say=(...a)=>{const s=a.join(' ');console.log(s);log.push(s);};
const t=async(name,u,o={})=>{ const t0=Date.now(); try{ const r=await fetch(u,{...o,signal:AbortSignal.timeout(60000)}); const b=await r.text(); say(name, r.status, ((Date.now()-t0)/1000).toFixed(1)+'s', b.slice(0,1500).replace(/\s+/g,' ')); return b; }catch(e){ say(name,'ERR',((Date.now()-t0)/1000).toFixed(1)+'s',e.cause?.code||e.name); } };
const EH={'xi-api-key':process.env.ELEVENLABS_API_KEY||''};
await t('el-user', 'https://api.elevenlabs.io/v1/user/subscription',{headers:EH});
await t('el-voices', 'https://api.elevenlabs.io/v2/voices?page_size=5',{headers:EH});
await t('el-shared', 'https://api.elevenlabs.io/v1/shared-voices?page_size=3&search=boy',{headers:EH});
const OH={'Authorization':`Bearer ${process.env.OPENROUTER_API_KEY}`};
const b = await t('or-audio-models','https://openrouter.ai/api/v1/models?output_modalities=audio',{headers:OH});
try{ fs.writeFileSync(`${out}/audio-models.json`, JSON.stringify(JSON.parse(b).data.map(m=>({id:m.id,desc:(m.description||'').slice(0,300),pricing:m.pricing,params:m.supported_parameters})),null,1)); }catch{}
await t('or-speech-models','https://openrouter.ai/api/v1/audio/speech/models',{headers:OH});
fs.writeFileSync(`${out}/log.txt`, log.join('\n'));
