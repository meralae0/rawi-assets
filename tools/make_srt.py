import json,sys
sys.path.insert(0,'.')
from translations import EN,FR
cl=json.load(open('clauses.json',encoding='utf-8'))
assert len(cl)==len(EN)==len(FR), (len(cl),len(EN),len(FR))
LEAD=0.6
def ts(x):
    ms=int(round(x*1000)); h=ms//3600000; m=ms%3600000//60000; s=ms%60000//1000; k=ms%1000
    return f"{h:02d}:{m:02d}:{s:02d},{k:03d}"
def merge(texts, minlen=1.2, maxlen=6.0):
    out=[]; buf=[]; start=None
    for i,((a,b,_),t) in enumerate(zip(cl,texts)):
        if start is None: start=a
        buf.append(t)
        end=b
        nxt_gap = (cl[i+1][0]-b) if i+1<len(cl) else 9
        if (end-start)>=minlen and (end-start)>=1.2 or nxt_gap>0.4 or i==len(cl)-1 or (end-start)>maxlen:
            out.append((start,end,' '.join(buf))); buf=[]; start=None
    return out
for lang,texts in (('ar',[c[2] for c in cl]),('en',EN),('fr',FR)):
    segs=merge(texts)
    with open(f'subs_{lang}.srt','w',encoding='utf-8') as f:
        for n,(a,b,t) in enumerate(segs,1):
            f.write(f"{n}\n{ts(a+LEAD)} --> {ts(b+LEAD)}\n{t}\n\n")
    print(lang,len(segs))
