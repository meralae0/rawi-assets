# Vertical shorts from trend-10 master: line ranges, RTL captions (proportional timing), headline, end card, SRT.
import json, subprocess, os, re, sys
os.chdir('/home/claude/t10')
W, H, FPS = 1080, 1920, 25; LEAD = 0.5; CUT = 1.4; END = 3.0
L = json.load(open('lines_t.json'))
SEGS = json.loads(sys.argv[1]); OUT = sys.argv[2]; HEAD = sys.argv[3]
from PIL import ImageFont
FNT = ImageFont.truetype('/root/.fonts/Tajawal-ExtraBold.ttf', 61.5, layout_engine=ImageFont.Layout.RAQM)
wl = lambda t: FNT.getlength(t, direction='rtl') if t else 0
enc = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-c:a', 'aac', '-ar', '48000', '-ac', '2']
parts = []
for k, (a, b) in enumerate(SEGS):
    t0 = L[a]['s'] + LEAD - 0.1; t1 = L[b - 1]['e'] + LEAD + 0.15
    o = f'v/{OUT}_{k}.mp4'
    fc = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=25:2,eq=brightness=-0.3[bg];"
          f"[b]scale={W}:-2[fg];[bg][fg]overlay=0:560,fps={FPS},format=yuv420p[v];"
          f"[0:a]afade=t=in:st=0:d=0.15,afade=t=out:st={t1-t0-0.2:.3f}:d=0.2[a]")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1-t0:.3f}', '-i', 'trend-10-yt.mp4', '-filter_complex', fc,
                    '-map', '[v]', '-map', '[a]', *enc, o], check=True)
    parts.append((o, t0, t1, a, b))
if not os.path.exists('v/tend.mp4'):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', 'g/endv.png', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(END),
                    '-vf', f'fps={FPS},format=yuv420p', *enc, '-shortest', 'v/tend.mp4'], check=True)
XF = 0.35  # transition overlap
clips = [p[0] for p in parts] + ['v/tend.mp4']
durs = [p[2] - p[1] for p in parts] + [END]
inp = []; [inp.extend(['-i', c]) for c in clips]
fc = ''; v = '[0:v]'; au = '[0:a]'; off = 0.0; joins = []
TR = ['smoothleft', 'zoomin', 'slideup', 'fadewhite']
for i in range(1, len(clips)):
    off += durs[i - 1] - XF; joins.append(off)
    tr = 'fadewhite' if i == len(clips) - 1 else TR[(i - 1) % 3]
    fc += f"{v}[{i}:v]xfade=transition={tr}:duration={XF}:offset={off:.3f}[v{i}];{au}[{i}:a]acrossfade=d={XF}[a{i}];"
    v = f'[v{i}]'; au = f'[a{i}]'
WH = '/home/claude/rawi-assets/sfx/whoosh_quick.wav'
for k, t in enumerate(joins):
    inp.extend(['-i', WH]); n = len(clips) + k
    fc += f"[{n}:a]adelay={int(max(0, t - 0.1) * 1000)}|{int(max(0, t - 0.1) * 1000)},volume=0.5[w{k}];"
mix = au + ''.join(f'[w{k}]' for k in range(len(joins)))
fc += f"{mix}amix=inputs={len(joins) + 1}:normalize=0[aout]"
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *inp, '-filter_complex', fc, '-map', v, '-map', '[aout]', *enc, 'v/cat.mp4'], check=True)
STARTS = [0.0] + joins[:len(parts) - 1]
caps = []; srt = []
for (o, t0, t1, a, b), base in zip(parts, STARTS):
    for i in range(a, b):
        s = L[i]['s'] + LEAD - t0 + base; e = L[i]['e'] + LEAD - t0 + base; txt = L[i]['text']; e = min(e, base + t1 - t0 - XF)
        srt.append((s, e, txt))
        w = txt.split(); groups = []; cur = []
        for x in w:
            if cur and (len(cur) >= 5 or wl(' '.join(cur + [x])) > 600): groups.append(cur); cur = []
            cur.append(x)
        groups.append(cur)
        tot = sum(len(' '.join(g)) for g in groups); t = s
        for g in groups:
            d = (e - s) * len(' '.join(g)) / tot; caps.append((t, t + d, ' '.join(g))); t += d
base = joins[-1]
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Tajawal ExtraBold,88,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,4,2,60,60,420,-1
Style: Head,Tajawal ExtraBold,84,&H0000D8FF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,8,70,70,330,-1
Style: Bar,Arial,20,&H0000D8FF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Tag,Tajawal ExtraBold,44,&H00FFFFFF,&H00FFFFFF,&H002828D6,&H002828D6,-1,0,0,0,100,100,0,0,3,14,0,9,0,60,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,{ts(0)},{ts(base)},Tag,,0,0,0,,ترند
Dialogue: 0,{ts(0)},{ts(base)},Head,,0,0,0,,{HEAD}
Dialogue: 2,{ts(0)},{ts(base+END)},Bar,,0,0,0,,{{\\pos(0,0)\\clip(1080,0,1080,14)\\t(0,{int((base+END)*1000)},\\clip(0,0,1080,14))\\p1}}m 0 0 l 1080 0 1080 14 0 14{{\\p0}}
"""
POP = '{\\fscx82\\fscy82\\t(0,140,\\fscx100\\fscy100)}'
for a, b, t in caps: ass += f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{POP}{t}\n"
open(f'v/{OUT}.ass', 'w', encoding='utf-8').write(ass)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'v/cat.mp4', '-vf', f'ass=v/{OUT}.ass,fade=t=in:st=0:d=0.3', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', f'{OUT}.mp4'], check=True)
def st(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int(round(x%1*1000))%1000:03d}"
with open(f'{OUT}.srt', 'w', encoding='utf-8') as f:
    for i, (s, e, t) in enumerate(srt): f.write(f"{i+1}\n{st(s)} --> {st(e)}\n{t}\n\n")
print(OUT, round(base + END, 1))
