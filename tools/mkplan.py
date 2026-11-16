import json,re,subprocess
cuts=[0]+[float(x) for x in open('cuts.txt').read().split()]
lines=[]
for i in range(3):
    for it in open(f'a{i}.txt',encoding='utf-8').read().strip().split(';'):
        t,w=it.split('|',1); lines.append(f'{float(t)+cuts[i]:.2f}|{w}')
open('asr.txt','w',encoding='utf-8').write('\n'.join(lines))
subprocess.run(['python3','align5.py'],check=True,stdout=open('align.log','w'))
cl=json.load(open('clauses.json',encoding='utf-8'))
# clause -> line index
txt=open('narration.txt',encoding='utf-8').read().strip().split('\n')
owner=[]
for li,l in enumerate(txt,1):
    n=len([c for c in re.split(r'(?<=[\.\?؟،:])\s+|(?<=\.\.\.)\s+',l) if c.strip()])
    owner+= [li]*n
assert len(owner)==len(cl),(len(owner),len(cl))
first={};alls={}
for i,li in enumerate(owner): first.setdefault(li,i); alls.setdefault(li,[]).append(i)
mp=json.load(open('map.json'))
plan=[];used={}
for k,r in mp:
    idxs=alls[r]; n=used.get(r,0); used[r]=n+1
    cnt=sum(1 for kk,rr in mp if rr==r)
    ci=idxs[min(len(idxs)-1, round(n*len(idxs)/cnt))]
    plan.append([k,cl[ci][0]])
plan[0][1]=0.0
for a,b in zip(plan,plan[1:]): assert b[1]>a[1],(a,b)
json.dump(plan,open('plan.json','w'))
for p in plan: print(p)
