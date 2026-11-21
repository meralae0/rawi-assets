# News-style animated graphics for ترند 10 (Shenzhen summit). Code-drawn, no third-party IP.
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1920, 1080
TB = '/root/.fonts/Tajawal-ExtraBold.ttf'; TR = '/root/.fonts/Tajawal-Bold.ttf'
NAVY = (8, 16, 34); NAVY2 = (14, 28, 58); RED = (200, 30, 45); WH = (240, 244, 250); YEL = (255, 200, 0); MU = (140, 160, 190); BLUE = (40, 110, 200)
_fc = {}
def f(s, b=True):
    k = (s, b)
    if k not in _fc: _fc[k] = ImageFont.truetype(TB if b else TR, s)
    return _fc[k]
def ar(s): return any('؀' <= c <= 'ۿ' for c in s)
def T(d, xy, s, size, col=WH, anchor='mm', b=True, stroke=0):
    d.text(xy, s, font=f(size, b), fill=col, anchor=anchor, direction='rtl' if ar(s) else None, stroke_width=stroke, stroke_fill=(0, 0, 0))
def tw(s, size): return f(size).getlength(s, direction='rtl' if ar(s) else None)
def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)
def eo(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3
_bgc = {}
def bg(t):
    # animated news backdrop: navy gradient + moving diagonal light bands + world-grid dots
    key = int(t * 12) % 48
    if key in _bgc: return _bgc[key].copy()
    im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
    for y in range(0, H, 6):
        c = tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * (1 - abs(y - H / 2) / (H / 2))) for i in range(3))
        d.rectangle([0, y, W, y + 6], fill=c)
    ph = key / 48
    for k in range(4):
        x0 = (ph * W * 1.5 + k * 700) % (W * 1.6) - 400
        d.polygon([(x0, 0), (x0 + 120, 0), (x0 - 300, H), (x0 - 420, H)], fill=(18, 36, 72))
    for gx in range(60, W, 60):
        for gy in range(60, H, 60):
            d.point((gx, gy), fill=(40, 62, 100))
    _bgc[key] = im
    return im.copy()
def panel(d, box, fill=(255, 255, 255), r=18): d.rounded_rectangle(box, r, fill=fill)
def redtag(d, xy, s, size=40, anchor_right=True):
    w = tw(s, size) + 50; x, y = xy
    box = [x - w, y, x, y + size + 30] if anchor_right else [x, y, x + w, y + size + 30]
    d.rounded_rectangle(box, 10, fill=RED); T(d, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + 2), s, size)
def wrap(s, size, maxw):
    words = s.split(); lines = []; cur = ''
    for w in words:
        c = (cur + ' ' + w).strip()
        if tw(c, size) > maxw and cur: lines.append(cur); cur = w
        else: cur = c
    lines.append(cur); return lines
_ph = {}
def photo(path, size):
    k = (path, size)
    if k not in _ph:
        im = Image.open(path).convert('RGB'); im = im.resize(size) if False else im
        tw_, th = size; r = max(tw_ / im.width, th / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1)); l = (im.width - tw_) // 2; tp = (im.height - th) // 4
        _ph[k] = im.crop((l, tp, l + tw_, tp + th))
    return _ph[k]

