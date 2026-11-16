import subprocess, os, json
os.chdir('/home/claude/trend05')
W,H,FPS=1080,1920,25
LEAD=0.6; TAIL=2.5; XF=0.5
cl=json.load(open('clauses.json',encoding='utf-8'))
audio_dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','voice.wav']).decode().strip())
starts=[(1,0),(2,2),(3,5),(4,7),(5,10),(6,13),(7,15),(8,19),(9,23),(10,26),(18,30),(11,34),(12,38),(13,40),(14,42),(15,44),(16,47),(1,48),(17,51)]
car={'02','08','09','13','14','15','18'}
fit=set()
focus={'03':0.45,'07':0.43,'11':0.6,'12':0.38,'17':0.52}
bounds=[]
for n,(img,ci) in enumerate(starts):
    t0=cl[ci][0]+LEAD
    t1=(cl[starts[n+1][1]][0]+LEAD) if n+1<len(starts) else audio_dur+LEAD+TAIL
    bounds.append((img,t0,t1))
bounds[0]=(bounds[0][0],0.0,bounds[0][2])
clips=[]
for n,(img,t0,t1) in enumerate(bounds):
    d=t1-t0+XF; frames=int(round(d*FPS)); key=f'{img:02d}'
    z = "1+0.10*on/%d"%frames if n%2==0 else "1.10-0.10*on/%d"%frames
    zp=f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
    out=f'vclip{n:02d}.mp4'
    if key in car:
        src=f'imgv/{key}.png'
        cmd=['ffmpeg','-y','-loglevel','error','-loop','1','-i',src,'-vf',"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"+zp,'-t',f'{d:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out]
    elif key in fit:
        src=f'img/{key}.png'
        fc=(f"[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,gblur=sigma=40,eq=brightness=-0.15[bg];"
            f"[0:v]scale=2160:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"+zp)
        cmd=['ffmpeg','-y','-loglevel','error','-loop','1','-i',src,'-filter_complex',fc,'-t',f'{d:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out]
    else:
        src=f'img/{key}.png'
        fx=focus.get(key,0.5)
        cmd=['ffmpeg','-y','-loglevel','error','-loop','1','-i',src,'-vf',f"scale=-2:3840,crop=2160:3840:x='max(0,min(iw-2160,iw*{fx}-1080))',"+zp,'-t',f'{d:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out]
    subprocess.run(cmd,check=True); clips.append((out,d)); print(key,round(t0,1),round(t1,1))
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
import re as _re
_o=subprocess.run(['ffmpeg','-hide_banner','-i','voice.wav','-af','silencedetect=noise=-30dB:d=0.04','-f','null','-'],capture_output=True,text=True).stderr
MICRO=list(zip([float(x) for x in _re.findall(r'silence_start: ([\d\.]+)',_o)],[float(x) for x in _re.findall(r'silence_end: ([\d\.]+)',_o)]))
caps=[]
units=[]
for a,b,txt in cl:
    w=txt.split()
    if len(w)>5:
        import math
        k=math.ceil(len(w)/5); per=math.ceil(len(w)/k)
        cuts=list(range(per,len(w),per))
        mp=[(x+y)/2 for x,y in MICRO if a+0.3<x<b-0.3]
        prev=a; prevw=0
        for c in cuts:
            m=a+(b-a)*c/len(w)
            if mp:
                best=min(mp,key=lambda t:abs(t-m))
                if abs(best-m)<0.8 and best>prev+0.3: m=best
            units.append((prev,m,' '.join(w[prevw:c]))); prev=m; prevw=c
        units.append((prev,b,' '.join(w[prevw:])))
    else: units.append((a,b,txt))
buf=''; bstart=None; bwords=0
for i,(a,b,txt) in enumerate(units):
    if bstart is None: bstart=a
    buf=(buf+' '+txt).strip(); bwords+=len(txt.split())
    nxt=units[i+1] if i+1<len(units) else None
    nxt_gap=(nxt[0]-b) if nxt else 9
    nxt_w=len(nxt[2].split()) if nxt else 99
    if (b-bstart)>=0.9 or i==len(units)-1 or nxt_gap>0.3 or bwords+nxt_w>5:
        caps.append([bstart+LEAD,b+LEAD+0.1,buf]); buf=''; bstart=None; bwords=0
for i in range(len(caps)-1):
    caps[i][1]=min(caps[i+1][0],caps[i][1]+0.6)
total=audio_dur+LEAD+TAIL
ass=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Tajawal ExtraBold,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,480,-1
Style: CapY,Tajawal ExtraBold,92,&H0000D8FF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,2,60,60,480,-1
Style: Tag,Tajawal ExtraBold,44,&H00FFFFFF,&H00FFFFFF,&H001F1FE0,&H001F1FE0,-1,0,0,0,100,100,0,0,3,14,0,9,0,60,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(total)},Tag,,0,0,0,,ترند
"""
from PIL import ImageFont
FNT=ImageFont.truetype('/root/.fonts/Tajawal-ExtraBold.ttf',61.5,layout_engine=ImageFont.Layout.RAQM)
def wl(t): return FNT.getlength(t,direction='rtl') if t else 0
POP='{\\fscx82\\fscy82\\t(0,140,\\fscx100\\fscy100)}'
for a,b,txt in caps:
    # layer 0: whole line white; layer 1: same line yellow, clipped to the spoken word.
    # (\\k sweeps left-to-right and inline colour tags break Arabic word order in libass)
    ws=txt.split(); L=[max(1,len(w)) for w in ws]; speak=max(0.3,(b-a)-0.55)
    full=wl(txt); right=540+full/2
    ass+=f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{POP}{txt}\n"
    t=a
    for j,w in enumerate(ws):
        d=speak*L[j]/sum(L); e=b if j==len(ws)-1 else t+d
        pre=wl(' '.join(ws[:j])+' ') if j else 0
        x2=right-pre+10; x1=right-pre-wl(w)-10
        ass+=f"Dialogue: 1,{ts(t)},{ts(e)},CapY,,0,0,0,,{POP if j==0 else ''}{{\\clip({x1:.0f},1280,{x2:.0f},1490)}}{txt}\n"; t=e
open('vertical.ass','w',encoding='utf-8').write(ass)
if os.environ.get('ASS_ONLY'): raise SystemExit
inputs=[]
for c,_ in clips: inputs+=['-i',c]
fc=[]; prev='[0:v]'; off=0.0
for i in range(1,len(clips)):
    off+=clips[i-1][1]-XF
    fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); prev=f'[v{i}]'
tot=off+clips[-1][1]
fc.append(f"{prev}ass=vertical.ass,fade=t=in:st=0:d=0.6,fade=t=out:st={tot-1.0:.3f}:d=1.0[vout]")
offs=[];o=0.0
for i in range(1,len(clips)):
    o+=clips[i-1][1]-XF; offs.append(o)
NA=len(clips)
fc.append(f"[{NA}:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{tot:.3f},aformat=channel_layouts=stereo,aresample=48000[voice]")
fc.append(f"[{NA+1}:a]volume=0.07,atrim=0:{tot:.3f},aresample=48000[mus]")
ws=[]
fc.append(f"[{NA+2}:a]asplit={len(offs)}"+"".join(f"[ws{k}]" for k in range(len(offs))))
for k,t in enumerate(offs):
    fc.append(f"[ws{k}]volume=0.22,adelay={int((t+XF/2-0.3)*1000)}|{int((t+XF/2-0.3)*1000)},aresample=48000[w{k}]"); ws.append(f"[w{k}]")
fc.append(f"[voice][mus]{''.join(ws)}amix=inputs={2+len(ws)}:normalize=0:duration=first,afade=t=out:st={tot-1.0:.3f}:d=1.0,alimiter=limit=0.95[aout]")
subprocess.run(['ffmpeg','-y','-loglevel','error']+inputs+['-i','voice.wav','-i','music.wav','-i','whoosh.wav','-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart','trend-05-vertical.mp4'],check=True)
print('total',round(tot,2))
