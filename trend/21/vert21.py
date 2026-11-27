import json, subprocess, os
from PIL import Image, ImageDraw, ImageFont
L=json.load(open('lines.json')); W=1080
TJ=ImageFont.truetype('/root/.fonts/Tajawal-ExtraBold.ttf',72,layout_engine=ImageFont.Layout.RAQM)
os.makedirs('vt',exist_ok=True)
def run(a): subprocess.run(['ffmpeg','-y','-v','error']+a,check=True)
caps=[]
for li,l in enumerate(L):
    words=l['text'].split(); t0,t1=l['s']+0.05,l['e']-0.1
    tot=sum(len(w)+1 for w in words); t=t0; times=[]
    for w in words: d=(t1-t0)*(len(w)+1)/tot; times.append((t,t+d)); t+=d
    chunks=[];c0=0
    while c0<len(words):
        n=1
        while c0+n<len(words) and n<4 and TJ.getlength(' '.join(words[c0:c0+n+1]),direction='rtl')<960: n+=1
        chunks.append((c0,n)); c0+=n
    for c0,n in chunks:
        ch=words[c0:c0+n]
        for k in range(len(ch)):
            im=Image.new('RGBA',(W,240),(0,0,0,0)); d=ImageDraw.Draw(im)
            wf=TJ.getlength(' '.join(ch),direction='rtl'); x=W/2+wf/2
            for j,w in enumerate(ch):
                ww=TJ.getlength(w,direction='rtl')
                d.text((x,120),w,font=TJ,fill=(255,214,0) if j==k else (255,255,255),anchor='rm',direction='rtl',stroke_width=8,stroke_fill=(0,0,0))
                x-=ww+TJ.getlength(' ')
            p=f'vt/c{li:02d}_{c0+k:02d}.png'; im.save(p)
            a,b=times[c0+k]
            if k==len(ch)-1: b=times[min(c0+k+1,len(times)-1)][0] if c0+k+1<len(times) else b
            caps.append((a,b,p))
vd=133.4
fc=[f"[0:v]split=2[a0][b0];[a0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.2[bg];[b0]scale=1080:-2[fg];[bg][fg]overlay=0:560,setsar=1[v0]"]
ins=['-i','t21.mp4']; last='[v0]'
for k,(a,b,p) in enumerate(caps):
    ins+=['-i',p]; fc.append(f"{last}[{k+1}:v]overlay=0:1300:enable='between(t,{a:.3f},{b:.3f})'[c{k}]"); last=f'[c{k}]'
fc.append(f"color=c=0xFFD600:s=1080x12:d={vd}[bar];{last}[bar]overlay=x='W-W*t/{vd}':y=0[vo]")
open('vt/fc.txt','w').write(';'.join(fc))
run(ins+['-filter_complex_script','vt/fc.txt','-map','[vo]','-map','0:a','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-c:a','copy','-t',str(vd),'t21_v_full.mp4'])
print(len(caps))
