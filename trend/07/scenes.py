import sys; sys.path.insert(0, '/home/claude/rawi-assets/tools')
import reportage_gfx as g
from agfx import Layer, Dyn, text_img, render, eo_cubic, eo_back
from PIL import Image, ImageDraw
import math
g.badge.__defaults__ = ('ترند',)
W, H = 1920, 1080
RED, YEL, INK, PAPER = g.RED, g.YEL, g.INK, g.PAPER
GOLD = (214, 160, 30); BTC = (247, 147, 26); GREEN = (30, 140, 70)

_bg = None
def bg():
    global _bg
    if _bg is None: _bg = g.badge(g.kraft())
    return _bg

def card(w, h, fill=PAPER):
    return Image.new('RGBA', (w, h), fill + (255,))

def cal_card(month, day, year):
    c = card(460, 500); d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 460, 130), fill=RED)
    for i in range(5): d.ellipse((60 + i * 80 - 10, 16, 60 + i * 80 + 10, 36), fill=(60, 20, 20))
    g.text(d, (230, 88), month, g.F(g.FB, 60), (255, 255, 255))
    g.text(d, (230, 290), str(day), g.F(g.FB, 200 if len(str(day))<3 else 150), INK)
    g.text(d, (230, 445), str(year), g.F(g.FB, 66), RED)
    return c

def sticker(txt, color=YEL, fg=INK, size=56):
    t = text_img(txt, size, fg); c = card(t.width + 50, t.height + 24, color); c.alpha_composite(t, (25, 12)); return c

def arrow(up, color, s=120):
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if up: d.polygon([(s / 2, 4), (s - 6, s * 0.55), (s * 0.68, s * 0.55), (s * 0.68, s - 4), (s * 0.32, s - 4), (s * 0.32, s * 0.55), (6, s * 0.55)], fill=color)
    else: d.polygon([(s / 2, s - 4), (s - 6, s * 0.45), (s * 0.68, s * 0.45), (s * 0.68, 4), (s * 0.32, 4), (s * 0.32, s * 0.45), (6, s * 0.45)], fill=color)
    return im

def counter(a, b, dur, fmt, color, size=230, delay=0.0):
    def f(t):
        x = eo_cubic((t - delay) / dur) if t >= delay else 0
        v = a + (b - a) * x
        return text_img(fmt(v), size, color, stroke=6, stroke_fill=(40, 30, 20))
    return f

money = lambda v: f"{int(round(v)):,}$"

