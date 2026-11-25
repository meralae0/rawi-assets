import json, subprocess, os, sys
sys.path.insert(0, '/home/claude/t20')
from PIL import Image, ImageDraw, ImageFilter
from gfx20 import frames20, T, tw, wrap, eo, W, H, RED, YEL, WH, panel
os.chdir('/home/claude/t20'); os.makedirs('seg', exist_ok=True); os.makedirs('ov', exist_ok=True)
FPS = 25
L = json.load(open('lines.json')); VD = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice.wav']).decode())
END = VD + 1.2
S = [l['s'] for l in L] + [END]
DK = (20, 20, 30)
V = lambda f, o=0: ('v', f, o)
P = lambda f: ('p', f)
G = lambda k, **a: ('g', k, a)
B = lambda k, **a: ('b', k, a)
PLAN = {
 0: [(1, B('play', clip='B', s0=0.0, tag='هل هذا حقيقي؟'), None)],
 1: [(0.55, B('play', clip='A', s0=0.0, label='المقطع 1'), None), (1, B('play', clip='A', s0=8.6, sp=0.5, freeze=1.2, label='المقطع 1', text=['ثم تقف سالمة!'], ring=(360, 690, 120), rt=1.2), None)],
 2: [(1, V('m/px_7025302.mp4', 5), ('tag', 'تعليقات كثيرة: هل هذا حقيقي؟'))],
 3: [(1, B('play', clip='A', s0=3.0, freeze=0, stamp='ذكاء اصطناعي'), None)],
 4: [(1, V('m/px_7025303.mp4', 8), ('tag', '5 علامات تكشف الحقيقة'))],
 5: [(1, B('pair', title='العلامة 1: المدّة', frames=[('A', 4), ('B', 3)], labels=['المقطع 1', 'المقطع 2'], count=1), None)],
 6: [(1, V('m/px_38110167.mp4', 1), ('tag', 'أدوات توليد الفيديو: مقاطع قصيرة'))],
 7: [(1, B('recipe', d2=4.0), None)],
 9: [(0.5, B('play', clip='A', s0=1.0, sp=0.5, tag='العلامة 3: الجسم'), None), (1, B('play', clip='A', s0=1.0, freeze=0, tag='العلامة 3: الجسم', text=['جسم متصلّب', 'كأنه دمية'], tt=0.1, ring=(355, 275, 130), rt=0.1), None)],
 10: [(1, V('m/px_38847733.mp4', 0), ('tag', 'حيوان حقيقي: كل الأرجل تعمل'))],
 11: [(0.5, B('play', clip='B', s0=1.5, tag='العلامة 4: الكاميرا', text=['الكاميرا تسقط', 'مع العنزة!'], tt=0.8), None), (1, V('m/px_18675523.mp4', 0), ('tag', 'تصوير حقيقي'))],
 12: [(0.45, B('play', clip='A', s0=8.4, sp=0.6, tag='العلامة 5: الهبوط'), None), (1, B('play', clip='A', s0=9.4, freeze=0, tag='العلامة 5: الهبوط', text=['لا غبار', 'ولا حجارة تتساقط'], tt=0.1, ring=(360, 690, 120), rt=0.1), None)],
 13: [(1, V('m/px_7025303.mp4', 25), None)],
 14: [(0.5, V('m/px_30318371.mp4', 2), ('label', 'خطوة خطوة')), (1, V('m/px_40317668.mp4', 0), None)],
 15: [(1, V('m/px_38870115.mp4', 3), ('num', '3.5 م', 'أطول قفزة للماعز الجبلي'))],
 16: [(0.5, P('m/c_goat2.jpg'), ('label', 'حافر من إصبعين')), (1, V('m/px_15467574.mp4', 5), ('label', 'وسادة خشنة تمسك الصخر'))],
 17: [(1, P('m/c_dam4.jpg'), ('tag', 'إيطاليا — جبال الألب'))],
 18: [(1, P('m/c_dam1.jpg'), ('num', '49 م', 'سدّ تشينغينو'))],
 19: [(0.5, P('m/c_dam2.jpg'), None), (1, P('m/c_dam3.jpg'), ('label', 'وعل الألب يلعق الملح'))],
 20: [(0.5, P('m/c_ibex_wall.jpg'), ('tag', 'صور حقيقية')), (1, P('m/c_wall_v.jpg'), None)],
 21: [(1, V('m/px_8217800.mp4', 2), ('tag', 'القاعدة: ابحث عن العلامات'))],
 22: [(1, B('signs'), None)],
 23: [(1, V('m/px_26612570.mp4', 2), None)],
 24: [(1, V('m/px_32575254.mp4', 0), None)],
}
def ov_png(kind, a, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind in ('num', 'name', 'label', 'tag', 'list'):
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for y in range(H // 2, H):
            gd.line([(0, y), (W, y)], fill=(0, 0, 0, int(170 * (y - H / 2) / (H / 2))))
        im.alpha_composite(g); d = ImageDraw.Draw(im)
    if kind == 'num':
        v, cap = a
        T(d, (W - 150, 800), v, 190, YEL, 'rm', stroke=6)
        T(d, (W - 150, 960), cap, 62, WH, 'rm', stroke=4)
    elif kind in ('name', 'label'):
        s = a; w = tw(s, 60) + 80
        d.rectangle([W - 150 - w, 880, W - 150, 980], fill=(255, 255, 255)); d.rectangle([W - 150, 880, W - 130, 980], fill=RED)
        T(d, (W - 150 - w / 2, 932), s, 60, DK)
    elif kind == 'tag':
        s = a; w = tw(s, 52) + 70
        d.rounded_rectangle([W - 150 - w, 900, W - 150, 990], 12, fill=RED); T(d, (W - 150 - w / 2, 947), s, 52, WH)
    elif kind == 'list':
        dim = Image.new('RGBA', (W, H), (0, 0, 0, 110)); im.alpha_composite(dim); d = ImageDraw.Draw(im)
        T(d, (W - 160, 150), 'الاتفاقية الأولى: الموقّعون', 60, WH, 'rm', stroke=3)
        for i, s in enumerate(a):
            y = 240 + i * 120; x1 = W - 160
            panel(d, [x1 - 900, y, x1, y + 100], (255, 255, 255)); d.rounded_rectangle([x1 - 100, y, x1, y + 100], 14, fill=RED)
            T(d, (x1 - 50, y + 52), str(i + 1), 52); T(d, (x1 - 130, y + 52), s, 46, DK, 'rm')
    im.save(path)
def run(cmd): subprocess.run(cmd, check=True)
ENC = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
segs = []; sfx = []; n = 0
keys = sorted(PLAN)
for idx, li in enumerate(keys):
    t0 = S[li]; t1 = S[keys[idx + 1]] if idx + 1 < len(keys) else END
    cur = t0
    for (fe, shot, ov) in PLAN[li]:
        te = fe if fe > 2 else t0 + (t1 - t0) * fe
        if fe == 1: te = t1
        dur = round(te - cur, 3); out = f'seg/s{n:03d}.mp4'
        if shot[0] == 'v':
            vf = 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,eq=contrast=1.05:saturation=1.08'
            run(['ffmpeg', '-y', '-v', 'error', '-ss', str(shot[2]), '-i', shot[1], '-t', str(dur), '-vf', vf, '-an'] + ENC + ['tmp.mp4'])
        elif shot[0] == 'p':
            im = Image.open(shot[1]).convert('RGB'); r = max(3840 / im.width, 2160 / im.height)
            im = im.resize((int(im.width * r) + 2, int(im.height * r) + 2), Image.LANCZOS)
            l = (im.width - 3840) // 2; tp = max(0, (im.height - 2160) // 3); im.crop((l, tp, l + 3840, tp + 2160)).save('tmp.jpg', quality=93)
            fr = int(dur * FPS) + 1
            z = f"1+0.08*on/{fr}" if n % 2 == 0 else f"1.08-0.08*on/{fr}"
            run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', 'tmp.jpg', '-vf', f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s=1920x1080:fps=25", '-t', str(dur)] + ENC + ['tmp.mp4'])
        else:
            gen = frames20(shot[1], shot[2], dur)
            p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + ENC + ['tmp.mp4'], stdin=subprocess.PIPE)
            for im in gen: p.stdin.write(im.convert('RGB').tobytes())
            p.stdin.close(); p.wait()
            if shot[1] in ('pair', 'recipe', 'signs') or shot[2].get('stamp'): sfx.append(('page_turn_ms.wav', cur))
        if ov:
            ov_png(ov[0], ov[1] if len(ov) == 2 else ov[1:], 'ov/o.png')
            run(['ffmpeg', '-y', '-v', 'error', '-i', 'tmp.mp4', '-loop', '1', '-i', 'ov/o.png', '-filter_complex', '[1:v]format=rgba,fade=in:st=0.25:d=0.35:alpha=1[o];[0:v][o]overlay=0:0:shortest=1'] + ENC + [out])
            if ov[0] == 'num': sfx.append(('envelope_slide.wav', cur + 0.25))
        else:
            os.replace('tmp.mp4', out)
        segs.append((out, dur)); cur = te; n += 1
        print(out, li, round(dur, 2), shot[0], ov[0] if ov else '')
open('seg/list.txt', 'w').write(''.join(f"file '{os.path.basename(s)}'\n" for s, _ in segs))
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'seg/list.txt', '-c', 'copy', 'body.mp4'])
json.dump(sfx, open('sfx.json', 'w'))
print('total', sum(d for _, d in segs), 'END', END)
