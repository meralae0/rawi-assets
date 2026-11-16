# Générateurs graphiques "reportage" (Rawi Zone) — 1920x1080 PNG
# kraft background, framed media with source, tear-off calendar, sticker label,
# document card (browser-like), big number, list card.
import random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1920, 1080
RED = (214, 40, 40); YEL = (255, 200, 0); INK = (30, 26, 22); PAPER = (250, 246, 236)
FB = '/root/.fonts/Tajawal-ExtraBold.ttf'; FR = '/root/.fonts/Tajawal-Bold.ttf'
FM = '/root/.fonts/Tajawal-Bold.ttf'

def F(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)

def tw(d, txt, font):
    return d.textlength(txt, font=font, direction='rtl' if any('؀' <= c <= 'ۿ' for c in txt) else None)

def text(d, xy, txt, font, fill=INK, anchor='mm'):
    ar = any('؀' <= c <= 'ۿ' for c in txt)
    d.text(xy, txt, font=font, fill=fill, anchor=anchor, direction='rtl' if ar else None)

_kraft = None
def kraft():
    global _kraft
    if _kraft is None:
        random.seed(7)
        base = Image.new('RGB', (W, H), (196, 164, 120))
        n = Image.effect_noise((W, H), 40).convert('L').filter(ImageFilter.GaussianBlur(1.2))
        fib = Image.effect_noise((W // 4, H // 4), 60).convert('L').resize((W, H)).filter(ImageFilter.GaussianBlur(3))
        k = Image.merge('RGB', [n.point(lambda v: v * 0.25 + 175), n.point(lambda v: v * 0.22 + 143), n.point(lambda v: v * 0.18 + 100)])
        k = Image.blend(k, Image.merge('RGB', [fib.point(lambda v: v * 0.3 + 160)] * 3), 0.15)
        vig = Image.radial_gradient('L').resize((W, H)).point(lambda v: int(v * 0.55))
        _kraft = Image.composite(Image.new('RGB', (W, H), (90, 66, 40)), k, vig)
    return _kraft.copy()

def shadow_paste(bg, card, xy, angle=0.0, blur=18, off=(10, 14), alpha=110):
    card = card.convert('RGBA')
    if angle:
        card = card.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new('RGBA', card.size, (0, 0, 0, 0))
    sh.putalpha(card.split()[3].point(lambda v: alpha if v > 0 else 0))
    pad = blur * 3
    big = Image.new('RGBA', (card.width + pad * 2, card.height + pad * 2), (0, 0, 0, 0))
    big.paste(sh, (pad, pad), sh)
    big = big.filter(ImageFilter.GaussianBlur(blur))
    x, y = xy
    bg.paste(big, (x - pad + off[0], y - pad + off[1]), big)
    bg.paste(card, (x, y), card)
    return bg

def badge(bg, series='ملفات'):
    d = ImageDraw.Draw(bg)
    f = F(FB, 34)
    w = tw(d, series, f) + 40
    d.rounded_rectangle((W - 60 - w, 40, W - 60, 92), 10, fill=RED)
    text(d, (W - 60 - w / 2, 66), series, f, (255, 255, 255))
    return bg

def source_tag(card, src):
    d = ImageDraw.Draw(card)
    f = F(FM, 26)
    w = tw(d, src, f) + 28
    d.rectangle((card.width - w - 12, card.height - 50, card.width - 12, card.height - 12), fill=(20, 20, 20))
    text(d, (card.width - 12 - w / 2, card.height - 31), src, f, (255, 255, 255))

def media(img_path, src, angle=-1.2, maxw=1500, maxh=820, bg=None, label=None):
    """Photo in white border frame on kraft, with source tag."""
    bg = bg or kraft()
    im = Image.open(img_path).convert('RGB')
    s = min(maxw / im.width, maxh / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    b = 18
    card = Image.new('RGB', (im.width + 2 * b, im.height + 2 * b), PAPER)
    card.paste(im, (b, b))
    source_tag(card, src)
    x = (W - card.width) // 2; y = (H - card.height) // 2 + 10
    shadow_paste(bg, card, (x, y), angle)
    if label:
        sticker(bg, label, (x + card.width - 40, y + 10), angle=4)
    return badge(bg)

def sticker(bg, txt, xy, angle=-4, color=YEL, fg=INK, size=46):
    d0 = ImageDraw.Draw(bg)
    f = F(FB, size)
    w = int(tw(d0, txt, f)) + 60; h = size + 44
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=color + (255,), outline=(255, 255, 255, 255), width=5)
    text(d, (w / 2, h / 2 + 2), txt, f, fg)
    x, y = xy
    shadow_paste(bg, c, (int(x - w / 2), int(y - h / 2)), angle, blur=8, off=(5, 7), alpha=120)
    return bg

def calendar(day, month, year, sub=None, bg=None):
    bg = bg or kraft()
    cw, ch = 560, 600
    c = Image.new('RGB', (cw, ch), PAPER)
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, cw, 150), fill=RED)
    for i in range(6):
        cx = 70 + i * 84
        d.ellipse((cx - 12, 18, cx + 12, 42), fill=(60, 20, 20))
    text(d, (cw / 2, 100), month, F(FB, 66), (255, 255, 255))
    text(d, (cw / 2, 330), str(day), F(FB, 250), INK)
    text(d, (cw / 2, 520), str(year), F(FB, 76), RED)
    # torn bottom edge
    for x in range(0, cw, 16):
        d.polygon([(x, ch), (x + 8, ch - random.randint(6, 14)), (x + 16, ch)], fill=(196, 164, 120))
    shadow_paste(bg, c, ((W - cw) // 2, (H - ch) // 2 - (40 if sub else 0)), angle=2.0)
    if sub:
        sticker(bg, sub, (W // 2, H // 2 + 330), angle=-2, size=50)
    return badge(bg)

def doc_card(header, lines_en, lines_ar, src, bg=None):
    """Browser-like card: header bar, original English (small), Arabic translation (big)."""
    bg = bg or kraft()
    cw = 1500
    fen = F(FM, 34); far = F(FB, 54)
    d0 = ImageDraw.Draw(bg)
    h = 90 + 40 + len(lines_en) * 48 + 30 + len(lines_ar) * 80 + 90
    c = Image.new('RGB', (cw, h), (255, 255, 255))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, cw, 70), fill=(232, 232, 232))
    for i, col in enumerate([(237, 106, 94), (245, 191, 79), (97, 197, 84)]):
        d.ellipse((24 + i * 36, 24, 46 + i * 36, 46), fill=col)
    d.rounded_rectangle((150, 16, cw - 30, 54), 18, fill=(255, 255, 255))
    text(d, (cw / 2, 36), header, F(FM, 26), (90, 90, 90))
    y = 120
    for l in lines_en:
        d.text((60, y), l, font=fen, fill=(110, 110, 110)); y += 48
    y += 20
    d.line((60, y, cw - 60, y), fill=(220, 220, 220), width=3); y += 30
    for l in lines_ar:
        text(d, (cw - 60, y + 30), l, far, INK, anchor='rm'); y += 80
    source_tag(c, src)
    shadow_paste(bg, c, ((W - cw) // 2, max(40, (H - h) // 2)), angle=-0.8)
    return badge(bg)

def bignum(num, caption, bg=None, color=RED):
    bg = bg or kraft()
    d = ImageDraw.Draw(bg)
    f = F(FB, 260)
    text(d, (W // 2 + 6, H // 2 - 60 + 8), num, f, (40, 30, 20))
    text(d, (W // 2, H // 2 - 60), num, f, color)
    sticker(bg, caption, (W // 2, H // 2 + 170), angle=-2, size=58)
    return badge(bg)

def list_card(title, items, bg=None):
    bg = bg or kraft()
    cw = 1300; h = 160 + len(items) * 110 + 40
    c = Image.new('RGB', (cw, h), PAPER)
    d = ImageDraw.Draw(c)
    # ruled lines
    for yy in range(150, h, 55):
        d.line((40, yy, cw - 40, yy), fill=(220, 210, 190), width=2)
    text(d, (cw - 60, 80), title, F(FB, 64), RED, anchor='rm')
    y = 200
    for it in items:
        d.ellipse((cw - 90, y - 16, cw - 58, y + 16), fill=RED)
        text(d, (cw - 120, y), it, F(FB, 56), INK, anchor='rm'); y += 110
    shadow_paste(bg, c, ((W - cw) // 2, (H - h) // 2), angle=1.0)
    return badge(bg)

def title_card(line1, line2=None, bg=None):
    bg = bg or kraft()
    d = ImageDraw.Draw(bg)
    for dx, dy in [(-6, 0), (6, 0), (0, -6), (0, 6), (-5, -5), (5, 5), (-5, 5), (5, -5)]:
        text(d, (W // 2 + dx, H // 2 - 70 + dy), line1, F(FB, 140), INK)
    text(d, (W // 2, H // 2 - 70), line1, F(FB, 140), YEL)
    if line2:
        sticker(bg, line2, (W // 2, H // 2 + 120), angle=-2, color=RED, fg=(255, 255, 255), size=60)
    return badge(bg)

def video_bg_frame():
    """transparent overlay: series badge only (for video clips)."""
    o = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    return badge(o)
