# Склеивает фразы с салаватом (ﷺ) в одну плавную запись: русская часть и арабский салават идут подряд, без обрыва.
# python3 voice/merge.py rodoslov — склеить все составные фразы этапа (например, где имена читает арабский голос).
import json,subprocess,numpy as np,hashlib,os,sys
STAGE=sys.argv[1] if len(sys.argv)>1 else None
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
    if not ps: continue
    if STAGE: 
        if it.get('stage')!=STAGE: continue
    elif not any(p=='ar:صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ' for p in ps): continue
    keys=[p[3:] if p.startswith('ar:') else p for p in ps]
    if not all(k in ix for k in keys): continue
    segs=[]
    for j,k in enumerate(keys):
        segs.append(load(ix[k]))
        if j+1<len(keys):   # пауза: между предложениями длиннее, внутри — короткая
            nx=keys[j+1]; end=(it['key'].split(k,1)+[''])[1][:3] if not ps[j].startswith('ar:') else ''
            long = nx[:1].isupper() and not ps[j+1].startswith('ar:') or any(ch in end for ch in '.!?')
            segs.append(np.zeros(int(SR*(.34 if long else .1)),np.float32))
    b=np.concatenate(segs+[np.zeros(int(SR*.1),np.float32)])
    out='voice/files/m-'+hashlib.md5(('|'.join(ix[k] for k in keys)).encode()).hexdigest()[:12]+'.mp3'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-f','s16le','-ar',str(SR),'-ac','1','-i','-','-b:a','64k',R+out],input=(np.clip(b,-1,1)*32767).astype(np.int16).tobytes(),check=True)
    ix[it['key']]=out; ix.get('__parts',{}).pop(it['key'],None); n+=1
json.dump(ix,open(R+'voice/index.json','w'),ensure_ascii=False,indent=1); print('merged',n)
