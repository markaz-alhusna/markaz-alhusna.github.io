# Убирает хвост тишины и щелчок в конце русских записей, мягкое затухание. Запускать после озвучки (Claude делает это сам).
import json,subprocess,numpy as np,sys,os
R='/home/claude/markaz-alhusna.github.io/'
L=json.load(open(R+'voice/list.json'))['items']; ix=json.load(open(R+'voice/index.json'))
done=set(json.load(open(R+'voice/trimmed.json'))) if os.path.exists(R+'voice/trimmed.json') else set()
ru=sorted({ix[i['key']] for i in L if i.get('lang')=='ru' and i['key'] in ix} - done)
SR=44100; W=int(SR*0.02); stats=[]
for f in ru:
    p=R+f
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',p,'-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768
    n=len(a)//W
    if n<5: continue
    db=20*np.log10(np.sqrt((a[:n*W].reshape(n,W)**2).mean(1))+1e-9)
    loud=np.where(db>-38)[0]
    if not len(loud): continue
    end=min(len(a),(loud[-1]+1)*W+int(SR*0.15))
    b=a[:end].copy(); fl=int(SR*0.08); b[-fl:]*=np.linspace(1,0,fl)**2
    b=np.concatenate([b,np.zeros(int(SR*0.12),np.float32)])
    stats.append((len(a)-end)/SR)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-f','s16le','-ar',str(SR),'-ac','1','-i','-','-b:a','64k',p],input=(b*32767).astype(np.int16).tobytes(),check=True)
json.dump(sorted(done|set(ru)),open(R+'voice/trimmed.json','w'),indent=0)
s=np.array(stats or [0]); print(len(s),'trimmed mean',s.mean().round(3),'max',s.max().round(2))
