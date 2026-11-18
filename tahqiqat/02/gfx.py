# Animated explainer graphics for تحقيقات 02 (code-drawn, no third-party IP)
import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 25
F = '/root/.fonts/Cairo.ttf'
BG = (9, 15, 28); GRID = (22, 34, 56); CY = (76, 201, 240); RD = (230, 57, 70); AM = (244, 162, 97); WH = (235, 240, 248); MU = (120, 140, 170)
def font(s, b=True):
    f = ImageFont.truetype(F, s)
    try: f.set_variation_by_name('Bold' if b else 'Regular')
    except Exception: pass
    return f
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def base():
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    for x in range(0, W, 80): d.line([(x, 0), (x, H)], GRID, 1)
    for y in range(0, H, 80): d.line([(0, y), (W, y)], GRID, 1)
    return im, d
def txt(d, xy, s, size, col=WH, anchor='mm', b=True):
    d.text(xy, s, font=font(size, b), fill=col, anchor=anchor, direction='rtl' if any('؀' <= c <= 'ۿ' for c in s) else None)
def title(d, s, a=1.0):
    c = tuple(int(v * a + BG[i] * (1 - a)) for i, v in enumerate(AM))
    txt(d, (W - 90, 80), s, 52, c, 'rm')
def dot(d, p, r, col, glow=True):
    if glow:
        for k in range(3, 0, -1): d.ellipse([p[0] - r * k, p[1] - r * k, p[0] + r * k, p[1] + r * k], outline=col, width=1)
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)
def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
def path_pt(pts, t):
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L); s = t * tot
    for i, l in enumerate(L):
        if s <= l or i == len(L) - 1: return lerp(pts[i], pts[i + 1], min(1, s / l if l else 0))
        s -= l
def partial(d, pts, t, col, w, dash=False):
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L); s = t * tot; acc = [pts[0]]
    for i, l in enumerate(L):
        if s >= l: acc.append(pts[i + 1]); s -= l
        else: acc.append(lerp(pts[i], pts[i + 1], s / l)); break
    if dash:
        for i in range(len(acc) - 1):
            a, b = acc[i], acc[i + 1]; n = max(1, int(math.dist(a, b) / 24))
            for k in range(n):
                if k % 2 == 0: d.line([lerp(a, b, k / n), lerp(a, b, (k + 1) / n)], col, w)
    else: d.line(acc, col, w, joint='curve')

# ---------- scenes: f(t, dur) -> Image ----------
RIVER = [(560, -40), (640, 200), (760, 420), (900, 620), (1020, 820), (1100, 1120)]
ROUTE4 = [(600, 60), (690, 260), (800, 450), (930, 640), (1040, 860)]
RWY = ((1130, 520), (1330, 330))  # runway 33 (threshold SE -> NW)
APP = [(1700, 960), (1500, 760), (1330, 600), (1170, 500)]
HIT = (985, 712)
def map_base(d, labels=True):
    # river
    for k, w in ((0, 120), (1, 90)):
        d.line(RIVER, (14, 38, 70) if k == 0 else (18, 52, 95), w, joint='curve')
    # runway
    a, b = RWY; d.line([a, b], (70, 80, 95), 34); d.line([a, b], (200, 205, 215), 2)
    if labels:
        txt(d, (1360, 300), 'DCA  RWY 33', 30, WH, 'lm'); txt(d, (470, 120), 'نهر بوتوماك', 30, MU)
def g_map(t, D, mode='full'):
    im, d = base(); map_base(d)
    p = ease(t / max(D * 0.8, 0.1))
    if mode in ('full', 'route'):
        partial(d, ROUTE4, ease(t / (D * 0.5)) if mode == 'route' else 1, CY, 6, dash=True); txt(d, (520, 330), 'المسار 4', 40, CY)
    if mode in ('full', 'rwy'):
        partial(d, APP, ease(t / (D * 0.5)) if mode == 'rwy' else 1, AM, 6, dash=True); txt(d, (1640, 760), 'طريق الهبوط', 40, AM)
    if mode == 'full':
        h = path_pt(ROUTE4[:3] + [HIT], p); a = path_pt(APP[:2] + [(1240, 640), HIT], p)
        dot(d, h, 14, CY); dot(d, a, 14, AM)
        txt(d, (h[0] - 40, h[1]), 'PAT25', 30, CY, 'rm'); txt(d, (a[0] + 40, a[1]), '5342', 30, AM, 'lm')
        if p >= 0.999:
            fl = 0.5 + 0.5 * math.sin(t * 12); r = 40 + 30 * fl
            d.ellipse([HIT[0] - r, HIT[1] - r, HIT[0] + r, HIT[1] + r], outline=RD, width=6)
    if mode == 'cross':
        partial(d, ROUTE4, 1, CY, 6, dash=True); partial(d, APP, 1, AM, 6, dash=True)
        fl = 0.5 + 0.5 * math.sin(t * 6); r = 50 + 25 * fl
        d.ellipse([HIT[0] - r, HIT[1] - r, HIT[0] + r, HIT[1] + r], outline=RD, width=5)
        txt(d, (HIT[0] - 90, HIT[1] + 30), 'نقطة التقاطع', 40, RD, 'rm')
    title(d, {'full': 'مساران… نقطة واحدة', 'route': 'مسار المروحيات', 'rwy': 'الهبوط على المدرج 33', 'cross': 'المسار يعبر تحت طريق الهبوط'}[mode])
    return im
