# ترند 09 — Nvidia Q3 FY27. 16:9 build
import json, os, subprocess, sys
os.chdir('/home/claude/t09')
sys.path.insert(0, '/home/claude/rawi-assets/tools')
import agfx
W, H, FPS, LEAD, TAIL = 1920, 1080, 25, 0.6, 3.5
LT = json.load(open('lines_t.json'))
VOICE_END = LT[-1][1]
SRC = {'G': 'src/v5090.webm', 'E': 'src/v5080.webm', 'S': 'src/vsmc.webm', 'F': 'src/vst.webm', 'D': 'src/vdc.webm'}
IMG = {}
P = {0: ['E0', 'G77.8'], 1: ['G50', 'G16'], 2: ['S41.7', 'S44.5'], 3: ['S42.5', 'G29.2', 'S50', 'G24.3'], 4: ['G111.8', 'E0.5'],
     5: ['G53.5', 'G57'], 6: ['E40', 'E50', 'E60'], 7: ['G58.3', 'G66'], 8: ['E100', 'E110'], 9: ['S8.3', 'S16.7'],
     10: ['S91.8', 'S100', 'S108.5'], 11: ['S117', 'S125'], 12: ['E120', 'E130'], 13: ['G68', 'G72.9'], 14: ['S125.5', 'E205.5'],
     15: ['G82.6', 'G87.5', 'G102'], 16: ['E95'], 17: ['E70', 'E80', 'S100.5'], 18: ['S0', 'S133.6', 'D182'], 19: ['G0.5', 'G19.4'],
     20: ['S75', 'D205'], 21: ['S41.9', 'G97.2'], 22: ['S109', 'E1'], 23: ['G16.5', 'G78.5']}
VF = {'G': 'scale=1920:1080', 'E': 'crop=iw*0.86:ih*0.86:iw*0.14:ih*0.12,scale=1920:1080', 'S': 'scale=1920:1080',
      'F': 'scale=1920:1080', 'D': 'crop=iw*0.9:ih*0.9:iw*0.05:ih*0.05,scale=1920:1080:flags=lanczos'}
shots = []
for i, (a, b) in enumerate(LT):
    t0 = 0.0 if i == 0 else a + LEAD
    t1 = (LT[i + 1][0] + LEAD) if i + 1 < len(LT) else VOICE_END + LEAD + TAIL
    lst = P[i]; d = (t1 - t0) / len(lst)
    for k, s in enumerate(lst):
        shots.append((s, t0 + k * d, d))
os.makedirs('clips', exist_ok=True)
REDO = set(os.environ.get('REDO', '').split(',')) - {''}
GRADE = "eq=contrast=1.12:brightness=-0.02:saturation=1.08,unsharp=5:5:0.6,vignette=PI/5,format=yuv420p"
with open('clips/list.txt', 'w') as Lf:
    for n, (s, t0, d) in enumerate(shots):
        o = f'clips/c{n:03d}.mp4'; fr = round(d * FPS)
        if not os.path.exists(o) or str(n) in REDO:
            if s[0] == 'I':
                img = 'src/' + IMG[s[1:]]; zin = n % 2 == 0
                z = f"'min(1+0.0010*on,1.12)'" if zin else f"'max(1.12-0.0010*on,1.0)'"
                vf = (f"scale=2400:1350:force_original_aspect_ratio=increase,crop=2400:1350,"
                      f"zoompan=z={z}:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={fr}:s=1920x1080:fps=25,{GRADE}")
                cmd = ['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', img, '-vf', vf, '-frames:v', str(fr)]
            else:
                src, st = s[0], float(s[1:])
                vf = (f"fps=25,{VF[src]},"
                      f"zoompan=z='min(1+0.0009*on,1.08)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=25,{GRADE}")
                cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', f'{st:.2f}', '-t', f'{d + 0.3:.3f}', '-i', SRC[src], '-an', '-vf', vf, '-frames:v', str(fr)]
            subprocess.run(cmd + ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', o], check=True)
        Lf.write(f"file '{os.path.abspath(o)}'\n")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'clips/list.txt', '-c', 'copy', 'video_only.mp4'], check=True)
