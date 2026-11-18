# تحقيقات 02 — Nvidia Q3 FY27. 16:9 build
import json, os, subprocess, sys
os.chdir('/home/claude/q02')
sys.path.insert(0, '/home/claude/rawi-assets/tools')
import agfx
W, H, FPS, LEAD, TAIL = 1920, 1080, 25, 0.6, 3.5
LT = json.load(open('lines_t.json'))
VOICE_END = LT[-1][1]
SRC = {'A': 'src/anim.webm', 'W': 'src/wreck.webm', 'B': 'src/brief.webm', 'C': 'src/cctv.webm', 'E': 'src/earthcam.webm',
       'K': 'src/crash.webm', 'T': 'src/teb.webm', 'X': 'src/bh1.webm', 'Y': 'src/bh3.webm', 'Z': 'src/bh4.webm', 'V': 'src/bh5.webm'}
IMG = {f'ph{i:03d}': f'../ph/ph{i:03d}.jpg' for i in range(118)}
P = {0: ['T3@0', 'Iph004@1'], 1: ['T10@0', 'A320@1'], 2: ['A88@0', 'Iph010@1', 'X5@2'], 3: ['E20@0', 'K14@1'], 4: ['Iph003@0', 'Iph001@1'],
 5: ['Iph000@0'], 6: ['Iph009@0', 'A60@1', 'Iph105@2', 'Iph106@4'], 7: ['X20@0', 'Iph108@1', 'Iph083@2'],
 8: ['T21@0', 'T25@1'], 9: ['Gplane@0', 'Iph102@2'], 10: ['X10@0', 'Z5@1', 'Gheli@2'], 11: ['Iph107@0'],
 12: ['Z20@0', 'Gmaproute@1'], 13: ['Gmaprwy@0', 'Iph087@1', 'Gmapcross@2'], 14: ['Gtime1@0', 'A420@2'], 15: ['A45@0', 'Iph113@2'],
 16: ['Iph111@0'], 17: ['Gtime4@0'], 18: ['Iph030@0', 'Iph116@1'], 19: ['Iph088@0', 'Galt0@1'], 20: ['Iph022@0', 'Galt1@1'],
 21: ['Iph086@0'], 22: ['Galt3@0'], 23: ['Iph117@0', 'A30@1', 'A90@2'], 24: ['A240@0', 'T6@1', 'A270@2'], 25: ['Iph112@0', 'A75@1', 'Iph110@2'],
 26: ['Gradar0@0'], 27: [], 28: ['B60@0', 'Iph012@1'], 29: ['Gradar@0'], 30: ['A300@0'], 31: ['Gtime3@0'], 32: ['Iph016@0', 'Iph103@1'],
 33: ['Iph031@0'], 34: ['Iph020@0'], 35: ['Y6@0', 'Gradio@1'], 36: [], 37: ['Y17@0'], 38: ['V92@0', 'Iph034@1'], 39: ['X30@0', 'A115@1'],
 40: ['A258@0', 'A200@1', 'Z30@2'], 41: ['Gmap@0'], 42: ['K12@0', 'Iph015@1'], 43: ['W30@0'], 44: ['W40@0', 'W60@1'], 45: ['Gcount@0'], 46: [],
 47: ['Iph085@0'], 48: ['W90@0', 'W75@1'], 49: ['A485@0', 'Iph114@1', 'W120@2'], 50: ['B1000@0', 'Iph048@1', 'B300@2'],
 51: ['Gverdict@0'], 52: [], 53: ['Iph023@0', 'Iph027@1'], 54: ['B1100@0', 'Iph043@1'], 55: ['Iph046@0'], 56: ['Iph024@0', 'Iph028@1', 'W280@2'],
 57: ['Iph008@0', 'Iph011@1']}
VF = {'A': 'scale=1920:1080', 'W': 'scale=1920:1080', 'B': 'crop=iw*0.62:ih*0.62:iw*0.19:ih*0.08,scale=1920:1080:flags=lanczos',
      'C': 'scale=1920:1080', 'E': 'crop=iw*0.8:ih*0.8:iw*0.06:ih*0.12,scale=1920:1080:flags=lanczos',
      'K': 'crop=iw*0.8:ih*0.8:iw*0.06:ih*0.12,scale=1920:1080:flags=lanczos', 'T': 'scale=1920:1080', 'X': 'scale=1920:1080',
      'Y': 'scale=1920:1080', 'Z': 'scale=1920:1080', 'V': 'scale=1920:1080'}
