# تحقيقات 01 — Hindenburg. 16:9 build: shots -> concat -> ASS overlays -> pro audio mix
import json, os, subprocess, sys
os.chdir('/home/claude/q01')
sys.path.insert(0, '/home/claude/rawi-assets/tools')
import agfx
W, H, FPS, LEAD, TAIL = 1920, 1080, 25, 0.6, 3.5
LT = json.load(open('lines_t.json'))
VOICE_END = LT[-1][1]
SRC = {'E': 'src/explodes.webm', 'S': 'src/special.webm', 'A': 'src/akron.ogv', 'G': 'src/graf.webm'}
P = {0: ['E200', 'S54', 'S60'], 1: ['S44', 'S62'], 2: ['S73', 'E208'], 3: ['E212', 'S88', 'E232'], 4: ['S130', 'E268', 'S150'],
     5: ['E284'], 6: ['E26', 'E34', 'E120', 'S67'], 7: ['E86', 'E64'], 8: ['S20', 'E62', 'S24'], 9: ['A4', 'A140'],
     10: ['A160', 'A300'], 11: ['E170', 'E178'], 12: ['G2', 'G30', 'E138', 'E142'], 13: ['E54', 'E78'], 14: ['A12', 'E314'],
     15: ['E144', 'E318'], 16: ['E196', 'S56'], 17: ['E316', 'A100'], 18: ['S6', 'S10'], 19: ['S46', 'E68'],
     20: ['E104', 'E108', 'E112'], 21: ['S60'], 22: ['E114', 'E100'], 23: ['S69', 'S72.6'], 24: ['S76', 'E214'],
     25: ['S84', 'E224'], 26: ['E236', 'S100'], 27: ['S104', 'E270'], 28: ['S181', 'S188', 'S196'],
     29: ['S248', 'S256', 'S232', 'S240'], 30: ['S276'], 31: ['S200'], 32: ['E92', 'E40'], 33: ['S280', 'S284'],
     34: ['A305', 'A320'], 35: ['S204', 'S208', 'S212'], 36: ['S216', 'S220', 'S224'], 37: ['E60'],
     38: ['E88', 'S20', 'E96', 'S28'], 39: ['S80', 'E220', 'S90'], 40: ['E228', 'S92'], 41: ['E312'], 42: ['E116'],
     43: ['E118', 'S58'], 44: ['S70', 'S73'], 45: ['S276', 'S284', 'S288'], 46: ['A40', 'A60'],
     47: ['S224', 'S228', 'S236'], 48: ['S140', 'E276'], 49: ['E284', 'S156', 'E288'], 50: ['E312', 'G60', 'E318'], 51: ['G70']}
shots = []
for i, (a, b) in enumerate(LT):
    t0 = 0.0 if i == 0 else a + LEAD
    t1 = (LT[i + 1][0] + LEAD) if i + 1 < len(LT) else VOICE_END + LEAD + TAIL
    lst = P[i]; d = (t1 - t0) / len(lst)
    for k, s in enumerate(lst):
        shots.append((s[0], float(s[1:]), t0 + k * d, d))
os.makedirs('clips', exist_ok=True)
REDO = set(os.environ.get('REDO', '').split(',')) - {''}
VF = ("scale=1920:1440:flags=lanczos,crop=1920:1080:0:180,"
      "zoompan=z='min(1+0.0009*on,1.08)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=25,"
      "eq=contrast=1.12:brightness=-0.02:saturation=0,unsharp=5:5:0.6,vignette=PI/5,format=yuv420p")
with open('clips/list.txt', 'w') as L:
    for n, (src, st, t0, d) in enumerate(shots):
        o = f'clips/c{n:03d}.mp4'
        if not os.path.exists(o) or str(n) in REDO:
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{st:.2f}', '-t', f'{d + 0.05:.3f}', '-i', SRC[src], '-an', '-vf', VF,
                            '-frames:v', str(round(d * FPS)), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', o], check=True)
        L.write(f"file '{os.path.abspath(o)}'\n")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'clips/list.txt', '-c', 'copy', 'video_only.mp4'], check=True)