def scene(name, d, marks):
    """marks: relative times (s) of the clause starts inside the shot."""
    m = lambda k, dflt: marks[k] if k < len(marks) else dflt
    if name == 'cal_jan':
        it = [Layer(cal_card('يناير', 2026, ''), 960, 470, 0.1, 'drop', sfx='paper'),
              Layer(sticker('رقمٌ قياسي للذهب', RED, (255, 255, 255)), 960, 800, 0.8, 'stamp', sfx='stamp', angle=-3)]
    elif name == 'gold_rec':
        it = [Dyn(counter(0, 5600, 1.4, money, GOLD), 960, 470, 0.1, sfx='tick'),
              Layer(arrow(True, GREEN, 150), 1530, 470, 0.4, 'pop', sfx=None),
              Layer(sticker('للأونصة — يناير 2026'), 960, 740, 1.2, 'slide', sfx='paper', angle=2)]
    elif name == 'gold_fall':
        it = [Layer(cal_card('نوفمبر', 16, 2026).resize((276, 300)), 1620, 300, 0.0, 'drop', sfx='flip'),
              Dyn(counter(5600, 3865, 1.6, money, RED, delay=0.5), 900, 470, 0.0, sfx='tick'),
              Layer(arrow(False, RED, 150), 900 - 520, 470, 1.6, 'pop', sfx=None),
              Layer(sticker('أدنى مستوى منذ أكتوبر 2025', INK, (255, 255, 255), 50), 900, 760, 1.9, 'slide', sfx='paper', angle=-2)]
    elif name == 'third':
        it = [Dyn(counter(0, 31, 1.0, lambda v: f"-{int(round(v))}%", RED, 300), 960, 450, 0.1, sfx='tick'),
              Layer(sticker('قرابة الثلث في 10 أشهر'), 960, 760, 0.9, 'stamp', sfx='stamp', angle=-2)]
    elif name == 'btc_peak':
        it = [Layer(sticker('أكتوبر 2025', INK, (255, 255, 255), 50), 960, 230, 0.1, 'drop', sfx='paper'),
              Dyn(counter(0, 126000, 1.5, money, BTC), 960, 500, 0.4, sfx='tick'),
              Layer(arrow(True, GREEN, 140), 1640, 500, 1.4, 'pop', sfx=None)]
    elif name == 'btc_fall':
        it = [Dyn(counter(126000, 64000, 1.5, money, RED, delay=0.2), 960, 450, 0.0, sfx='tick'),
              Layer(sticker('-49%', RED, (255, 255, 255), 110), 1560, 760, 1.6, 'stamp', sfx='stamp', angle=-6)]
    elif name == 'etf':
        c = card(1100, 470); dd = ImageDraw.Draw(c)
        dd.rectangle((0, 0, 1100, 90), fill=INK)
        g.text(dd, (550, 46), 'صناديق البيتكوين المتداولة', g.F(g.FB, 52), (255, 255, 255))
        g.text(dd, (550, 240), '-2 مليار دولار', g.F(g.FB, 150), RED)
        g.text(dd, (550, 400), 'خرجت في نوفمبر 2026 وحده', g.F(g.FB, 54), INK)
        it = [Layer(c, 960, 520, 0.1, 'drop', sfx='paper', angle=-1.5)]
    elif name == 'gauge':
        def gauge(t):
            im = Image.new('RGBA', (1000, 620), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
            cx, cy, R = 500, 520, 420
            cols = [(200, 40, 40), (235, 120, 40), (240, 200, 40), (140, 200, 60), (40, 160, 70)]
            for k, col in enumerate(cols):
                dd.pieslice((cx - R, cy - R, cx + R, cy + R), 180 + k * 36, 180 + (k + 1) * 36, fill=col)
            dd.pieslice((cx - R + 110, cy - R + 110, cx + R - 110, cy + R - 110), 180, 360, fill=PAPER)
            p = eo_back(t / 1.6, 1.3) if t < 1.6 else 1
            v = 50 + (10 - 50) * p
            ang = math.radians(180 + v / 100 * 180)
            dd.line((cx, cy, cx + (R - 60) * math.cos(ang), cy + (R - 60) * math.sin(ang)), fill=INK, width=18)
            dd.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=INK)
            g.text(dd, (cx, cy - 140), str(int(round(max(v, 0)))), g.F(g.FB, 150), RED if v < 25 else INK)
            return im
        it = [Layer(sticker('مؤشر الخوف والطمع', INK, (255, 255, 255), 54), 960, 170, 0.0, 'drop', sfx='paper'),
              Dyn(gauge, 960, 600, 0.3, sfx='whoosh'),
              Layer(sticker('خوفٌ شديد', RED, (255, 255, 255), 70), 1500, 860, 1.8, 'stamp', sfx='stamp', angle=-5)]
    elif name == 'chain':
        steps = [('التضخم', True, RED), ('الفائدة', True, RED), ('الدولار  •  السندات ≈ 5%', True, GREEN), ('الذهب والبيتكوين', False, RED)]
        it = []
        for k, (txt, up, col) in enumerate(steps):
            c = card(1100, 150); dd = ImageDraw.Draw(c)
            g.text(dd, (1060, 75), txt, g.F(g.FB, 72), INK, anchor='rm')
            c.alpha_composite(arrow(up, col, 110), (40, 20))
            t0 = [0.05, 0.8, m(1, 1.6), m(3, 3.2)][k]
            it.append(Layer(c, 960, 190 + k * 225, max(0.05, t0), 'slide', sfx='whoosh' if k else 'paper', angle=(-1) ** k * 0.8))
    elif name == 'equation':
        it = [Layer(sticker('المعادلة ببساطة', INK, (255, 255, 255), 60), 960, 150, 0.05, 'drop', sfx='paper'),
              Layer(sticker('فائدةٌ أعلى', RED, (255, 255, 255), 80), 1400, 380, m(1, 0.1), 'pop', sfx='paper', angle=-2),
              Layer(text_img('+', 120, INK), 960, 380, m(1, 0.1) + 0.4, 'pop', sfx=None),
              Layer(sticker('دولارٌ أقوى', GREEN, (255, 255, 255), 80), 520, 380, m(2, 0.9), 'pop', sfx='paper', angle=2),
              Layer(sticker('= الذهب والبيتكوين يهبطان', INK, (255, 255, 255), 74), 960, 700, m(2, 0.9) + 0.9, 'slide', sfx='whoosh', angle=-1)]
    elif name == 'disclaimer':
        c = card(1200, 330); dd = ImageDraw.Draw(c)
        g.text(dd, (600, 110), 'شرحٌ لما يحدث في الأسواق', g.F(g.FB, 76), INK)
        g.text(dd, (600, 230), 'وليس نصيحةً بالشراء أو البيع', g.F(g.FB, 76), RED)
        it = [Layer(c, 960, 520, 0.05, 'drop', sfx='paper', angle=1.2),
              Layer(sticker('تنبيه', RED, (255, 255, 255), 64), 1500, 300, 0.7, 'stamp', sfx='stamp', angle=-8)]
    elif name == 'end':
        it = [Layer(text_img('اشتركوا في القناة', 140, YEL, stroke=8, stroke_fill=INK), 960, 450, 0.1, 'pop', sfx='paper', shadow=False),
              Layer(sticker('ترند | الراوي', RED, (255, 255, 255), 64), 960, 650, 0.6, 'slide', sfx='whoosh', angle=-2)]
    else:
        raise KeyError(name)
    return it

def make(name, d, marks, out):
    return render(bg(), scene(name, d, marks), d, out)