TOTAL = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'video_only.mp4']))
def ts(x): return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
T = lambda i, off=0.0: LT[i][0] + LEAD + off
ev, sfx = [], []
ev.append(f"Dialogue: 5,{ts(0)},{ts(TOTAL)},Badge,,0,0,0,,{{\\an9\\pos(1850,60)}}ترند")
def card(i, big, small, dur=None):
    a = T(i, -0.15); b = a + (dur or (LT[i][1] - LT[i][0] + 0.6))
    ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Dim,,0,0,0,,{{\\an7\\pos(0,0)\\fad(250,300)\\p1}}m 0 0 l 1920 0 1920 1080 0 1080{{\\p0}}")
    ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Small,,0,0,0,,{{\\an5\\pos(960,430)\\fad(200,300)}}{small}")
    ev.append(f"Dialogue: 3,{ts(a + 0.25)},{ts(b)},Big,,0,0,0,,{{\\an5\\pos(960,560)\\fad(150,300)\\fscx130\\fscy130\\t(0,250,\\fscx100\\fscy100)}}{big}")
    sfx.append((a + 0.25, 'chapter'))
def stat(i, txt, off=0.3, dur=3.2):
    a = T(i, off); b = a + dur
    ev.append(f"Dialogue: 4,{ts(a)},{ts(b)},Stat,,0,0,0,,{{\\an3\\pos(1850,1000)\\fad(200,250)\\move(1910,1000,1850,1000,0,250)}}{txt}")
    sfx.append((a, 'stat'))
def num(i, big, small, off=0.0, dur=None):
    a = T(i, off - 0.1); b = a + (dur or (LT[i][1] - LT[i][0] + 0.5))
    ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Dim,,0,0,0,,{{\\an7\\pos(0,0)\\fad(250,300)\\p1}}m 0 0 l 1920 0 1920 1080 0 1080{{\\p0}}")
    ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Small,,0,0,0,,{{\\an5\\pos(960,400)\\fad(200,300)}}{small}")
    ev.append(f"Dialogue: 3,{ts(a + 0.2)},{ts(b)},Big,,0,0,0,,{{\\an5\\pos(960,560)\\fad(150,300)\\fscx130\\fscy130\\t(0,250,\\fscx100\\fscy100)}}{big}")
    sfx.append((a + 0.2, 'stat'))
num(0, '115.8 مليار $', 'إيرادات إنفيديا في 3 أشهر', dur=3.6)
card(2, 'بدون هوانغ', 'أول تقرير', dur=2.8)
stat(3, '33 عامًا', off=1.0)
num(5, '109 ← 115.8', 'المتوقع ← الحقيقي (مليار $)', off=0.3, dur=4.5)
stat(6, '+103٪ في عام', off=0.5)
stat(7, '2.68 $ / المتوقع 2.48 $', off=0.6, dur=3.2)
num(8, '65.3 مليار $', 'صافي الربح', off=0.6, dur=4.0)
num(10, '107.6 مليار $', 'مراكز البيانات', off=0.1, dur=4.2)
stat(11, '93 من كل 100 $', off=0.5)
card(12, 'فيرا روبن', 'الجيل الجديد', dur=2.6)
num(14, '130 مليار $', 'توقعات الربع القادم', off=0.8, dur=3.8)
stat(15, '28.1 مليار $ للمساهمين', off=2.0, dur=3.6)
card(16, 'لكن…', 'إشارتان', dur=2.4)
stat(17, '75٪ ← 72-71٪', off=2.0, dur=4.5)
stat(18, 'الصين: صفر', off=4.5, dur=3.5)
stat(19, '+3٪ بعد الإغلاق', off=2.5, dur=3.8)
card(21, 'الآلة… أم صانعها؟', 'الخلاصة', dur=3.0)
hdr = open('/home/claude/t09/ass_hdr.txt').read()
open('ov.ass', 'w', encoding='utf-8').write(hdr + '\n'.join(ev) + '\n')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_only.mp4', '-vf', "ass=ov.ass:fontsdir=/root/.fonts", '-c:v', 'libx264', '-preset', 'veryfast',
                '-crf', '19', '-pix_fmt', 'yuv420p', 'video_ov.mp4'], check=True)
agfx.sfx_track(sorted(sfx), TOTAL, 'sfx.wav', gain=0.45)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_ov.mp4', '-i', 'voice.wav', '-i', 'sfx.wav', '-filter_complex',
                f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad[v];[v][2:a]amix=inputs=2:normalize=0:duration=first[a]", '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-t', str(TOTAL), 'nomusic.mp4'], check=True)
subprocess.run([sys.executable, '/home/claude/rawi-assets/tools/mix.py', 'video_ov.mp4', 'voice.wav', 'trend-09-yt.mp4', '--mood', 'tech',
                '--track', os.environ.get('TRACK', 'tech_breaking-news-countdown-report.mp3'), '--sfx', 'sfx.wav', '--lead', str(LEAD)], check=True)
json.dump(shots, open('shots.json', 'w'))
print('done', TOTAL, len(shots))
