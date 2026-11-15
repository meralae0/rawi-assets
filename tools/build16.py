import subprocess, os, json
os.chdir('/home/claude/trend03')
AUDIO='voice.wav'; OUT='trend-03-groundstop.mp4'
audio_dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',AUDIO]).decode().strip())
cl=json.load(open('clauses.json',encoding='utf-8'))
LEAD=0.6; TAIL=2.5; XF=0.6; FPS=25; W,H=1920,1080
starts=[(1,0),(2,5),(3,7),(4,12),(5,15),(6,17),(7,22),(8,29),(9,34),(10,38),(11,42),(12,46),(13,56),(14,61)]
bounds=[]
for n,(img,ci) in enumerate(starts):
    t0=cl[ci][0]+LEAD
    t1=(cl[starts[n+1][1]][0]+LEAD) if n+1<len(starts) else audio_dur+LEAD+TAIL
    bounds.append((img,t0,t1))
bounds[0]=(bounds[0][0],0.0,bounds[0][2])
moves=['in','out','panr','in','panl','out','in','panr','out','in','panl','out','in','out']
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
    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',f'img/{img:02d}.png','-vf',vf,'-t',f'{d_clip:.3f}','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','18',out],check=True)
    clips.append((out,d_clip)); print(out, round(t0,1), round(t1,1))
inputs=[]
for c,_ in clips: inputs+=['-i',c]
fc=[]; prev='[0:v]'; offset=0.0
for i in range(1,len(clips)):
    offset+=clips[i-1][1]-XF
    fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[v{i}]"); prev=f'[v{i}]'
total=offset+clips[-1][1]
fc.append(f"{prev}fade=t=in:st=0:d=0.8,fade=t=out:st={total-1.2:.3f}:d=1.2[vout]")
fc.append(f"[{len(clips)}:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{total:.3f},afade=t=out:st={total-1.0:.3f}:d=1.0,aformat=channel_layouts=stereo,aresample=48000[aout]")
subprocess.run(['ffmpeg','-y','-loglevel','error']+inputs+['-i',AUDIO,'-filter_complex',';'.join(fc),'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT],check=True)
print('total',round(total,2),'audio',round(audio_dur,2))