# ---------- cards ----------
def g_breaking(t, D, a):
    im = Image.open('m/img/005.jpg').convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(14))
    im = Image.blend(im, Image.new('RGB', (W, H), NAVY), 0.55); d = ImageDraw.Draw(im)
    k = eo(t / 0.5); w = int(1200 * k)
    d.rectangle([W // 2 - w // 2, 330, W // 2 + w // 2, 470], fill=RED)
    if t > 0.25: T(d, (W // 2, 402), 'تحليل', 96)
    if t > 0.6:
        T(d, (W // 2, 560), 'أول قمة ثلاثية في التاريخ', 70, WH)
        T(d, (W // 2, 650), 'أمريكا • الصين • روسيا', 54, YEL)
    if t > 1.1: T(d, (W // 2, 740), 'شنجن — 19 نوفمبر 2026', 44, MU)
    return im
def g_share(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 150), 'الرؤوس النووية في العالم', 58, WH, 'rm')
    n = 10; on = min(n, int(eo(t / 2.0) * 9.999) + 1) if t > 0.3 else 0
    for i in range(n):
        x = W - 260 - i * 150; y = 520
        col = RED if i < 9 and i < on else (70, 90, 130)
        d.polygon([(x, y - 90), (x + 52, y - 30), (x + 52, y + 90), (x - 52, y + 90), (x - 52, y - 30)], fill=col)
    if t > 1.6:
        T(d, (W // 2, 760), 'قرابة 9 من كل 10', 92, YEL)
        T(d, (W // 2, 860), 'تملكها الدول الثلاث مجتمعة', 46, WH)
    return im
def g_paper(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    k = eo(t / 0.6); y0 = int(1100 - 900 * k)
    panel(d, [560, y0, 1360, y0 + 820], (246, 244, 236))
    T(d, (960, y0 + 90), 'إعلان نحو السلام', 60, (20, 20, 30))
    T(d, (960, y0 + 160), 'الصين • روسيا • الولايات المتحدة', 36, RED)
    for i in range(4):
        if t > 0.8 + i * 0.35:
            yy = y0 + 270 + i * 120
            d.ellipse([1180, yy - 34, 1248, yy + 34], fill=RED); T(d, (1214, yy + 2), str(i + 1), 40)
            d.rounded_rectangle([640, yy - 14, 1150, yy + 14], 8, fill=(200, 200, 205))
    return im
def g_chapter(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    k = eo(t / 0.45); x = int(W + 200 - (W // 2 + 200) * k)
    d.rectangle([0, 470, W, 610], fill=(0, 0, 0))
    d.rectangle([W - int((W) * k), 470, W, 478], fill=RED)
    T(d, (x + 80, 540), a['t'], 84, WH)
    T(d, (x + 80 + tw(a['t'], 84) / 2 + 90, 540), str(a['n']), 84, YEL)
    return im
def g_timeline(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    ev = [('أغسطس 2025', 'ترامب وبوتين', 'ألاسكا'), ('مايو 2026', 'ترامب في بكين', 'الصين'), ('سبتمبر 2026', 'شي في البيت الأبيض', 'واشنطن'), ('19 نوفمبر 2026', 'أول قمة ثلاثية', 'شنجن')]
    T(d, (W - 160, 150), 'الطريق إلى شنجن', 60, WH, 'rm')
    k = a.get('k', 1); xs = [W - 300 - i * 440 for i in range(4)]
    prog = eo(t / 1.2)
    d.line([(xs[0], 560), (xs[0] - (xs[0] - xs[3]) * prog, 560)], fill=(90, 110, 150), width=6)
    for i, (dt, s1, s2) in enumerate(ev):
        if t < 0.25 * i: continue
        hi = (k == 1 and i == 0) or (k == 3 and i >= 2)
        col = YEL if hi else WH
        d.ellipse([xs[i] - 26, 534, xs[i] + 26, 586], fill=RED if hi else (90, 110, 150))
        T(d, (xs[i], 470), dt, 44, col); T(d, (xs[i], 660), s1, 42, WH); T(d, (xs[i], 720), s2, 36, MU)
    return im
def g_context(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    items = [('2022', 'حرب في أوكرانيا'), ('فبراير 2026', 'حرب مع إيران'), ('~20%', 'من نفط العالم يمرّ من هرمز')]
    for i, (n, s) in enumerate(items):
        if t < 0.3 + i * 1.6: continue
        k = eo((t - 0.3 - i * 1.6) / 0.5); y = 250 + i * 230
        x1 = W - 200; x0 = int(x1 - 1300 * k)
        panel(d, [x0, y, x1, y + 170], (255, 255, 255))
        d.rectangle([x1 - 16, y, x1, y + 170], fill=RED)
        if k > 0.7: T(d, (x1 - 60, y + 85), s, 54, (20, 20, 30), 'rm'); T(d, (x0 + 60, y + 85), n, 64, RED, 'lm')
    return im
def g_clock(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    cx, cy, R = 960, 470, 250
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=WH, width=10)
    for i in range(12):
        an = i / 12 * 2 * math.pi; d.line([(cx + math.sin(an) * (R - 30), cy - math.cos(an) * (R - 30)), (cx + math.sin(an) * (R - 8), cy - math.cos(an) * (R - 8))], fill=WH, width=6)
    m = 30 + 80 * eo((t - 0.4) / max(1, D - 1.6)); hh = 8 + m / 60
    ang0 = 30 / 60 * 2 * math.pi; ang1 = (m % 60) / 60 * 2 * math.pi
    if m > 30: d.pieslice([cx - R + 14, cy - R + 14, cx + R - 14, cy + R - 14], math.degrees(ang0) - 90, math.degrees(ang0 + (m - 30) / 60 * 2 * math.pi) - 90, fill=(140, 30, 40))
    d.line([(cx, cy), (cx + math.sin(ang1) * (R - 50), cy - math.cos(ang1) * (R - 50))], fill=YEL, width=10)
    ha = (hh % 12) / 12 * 2 * math.pi; d.line([(cx, cy), (cx + math.sin(ha) * (R - 120), cy - math.cos(ha) * (R - 120))], fill=WH, width=14)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=RED)
    mm = int(m) % 60; T(d, (960, 800), '%02d:%02d GMT' % (int(hh), mm), 64, YEL)
    if t > D - 1.4: T(d, (960, 880), 'نحو 80 دقيقة', 50, WH)
    return im
PTS = [('الأمم المتحدة', 'إصلاح مجلس الأمن'), ('الطاقة', 'زيادة المشتقات النفطية'), ('المحاكم الدولية', 'حصانة المسؤولين'), ('السلاح النووي', 'حرب لا يمكن كسبها')]
def g_points(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im); h = a.get('h', 0)
    T(d, (W - 160, 140), 'إعلان شنجن: 4 نقاط', 60, WH, 'rm')
    for i, (s1, s2) in enumerate(PTS):
        st = 0.15 * i if h else 0.5 * i
        if t < st: continue
        k = eo((t - st) / 0.4); y = 250 + i * 165
        on = (h == i + 1); x1 = W - 200; x0 = int(x1 - 1300 * k)
        panel(d, [x0, y, x1, y + 135], (255, 255, 255) if (on or h == 0) else (70, 85, 115))
        d.rounded_rectangle([x1 - 135, y, x1, y + 135], 18, fill=RED if (on or h == 0) else (90, 100, 130))
        if k > 0.6:
            T(d, (x1 - 67, y + 70), str(i + 1), 70)
            c = (20, 20, 30) if (on or h == 0) else (190, 200, 215)
            T(d, (x1 - 175, y + 50), s1, 50, c, 'rm'); T(d, (x1 - 175, y + 102), s2, 34, RED if on else (MU if h else (90, 90, 100)), 'rm')
    return im
def g_question(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    for i, s in enumerate(['أيّ إصلاح؟', 'متى؟', 'كيف؟']):
        st = 0.5 + i * 1.1
        if t < st: continue
        k = eo((t - st) / 0.35); sz = int(110 * (0.6 + 0.4 * k))
        T(d, (W - 380 - i * 560, 520), s, sz, YEL if i == 0 else WH)
    T(d, (960, 820), 'الوثيقة لا تجيب', 50, MU)
    return im
def g_oil(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 150), 'سعر برميل «برنت»', 60, WH, 'rm')
    # simple price curve: pre-war ~70 -> peak ~120 -> now
    pts = [(0, 72), (0.15, 74), (0.25, 100), (0.35, 118), (0.45, 104), (0.6, 96), (0.75, 85), (1.0, 88)]
    pr = eo(t / max(1.5, D * 0.7))
    X = lambda u: 260 + u * 1400; Y = lambda v: 900 - (v - 50) * 7.5
    d.line([(260, 900), (1660, 900)], fill=(90, 110, 150), width=3)
    for v in (60, 80, 100, 120):
        d.line([(260, Y(v)), (1660, Y(v))], fill=(30, 50, 85), width=2); T(d, (230, Y(v)), str(v), 30, MU, 'rm')
    seg = [p for p in pts if p[0] <= pr]
    if pr > 0 and len(seg) < len(pts):
        a0, b0 = seg[-1], pts[len(seg)]; u = (pr - a0[0]) / (b0[0] - a0[0]); seg = seg + [(pr, a0[1] + (b0[1] - a0[1]) * u)]
    if len(seg) > 1: d.line([(X(u), Y(v)) for u, v in seg], fill=YEL, width=8, joint='curve')
    if pr > 0.35:
        d.ellipse([X(0.35) - 14, Y(118) - 14, X(0.35) + 14, Y(118) + 14], fill=RED)
        T(d, (X(0.35), Y(118) - 60), 'قرابة 120 دولارًا', 46, WH)
    T(d, (X(0.0), 950), 'قبل الحرب', 32, MU); T(d, (X(0.35), 950), 'ذروة أزمة هرمز', 32, MU)
    return im
def g_icc(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    k = eo(t / 0.6); y0 = int(1100 - 880 * k)
    panel(d, [520, y0, 1400, y0 + 700], (246, 244, 236))
    T(d, (960, y0 + 90), 'المحكمة الجنائية الدولية', 56, (20, 20, 30))
    d.line([(600, y0 + 150), (1320, y0 + 150)], fill=(180, 180, 180), width=3)
    T(d, (960, y0 + 250), 'مذكرة توقيف', 80, RED)
    T(d, (960, y0 + 360), 'بحق فلاديمير بوتين', 54, (20, 20, 30))
    T(d, (960, y0 + 440), 'مارس 2023', 50, (90, 90, 100))
    if t > 1.6:
        d.rounded_rectangle([700, y0 + 520, 1220, y0 + 620], 12, outline=RED, width=6)
        T(d, (960, y0 + 572), 'موسكو ترفض الاتهامات', 44, RED)
    return im
def flag(d, box, kind):
    x0, y0, x1, y1 = box; w = x1 - x0; h = y1 - y0
    if kind == 'us':
        for i in range(13): d.rectangle([x0, y0 + i * h / 13, x1, y0 + (i + 1) * h / 13], fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
        d.rectangle([x0, y0, x0 + w * 0.4, y0 + h * 7 / 13], fill=(60, 59, 110))
    elif kind == 'cn':
        d.rectangle(box, fill=(222, 41, 16)); cx, cy, r = x0 + w * 0.17, y0 + h * 0.3, h * 0.15
        d.regular_polygon((cx, cy, r), 5, fill=(255, 222, 0))
    elif kind == 'ru':
        for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 43, 30)]): d.rectangle([x0, y0 + i * h / 3, x1, y0 + (i + 1) * h / 3], fill=c)
def g_notmembers(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (960, 200), 'أعضاء في المحكمة الجنائية الدولية؟', 60, WH)
    for i, (k, n) in enumerate([('us', 'الولايات المتحدة'), ('cn', 'الصين'), ('ru', 'روسيا')]):
        st = 0.3 + i * 0.5
        if t < st: continue
        x = 1460 - i * 500; flag(d, [x - 170, 380, x + 170, 600], k); T(d, (x, 660), n, 46)
        if t > st + 0.4:
            d.line([(x - 120, 400), (x + 120, 580)], fill=RED, width=18); d.line([(x + 120, 400), (x - 120, 580)], fill=RED, width=18)
    if t > 2.2: T(d, (960, 820), 'ليست أعضاء', 80, YEL)
    return im
def g_quote(t, D, a):
    if a.get('img'):
        im = Image.new('RGB', (W, H), NAVY); ph = photo(a['img'], (760, 1080)); im.paste(ph, (W - 760, 0))
        d = ImageDraw.Draw(im); d.rectangle([W - 770, 0, W - 760, H], fill=RED); xr = W - 860
    else:
        im = bg(t); d = ImageDraw.Draw(im); xr = W - 200
    k = eo(t / 0.5); q = a['q']; sz = 76 if len(q) < 26 else 62
    lines = wrap(q, sz, xr - 220)
    T(d, (xr, 260), '“', 200, RED, 'rm')
    for i, l in enumerate(lines):
        if k > 0.2: T(d, (xr - int(60 * (1 - k)), 420 + i * (sz + 30)), l, sz, WH, 'rm')
    if t > 0.7:
        y = 420 + len(lines) * (sz + 30) + 50; d.rectangle([xr - 8, y, xr, y + 60], fill=RED)
        T(d, (xr - 30, y + 32), a['who'], 40, YEL, 'rm')
    return im
def g_count(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    v = int(a['a'] * eo((t - 0.2) / 1.6))
    T(d, (960, 330), a['y'], 70, MU)
    T(d, (960, 520), f'{v:,}', 190, YEL)
    T(d, (960, 700), a['cap'], 50, WH)
    return im
def g_share86(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 150), 'من يملك الرؤوس النووية؟', 60, WH, 'rm')
    p = eo((t - 0.2) / 1.4)
    d.rounded_rectangle([260, 480, 1660, 600], 20, fill=(50, 66, 100))
    w = int(1400 * 0.86 * p); d.rounded_rectangle([1660 - w, 480, 1660, 600], 20, fill=RED)
    T(d, (1660 - w / 2 if w > 300 else 1400, 540), f'{int(86 * p)}%', 70)
    T(d, (1660, 660), 'أمريكا + روسيا', 46, WH, 'rm'); T(d, (260, 660), 'باقي العالم', 40, MU, 'lm')
    if t > 1.8: T(d, (960, 820), 'من أصل نحو 12187 رأسًا', 50, YEL)
    return im
def g_cap1550(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (960, 230), 'معاهدة «نيو ستارت» — 2010', 60, WH)
    T(d, (960, 470), '1550', 220, YEL)
    T(d, (960, 650), 'رأسًا استراتيجيًا منتشرًا كحدٍّ أقصى لكل طرف', 48, WH)
    return im
def g_expired(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (960, 360), 'نيو ستارت', 120, WH)
    if t > 0.6:
        k = eo((t - 0.6) / 0.25); im2 = Image.new('RGBA', (900, 220), (0, 0, 0, 0)); d2 = ImageDraw.Draw(im2)
        d2.rounded_rectangle([10, 10, 890, 210], 20, outline=RED, width=14); d2.text((450, 112), 'انتهت — فبراير 2026', font=f(84), fill=RED, anchor='mm', direction='rtl')
        im2 = im2.rotate(-8, expand=True); s = 1.6 - 0.6 * k; im2 = im2.resize((int(im2.width * s), int(im2.height * s)))
        im.paste(im2, (960 - im2.width // 2, 600 - im2.height // 2), im2)
    if t > 2.0: T(d, (960, 900), 'لا سقف قانونيًا اليوم', 50, YEL)
    return im
ABS = [('أوكرانيا', 'حرب منذ 2022'), ('إيران', 'حرب منذ فبراير 2026'), ('كوريا الشمالية', 'برنامج نووي'), ('تايوان', 'أكثر الملفات حساسية')]
def g_absent(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im); k = a.get('k', 3)
    T(d, (W - 160, 140), 'غائب عن نص الإعلان', 60, WH, 'rm')
    for i, (s1, s2) in enumerate(ABS[:k]):
        st = (0.4 + i * 1.0) if k == 3 else (0 if i < 3 else 0.6)
        if t < st: continue
        y = 260 + i * 165; x1 = W - 200; x0 = 520
        panel(d, [x0, y, x1, y + 135], (255, 255, 255))
        T(d, (x1 - 40, y + 50), s1, 52, (20, 20, 30), 'rm'); T(d, (x1 - 40, y + 102), s2, 32, (90, 90, 100), 'rm')
        if t > st + 0.35:
            cx = x0 + 90; d.line([(cx - 40, y + 28), (cx + 40, y + 108)], fill=RED, width=16); d.line([(cx + 40, y + 28), (cx - 40, y + 108)], fill=RED, width=16)
    return im
def g_intent(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (1360, 470), 'إعلان نوايا', 96, YEL)
    if t > 0.8: T(d, (960, 470), '≠', 120, WH)
    if t > 1.4:
        T(d, (560, 470), 'معاهدة سلام', 96, WH)
    if t > 2.0: T(d, (960, 700), 'لا مواعيد • لا آليات • لا التزامات', 50, MU)
    return im
def g_hormuz(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 140), 'مضيق هرمز', 64, WH, 'rm')
    # schematic coastlines (not a political map)
    d.polygon([(200, 300), (1000, 280), (1250, 420), (1380, 560), (1100, 600), (800, 520), (200, 560)], fill=(60, 74, 60))   # north shore (schematic)
    d.polygon([(300, 1000), (900, 760), (1200, 700), (1330, 640), (1500, 700), (1700, 1000)], fill=(80, 74, 56))              # south shore (schematic)
    p = eo((t - 0.4) / 1.6)
    for i in range(6):
        u = (p * 1.0 + i / 6) % 1.0
        x = 1700 - u * 1300; y = 640 + 40 * math.sin(u * 6)
        d.rounded_rectangle([x - 34, y - 12, x + 34, y + 12], 6, fill=YEL)
    T(d, (960, 880), 'نحو خُمس نفط العالم يمرّ من هنا', 54, WH)
    T(d, (960, 950), 'رسم توضيحي', 26, MU)
    return im
SC = [('السيناريو الأول', 'بداية مسار', 'حوار نووي + لقاءات جديدة — قمة العشرين في ديسمبر'), ('السيناريو الثاني', 'صورة بلا مضمون', 'الوثيقة حبر على ورق… والحروب مستمرة'), ('السيناريو الثالث', 'تفاهمات الكبار', 'اتفاقات بين ثلاث عواصم… على حساب الآخرين')]
def g_scen(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im); k = a['k']
    for i in range(3):
        x1 = W - 120 - i * 580; x0 = x1 - 540; on = (i + 1 == k); done = i + 1 < k
        if i + 1 > k: col = (40, 55, 85)
        else: col = (255, 255, 255) if on else (90, 105, 135)
        kk = eo(t / 0.4) if on else 1
        y0 = 260 + int(60 * (1 - kk))
        panel(d, [x0, y0, x1, y0 + 560], col)
        if i + 1 <= k:
            c1 = RED if on else WH; c2 = (20, 20, 30) if on else WH
            T(d, ((x0 + x1) / 2, y0 + 80), SC[i][0], 40, c1)
            T(d, ((x0 + x1) / 2, y0 + 190), SC[i][1], 58, c2)
            for j, l in enumerate(wrap(SC[i][2], 36, 460)): T(d, ((x0 + x1) / 2, y0 + 310 + j * 56), l, 36, (60, 60, 70) if on else (200, 210, 225))
        else:
            T(d, ((x0 + x1) / 2, y0 + 280), str(i + 1), 120, (70, 85, 115))
    return im
def g_final(t, D, a):
    im = Image.open('m/img/003.jpg').convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(10))
    im = Image.blend(im, Image.new('RGB', (W, H), NAVY), 0.6); d = ImageDraw.Draw(im)
    T(d, (960, 420), 'بداية سلام…', 100, WH)
    if t > 1.2: T(d, (960, 600), 'أم بداية تقاسم جديد للعالم؟', 90, YEL)
    return im
def g_comment(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    panel(d, [460, 330, 1460, 700], (255, 255, 255)); d.polygon([(1300, 700), (1380, 700), (1260, 800)], fill=(255, 255, 255))
    T(d, (960, 470), 'ما رأيك؟', 90, (20, 20, 30)); T(d, (960, 600), 'اكتب في التعليقات', 56, RED)
    return im
def g_subscribe(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    zw = tw('Zone', 110); rw = tw('Rawi ', 110)
    d.text((960 - (zw + rw) / 2, 330), 'Rawi ', font=f(110), fill=YEL, anchor='lm'); d.text((960 - (zw + rw) / 2 + rw, 330), 'Zone', font=f(110), fill=WH, anchor='lm')
    s = 1 + 0.06 * math.sin(t * 6) if t > 0.6 else 1
    w = int(620 * s); h = int(130 * s); d.rounded_rectangle([960 - w // 2, 560 - h // 2, 960 + w // 2, 560 + h // 2], 65, fill=RED)
    T(d, (960, 563), 'اشترك وفعّل الجرس', int(60 * s))
    T(d, (960, 760), 'الترند القادم… لا يفوتك', 50, WH)
    return im

def g_title(t, D, a):
    im = Image.open('m/f_title.jpg').convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(8))
    im = Image.blend(im, Image.new('RGB', (W, H), NAVY), 0.5); d = ImageDraw.Draw(im)
    k = eo(t / 0.5); w = int(900 * k)
    d.rectangle([W // 2 - w // 2, 300, W // 2 + w // 2, 430], fill=RED)
    if t > 0.25: T(d, (W // 2, 367), 'تحليل', 90)
    if t > 0.6: T(d, (W // 2, 540), 'الأسد الإفريقي', 110, WH, stroke=3)
    if t > 1.0: T(d, (W // 2, 680), 'المغرب… مختبر حروب المستقبل؟', 60, YEL, stroke=2)
    return im
def g_q2(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    for i, s in enumerate(['لماذا صحراء المغرب؟', 'وماذا يربح المغرب؟']):
        st = 0.3 + i * 1.6
        if t < st: continue
        k = eo((t - st) / 0.4); y = 380 + i * 220
        x1 = W - 260; x0 = int(x1 - 1100 * k)
        panel(d, [x0, y, x1, y + 150], (255, 255, 255))
        d.rounded_rectangle([x1 - 150, y, x1, y + 150], 18, fill=RED)
        if k > 0.6: T(d, (x1 - 75, y + 78), '؟', 90); T(d, (x1 - 190, y + 78), s, 64, (20, 20, 30), 'rm')
    return im
def g_stat2(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 150), 'الأسد الإفريقي 2026', 58, WH, 'rm')
    v1 = int(5600 * eo((t - 0.2) / 1.4)); v2 = int(40 * eo((t - 0.6) / 1.2))
    T(d, (1380, 470), f'{v1}', 170, YEL); T(d, (1380, 620), 'أكثر من … عسكري', 56, WH)
    T(d, (560, 470), f'{v2}', 170, YEL); T(d, (560, 620), 'نحو … دولة', 56, WH)
    if t > 1.4: T(d, (960, 820), '20 أبريل — 8 مايو 2026', 54, MU)
    return im
def g_countries(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 150), 'أين جرت المناورات؟', 58, WH, 'rm')
    C = ['المغرب', 'تونس', 'السنغال', 'غانا']
    for i, c in enumerate(C):
        st = 0.2 + i * 0.3
        if t < st: continue
        k = eo((t - st) / 0.4); x = W - 330 - i * 400; y = 470
        hi = (i == 0); w = 340; h = int(150 * k)
        d.rounded_rectangle([x - w // 2, y - h // 2, x + w // 2, y + h // 2], 20, fill=RED if hi else (60, 80, 120))
        if k > 0.7: T(d, (x, y + 4), c, 62, WH)
    if t > 1.8:
        T(d, (960, 700), 'أكادير  •  رأس درعة  •  طانطان', 58, YEL)
        T(d, (960, 800), 'قلب المناورات في جنوب المغرب', 44, WH)
    return im
def g_count2(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    v = a['a'] * eo((t - 0.2) / 1.4); fmt = a.get('fmt', '{:,.0f}')
    if a.get('y'): T(d, (960, 300), a['y'], 66, MU)
    T(d, (960, 500), a.get('pre', '') + fmt.format(v) + a.get('suf', ''), 190, YEL)
    for i, l in enumerate(wrap(a['cap'], 52, 1500)): T(d, (960, 690 + i * 70), l, 52, WH)
    return im
def g_first(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    k = eo(t / 0.5); redtag(d, (W - 200, 220), 'لأول مرة', 64)
    if t > 0.4: T(d, (W - 200, 470), 'سرب «أباتشي» المغربي', 84, WH, 'rm')
    if t > 0.9: T(d, (W - 200, 590), 'يحلّق مع سلاح الجو الأمريكي', 70, YEL, 'rm')
    return im
def g_four(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 140), 'كيف تُصطاد المسيّرات؟', 60, WH, 'rm')
    it = [('كشف', 'رادارات وحساسات'), ('تدمير مباشر', 'صواريخ ومقذوفات'), ('تشويش إلكتروني', 'قطع الاتصال والتوجيه'), ('حماية سلبية', 'تمويه وتحصين')]
    for i, (s1, s2) in enumerate(it):
        st = 0.3 + 0.55 * i
        if t < st: continue
        k = eo((t - st) / 0.4); y = 260 + i * 170; x1 = W - 200; x0 = int(x1 - 1300 * k)
        panel(d, [x0, y, x1, y + 140], (255, 255, 255)); d.rounded_rectangle([x1 - 140, y, x1, y + 140], 18, fill=RED)
        if k > 0.6: T(d, (x1 - 70, y + 72), str(i + 1), 70); T(d, (x1 - 180, y + 52), s1, 54, (20, 20, 30), 'rm'); T(d, (x1 - 180, y + 108), s2, 36, RED, 'rm')
    return im
def g_tl(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 150), 'طانطان: الجدول الزمني', 60, WH, 'rm')
    ev = [('فبراير — مارس 2027', 'العروض الأولى'), ('أبريل — مايو 2027', 'تقييم عملي خلال الأسد الإفريقي 2027')]
    xs = [1380, 540]; pr = eo(t / 1.0)
    d.line([(xs[0], 560), (xs[0] - (xs[0] - xs[1]) * pr, 560)], fill=(90, 110, 150), width=8)
    for i, (a1, a2) in enumerate(ev):
        if t < 0.2 + i * 0.8: continue
        d.ellipse([xs[i] - 30, 530, xs[i] + 30, 590], fill=RED)
        T(d, (xs[i], 460), a1, 54, YEL)
        for j, l in enumerate(wrap(a2, 44, 700)): T(d, (xs[i], 660 + j * 60), l, 44, WH)
    return im
def g_x5(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 150), 'حلف الناتو — قبل نهاية 2027', 58, WH, 'rm')
    n = min(5, int(eo(t / 1.4) * 5.99))
    for i in range(5):
        x = 1500 - i * 240; col = YEL if i < n else (70, 90, 130)
        d.ellipse([x - 50, 380, x + 50, 480], fill=col); d.rounded_rectangle([x - 75, 495, x + 75, 640], 40, fill=col)
    if t > 1.5: T(d, (960, 760), 'خمسة أضعاف', 84, YEL); T(d, (960, 860), 'عدد مشغّلي المسيّرات المدرَّبين', 56, WH)
    return im
def g_royal(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    redtag(d, (W - 200, 200), '18 نوفمبر 2026', 50)
    if t > 0.4: T(d, (W - 200, 430), 'جلسة عمل بالقصر الملكي بالرباط', 72, WH, 'rm')
    if t > 0.9: T(d, (W - 200, 560), '«عرض المغرب»', 96, YEL, 'rm')
    if t > 1.4: T(d, (W - 200, 690), 'خارطة طريق الصناعة الوطنية للدفاع والأمن', 52, WH, 'rm')
    return im
def g_pct(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im); p = a['p'] * eo((t - 0.2) / 1.3)
    T(d, (W - 160, 150), 'أهداف 2035', 60, WH, 'rm')
    cx, cy, r = 600, 560, 230
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 80, 120), width=40)
    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * p / 100, fill=YEL, width=40)
    T(d, (cx, cy), f'{p:.0f}%', 120, YEL)
    for i, l in enumerate(wrap(a['cap'], 58, 820)): T(d, (W - 200, 480 + i * 80), l, 58, WH, 'rm')
    return im
def g_sectors(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 140), 'القطاعات ذات الأولوية', 60, WH, 'rm')
    it = ['المسيّرات والأنظمة الذاتية', 'الإلكترونيات الدفاعية', 'الدفاع السيبراني', 'الذكاء الاصطناعي']
    for i, s1 in enumerate(it):
        st = 0.3 + 0.5 * i
        if t < st: continue
        k = eo((t - st) / 0.4); y = 260 + i * 170; x1 = W - 200; x0 = int(x1 - 1200 * k)
        panel(d, [x0, y, x1, y + 140], (255, 255, 255)); d.rounded_rectangle([x1 - 140, y, x1, y + 140], 18, fill=RED)
        if k > 0.6: T(d, (x1 - 70, y + 72), str(i + 1), 70); T(d, (x1 - 180, y + 72), s1, 56, (20, 20, 30), 'rm')
    return im
def g_projects(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im); h = a.get('h', 1)
    T(d, (W - 160, 140), 'مشاريع بدأت على الأرض', 60, WH, 'rm')
    it = [('برشيد', 'مدرعات «واب» 8×8'), ('سيدي يحيى', 'ذخائر متوسطة وكبيرة العيار'), ('بنسليمان', 'تصنيع وصيانة المسيّرات')]
    for i, (c, s) in enumerate(it):
        st = (0.3 + 0.5 * i) if h == 1 else 0.1 * i
        if t < st: continue
        on = (h == 1 and i == 0) or (h == 2 and i > 0)
        k = eo((t - st) / 0.4); y = 290 + i * 200; x1 = W - 200; x0 = int(x1 - 1300 * k)
        panel(d, [x0, y, x1, y + 160], (255, 255, 255) if on else (70, 85, 115))
        d.rounded_rectangle([x1 - 320, y, x1, y + 160], 18, fill=RED if on else (90, 100, 130))
        if k > 0.6: T(d, (x1 - 160, y + 82), c, 54, WH); T(d, (x1 - 360, y + 82), s, 52, (20, 20, 30) if on else (190, 200, 215), 'rm')
    return im
def g_zones(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 140), 'مناطق صناعية للدفاع', 60, WH, 'rm')
    Z = [('النواصر', 'انطلقت'), ('سيدي يحيى', 'انطلقت'), ('بنجرير', 'مبرمجة'), ('بنسليمان', 'مبرمجة')]
    for i, (z, s) in enumerate(Z):
        st = 0.2 + 0.35 * i
        if t < st: continue
        k = eo((t - st) / 0.4); x = 1520 - i * 380; y = 560; h = int(260 * k)
        d.rounded_rectangle([x - 170, y - h // 2, x + 170, y + h // 2], 22, fill=RED if s == 'انطلقت' else (60, 80, 120))
        if k > 0.7: T(d, (x, y - 30), z, 56, WH); T(d, (x, y + 50), s, 40, YEL)
    return im
def g_final2(t, D, a):
    im = Image.open('m/f_final.jpg').convert('RGB').resize((W, H)).filter(ImageFilter.GaussianBlur(10))
    im = Image.blend(im, Image.new('RGB', (W, H), NAVY), 0.6); d = ImageDraw.Draw(im)
    T(d, (960, 420), 'مُنتِجٌ لتكنولوجيا الدفاع…', 96, WH, stroke=2)
    if t > 1.4: T(d, (960, 600), 'أم أفضل حقل تجارب لها؟', 96, YEL, stroke=2)
    return im
CARDS = {k[2:]: v for k, v in globals().items() if k.startswith('g_')}
def frames(kind, args, dur, fps=25):
    fn = CARDS[kind]; n = max(1, int(round(dur * fps)))
    for i in range(n): yield fn(i / fps, dur, args)