def g_alt(t, D, stage=3):
    im, d = base(); X0, X1, Y0 = 220, 1700, 900; sc = 1.9  # px per ft
    y = lambda ft: Y0 - ft * sc
    d.line([(X0, Y0), (X1, Y0)], MU, 3); txt(d, (X0 - 20, Y0), '0', 30, MU, 'rm')
    for ft in (100, 200, 300):
        d.line([(X0 - 10, y(ft)), (X0, y(ft))], MU, 2); txt(d, (X0 - 20, y(ft)), f'{ft} ft', 28, MU, 'rm')
    a = ease(t / 1.2)
    partial(d, [(X0, y(200)), (X1, y(200))], a, CY, 4, dash=True); txt(d, (X1, y(200) - 30), 'الحد الأقصى للمروحية: 200 قدم', 34, CY, 'rm')
    # plane glide path
    if True:
        b = ease((t - 0.8) / 1.5)
        partial(d, [(X0, y(470)), (X1, y(40))], b, AM, 5)
        if b > 0.3: txt(d, (X0 + 80, y(470) - 40), 'طريق هبوط الطائرة', 34, AM, 'lm')
    hx = 881
    if stage == 1:
        c = ease((t - 1.6) / 1.2); hy = y(200 + 78 * c)
        dot(d, (hx, hy), 16, RD); txt(d, (hx - 40, hy - 40), f'{int(200 + 78 * c)} قدمًا', 44, RD, 'rm')
    if stage >= 3:
        dot(d, (hx, y(200)), 16, CY)
        e = ease((t - 2.4) / 1.0)
        if e > 0:
            gp = y(275)
            d.line([(hx, y(200) - 18), (hx, gp)], WH, 3); d.line([(hx - 14, gp), (hx + 14, gp)], WH, 3)
            txt(d, (hx + 40, (gp + y(200)) / 2 - 10), '≈ 75 قدمًا فقط', int(40 + 8 * e), WH, 'lm')
    title(d, 'الارتفاع فوق النهر')
    return im
WORDS = ['PAT25', 'pass', 'behind', 'the', 'CRJ']
def g_radio(t, D):
    im, d = base(); cy = 520
    rnd = lambda k: (math.sin(k * 12.9898) * 43758.5453) % 1
    for i in range(0, 1500, 6):
        x = 210 + i; amp = 20 + 140 * abs(math.sin(i * 0.031)) * (0.4 + 0.6 * rnd(i))
        on = (x - 210) / 1500 < ease(t / 1.6)
        if on: d.line([(x, cy - amp), (x, cy + amp)], (90, 170, 210), 3)
    xs = [330, 640, 900, 1150, 1450]
    for w, x in zip(WORDS, xs): txt(d, (x, cy + 240), w, 54, WH)
    k = ease((t - 2.0) / 0.4)
    if k > 0:
        d.rectangle([440, cy - 200, 1070, cy + 290], fill=(60, 10, 18), outline=RD, width=5)
        txt(d, (755, cy - 10), 'محجوب بضغطة ميكروفون', 44, RD); txt(d, (755, cy + 80), '0.8 ثانية', 74, WH)
    title(d, 'ما سمعته المروحية')
    return im
EVTS = [('20:46', 'البرج ينبّه المروحية'), ('20:47:39', 'إنذار تصادم في البرج'), ('20:47:42', '«مُرّوا خلف…»'), ('20:47:59', 'الاصطدام')]
def g_time(t, D, upto=4):
    im, d = base(); y0 = 560; X = [1620, 1180, 760, 320]
    d.line([(260, y0), (1680, y0)], MU, 4)
    for i, ((tm, lab), x) in enumerate(zip(EVTS, X)):
        if i >= upto: break
        a = ease((t - i * 0.7) / 0.5)
        if a <= 0: continue
        col = RD if i == 3 else (AM if i else CY)
        dot(d, (x, y0), int(16 * a), col, glow=i == 3)
        txt(d, (x, y0 - 70), tm, 50, col); txt(d, (x, y0 + 80), lab, 38, WH)
    title(d, 'آخر دقيقتين')
    return im
def g_count(t, D):
    im, d = base(); n = int(85 * ease(t / max(2.5, D * 0.6)))
    for i in range(85):
        r, c = divmod(i, 17); x = 1620 - c * 80; y = 380 + r * 90
        col = RD if i < n else (35, 45, 66); d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=col)
    txt(d, (W / 2, 250), str(n), 120, RD); txt(d, (W / 2, 900), 'حالة اقتراب خطير — أكتوبر 2021 إلى ديسمبر 2024', 44, WH)
    title(d, 'تحذيرات سابقة')
    return im
