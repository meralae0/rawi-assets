import subprocess, os, json
os.chdir('/home/claude/trend03')
W,H,FPS=1080,1920,25
LEAD=0.6; TAIL=2.5; XF=0.5
cl=json.load(open('clauses.json',encoding='utf-8'))
audio_dur=149.52
starts=[(1,0),(2,5),(3,7),(4,12),(5,15),(6,17),(7,22),(8,29),(9,34),(10,38),(11,42),(12,46),(13,56),(14,61)]
car={'04','06','07','11'}          # vertical versions exist in imgv/<key>v.png
fit={'03','05','08','10','12'}          # wide scenes: fit on blurred background
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
        src=f'imgv/{key}v.png'
        cmd=['ffmpeg','-y','-loglevel','error','-loop','1','-i',src,'-vf',"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"+zp,'-t',f'{d:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out]
    elif key in fit:
        src=f'img/{key}.png'
        fc=(f"[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,gblur=sigma=40,eq=brightness=-0.15[bg];"
            f"[0:v]scale=2160:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,"+zp)
        cmd=['ffmpeg','-y','-loglevel','error','-loop','1','-i',src,'-filter_complex',fc,'-t',f'{d:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out]
    else:
        src=f'img/{key}.png'
        cmd=['ffmpeg','-y','-loglevel','error','-loop','1','-i',src,'-vf',"scale=-2:3840,crop=2160:3840,"+zp,'-t',f'{d:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out]
    subprocess.run(cmd,check=True); clips.append((out,d)); print(key,round(t0,1),round(t1,1))
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
import re as _re
_o=subprocess.run(['ffmpeg','-hide_banner','-i','voice.wav','-af','silencedetect=noise=-30dB:d=0.04','-f','null','-'],capture_output=True,text=True).stderr
MICRO=list(zip([float(x) for x in _re.findall(r'silence_start: ([\d\.]+)',_o)],[float(x) for x in _re.findall(r'silence_end: ([\d\.]+)',_o)]))
caps=[]
units=[]
for a,b,txt in cl:
    w=txt.split()
    if len(w)>7:
        h=(len(w)+1)//2; m=a+(b-a)*h/len(w)
        mp=[(x+y)/2 for x,y in MICRO if a+0.3<x<b-0.3]
        if mp:
            best=min(mp,key=lambda t:abs(t-m))
            if abs(best-m)<0.8: m=best
        units.append((a,m,' '.join(w[:h]))); units.append((m,b,' '.join(w[h:])))
    else: units.append((a,b,txt))
buf=''; bstart=None; bwords=0
for i,(a,b,txt) in enumerate(units):
    if bstart is None: bstart=a
    buf=(buf+' '+txt).strip(); bwords+=len(txt.split())
    nxt=units[i+1] if i+1<len(units) else None
    nxt_gap=(nxt[0]-b) if nxt else 9
    nxt_w=len(nxt[2].split()) if nxt else 99
    if (b-bstart)>=0.9 or i==len(units)-1 or nxt_gap>0.3 or bwords+nxt_w>7:
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
Style: Cap,Tajawal ExtraBold,80,&H0000D8FF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,480,1
Style: Tag,Tajawal ExtraBold,44,&H00FFFFFF,&H00FFFFFF,&H001F1FE0,&H001F1FE0,-1,0,0,0,100,100,0,0,3,14,0,9,0,60,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(total)},Tag,,0,0,0,,ترند
"""
for a,b,txt in caps:
    # dynamic caption: pop-in + word-by-word yellow highlight (karaoke \k, per-word time ~ letters)
    ws=txt.split(); L=[max(1,len(w)) for w in ws]; speak=max(0.3,(b-a)-0.55)
    ks=[max(8,int(round(speak*100*l/sum(L)))) for l in L]
    body=' '.join(f"{{\\k{k}}}{w}" for k,w in zip(ks,ws))
    ass+=f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fscx82\\fscy82\\t(0,140,\\fscx100\\fscy100)}}{body}\n"
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
fc.append(f"[{len(clips)}:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{tot:.3f},afade=t=out:st={tot-1.0:.3f}:d=1.0,aformat=channel_layouts=stereo,aresample=48000[aout]")
subprocess.run(['ffmpeg','-y','-loglevel','error']+inputs+['-i','voice.wav','-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','medium','-crf','20','-c:a','aac','-b:a','192k','-movflags','+faststart','trend-03-vertical.mp4'],check=True)
print('total',round(tot,2))
