import re,subprocess,json,sys
D=float(sys.argv[1]) if len(sys.argv)>1 else 0.15
txt=open('narration.txt',encoding='utf-8').read()
clauses=[c.strip() for c in re.split(r'(?<=[\.\?؟،:])\s+|(?<=\.\.\.)\s+|\n',txt) if c.strip()]
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','voice.wav']).decode())
out=subprocess.run(['ffmpeg','-hide_banner','-i','voice.wav','-af',f'silencedetect=noise=-35dB:d={D}','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d\.]+)',out)]; en=[float(x) for x in re.findall(r'silence_end: ([\d\.]+)',out)]
segs=[];prev=0.0
for s,e in zip(st,en):
    if s>prev+0.05: segs.append((prev,s))
    prev=e
if dur>prev+0.05: segs.append((prev,dur))
strip=lambda t: re.sub(r'[ً-ْٰ\s\.\،\?؟:!"«»…,]','',t)
C=[max(1,len(strip(c))) for c in clauses]
N,M=len(clauses),len(segs)
speech=sum(b-a for a,b in segs); rate=speech/sum(C)
INF=1e18
dp=[[INF]*(M+1) for _ in range(N+1)]; bk=[[0]*(M+1) for _ in range(N+1)]
dp[0][0]=0
for i in range(1,N+1):
    for j in range(i,M-(N-i)+1):
        for k in range(i-1,j):
            if dp[i-1][k]>=INF: continue
            sp=sum(b-a for a,b in segs[k:j])
            v=dp[i-1][k]+abs(sp-C[i-1]*rate)**2
            if v<dp[i][j]: dp[i][j]=v; bk[i][j]=k
j=M; bounds=[]
for i in range(N,0,-1):
    k=bk[i][j]; bounds.append((k,j)); j=k
bounds.reverse()
res=[(round(segs[k][0],2),round(segs[j-1][1],2),clauses[i]) for i,(k,j) in enumerate(bounds)]
# also store internal pauses (sub-segment starts) per clause for caption splitting
subs=[[round(s[0],2) for s in segs[k+1:j]] for (k,j) in bounds]
json.dump(res,open('clauses.json','w'),ensure_ascii=False,indent=0)
json.dump(subs,open('subpauses.json','w'))
print(f'D={D} segs={M} clauses={N} cost={dp[N][M]:.2f}')
