# Cartes graphiques ترند 19 — industrie de défense marocaine (style des cartes ترند 11)
import sys
sys.path.insert(0, '/home/claude/rawi-assets/trend/11')
from gfx import *  # bg, T, tw, panel, redtag, wrap, eo, ease, W, H, couleurs
from PIL import Image, ImageDraw, ImageFilter

DK = (20, 20, 30)

def g_date(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    redtag(d, (W - 200, 200), 'الأربعاء 25 نوفمبر 2026', 50)
    if t > 0.4: T(d, (W - 200, 430), 'القصر الملكي بالرباط', 84, WH, 'rm')
    if t > 0.9: T(d, (W - 200, 570), 'توقيع اتفاقيتين', 96, YEL, 'rm')
    if t > 1.4: T(d, (W - 200, 700), 'خارطة طريق الصناعة الوطنية للدفاع والأمن', 52, WH, 'rm')
    return im

def _list(t, title, items, tag=None, step=0.35):
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 140), title, 60, WH, 'rm')
    if tag: redtag(d, (W - 160, 200), tag, 40)
    n = len(items); hh = min(130, int(700 / n)); y0 = 300 if tag else 260
    for i, s in enumerate(items):
        st = 0.25 + step * i
        if t < st: continue
        k = eo((t - st) / 0.35); y = y0 + i * (hh + 14); x1 = W - 200; x0 = int(x1 - 1250 * k)
        panel(d, [x0, y, x1, y + hh], (255, 255, 255)); d.rounded_rectangle([x1 - hh, y, x1, y + hh], 16, fill=RED)
        if k > 0.6:
            T(d, (x1 - hh // 2, y + hh // 2 + 2), str(i + 1), int(hh * 0.5)); T(d, (x1 - hh - 40, y + hh // 2 + 2), s, int(hh * 0.4), DK, 'rm')
    return im

def g_sign1(t, D, a):
    return _list(t, 'الاتفاقية الأولى: التمويل', ['وزارة الداخلية', 'وزارة الاقتصاد والمالية', 'وزارة الصناعة والتجارة', 'إدارة الدفاع الوطني', 'صندوق الإيداع والتدبير', 'صندوق الحسن الثاني', 'جامعة محمد السادس متعددة التخصصات'], 'نحو 22 مليار درهم', 0.9)

def g_sign2(t, D, a):
    return _list(t, 'الاتفاقية الثانية: القطاع الخاص', ['بنك المغرب', 'التجمع المهني لبنوك المغرب', 'بورصة الدار البيضاء', 'الهيئة المغربية لسوق الرساميل', 'الاتحاد العام لمقاولات المغرب'], None, 0.9)

def g_agency(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    redtag(d, (W - 200, 170), 'وكالة جديدة', 46)
    k = eo((t - 0.2) / 0.6)
    if t > 0.2:
        w = int(760 * k); d.rounded_rectangle([960 - w // 2, 330, 960 + w // 2, 560], 26, fill=YEL)
        if k > 0.7: T(d, (960, 445), '«دِفاع»', 150, DK)
    if t > 1.0: T(d, (960, 660), 'الوكالة المغربية لصناعة الدفاع والأمن', 64, WH)
    if t > 1.6: T(d, (960, 780), 'جلب المستثمرين • الأراضي • الكفاءات • الطلبيات العمومية', 44, MU)
    return im

def g_fields(t, D, a):
    return _list(t, 'مجالات الصناعة الدفاعية', ['الطائرات المسيّرة', 'الأنظمة الذاتية', 'العتاد البري والبحري', 'الإلكترونيات الدفاعية', 'الأمن السيبراني', 'الذكاء الاصطناعي'], None, 1.5)

def g_goals(t, D, a):
    # 4 objectifs 2035, révélés au fil de la voix (a['n'] = nombre de cases visibles au début)
    im = bg(t); d = ImageDraw.Draw(im)
    T(d, (W - 160, 140), 'أهداف 2035', 64, WH, 'rm')
    G = [('40%', 'من حاجيات القوات المسلحة الملكية والأجهزة الأمنية'), ('50', 'مليار درهم رقم معاملات سنوي'), ('+65%', 'من الإيرادات من التصدير'), ('50000', 'منصب شغل مباشر وغير مباشر')]
    reveal = a.get('at', [0.2, 7.3, 13.9, 17.6])
    for i, (v, c) in enumerate(G):
        st = reveal[i]
        if t < st: continue
        k = eo((t - st) / 0.5); col = i % 2; row = i // 2
        x = 1420 - col * 900; y = 360 + row * 330
        hi = i == max(j for j in range(4) if t >= reveal[j])
        d.rounded_rectangle([x - 400, y - 130, x + 400, y + 130], 24, fill=(255, 255, 255) if hi else (40, 60, 100))
        num = v
        if v.replace('%', '').replace('+', '').isdigit():
            n = int(v.replace('%', '').replace('+', '')); cur = int(n * eo((t - st) / 1.0))
            num = ('+' if v.startswith('+') else '') + f'{cur}' + ('%' if '%' in v else '')
        T(d, (x, y - 40), num, 110, RED if hi else YEL)
        for j, l in enumerate(wrap(c, 36, 720)): T(d, (x, y + 55 + j * 44), l, 36, DK if hi else WH)
    return im

def g_projects(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    redtag(d, (W - 200, 170), 'نوفمبر 2026', 46)
    T(d, (W - 200, 300), 'مشاريع صناعية دفاعية مرخّصة', 66, WH, 'rm')
    v1 = int(333 * eo((t - 0.4) / 1.2)); v2 = int(3500 * eo((t - 1.0) / 1.2))
    if t > 0.4: T(d, (1380, 560), f'{v1}', 170, YEL); T(d, (1380, 700), 'مليون دولار استثمار', 52, WH)
    if t > 1.0: T(d, (560, 560), f'+{v2}', 170, YEL); T(d, (560, 700), 'منصب شغل مباشر', 52, WH)
    return im

def g_q(t, D, a):
    im = bg(t); d = ImageDraw.Draw(im)
    if t > 0.2: T(d, (960, 380), 'من مشترٍ للعتاد…', 100, WH, stroke=2)
    if t > 1.6: T(d, (960, 560), 'إلى منتجٍ ومُصدِّر؟', 110, YEL, stroke=2)
    if t > 2.4:
        k = eo((t - 2.4) / 0.5); w = int(520 * k)
        d.rounded_rectangle([960 - w // 2, 720, 960 + w // 2, 840], 18, fill=RED)
        if k > 0.7: T(d, (960, 782), 'الموعد: 2035', 64)
    return im

CARDS19 = {k[2:]: v for k, v in globals().items() if k.startswith('g_') and v.__module__ == __name__}
def frames19(kind, args, dur, fps=25):
    fn = CARDS19[kind]; n = max(1, int(round(dur * fps)))
    for i in range(n): yield fn(i / fps, dur, args)
