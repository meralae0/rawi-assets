import json, subprocess, os, sys
sys.path.insert(0, '/home/claude/rawi-assets/tools')
import build as B
from agfx import sfx_track
FPS = 30
seq = json.load(open('seq.json'))
os.makedirs('shots2', exist_ok=True)
B.BG = None
cnt = {}
events = []
t = 0.0
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())
lst = open('shots2/list.txt', 'w')
for out, i, j, d, v, ovs in seq:
    o2 = 'shots2/' + os.path.basename(out)
    real_d = dur(out)
    skip = os.path.exists(o2) and os.path.getmtime(o2) > os.path.getmtime(out)
    ins = ['-i', out]; fc = []; last = '[0:v]'; k = 1
    items = list(ovs)
    if v.startswith('a:'): items.append(('aitag', ''))
    for item in items:
        kind, text = item[0], item[1]
        name = f'{i:02d}_{j}_{kind}_{k}'
        B.ov_png(kind, text, name)
        if kind == 'chapter': st, en = 0.0, min(2.4, real_d - 0.1); events.append((t + 0.05, 'chapter'))
        elif kind == 'big': st, en = 0.4, min(real_d - 0.2, 3.6); events.append((t + 0.4, 'stat'))
        elif kind == 'hyp': st, en = 0.2, real_d - 0.3; events.append((t + 0.2, 'chapter'))
        elif kind == 'date': st, en = 0.3, real_d - 0.3; events.append((t + 0.3, 'stat'))
        elif kind == 'quote': st, en = 0.4, real_d - 0.3
        elif kind == 'face': st, en = 0.3, real_d - 0.2; events.append((t + 0.3, 'stat'))
        else: st, en = 0.4, real_d - 0.3
        if any(x[0] == 'chapter' for x in items) and kind in ('date', 'label'): st = 2.5
        if en - st < 0.8: continue
        ins += ['-loop', '1', '-t', f'{real_d:.3f}', '-i', f'ov/{name}.png']
        fc.append(f"[{k}:v]format=rgba,fade=in:st={st:.2f}:d=0.35:alpha=1,fade=out:st={en - 0.3:.2f}:d=0.3:alpha=1[o{k}]")
        fc.append(f"{last}[o{k}]overlay=0:0:shortest=1[v{k}]"); last = f'[v{k}]'; k += 1
    if skip: pass
    elif k == 1:
        (os.remove(o2) if os.path.exists(o2) else None); os.link(out, o2)
    else:
        subprocess.run(['ffmpeg', '-y', '-v', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-map', last, '-r', str(FPS), '-pix_fmt', 'yuv420p',
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', o2], check=True)
    lst.write(f"file '{os.path.basename(o2)}'\n")
    t += real_d
lst.close()
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'shots2/list.txt', '-c', 'copy', 'body.mp4'], check=True)
tot = dur('body.mp4')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'body.mp4', '-loop', '1', '-i', 'ov/pastille.png', '-filter_complex', '[0:v][1:v]overlay=0:0:shortest=1',
                '-r', str(FPS), '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', 'body2.mp4'], check=True)
sfx_track(events, tot, 'sfx.wav', gain=0.3)
json.dump(events, open('events.json', 'w'))
print('video', tot, 'events', len(events))
