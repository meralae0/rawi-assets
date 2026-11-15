import re,subprocess,json,statistics
txt=open('narration.txt',encoding='utf-8').read()
cl=[c.strip() for c in re.split(r'(?<=[\.\?؟،:])\s+|(?<=\.\.\.)\s+|\n',txt) if c.strip()]
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','voice.wav']).decode())
def segs(D,noise=-35):
    o=subprocess.run(['ffmpeg','-hide_banner','-i','voice.wav','-af',f'silencedetect=noise={noise}dB:d={D}','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d\.]+)',o)]; en=[float(x) for x in re.findall(r'silence_end: ([\d\.]+)',o)]
    s=[];p=0.0
    for a,b in zip(st,en):
        if a>p+0.05: s.append((p,a))
        p=b
    if dur>p+0.05: s.append((p,dur))
    return s
F=segs(0.06)
W=[0.0,0.8,3.4,5.0,7.8,9.6,10.9,13.0,13.6,15.6,18.7,20.2,21.5,23.9,27.8,29.1,30.1,31.1,32.8,36.7,38.3,39.9,41.8,44.7,47.6,49.4,51.2,52.8,54.1,55.6,57.3,61.3,64.9,67.5,70.9,71.8,72.6,76.6,79.6,81.9,84.7,85.9,87.3,None,None,None,102.0,105.3,108.8,110.5,113.1,114.9,117.0,119.6,121.1,122.7,124.4,129.9,132.3,134.7,136.7,138.9,140.3,141.8]
assert len(W)==len(cl)==64,(len(W),len(cl))
starts_seg=[a for a,b in F]
diffs=[]
for w in W:
    if w is None: continue
    n=min(starts_seg,key=lambda x:abs(x-w))
    if abs(n-w)<1.0: diffs.append(n-w)
bias=statistics.median(diffs); print('bias',round(bias,2),'n',len(diffs))
st=[]
for w in W:
    if w is None: st.append(None); continue
    t=w+bias; n=min(starts_seg,key=lambda x:abs(x-t))
    st.append(n if abs(n-t)<0.5 else round(t,2))
# fill gap 43-45 with speech segments between st[42] end region and st[46]
lo,hi=st[42],st[46]
inner=[a for a,b in F if lo+0.5<a<hi-0.2]
strip=lambda t: re.sub(r'[ً-ْٰ\s\.\،\?؟:!"«»…,]','',t)
L=[len(strip(cl[i])) for i in range(42,46)]
tot=hi-lo; cum=lo; targets=[]
for l in L[:-1]:
    cum+=tot*l/sum(L); targets.append(cum)
for k,tg in zip((43,44,45),targets):
    st[k]=min(inner,key=lambda x:abs(x-tg)) if inner else round(tg,2)
st[0]=F[0][0]
res=[]
for i in range(64):
    a=st[i]; nxt=st[i+1] if i<63 else dur
    ends=[b for (x,b) in F if x<nxt-0.05 and b>a]
    e=min(max(ends) if ends else nxt, nxt)
    res.append([round(a,2),round(e,2),cl[i]])
ok=all(res[i][0]<res[i][1]<=res[i+1][0]+0.01 for i in range(63))
print('ok',ok)
for i in range(63):
    if not(res[i][0]<res[i][1]<=res[i+1][0]+0.01): print('BAD',i,res[i][:2],res[i+1][:2])
json.dump(res,open('clauses.json','w'),ensure_ascii=False,indent=0)
for i in (40,41,42,43,44,45,46): print(i,res[i][:2],res[i][2][:30])
