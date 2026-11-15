import re,subprocess,json
cl=[c[2] for c in json.load(open('c12.json',encoding='utf-8'))]
def segs_for(D):
    out=subprocess.run(['ffmpeg','-hide_banner','-i','voice.wav','-af',f'silencedetect=noise=-35dB:d={D}','-f','null','-'],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r'silence_start: ([\d\.]+)',out)]; en=[float(x) for x in re.findall(r'silence_end: ([\d\.]+)',out)]
    s=[];p=0.0
    for a,b in zip(st,en):
        if a>p+0.05: s.append((p,a))
        p=b
    s.append((p,149.52)); return s
S=segs_for(0.12); F=segs_for(0.06)
# whisper start of each clause (first word), from browser ASR; None = ASR gap
W=[0.0,3.46,4.54,6.04,7.44,8.78,10.40,12.34,14.04,15.62,17.98,21.26,23.50,27.22,28.08,31.40,34.94,37.12,38.02,40.50,
   43.32,45.42,47.18,49.80,51.98,53.34,55.28,56.64,59.20,61.22,62.84,64.98,67.16,72.42,75.14,76.72,77.34,78.96,81.88,87.92,
   None,None,None,None,None,None,None,None,None,None,118.9,119.86,120.76,122.54,124.06,125.52,126.80,128.96,130.86,133.92,136.0,
   140.14,141.86,144.46,145.88,146.84]
assert len(W)==66
c12=json.load(open('c12.json',encoding='utf-8'))
starts=[]
for i,w in enumerate(W):
    if w is None: starts.append(c12[i][0]); continue
    t=w+0.45
    cand=[a for a,b in F]
    near=min(cand,key=lambda x:abs(x-t))
    starts.append(near if abs(near-t)<0.6 else round(t,2))
# manual fixes from segment inspection
starts[50]=None   # 'وليس في منتصف الليل' is inside 116.16-119.84 with c49 -> place by ASR
starts[50]=118.9+0.45
starts[0]=F[0][0]
res=[]
for i in range(66):
    a=starts[i]; nxt=starts[i+1] if i<65 else 149.52
    # end = end of last speech piece starting before next start
    ends=[b for (x,b) in F if x<nxt-0.05 and b>a]
    e=min(max(ends) if ends else nxt, nxt)
    res.append((round(a,2),round(e,2),cl[i]))
mono=all(res[i][0]<res[i+1][0] for i in range(65))
json.dump(res,open('clauses.json','w'),ensure_ascii=False,indent=0)
print('monotonic',mono)
for i,(r,o) in enumerate(zip(res,json.load(open('clauses_old.json',encoding='utf-8')))):
    print(i,f'{r[0]:6.2f}-{r[1]:6.2f}  (old {o[0]:6.2f} {r[0]-o[0]:+.2f})',r[2][:30])
