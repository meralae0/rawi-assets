import re,subprocess,json
txt=[l.strip() for l in open('narration.txt',encoding='utf-8').read().split('\n') if l.strip() and not l.startswith('##')]
strip=lambda t: re.sub(r'[ً-ْ\s\.\،\?؟:!"«»…,]','',t)
def sil(f,d):
    o=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af',f'silencedetect=noise=-35dB:d={d}','-f','null','-'],capture_output=True,text=True).stderr
    return list(zip([float(x) for x in re.findall(r'silence_start: ([\d\.]+)',o)],[float(x) for x in re.findall(r'silence_end: ([\d\.]+)',o)]))
dur=lambda f: float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f]))
parts=[('p0.wav',0,20),('p1.wav',20,37),('p2.wav',37,51)]
off=0; res=[]; LS=[]
for f,l0,l1 in parts:
    big=sil(f,0.35); small=sil(f,0.1); D=dur(f)
    first=small[0][1] if small and small[0][0]<0.05 else 0
    lastend=max([a for a,b in small if a>D-3] or [D])
    cand=[first]+[b for a,b in big if first+0.5<b<lastend-0.5]
    lines=txt[l0:l1]; L=[len(strip(l)) for l in lines]; N=len(L); M=len(cand)
    rate=sum(L)/(lastend-first)
    gap=dict((b,b-a) for a,b in big)
    INF=1e18; dp=[[INF]*M for _ in range(N)]; bk=[[-1]*M for _ in range(N)]; dp[0][0]=0
    for i in range(1,N):
        for j in range(1,M):
            for k in range(max(0,j-15),j):
                if dp[i-1][k]>=INF: continue
                spk=max(0.3,cand[j]-cand[k]-gap.get(cand[j],0.3))
                c=dp[i-1][k]+((L[i-1]/spk)/rate-1)**2*L[i-1]
                if c<dp[i][j]: dp[i][j]=c; bk[i][j]=k
    best=min(range(M),key=lambda j: dp[N-1][j]+(((L[-1]/max(0.3,lastend-cand[j]))/rate-1)**2*L[-1]) if dp[N-1][j]<INF else INF)
    idx=[0]*N;j=best
    for i in range(N-1,-1,-1): idx[i]=j; j=bk[i][j]
    ls=[cand[k] for k in idx]; le=ls[1:]+[lastend]
    rates=[L[i]/(le[i]-ls[i]) for i in range(N)]
    print(f,'M',M,'N',N,'rate',round(rate,1),'min/max',round(min(rates),1),round(max(rates),1))
    for i,l in enumerate(lines):
        cs=[c for c in re.split(r'(?<=[\.\?؟،:…!])\s+',l) if c.strip()]
        Lc=[max(1,len(strip(c))) for c in cs]; a=ls[i]; e=le[i]
        ends=[x for x,y in big if a<x<=e+0.01]; send=max(ends) if ends else e
        st=[a]
        for k in range(1,len(cs)):
            cum=a+(send-a)*sum(Lc[:k])/sum(Lc)
            near=[y for _,y in small if st[-1]+0.3<y<send-0.3]
            n=min(near,key=lambda x:abs(x-cum)) if near else cum
            st.append(n if abs(n-cum)<0.8 else cum)
        for k,c in enumerate(cs):
            res.append([round(st[k]+off,2),round((st[k+1] if k+1<len(cs) else send)+off,2),c])
    off+=D
json.dump(res,open('clauses.json','w'),ensure_ascii=False,indent=0); print(len(res))
