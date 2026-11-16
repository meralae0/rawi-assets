import json, subprocess, os, re, sys
os.chdir('/home/claude/t06'); sys.path.insert(0, '/home/claude/rawi-assets/tools'); sys.path.insert(0, '.')
import reportage_gfx as g
from shots import S
g.badge.__defaults__ = ('ترند',)
from PIL import Image, ImageDraw
FPS = 25; W, H = 1920, 1080; LEAD = 0.6; TAIL = 2.5
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice.wav']).decode())
cl = json.load(open('clauses.json', encoding='utf-8'))
lines = [l.strip() for l in open('narration.txt', encoding='utf-8').read().split('\n') if l.strip() and not l.startswith('##')]
own = [i for i, l in enumerate(lines) for c in re.split(r'(?<=[\.\?؟،:…!])\s+', l) if c.strip()]
assert len(own) == len(cl), (len(own), len(cl))
lstart = [min(cl[k][0] for k in range(len(cl)) if own[k] == i) for i in range(len(lines))]
lend = lstart[1:] + [dur]; cst = [c[0] for c in cl]
T = []
for ln, fr, *_ in S:
    t = lstart[ln] + fr * (lend[ln] - lstart[ln])
    if fr > 0: t = min([c for c in cst if lstart[ln] < c < lend[ln]] or [t], key=lambda c: abs(c - t))
    T.append(t + LEAD)
T[0] = 0.0; total = dur + LEAD + TAIL
END = float(os.environ.get('END', '0')) or total
VID = {'nasa_night': 'src/nasa_night.webm', 'eas_pgh': 'src/eas_pgh.webm', 'rot': 'src/rot.webm'}
def overlay(i, credit, stamp):
    o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    f = g.F(g.FB, 34); w = g.tw(d, 'ترند', f) + 40
    d.rounded_rectangle((W - 60 - w, 40, W - 60, 92), 10, fill=g.RED); g.text(d, (W - 60 - w / 2, 66), 'ترند', f, (255, 255, 255))
    if credit:
        fc = g.F(g.FR, 26); d.text((42, H - 46), credit, font=fc, fill=(0, 0, 0, 160), direction='rtl' if any('؀' <= c <= 'ۿ' for c in credit) else None)
        d.text((40, H - 48), credit, font=fc, fill=(255, 255, 255, 220), direction='rtl' if any('؀' <= c <= 'ۿ' for c in credit) else None)
    p = f'ov/o{i:02d}.png'; o.save(p)
    if stamp:
        s = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(s); fs = g.F(g.FB, 44)
        tw = g.tw(d, stamp, fs); x2 = W - 60; x1 = x2 - tw - 60
        d.rectangle((x1, H - 210, x2, H - 140), fill=(15, 15, 15, 190)); d.rectangle((x2 - 10, H - 210, x2, H - 140), fill=g.YEL + (255,))
        g.text(d, ((x1 + x2 - 10) / 2, H - 175), stamp, fs, (255, 255, 255)); s.save(f'ov/s{i:02d}.png')
    return p
os.makedirs('ov', exist_ok=True); os.makedirs('clips', exist_ok=True)
clips = []
for i, (ln, fr, kind, src, st, stamp) in enumerate(S):
    credit = None
    t0 = T[i]; t1 = T[i + 1] if i + 1 < len(T) else total
    if t0 >= END: break
    t1 = min(t1, END); d = t1 - t0; n = int(round(d * FPS)); out = f'clips/c{i:02d}.mp4'
    if os.path.exists(out) and str(i) not in os.environ.get('REDO','').split(','):
        clips.append((out, t0, d)); continue
    if kind == 'end':
        g.title_card('اشتركوا في القناة', 'ترند | الراوي').save('ov/end.png')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', 'ov/end.png', '-vf', f'fps={FPS},format=yuv420p', '-t', f'{d:.3f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out], check=True)
        clips.append((out, t0, d)); continue
    ov = overlay(i, credit, stamp)
    stin = ['-loop', '1', '-i', f'ov/s{i:02d}.png'] if stamp else []
    if kind == 'v':
        base = (f"[0:v]fps={FPS},setpts=PTS-STARTPTS,split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.2[bg];"
                f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v0]")
        inp = ['-ss', str(st), '-i', VID[src]]
    else:
        pth = ('g/' if kind == 'g' else 'src/') + src; im = Image.open(pth).convert('RGB'); ar = im.width / im.height
        if 1.45 < ar < 2.0:
            base = f"[0:v]scale=2880:1620:force_original_aspect_ratio=increase,crop=2880:1620,zoompan=z='{'1+0.07*on/%d' % n if i % 2 == 0 else '1.07-0.07*on/%d' % n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}[v0]"
        elif ar >= 2.0:  # panorama: horizontal pan
            base = f"[0:v]scale=-2:{H},crop={W}:{H}:x='(iw-{W})*t/{d:.2f}':y=0,fps={FPS}[v0]"
        else:
            base = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.25[bg];"
                    f"[b]scale=-2:{H-80}[fg];[bg][fg]overlay=(W-w)/2:40,zoompan=z='1+0.05*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}[v0]")
        inp = ['-loop', '1', '-i', pth]
    fc = base + f";[v0][1:v]overlay=0:0[v1]"
    if stamp: fc += f";[2:v]fade=t=in:st=0.3:d=0.4:alpha=1,fade=t=out:st={max(0.8, min(3.6, d - 0.5)):.2f}:d=0.4:alpha=1[st];[v1][st]overlay=0:0[v2]"; last = 'v2'
    else: last = 'v1'
    fc += f";[{last}]format=yuv420p[v]"
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + inp + ['-loop', '1', '-i', ov] + stin + ['-filter_complex', fc, '-map', '[v]', '-t', f'{d:.3f}', '-r', str(FPS), '-an',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out], check=True)
    clips.append((out, t0, d)); print(out, round(t0, 1), round(d, 1), kind, src, flush=True)
with open('clips/list.txt', 'w') as f:
    for c, _, _ in clips: f.write(f"file '{os.path.basename(c)}'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'clips/list.txt', '-c', 'copy', 'video_only.mp4'], check=True)
tot = min(END, total)
fc = [f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{tot:.3f},aformat=channel_layouts=stereo,aresample=48000[voice]",
      f"[2:a]volume=0.07,atrim=0:{tot:.3f},aresample=48000[mus]",
      f"[voice][mus]amix=inputs=2:normalize=0:duration=first,afade=t=out:st={tot-1.0:.3f}:d=1.0,alimiter=limit=0.95[aout]",
      f"[0:v]fade=t=in:st=0:d=0.5,fade=t=out:st={tot-1.0:.3f}:d=1.0[vout]"]
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'video_only.mp4', '-i', 'voice.wav', '-i', 'music.wav', '-filter_complex', ';'.join(fc),
                '-map', '[vout]', '-map', '[aout]', '-t', f'{tot:.3f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '5M', '-bufsize', '10M',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', 'trend-06-yt.mp4'], check=True)
json.dump({'T': T, 'lstart': lstart}, open('times.json', 'w'))
print('done', round(tot, 1))
