import json, subprocess, os, json
os.chdir('/home/claude/malafat06')
AUDIO='voice.wav'; OUT='malafat-06.mp4'
audio_dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',AUDIO]).decode().strip())
cl=json.load(open('clauses.json',encoding='utf-8'))
LEAD=0.6; TAIL=2.5; XF=0.6; FPS=25; W,H=1920,1080
plan=json.load(open('plan.json'))
END=float(os.environ.get('END','0')) or None
bounds=[]
for n,(img,t) in enumerate(plan):
    t0=t+LEAD
    t1=(plan[n+1][1]+LEAD) if n+1<len(plan) else audio_dur+LEAD+TAIL
    if END is not None:
        if t0>=END: break
        t1=min(t1,END)
    bounds.append((img,t0,t1))
bounds[0]=(bounds[0][0],0.0,bounds[0][2])
moves=(['in','out','panr','in','panl','out','in','panr','out','in','panl','out','in','out']*3)[:len(bounds)]
clips=[]
for i,((img,t0,t1),mv) in enumerate(zip(bounds,moves)):
    d_clip=t1-t0+XF; frames=int(round(d_clip*FPS))
    if mv=='in':   z="1+0.10*on/%d"%frames; x="iw/2-(iw/zoom/2)"; y="ih/2-(ih/zoom/2)"
    elif mv=='out':z="1.10-0.10*on/%d"%frames; x="iw/2-(iw/zoom/2)"; y="ih/2-(ih/zoom/2)"
    elif mv=='panr':z="1.08"; x="(iw-iw/zoom)*on/%d"%frames; y="ih/2-(ih/zoom/2)"
    else:          z="1.08"; x="(iw-iw/zoom)*(1-on/%d)"%frames; y="ih/2-(ih/zoom/2)"
    vf=(f"scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    out=f"clip{i:02d}.mp4"
    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',f'img/{img}.png','-vf',vf,'-t',f'{d_clip:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out],check=True)
    clips.append((out,d_clip)); print(out, round(t0,1), round(t1,1))
inputs=[]
for c,_ in clips: inputs+=['-i',c]
fc=[]; prev='[0:v]'; offset=0.0
for i in range(1,len(clips)):
    offset+=clips[i-1][1]-XF
    fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[v{i}]"); prev=f'[v{i}]'
total=offset+clips[-1][1]
fc.append(f"{prev}fade=t=in:st=0:d=0.8,fade=t=out:st={total-1.2:.3f}:d=1.2[vout]")
offs=[];o=0.0
for i in range(1,len(clips)):
    o+=clips[i-1][1]-XF; offs.append(o)
NA=len(clips)
fc.append(f"[{NA}:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{total:.3f},aformat=channel_layouts=stereo,aresample=48000[voice]")
fc.append(f"[{NA+1}:a]volume=0.07,atrim=0:{total:.3f},aresample=48000[mus]")
ws=[]
fc.append(f"[{NA+2}:a]asplit={len(offs)}"+"".join(f"[ws{k}]" for k in range(len(offs))))
for k,t in enumerate(offs):
    fc.append(f"[ws{k}]volume=0.22,adelay={int((t+XF/2-0.3)*1000)}|{int((t+XF/2-0.3)*1000)},aresample=48000[w{k}]"); ws.append(f"[w{k}]")
fc.append(f"[voice][mus]{''.join(ws)}amix=inputs={2+len(ws)}:normalize=0:duration=first,afade=t=out:st={total-1.0:.3f}:d=1.0,alimiter=limit=0.95[aout]")
subprocess.run(['ffmpeg','-y','-loglevel','error']+inputs+['-i',AUDIO,'-i','music.wav','-i','whoosh.wav','-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT],check=True)
print('total',round(total,2),'audio',round(audio_dur,2))
