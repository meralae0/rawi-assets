# Vertical teaser from the 16:9 master: segments of lines, karaoke RTL captions, end card.
import json, subprocess, os, re, math
os.chdir('/home/claude/t06')
W, H, FPS = 1080, 1920, 25; LEAD = 0.6
cl = json.load(open('clauses.json', encoding='utf-8'))
tm = json.load(open('times.json'))
ls = tm['lstart']
SEGS = json.loads(os.environ.get('SEGS', '[[0,4],[9,14],[24,29]]'))
OUT = os.environ.get('OUT', 'trend-06-vertical.mp4')
ENDCARD = 3.0
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice.wav']).decode())
segs = []
for a, b in SEGS:
    t0 = ls[a] + LEAD - 0.15; t1 = (ls[b] if b < len(ls) else dur) + LEAD - 0.1
    segs.append((t0, t1))
# cut segments from master (video+audio), vertical layout
parts = []
for k, (t0, t1) in enumerate(segs):
    o = f'tseg{k}.mp4'
    fc = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=25:2,eq=brightness=-0.25[bg];"
          f"[b]scale={W}:-2[fg];[bg][fg]overlay=0:520,fps={FPS},format=yuv420p[v];"
          f"[0:a]afade=t=in:st=0:d=0.15,afade=t=out:st={t1-t0-0.2:.3f}:d=0.2[a]")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1-t0:.3f}', '-i', 'trend-06-yt.mp4', '-filter_complex', fc,
                    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-c:a', 'aac', '-ar', '48000', '-ac', '2', o], check=True)
    parts.append((o, t0, t1))
# end card
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', 'g/endv.png', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(ENDCARD),
                '-vf', f'fps={FPS},format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-c:a', 'aac', '-shortest', 'tend.mp4'], check=True)
with open('tlist.txt', 'w') as f:
    for o, _, _ in parts: f.write(f"file '{o}'\n")
    f.write("file 'tend.mp4'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'tlist.txt', '-c', 'copy', 'tcat.mp4'], check=True)
# captions (clauses inside segments, remapped)
WJ = json.load(open('words.json'))
units = []; base = 0.0
for (o, t0, t1) in parts:
    for k, (a, b, txt) in enumerate(cl):
        A = a + LEAD; B = b + LEAD
        if A >= t0 - 0.05 and B <= t1 + 0.3:
            units.append((A - t0 + base, min(B, t1) - t0 + base, txt, [x + LEAD - t0 + base for x in WJ[k]]))
    base += t1 - t0
from PIL import ImageFont as _IF
_F=_IF.truetype('/root/.fonts/Tajawal-ExtraBold.ttf',61.5,layout_engine=_IF.Layout.RAQM)
WL=lambda t:_F.getlength(t,direction='rtl')
caps = []
for a, b, txt, wts in units:
    w = txt.split(); wts = [x for x, ww in zip(wts, [y for y in w if re.sub(r'[ً-ْـ\W]', '', y)])]
    if len(wts) != len(w): wts = [a + (b - a) * i / len(w) for i in range(len(w))]
    wts = [wts[0]] + [min(x + 0.2, b - 0.1) for x in wts[1:]]
    groups = []; cur = []
    for x in w:
        if cur and (len(cur) >= 5 or WL(' '.join(cur + [x])) > 600): groups.append(cur); cur = []
        cur.append(x)
    groups.append(cur); done = 0
    for gr in groups:
        s0 = wts[done]; done += len(gr); e = wts[done] if done < len(w) else b
        caps.append([s0, e, ' '.join(gr), wts[done-len(gr):done]])
for i in range(len(caps) - 1):
    caps[i][1] = min(caps[i + 1][0], caps[i][1] + 0.4)
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
total = base + ENDCARD
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Tajawal ExtraBold,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,480,-1
Style: CapY,Tajawal ExtraBold,92,&H0000D8FF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,2,60,60,480,-1
Style: Tag,Tajawal ExtraBold,44,&H00FFFFFF,&H00FFFFFF,&H002828D6,&H002828D6,-1,0,0,0,100,100,0,0,3,14,0,9,0,60,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(base)},Tag,,0,0,0,,ترند
"""
from PIL import ImageFont
FNT = ImageFont.truetype('/root/.fonts/Tajawal-ExtraBold.ttf', 61.5, layout_engine=ImageFont.Layout.RAQM)
def wl(t): return FNT.getlength(t, direction='rtl') if t else 0
POP = '{\\fscx82\\fscy82\\t(0,140,\\fscx100\\fscy100)}'
for a, b, txt, wt in caps:
    ws = txt.split(); L = [max(1, len(re.sub(r'[^\w]', '', x))) for x in ws]; speak = max(0.3, (b - a) - 0.3)
    full = wl(txt); right = 540 + full / 2
    ass += f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{POP}{txt}\n"
    t = a
    for j, w in enumerate(ws):
        t = wt[j]; e = b if j == len(ws) - 1 else wt[j + 1]
        pre = wl(' '.join(ws[:j]) + ' ') if j else 0
        x2 = right - pre + 10; x1 = right - pre - wl(w) - 10
        ass += f"Dialogue: 1,{ts(t)},{ts(e)},CapY,,0,0,0,,{POP if j == 0 else ''}{{\\clip({x1:.0f},1280,{x2:.0f},1490)}}{txt}\n"; t = e
open('teaser.ass', 'w', encoding='utf-8').write(ass)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'tcat.mp4', '-vf', 'ass=teaser.ass,fade=t=in:st=0:d=0.3', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', OUT], check=True)
print('teaser', round(total, 1))
