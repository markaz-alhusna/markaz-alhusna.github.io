# Склеивает фразы с салаватом (ﷺ) в одну плавную запись: русская часть и арабский салават идут подряд, без обрыва.
import json,subprocess,numpy as np,hashlib,os
R='/home/claude/markaz-alhusna.github.io/'
L=json.load(open(R+'voice/list.json'))['items']; ix=json.load(open(R+'voice/index.json'))
SR=44100; W=int(SR*0.01)
def load(f):
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',R+f,'-f','s16le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768; n=len(a)//W
    db=20*np.log10(np.sqrt((a[:n*W].reshape(n,W)**2).mean(1))+1e-9); on=np.where(db>-40)[0]
    a=a[max(0,on[0]*W-int(SR*.02)):min(len(a),(on[-1]+1)*W+int(SR*.06))].copy()
    f=int(SR*.012); a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f); return a
n=0
for it in L:
    ps=it.get('parts')
    if not ps or not any(p=='ar:صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ' for p in ps): continue
    keys=[p[3:] if p.startswith('ar:') else p for p in ps]
    if not all(k in ix for k in keys): continue
    segs=[]; gap=np.zeros(int(SR*.09),np.float32)
    for k in keys: segs+= [load(ix[k]),gap]
    b=np.concatenate(segs+[np.zeros(int(SR*.1),np.float32)])
    out='voice/files/m-'+hashlib.md5(('|'.join(ix[k] for k in keys)).encode()).hexdigest()[:12]+'.mp3'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-f','s16le','-ar',str(SR),'-ac','1','-i','-','-b:a','64k',R+out],input=(np.clip(b,-1,1)*32767).astype(np.int16).tobytes(),check=True)
    ix[it['key']]=out; ix.get('__parts',{}).pop(it['key'],None); n+=1
json.dump(ix,open(R+'voice/index.json','w'),ensure_ascii=False,indent=1); print('merged',n)
