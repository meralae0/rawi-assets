import json, subprocess, os, re
os.chdir('/home/claude/m07')
FPS = 25; W, H = 1920, 1080; LEAD = 0.6; TAIL = 2.5
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice.wav']).decode())
cl = json.load(open('clauses.json', encoding='utf-8'))
lines = [l.strip() for l in open('narration.txt', encoding='utf-8').read().split('\n') if l.strip() and not l.startswith('##')]
# clause -> line
own = [i for i, l in enumerate(lines) for c in re.split(r'(?<=[\.\?؟،:…!])\s+', l) if c.strip()]
assert len(own) == len(cl), (len(own), len(cl))
assert len(set(own)) == len(lines), (len(set(own)), len(lines))
lstart = [min(cl[k][0] for k in range(len(cl)) if own[k] == i) for i in range(len(lines))]
lend = lstart[1:] + [dur]
cstarts = [c[0] for c in cl]
plan = json.load(open('gplan.json', encoding='utf-8'))
T = []
for a, ln, fr in plan:
    t = lstart[ln] + fr * (lend[ln] - lstart[ln])
    if fr > 0:
        t = min([c for c in cstarts if lstart[ln] < c < lend[ln]] or [t], key=lambda c: abs(c - t))
    T.append(t + LEAD)
T[0] = 0.0
total = dur + LEAD + TAIL
END = float(os.environ.get('END', '0')) or total
VID = {'nightsky': 'v_nightsky.mp4', 'landing': 'v_landing.mp4', 'bills': 'v_bills.mp4', 'bills2': 'v_bills2.mp4',
       'depart': 'v_depart.mp4', 'rainwin': 'v_rainwin.mp4', 'fog': 'v_fog.mp4', 'fog2': 'v_fog.mp4'}
VSS = {'fog2': 4.0}
os.makedirs('clips', exist_ok=True)
clips = []
for i, (a, ln, fr) in enumerate(plan):
    t0 = T[i]; t1 = T[i + 1] if i + 1 < len(T) else total
    if t0 >= END: break
    t1 = min(t1, END); d = t1 - t0; fr_n = int(round(d * FPS))
    out = f'clips/c{i:02d}.mp4'
    if a.startswith('v:'):
        name = a[2:]; src = 'src/' + VID[name]
        vf = (f"[0:v]fps={FPS},setpts=PTS-STARTPTS,split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.15[bg];"
              f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)/2,eq=saturation=0.75:contrast=1.05[v0];"
              f"[v0][1:v]overlay=0:0,format=yuv420p[v]")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-stream_loop', '-1', '-ss', str(VSS.get(name, 0)), '-i', src,
                        '-i', 'g/badge.png', '-filter_complex', vf, '-map', '[v]', '-t', f'{d:.3f}', '-r', str(FPS), '-an',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out], check=True)
    else:
        z = f"1+0.06*on/{fr_n}" if i % 2 == 0 else f"1.06-0.06*on/{fr_n}"
        vf = (f"scale=2880:1620,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr_n}:s={W}x{H}:fps={FPS},format=yuv420p")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', a, '-vf', vf, '-t', f'{d:.3f}', '-r', str(FPS),
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out], check=True)
    clips.append((out, t0, d))
    print(out, round(t0, 1), round(d, 1), a, flush=True)
with open('clips/list.txt', 'w') as f:
    for c, _, _ in clips: f.write(f"file '{os.path.basename(c)}'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'clips/list.txt', '-c', 'copy', 'video_only.mp4'], check=True)
tot = min(END, total)
cuts = [t for _, t, _ in clips[1:]]
fc = [f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{tot:.3f},aformat=channel_layouts=stereo,aresample=48000[voice]",
      f"[2:a]volume=0.07,atrim=0:{tot:.3f},aresample=48000[mus]",
      f"[3:a]asplit={len(cuts)}" + ''.join(f'[ws{k}]' for k in range(len(cuts)))]
ws = []
for k, t in enumerate(cuts):
    ms = max(0, int((t - 0.25) * 1000))
    fc.append(f"[ws{k}]volume=0.16,adelay={ms}|{ms},aresample=48000[w{k}]"); ws.append(f'[w{k}]')
fc.append(f"[voice][mus]{''.join(ws)}amix=inputs={2+len(ws)}:normalize=0:duration=first,afade=t=out:st={tot-1.0:.3f}:d=1.0,alimiter=limit=0.95[aout]")
fc.append(f"[0:v]fade=t=in:st=0:d=0.5,fade=t=out:st={tot-1.0:.3f}:d=1.0[vout]")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'video_only.mp4', '-i', 'voice.wav', '-i', 'music.wav', '-i', 'whoosh.wav',
                '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-t', f'{tot:.3f}', '-c:v', 'libx264', '-preset', 'medium',
                '-crf', '20', '-maxrate', '6M', '-bufsize', '12M', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', 'malafat-07-yt.mp4'], check=True)
json.dump({'T': T, 'lstart': lstart}, open('times.json', 'w'))
print('done', round(tot, 1))
