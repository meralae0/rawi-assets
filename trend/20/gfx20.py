# Tableaux d'analyse ترند 20 — chèvres IA (clips IA figés/annotés sur fond de marque)
import sys
sys.path.insert(0, '/home/claude/rawi-assets/trend/11')
from gfx import *
from PIL import Image, ImageDraw, ImageFilter
DK = (20, 20, 30)
_cache = {}
def cf(c, t):
    i = min(250, max(1, int(round(t * 25)) + 1)); k = (c, i)
    if k in _cache: return _cache[k]
    im = Image.open(f'/home/claude/t20/f{c.lower()}/{i:03d}.jpg').convert('RGB')
    if c == 'B':
        box = (0, 20, 130, 245); r = im.crop(box).filter(ImageFilter.GaussianBlur(40)).resize((8, 10)).resize((130, 225), Image.BILINEAR)
        im.paste(r.filter(ImageFilter.GaussianBlur(12)), box[:2]); im = im.crop((0, 30, 720, 1110))
    else:
        im = im.crop((0, 0, 720, 930))
    if len(_cache) > 400: _cache.clear()
    _cache[k] = im; return im
def framed(base, im, x1, y0, h, label=None):
    w = int(im.width * h / im.height); x0 = x1 - w
    d = ImageDraw.Draw(base); d.rounded_rectangle([x0 - 8, y0 - 8, x1 + 8, y0 + h + 8], 14, fill=(255, 255, 255))
    base.paste(im.resize((w, h), Image.LANCZOS), (x0, y0))
    if label: redtag(d, (x1 + 8, y0 - 40), label, 34)
    return x0, w / im.width
def ring(d, cx, cy, r, k, col=RED):
    rr = r * (0.6 + 0.4 * eo(k)); d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=9)
def b_play(t, D, a):
    c = a['clip']; s0 = a.get('s0', 0); sp = a.get('sp', 1); fz = a.get('freeze')
    tl = t if fz is None else min(t, fz)
    im = bg(t); d = ImageDraw.Draw(im)
    fr = cf(c, s0 + tl * sp)
    x0, sc = framed(im, fr, W - 130, 100, 900, a.get('label', 'المقطع المتداول'))
    d = ImageDraw.Draw(im)
    if a.get('tag'): redtag(d, (x0 - 90, 190), a['tag'], 50)
    for i, s in enumerate(a.get('text', [])):
        st = a.get('tt', 0.5) + 0.45 * i
        if t > st: T(d, (x0 - 90, 380 + i * 130), s, 82 if i == 0 else 64, YEL if i == 0 else WH, 'rm', stroke=4)
    if a.get('ring') and t > a.get('rt', 0.3):
        cx, cy, r = a['ring']; ring(d, x0 + cx * sc, 100 + cy * sc, r * sc, (t - a.get('rt', 0.3)) / 0.4)
    if a.get('stamp') and t > 0.4:
        k = eo((t - 0.4) / 0.35); s = 1 + 1.2 * (1 - k)
        st = Image.new('RGBA', (760, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([10, 10, 750, 190], 20, outline=RED, width=14, fill=(255, 255, 255, 230))
        T(sd, (380, 104), a['stamp'], 92, RED)
        st = st.rotate(8, expand=True, resample=Image.BICUBIC); st = st.resize((int(st.width * s * 0.9), int(st.height * s * 0.9)))
        im.paste(st, (int(x0 + 300 - st.width / 2), int(560 - st.height / 2)), st)
    return im
def b_pair(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    redtag(d, (W - 140, 70), a['title'], 52)
    xs = [W - 260, W - 260 - 560 - 160]
    for j, (c, ts) in enumerate(a['frames']):
        x0, sc = framed(im, cf(c, ts), xs[j], 210, 690, a['labels'][j]); d = ImageDraw.Draw(im)
        cx = xs[j] - 230
        if a.get('count'):
            v = min(10.0, 10.0 * eo((t - 0.3) / 1.8)) if t > 0.3 else 0
            T(d, (cx, 975), f'00:{v:05.2f}'.replace('.', ':') if False else f'{v:0.2f} ث', 70, YEL, stroke=4)
        elif a.get('caps'):
            if t > 0.6 + 0.4 * j: T(d, (cx, 975), a['caps'][j], 66, a['capcol'][j], stroke=4)
    return im
def b_recipe(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    redtag(d, (W - 140, 110), 'العلامة 2: الوصفة نفسها', 52)
    labs = ['جرف', 'سقوط طويل', 'نهر فيروزي']; rows = [('A', [0.4, 3.0, 9.3]), ('B', [0.3, 4.6, 8.6])]
    for r, (c, tss) in enumerate(rows):
        y0 = 190 + r * 440; T(d, (W - 150, y0 + 170), f'المقطع {r + 1}', 50, WH, 'rm')
        for j, ts in enumerate(tss):
            st = 0.3 + 0.35 * j + (a.get('d2', 3.8) if r == 1 else 0)
            if t < st: continue
            x1 = W - 450 - j * 470; x0, sc = framed(im, cf(c, ts), x1, y0, 330); d = ImageDraw.Draw(im)
            T(d, ((x0 + x1) / 2, y0 + 380), labs[j], 46, YEL, stroke=3)
    return im
def b_signs(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 140), 'خمس علامات تكشف الفيديو المصنوع', 64, WH, 'rm')
    items = ['المدّة: عشر ثوانٍ بالضبط', 'التكرار: الوصفة نفسها', 'الجسم: متصلّب بلا حركة', 'الكاميرا: تسقط مع الحيوان', 'الهبوط: بلا غبار ولا حجارة']
    for i, s in enumerate(items):
        st = 0.2 + 0.55 * i
        if t < st: continue
        k = eo((t - st) / 0.35); y = 260 + i * 150; x1 = W - 200; x0 = int(x1 - 1200 * k); hh = 120
        panel(d, [x0, y, x1, y + hh], (255, 255, 255)); d.rounded_rectangle([x1 - hh, y, x1, y + hh], 16, fill=RED)
        if k > 0.6: T(d, (x1 - hh // 2, y + hh // 2 + 2), str(i + 1), 60); T(d, (x1 - hh - 40, y + hh // 2 + 2), s, 52, DK, 'rm')
    return im
def frames20(kind, a, dur):
    fn = {'play': b_play, 'pair': b_pair, 'recipe': b_recipe, 'signs': b_signs}[kind]
    for i in range(int(round(dur * 25))): yield fn(i / 25, dur, a)
