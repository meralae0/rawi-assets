import json, subprocess, os, sys
sys.path.insert(0, '/home/claude/t21')
from PIL import Image, ImageDraw, ImageFilter
from map21 import frames_map
sys.path.insert(0, '/home/claude/rawi-assets/trend/11')
from gfx import T, tw, wrap, eo, W, H, RED, YEL, WH, panel
os.chdir('/home/claude/t21'); os.makedirs('seg', exist_ok=True); os.makedirs('ov', exist_ok=True)
FPS = 25
L = json.load(open('lines.json')); VD = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice.wav']).decode())
END = VD + 1.2
S = [l['s'] for l in L] + [END]
DK = (20, 20, 30)
V = lambda f, o=0: ('v', f, o)
P = lambda f: ('p', f)
G = lambda k, **a: ('g', k, a)
B = lambda k, **a: ('b', k, a)
M = lambda k: ('m', k)
PLAN = {
 0: [(1, V('px/px_34711276.mp4', 1), ('tag', 'بنغازي — 22 نوفمبر 2026'))],
 1: [(0.55, V('px/px_12859922.mp4', 2), None), (1, P('cm/k002.jpg'), None)],
 2: [(0.5, V('px/px_35997572.mp4', 0), ('label', 'صور الأقمار الصناعية')), (1, V('px/px_11028763.mp4', 0), ('label', 'السفينة مقلوبة'))],
 3: [(0.55, P('cm/k003.jpg'), ('name', 'الكورفيت «ميركوري»')), (1, P('cm/k001.jpg'), ('num', '2023', 'سنة دخولها الخدمة'))],
 4: [(1, M('dist'), None)],
 5: [(0.5, P('cm/k023.jpg'), ('name', 'فولوديمير زيلينسكي')), (1, P('cm/k043.jpg'), ('num', '7', 'مسيّرات بحرية أوكرانية الصنع'))],
 6: [(0.5, V('px/px_40302723.mp4', 1), ('label', 'سفينة الشحن «أنغارا»')), (1, V('px/px_37858033.mp4', 2), None)],
 7: [(1, V('px/px_39508841.mp4', 1), ('tag', 'لماذا روسيا في ليبيا؟'))],
 8: [(0.5, P('cm/k028.jpg'), ('name', 'المشير خليفة حفتر')), (1, P('cm/k074.jpg'), ('label', 'شرق ليبيا: حضور عسكري روسي'))],
 9: [(1, P('cm/k087.jpg'), ('label', 'إمدادات نحو دول إفريقية'))],
 10: [(1, V('px/px_40881630.mp4', 0), ('tag', 'ليست الضربة الأولى'))],
 11: [(0.5, P('cm/k055.jpg'), ('label', 'مارس 2026: ناقلة غاز روسية')), (1, V('px/px_40462420.mp4', 1), ('label', 'بين ليبيا ومالطا'))],
 12: [(1, V('px/px_39077321.mp4', 1), ('tag', 'المتوسط: ساحة جديدة للحرب'))],
 13: [(1, V('px/px_11356694.mp4', 0), None)],
 14: [(1, P('cm/k034.jpg'), ('label', '«توجّهٌ خطير جداً»'))],
 15: [(1, P('cm/k018.jpg'), ('label', 'شرق ليبيا: «انتهاك للسيادة»'))],
 16: [(1, P('cm/k077.jpg'), ('label', '«ليبيا ليست ساحة لصراعات الآخرين»'))],
 17: [(1, V('px/px_34726277.mp4', 2), ('tag', 'وماذا يعني هذا لمنطقتنا؟'))],
 18: [(1, V('px/px_40622108.mp4', 1), ('label', 'المضائق التركية مغلقة منذ 2022'))],
 19: [(0.62, M('route'), None), (1, V('px/px_40401406.mp4', 0), ('label', 'مضيق جبل طارق'))],
 20: [(1, V('px/px_35239446.mp4', 1), None)],
 21: [(1, V('px/px_28496106.mp4', 1), None)],
 22: [(1, V('px/px_11335971.mp4', 1), None)],
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
            gen = frames_map(shot[1], dur)
            p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + ENC + ['tmp.mp4'], stdin=subprocess.PIPE)
            for im in gen: p.stdin.write(im.convert('RGB').tobytes())
            p.stdin.close(); p.wait()
            sfx.append(('page_turn_ms.wav', cur))
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
