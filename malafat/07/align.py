import re,subprocess,json,statistics,difflib,sys
txt='\n'.join(l for l in open('narration.txt',encoding='utf-8').read().split('\n') if not l.startswith('##'))
cl=[c.strip() for c in re.split(r'(?<=[\.\?؟،:…!])\s+|\n',txt) if c.strip()]
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','voice.wav']).decode())
def norm(w):
    w=re.sub(r'[ً-ْٰـ]','',w); w=re.sub(r'[^ء-ي0-9a-zA-Z]','',w)
    w=re.sub('[أإآ]','ا',w).replace('ة','ه').replace('ى','ي'); return w
asr=[l.split('|',1) for l in open('asr.txt',encoding='utf-8').read().split('\n') if '|' in l]
A=[(float(t),norm(w)) for t,w in asr for _ in [0] if norm(w)]
# expand multiword chunks
AA=[]
for t,w in [(float(t),w) for t,w in asr]:
    for x in w.split():
        if norm(x): AA.append((t,norm(x)))
toks=[];owner=[]
for i,c in enumerate(cl):
    for x in c.split():
        if norm(x): toks.append(norm(x)); owner.append(i)
sm=difflib.SequenceMatcher(None,toks,[w for t,w in AA],autojunk=False)
tmap={}
for a,b,n in sm.get_matching_blocks():
    for k in range(n): tmap[a+k]=AA[b+k][0]
# fuzzy single-token matches for replace blocks
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=='replace':
        for k in range(i1,i2):
            best=max(range(j1,j2),key=lambda j:difflib.SequenceMatcher(None,toks[k],AA[j][1]).ratio())
            if difflib.SequenceMatcher(None,toks[k],AA[best][1]).ratio()>0.6: tmap.setdefault(k,AA[best][0])
first=[owner.index(i) for i in range(len(cl))]
W=[tmap.get(f) for f in first]
print('matched clauses',sum(w is not None for w in W),'/',len(cl))
def segs(D,noise=-35):
    o=subprocess.run(['ffmpeg','-hide_banner','-i','voice.wav','-af',f'silencedetect=noise={noise}dB:d={D}','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d\.]+)',o)]; en=[float(x) for x in re.findall(r'silence_end: ([\d\.]+)',o)]
    s=[];p=0.0
    for a,b in zip(st,en):
        if a>p+0.05: s.append((p,a))
        p=b
    if dur>p+0.05: s.append((p,dur))
    return s
F=segs(0.06); S=[a for a,b in F]
diffs=[min(S,key=lambda x:abs(x-w))-w for w in W if w is not None and abs(min(S,key=lambda x:abs(x-w))-w)<1]
bias=statistics.median(diffs); print('bias',round(bias,2))
st=[]
for w in W:
    if w is None: st.append(None); continue
    t=w+bias; n=min(S,key=lambda x:abs(x-t)); st.append(n if abs(n-t)<0.5 else round(t,2))
st[0]=F[0][0]
# monotonic fix + interpolate gaps by char length
strip=lambda t: re.sub(r'[ً-ْ\s\.\،\?؟:!"«»…,]','',t)
for i in range(1,len(st)):
    if st[i] is not None and st[i-1] is not None and st[i]<=st[i-1]: st[i]=None
i=0
while i<len(st):
    if st[i] is None:
        j=i
        while j<len(st) and st[j] is None: j+=1
        lo=st[i-1]; hi=st[j] if j<len(st) else dur
        L=[len(strip(cl[k])) for k in range(i-1,j)]; cum=lo
        for k in range(i,j):
            cum+=(hi-lo)*L[k-i]/sum(L); n=min(S,key=lambda x:abs(x-cum)); st[k]=n if lo<n<hi else round(cum,2)
        i=j
    i+=1
res=[]
for i in range(len(cl)):
    a=st[i]; nxt=st[i+1] if i<len(cl)-1 else dur
    ends=[b for (x,b) in F if x<nxt-0.05 and b>a]; e=min(max(ends) if ends else nxt,nxt)
    res.append([round(a,2),round(e,2),cl[i]])
print('ok',all(res[i][0]<res[i][1]<=res[i+1][0]+0.01 for i in range(len(res)-1)))
json.dump(res,open('clauses.json','w'),ensure_ascii=False,indent=0)
for i,r in enumerate(res): print(i,r[0],r[1],r[2][:40])
