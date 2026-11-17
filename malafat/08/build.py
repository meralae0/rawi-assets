# ملفات 08 — Amelia Earhart. 16:9 build
import json, os, subprocess, sys
os.chdir('/home/claude/m08')
sys.path.insert(0, '/home/claude/rawi-assets/tools')
import agfx
W, H, FPS, LEAD, TAIL = 1920, 1080, 25, 0.6, 3.5
LT = json.load(open('lines_t.json'))
VOICE_END = LT[-1][1]
SRC = {'D': 'src/v_disappears.webm', 'V': 'src/v_venture.webm', 'H': 'src/v_heroine.webm', 'P': 'src/v_pacific.webm',
       'R': 'src/v_reception.webm', 'T': 'src/v_terraplane.webm'}
IMG = {'darwin': 'p_darwin.jpg', 'howN': 'p_howland_nasa.jpg', 'howC': 'p_howland_camp.jpg', 'itasca': 'p_itasca.jpg',
       'earhart': 'p_earhart.jpg', 'niku': 'p_niku.jpg', 'nikuL': 'p_niku_lagoon.jpg', 'nikuE': 'p_niku_entrance.jpg',
       'marshall': 'p_marshall.jpg', 'phoenix': 'p_phoenix_map.jpg'}
P = {0: ['D72', 'D57', 'V57', 'D75'], 1: ['D51', 'D48'], 2: ['H60'], 3: ['R18', 'R27', 'P45'], 4: ['H123', 'H63', 'R12', 'R24'],
     5: ['V39', 'D9'], 6: ['D3', 'D6', 'D18', 'D24'], 7: ['V45', 'V48', 'V54'], 8: ['V60', 'D72.5'], 9: ['Idarwin', 'D27'],
     10: ['D57.5', 'IhowN'], 11: ['IhowC', 'D73'], 12: ['Iitasca', 'D48.5'], 13: ['D33', 'D36', 'V57.5'], 14: ['V42', 'D12'],
     15: ['D46', 'D75.5', 'D50'], 16: ['V60.5', 'V56.5', 'D69', 'D57'], 17: ['D73.5', 'V56', 'D58'], 18: ['D76'], 19: ['D42'],
     20: ['D48', 'D54', 'D60', 'D64', 'D70'], 21: ['D44', 'D57.8'], 22: ['Iearhart', 'H138'], 23: ['D58.5'],
     24: ['D73', 'D57', 'V62.5'], 25: ['D56', 'D75'], 26: ['D54.5', 'D59'], 27: ['Iniku'], 28: ['Iphoenix', 'InikuE', 'InikuL'],
     29: ['InikuL', 'H57'], 30: ['Iearhart', 'P48', 'H126', 'H60.5'], 31: ['D42.5', 'D12.5', 'V42.5'], 32: ['Imarshall'],
     33: ['Imarshall', 'D60.5', 'D66'], 34: ['Imarshall', 'P36'], 35: ['D44.5'], 36: ['D42', 'D43.5', 'D45', 'R33'],
     37: ['InikuL', 'InikuE', 'Iniku'], 38: ['Iniku', 'D58'], 39: ['H57.5'], 40: ['V54', 'V57', 'P45.5'], 41: ['H60', 'P60'],
     42: ['V55', 'D72']}
# crop offset (of 1440) per source to drop top-right logos
CY = {'D': 300, 'V': 260, 'H': 300, 'P': 260, 'R': 300, 'T': 300}
shots = []
for i, (a, b) in enumerate(LT):
    t0 = 0.0 if i == 0 else a + LEAD
    t1 = (LT[i + 1][0] + LEAD) if i + 1 < len(LT) else VOICE_END + LEAD + TAIL
    lst = P[i]; d = (t1 - t0) / len(lst)
    for k, s in enumerate(lst):
        shots.append((s, t0 + k * d, d))
os.makedirs('clips', exist_ok=True)
REDO = set(os.environ.get('REDO', '').split(',')) - {''}
GRADE = "eq=contrast=1.12:brightness=-0.02:saturation=0,unsharp=5:5:0.6,vignette=PI/5,format=yuv420p"
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
                pre = "crop=464:352:88:4," if src == "V" else ""
                vf = (f"fps=25,{pre}scale=1920:1440:flags=lanczos,crop=1920:1080:0:{CY[src]},"
                      f"zoompan=z='min(1+0.0009*on,1.08)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=25,{GRADE}")
                cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', f'{st:.2f}', '-t', f'{d + 0.3:.3f}', '-i', SRC[src], '-an', '-vf', vf, '-frames:v', str(fr)]
            subprocess.run(cmd + ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', o], check=True)
        Lf.write(f"file '{os.path.abspath(o)}'\n")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'clips/list.txt', '-c', 'copy', 'video_only.mp4'], check=True)
TOTAL = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'video_only.mp4']))
def ts(x): return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
T = lambda i, off=0.0: LT[i][0] + LEAD + off
ev, sfx = [], []
ev.append(f"Dialogue: 5,{ts(0)},{ts(TOTAL)},Badge,,0,0,0,,{{\\an9\\pos(1850,60)}}ملفات")
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
card(2, 'أميليا إيرهارت', 'ملفّ', dur=2.6)
card(23, 'سقطت في البحر', 'الفرضيّة الأولى'); card(27, 'نيكومارورو', 'الفرضيّة الثانية'); card(32, 'أسرى اليابان', 'الفرضيّة الثالثة')
card(39, 'الملفّ مفتوح', '89 عامًا', dur=3.0)
stat(4, '1932 — الأطلسي وحدها'); stat(8, '35,000 كم ← 11,000 كم', dur=4.0); stat(10, '4,000 كم فوق الماء')
stat(11, 'الطول: أقلّ من 3 كم'); stat(16, '07:42', off=0.4); stat(17, '08:43 — آخر رسالة', off=0.4, dur=4.0)
stat(20, '16 يومًا'); stat(20, '650,000 كم²', off=4.0); stat(22, '5 يناير 1939'); stat(26, '2024')
stat(28, '1940', off=2.5); stat(30, '99%', off=4.0, dur=4.0); stat(34, '2017'); stat(36, '4,624 صفحة', off=2.0, dur=4.0)
stat(37, 'أكتوبر 2026', off=0.8)
hdr = open('/home/claude/m08/ass_hdr.txt').read()
open('ov.ass', 'w', encoding='utf-8').write(hdr + '\n'.join(ev) + '\n')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_only.mp4', '-vf', "ass=ov.ass:fontsdir=/root/.fonts", '-c:v', 'libx264', '-preset', 'veryfast',
                '-crf', '19', '-pix_fmt', 'yuv420p', 'video_ov.mp4'], check=True)
agfx.sfx_track(sorted(sfx), TOTAL, 'sfx.wav', gain=0.45)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_ov.mp4', '-i', 'voice.wav', '-i', 'sfx.wav', '-filter_complex',
                f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad[v];[v][2:a]amix=inputs=2:normalize=0:duration=first[a]", '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-t', str(TOTAL), 'nomusic.mp4'], check=True)
subprocess.run([sys.executable, '/home/claude/rawi-assets/tools/mix.py', 'video_ov.mp4', 'voice.wav', 'malafat-08-yt.mp4', '--mood', 'mystere',
                '--track', os.environ.get('TRACK', 'mystere_darkness-mystery.mp3'), '--sfx', 'sfx.wav', '--lead', str(LEAD)], check=True)
json.dump(shots, open('shots.json', 'w'))
print('done', TOTAL, len(shots))
