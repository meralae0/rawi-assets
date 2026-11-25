import json, subprocess, os, sys
sys.path.insert(0, '/home/claude/t19')
from PIL import Image, ImageDraw, ImageFilter
from gfx19 import frames19, T, tw, wrap, eo, W, H, RED, YEL, WH, MU, panel
from gfx import frames as frames11
import map19
os.chdir('/home/claude/t19'); os.makedirs('seg', exist_ok=True); os.makedirs('ov', exist_ok=True)
FPS = 25
L = json.load(open('lines.json')); VD = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice.wav']).decode())
END = VD + 1.2
S = [l['s'] for l in L] + [END]
DK = (20, 20, 30)
V = lambda f, o=0: ('v', f, o)
P = lambda f: ('p', f)
G = lambda k, **a: ('g', k, a)
# chaque entrée : ligne -> liste de (fraction_fin ou temps absolu, shot, overlay)
PLAN = {
 0: [(0.5, P('m/p_palace1.jpg'), ('tag', 'الرباط — اليوم')), (1, V('m/v3.webm', 2), None)],
 1: [(1, V('m/v1.webm', 24), ('num', '22', 'مليار درهم'))],
 2: [(0.5, V('m/v6.webm', 20), None), (1, V('m/v7.webm', 5), None)],
 3: [(22.0, P('m/p_palace2.jpg'), ('tag', 'الأربعاء 25 نوفمبر 2026')), (24.1, P('m/p_king_c.jpg'), ('name', 'الملك محمد السادس')), (1, P('m/p_prince.jpg'), ('name', 'وليّ العهد الأمير مولاي الحسن'))],
 4: [(1, V('m/v3.webm', 20), ('tag', 'الاتفاقية الأولى: التمويل'))],
 5: [(1, V('m/px_signing_8814707.mp4', 0), ('num', '22', 'مليار درهم — الشركاء العموميون'))],
 6: [(0.72, V('m/v3.webm', 24), ('list', ['وزارة الداخلية', 'وزارة الاقتصاد والمالية', 'وزارة الصناعة والتجارة', 'إدارة الدفاع الوطني', 'صندوق الإيداع والتدبير', 'صندوق الحسن الثاني'])), (1, P('m/p_um6p.jpg'), ('tag', 'جامعة محمد السادس متعددة التخصصات'))],
 7: [(1, V('m/px_business_8170593.mp4', 1), ('tag', 'الاتفاقية الثانية'))],
 8: [(0.5, P('m/p_bam.jpg'), ('tag', 'بنك المغرب')), (1, P('m/p_cfc.jpg'), ('tag', 'الأبناك • البورصة • الاتحاد العام لمقاولات المغرب'))],
 9: [(0.5, V('m/px_stock_38557069.mp4', 1), None), (1, V('m/px_stock_38656963.mp4', 4), ('tag', 'القطاع الخاص يدخل الصناعة الدفاعية'))],
 10: [(67.3, P('m/p_king.jpg'), ('name', 'الملك محمد السادس')), (1, G('agency'), None)],
 11: [(0.5, V('m/px_engineers_30283091.mp4', 6), None), (1, V('m/px_robotic_32386532.mp4', 1), None)],
 12: [(1/6, V('m/v6.webm', 40), ('label', 'الطائرات المسيّرة')), (2/6, V('m/v9.webm', 3), ('label', 'الأنظمة الذاتية')), (3/6, V('m/v2.webm', 2), ('label', 'العتاد البري والبحري')),
      (4/6, V('m/px_data_7140928.mp4', 1), ('label', 'الإلكترونيات الدفاعية')), (5/6, V('m/px_cyber_6346228.mp4', 3), ('label', 'الأمن السيبراني')), (1, V('m/px_robotic_32386590.mp4', 2), ('label', 'الذكاء الاصطناعي'))],
 13: [(98.81, G('goals', at=[2.3, 99, 99, 99]), None)],
 15: [(1, V('m/px_engineers_30288953.mp4', 20), ('num', '50', 'مليار درهم رقم معاملات سنوي'))],
 16: [(1, V('m/px_container_35907902.mp4', 10), ('num', '+65%', 'من الإيرادات من التصدير'))],
 17: [(1, V('m/px_car_6450803.mp4', 1), ('num', '50000', 'منصب شغل مباشر وغير مباشر'))],
 18: [(1, V('m/v1.webm', 10), None)],
 19: [(0.5, V('m/px_welding_6046358.mp4', 5), ('num', '333', 'مليون دولار — مشاريع مرخّصة')), (1, V('m/v8.webm', 30), ('num', '+3500', 'منصب شغل مباشر'))],
 20: [(1, ('map',), None)],
 21: [(0.5, V('m/px_aircraft_35080304.mp4', 0), ('label', 'صناعة الطائرات')), (1, V('m/px_car_4468754.mp4', 1), ('label', 'صناعة السيارات'))],
 22: [(1, G('q'), None)],
 23: [(1, V('m/v6.webm', 50), ('num', '2035', 'الموعد'))],
 24: [(1, V('m/v5.webm', 10), None)],
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
            if shot[0] == 'map': gen = (map19.g_map(i / FPS, dur, {}) for i in range(int(round(dur * FPS))))
            else: gen = frames19(shot[1], shot[2], dur)
            p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + ENC + ['tmp.mp4'], stdin=subprocess.PIPE)
            for im in gen: p.stdin.write(im.convert('RGB').tobytes())
            p.stdin.close(); p.wait(); sfx.append(('page_turn_ms.wav', cur))
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