CT = json.load(open('clause_t.json'))
ct = lambda li, ci: next(c[2] for c in CT if c[0] == li and c[1] == ci)
starts = []
for i in range(len(LT)):
    for x in P[i]:
        s, c = x.split('@'); starts.append((s, (0.0 if (i == 0 and c == '0') else ct(i, int(c)) + LEAD)))
END = VOICE_END + LEAD + TAIL
shots = [(s, t0, (starts[k + 1][1] if k + 1 < len(starts) else END) - t0) for k, (s, t0) in enumerate(starts)]
import gfx
gfx.VT = [ct(51, 1) - ct(51, 0), ct(52, 1) - ct(51, 0), ct(52, 2) - ct(51, 0)]
os.makedirs('clips', exist_ok=True)
REDO = set(os.environ.get('REDO', '').split(',')) - {''}
GRADE = "eq=contrast=1.12:brightness=-0.02:saturation=0.9,unsharp=5:5:0.6,vignette=PI/5,format=yuv420p"
with open('clips/list.txt', 'w') as Lf:
    for n, (s, t0, d) in enumerate(shots):
        o = f'clips/c{n:03d}.mp4'; fr = round(d * FPS)
        if not os.path.exists(o) or str(n) in REDO:
            if s[0] == 'G':
                gfx.render(s[1:], fr / FPS, o); Lf.write(f"file '{os.path.abspath(o)}'\n"); continue
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
ev.append(f"Dialogue: 5,{ts(0)},{ts(TOTAL)},Badge,,0,0,0,,{{\\an9\\pos(1850,60)}}تحقيقات")
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
card(8, 'تلك الليلة', 'الملف', dur=2.6)
card(18, 'المروحية', 'الشبهة الأولى', dur=2.6)
card(26, 'برج المراقبة', 'الشبهة الثانية', dur=2.6)
card(34, 'الكلمات الضائعة', 'الانقلاب', dur=2.6)
card(43, 'ما قبل الكارثة', 'الخيط الأخير', dur=2.6)
card(50, 'الحكم', 'بعد عام من التحقيق', dur=2.8)
num(4, '67', 'ضحية — لا ناجين', dur=2.6)
stat(5, 'منذ 2001', off=0.8)
stat(29, '20 ثانية قبل الاصطدام', off=0.3)
stat(22, '≈ 23 مترًا', off=ct(22, 3) - ct(22, 0), dur=2.6)
stat(42, '760 مترًا من بداية المدرج', off=ct(42, 1) - ct(42, 0), dur=3.5)
stat(50, '27 يناير 2026', off=3.0)
stat(53, '74 استنتاجًا — 50 توصية', off=0.1, dur=3.0)
hdr = open('/home/claude/q02/ass_hdr.txt').read()
open('ov.ass', 'w', encoding='utf-8').write(hdr + '\n'.join(ev) + '\n')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_only.mp4', '-vf', "ass=ov.ass:fontsdir=/root/.fonts", '-c:v', 'libx264', '-preset', 'veryfast',
                '-crf', '19', '-pix_fmt', 'yuv420p', 'video_ov.mp4'], check=True)
agfx.sfx_track(sorted(sfx), TOTAL, 'sfx.wav', gain=0.45)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_ov.mp4', '-i', 'voice.wav', '-i', 'sfx.wav', '-filter_complex',
                f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad[v];[v][2:a]amix=inputs=2:normalize=0:duration=first[a]", '-map', '0:v', '-map', '[a]',
                '-c:v', 'copy', '-t', str(TOTAL), 'nomusic.mp4'], check=True)
subprocess.run([sys.executable, '/home/claude/rawi-assets/tools/mix.py', 'video_ov.mp4', 'voice.wav', 'tahqiqat-02-yt.mp4', '--mood', 'enquete',
                '--track', os.environ.get('TRACK', 'enquete_mystery-detective-investigation-music.mp3'), '--sfx', 'sfx.wav', '--lead', str(LEAD)], check=True)
json.dump(shots, open('shots.json', 'w'))
print('done', TOTAL, len(shots))