TOTAL = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'video_only.mp4']))
# ---- overlays (ASS, libass shapes Arabic)
def ts(x): return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
T = lambda i, off=0.0: LT[i][0] + LEAD + off
ev, sfx = [], []
ev.append(f"Dialogue: 5,{ts(0)},{ts(TOTAL)},Badge,,0,0,0,,{{\\an9\\pos(1850,60)}}تحقيقات")
def card(i, big, small, dur=None, kind='impact'):
    a = T(i, -0.15); b = a + (dur or (LT[i][1] - LT[i][0] + 0.6))
    ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Dim,,0,0,0,,{{\\an7\\pos(0,0)\\fad(250,300)\\p1}}m 0 0 l 1920 0 1920 1080 0 1080{{\\p0}}")
    ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Small,,0,0,0,,{{\\an5\\pos(960,430)\\fad(200,300)}}{small}")
    ev.append(f"Dialogue: 3,{ts(a + 0.25)},{ts(b)},Big,,0,0,0,,{{\\an5\\pos(960,560)\\fad(150,300)\\fscx130\\fscy130\\t(0,250,\\fscx100\\fscy100)}}{big}")
    sfx.append((a + 0.25, kind))
def stat(i, txt, off=0.3, dur=3.2):
    a = T(i, off); b = a + dur
    ev.append(f"Dialogue: 4,{ts(a)},{ts(b)},Stat,,0,0,0,,{{\\an3\\pos(1840,960)\\fad(200,250)\\move(1900,960,1840,960,0,250)}}{txt}")
    sfx.append((a, 'stat'))
card(5, 'ملفّ: هيندنبورغ', 'تحقيقات', kind='boom_short'); sfx.append((T(5, -1.6), 'riser_short'))
card(31, 'التخريب', 'الفرضيّة الأولى'); card(37, 'الطلاء', 'الفرضيّة الثانية'); card(41, 'شرارة', 'الفرضيّة الثالثة')
card(48, 'حادث... لا مؤامرة', 'الحكم', dur=4.0, kind='boom_short')
stat(3, '32 ثانية'); stat(3, 'الطول: 245 م', off=3.6)
stat(8, '7,000,000 قدم³ من الهيدروجين', dur=4.0); stat(12, '97 على متنها: 36 راكبًا و61 من الطاقم', dur=4.5)
stat(22, '19:21 — إلقاء حبال الرسوّ'); stat(23, '19:25 — أوّل لهب', off=0.6)
stat(28, '36 قتيلًا', dur=4.5); stat(29, '62 ناجيًا', dur=4.0); stat(38, '1997'); stat(46, '2021 — معهد كالتك', dur=4.0)
sfx += [(T(2, 0.1), 'boom_cinematic'), (T(30, 0.2), 'riser_uneasy')]
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Badge,Tajawal ExtraBold,46,&H00FFFFFF,&H00FFFFFF,&H001A1AC8,&H001A1AC8,1,0,0,0,100,100,0,0,3,14,0,9,0,0,0,-1
Style: Big,Tajawal ExtraBold,150,&H0000D7FF,&H0000D7FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,4,5,0,0,0,-1
Style: Small,Tajawal ExtraBold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,2,5,0,0,0,-1
Style: Dim,Tajawal ExtraBold,10,&H70000000,&H70000000,&H70000000,&H70000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,-1
Style: Stat,Tajawal ExtraBold,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H50101010,1,0,0,0,100,100,0,0,3,18,0,3,0,0,0,-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open('ov.ass', 'w', encoding='utf-8').write(hdr + '\n'.join(ev) + '\n')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_only.mp4', '-vf', "ass=ov.ass:fontsdir=/root/.fonts", '-c:v', 'libx264', '-preset', 'veryfast',
                '-crf', '19', '-pix_fmt', 'yuv420p', 'video_ov.mp4'], check=True)
agfx.sfx_track(sorted(sfx), TOTAL, 'sfx.wav', gain=0.45)
subprocess.run([sys.executable, '/home/claude/rawi-assets/tools/mix.py', 'video_ov.mp4', 'voice.wav', 'tahqiqat-01-yt.mp4', '--mood', 'enquete',
                '--track', os.environ.get('TRACK', 'enquete_mystery-detective-investigation-music.mp3'), '--sfx', 'sfx.wav', '--lead', str(LEAD)], check=True)
json.dump(shots, open('shots.json', 'w'))
print('done', TOTAL, len(shots))