VT = [0.3, 1.2, 2.1]
BOX = [('إدارة الطيران الفيدرالية', 'مسار مروحيات قريب جدًا من الهبوط'), ('إجراءات المراقبة', 'الانسيابية قبل الفصل الآمن'), ('طاقم المروحية', 'غياب فصل بصري فعّال')]
def g_verdict(t, D):
    im, d = base()
    for i, (a, b) in enumerate(BOX):
        e = ease((t - VT[i]) / 0.5)
        if e <= 0: continue
        x1 = 1790 - i * 590; y = 360 + int(40 * (1 - e))
        d.rounded_rectangle([x1 - 560, y, x1, y + 380], 24, outline=RD if i == 0 else AM, width=5, fill=(16, 24, 42))
        txt(d, (x1 - 280, y + 110), a, 42, RD if i == 0 else AM); txt(d, (x1 - 280, y + 230), b, 31, WH)
    title(d, 'الأسباب حسب المجلس الوطني لسلامة النقل')
    return im
def g_cards(t, D, which='both'):
    im, d = base()
    C = [('الرحلة 5342', 'من ويتشيتا إلى مطار ريغان', '60 راكبًا + 4 من الطاقم', AM), ('PAT25 — بلاك هوك', 'رحلة تدريب ليلية', '3 جنود — نظارات رؤية ليلية', CY)]
    sel = C if which == 'both' else [C[0]] if which == 'plane' else [C[1]]
    for i, (a, b, c, col) in enumerate(sel):
        e = ease((t - 0.2 - i * 0.8) / 0.5)
        if e <= 0: continue
        cx = W / 2 if len(sel) == 1 else (1380 if i == 0 else 540)
        y = 300 + int(50 * (1 - e))
        d.rounded_rectangle([cx - 400, y, cx + 400, y + 480], 28, outline=col, width=5, fill=(16, 24, 42))
        txt(d, (cx, y + 100), a, 58, col); txt(d, (cx, y + 240), b, 40, WH); txt(d, (cx, y + 350), c, 40, WH)
    title(d, 'على متن الطائرتين')
    return im
def g_radar(t, D, alert=True):
    im, d = base(); cx, cy, R = 960, 560, 430
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(6, 22, 16), outline=(40, 140, 90), width=3)
    for r in (R * 0.33, R * 0.66): d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(25, 80, 55), width=2)
    ang = t * 2.2; d.line([(cx, cy), (cx + R * math.cos(ang), cy + R * math.sin(ang))], (60, 220, 130), 3)
    p = ease(t / max(D, 0.1)) * 0.85
    a = lerp((cx + 300, cy + 260), (cx - 20, cy + 40), p); h = lerp((cx - 260, cy - 300), (cx - 20, cy + 40), p)
    dot(d, a, 10, AM, False); dot(d, h, 10, CY, False)
    txt(d, (a[0] + 24, a[1]), 'CRJ', 28, AM, 'lm'); txt(d, (h[0] - 24, h[1]), 'PAT25', 28, CY, 'rm')
    if alert and t > D * 0.35 and int(t * 3) % 2 == 0:
        d.rectangle([cx - 330, 60, cx + 330, 150], fill=(80, 10, 18), outline=RD, width=4); txt(d, (cx, 105), 'CONFLICT ALERT', 52, RD)
    title(d, 'شاشة البرج')
    return im
SCENES = {'map': lambda t, D: g_map(t, D, 'full'), 'maproute': lambda t, D: g_map(t, D, 'route'), 'maprwy': lambda t, D: g_map(t, D, 'rwy'),
          'mapcross': lambda t, D: g_map(t, D, 'cross'), 'alt1': lambda t, D: g_alt(t, D, 1), 'alt3': lambda t, D: g_alt(t, D, 3),
          'radio': g_radio, 'time2': lambda t, D: g_time(t, D, 2), 'time3': lambda t, D: g_time(t, D, 3), 'time4': lambda t, D: g_time(t, D, 4), 'time1': lambda t, D: g_time(t, D, 1),
          'count': g_count, 'verdict': g_verdict, 'plane': lambda t, D: g_cards(t, D, 'plane'), 'heli': lambda t, D: g_cards(t, D, 'heli'),
          'radar': g_radar, 'radar0': lambda t, D: g_radar(t, D, False), 'alt0': lambda t, D: g_alt(t, D, 0)}
def render(name, dur, out):
    n = round(dur * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-vf', 'vignette=PI/5,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(SCENES[name](k / FPS, dur).tobytes())
    p.stdin.close(); p.wait()
if __name__ == '__main__':
    name, dur, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    if out.endswith('.png'): SCENES[name](dur, dur).save(out)
    else: render(name, dur, out)
