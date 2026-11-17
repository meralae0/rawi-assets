import re,json,subprocess,difflib,glob
norm=lambda w: re.sub(r'[ً-ْـ\W]','',w).replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ة','ه').replace('ى','ي')
lines=[l.strip() for l in open('narration.txt',encoding='utf-8').read().split('\n') if l.strip() and not l.startswith('##')]
cl=[]
for l in lines:
    for c in re.split(r'(?<=[\.\?؟،:…!])\s+',l):
        if c.strip(): cl.append(c.strip())
SW=[];own=[]
for k,c in enumerate(cl):
    for w in c.split():
        if norm(w): SW.append(norm(w)); own.append(k)
ch=json.load(open('chunks.json'))
A=[]
for n,off,d in ch:
    try: s=open(f'asr{n}.txt',encoding='utf-8').read().strip()
    except FileNotFoundError: continue
    for it in s.split(';'):
        t,w=it.split('|',1)
        if norm(w): A.append((float(t)+off,norm(w)))
# DP alignment
N,M=len(SW),len(A); INF=1e9
sim=lambda a,b: difflib.SequenceMatcher(None,a,b).ratio()
D=[[INF]*(M+1) for _ in range(N+1)]; B=[[0]*(M+1) for _ in range(N+1)]
for i in range(N+1): D[i][0]=i*0.6
for j in range(M+1): D[0][j]=j*0.6
for i in range(1,N+1):
    for j in range(max(1,int(j0:=0)),M+1):
        s=sim(SW[i-1],A[j-1][1]); c=D[i-1][j-1]+(1-s)*1.5
        if c<D[i][j]: D[i][j]=c;B[i][j]=0
        if D[i-1][j]+0.6<D[i][j]: D[i][j]=D[i-1][j]+0.6;B[i][j]=1
        if D[i][j-1]+0.6<D[i][j]: D[i][j]=D[i][j-1]+0.6;B[i][j]=2
i,j=N,M; wt=[None]*N
while i>0 and j>0:
    b=B[i][j]
    if b==0:
        if sim(SW[i-1],A[j-1][1])>0.45: wt[i-1]=A[j-1][0]
        i-=1;j-=1
    elif b==1: i-=1
    else: j-=1
def sil(f,d):
    o=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af',f'silencedetect=noise=-35dB:d={d}','-f','null','-'],capture_output=True,text=True).stderr
    return [float(x) for x in re.findall(r'silence_end: ([\d\.]+)',o)],[float(x) for x in re.findall(r'silence_start: ([\d\.]+)',o)]
ends,starts=sil('voice.wav',0.06)
total=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','voice.wav']))
cs=[]
for k in range(len(cl)):
    ws=[wt[i] for i in range(N) if own[i]==k and wt[i] is not None]
    fi=[i for i in range(N) if own[i]==k][0]
    t=wt[fi] if wt[fi] is not None else None
    cs.append(t)
# interpolate missing by char count
known=[(k,t) for k,t in enumerate(cs) if t is not None]
for k in range(len(cs)):
    if cs[k] is None:
        p=max([x for x in known if x[0]<k],default=(0,0.0)); q=min([x for x in known if x[0]>k],default=(len(cs),total))
        L=[len(norm(c)) for c in cl]; a=sum(L[p[0]:k]); b=sum(L[p[0]:q[0]]) or 1
        cs[k]=p[1]+(q[1]-p[1])*a/b; print('interp',k,cl[k][:30])
# snap to nearest preceding/near silence end
out=[]
for k,t in enumerate(cs):
    near=[e for e in ends if abs(e-t)<0.45]
    if near: t=min(near,key=lambda e:abs(e-t))
    out.append(round(max(0,t-0.05),2))
res=[[out[k],out[k+1] if k+1<len(out) else round(total,2),cl[k]] for k in range(len(cl))]
for k in range(1,len(res)):
    if res[k][0]<=res[k-1][0]: print('WARN order',k,res[k])
json.dump(res,open('clauses.json','w'),ensure_ascii=False,indent=0)
print(len(res),'missing words',sum(1 for x in wt if x is None),'/',N)
# per-clause word start times (interpolated where missing)
W=[]
for k in range(len(cl)):
    idx=[i for i in range(N) if own[i]==k]; a=res[k][0]; b=res[k][1]
    ts_=[wt[i] for i in idx]; ts_[0]=a
    for j in range(len(ts_)):
        if ts_[j] is None or not (a-0.01<=ts_[j]<b):
            nxt=next((ts_[m] for m in range(j+1,len(ts_)) if ts_[m] is not None and a<=ts_[m]<b),b)
            prv=ts_[j-1]; ts_[j]=prv+(nxt-prv)/2 if nxt>prv else prv+0.1
        ts_[j]=max(ts_[j],ts_[j-1]+0.08) if j else ts_[j]
    W.append([round(x,2) for x in ts_])
json.dump(W,open('words.json','w'))
