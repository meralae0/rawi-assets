import json, subprocess, os, math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H, FPS = 1920, 1080, 30
CA = '/root/.fonts/Cairo.ttf'; TJ = '/root/.fonts/Tajawal-ExtraBold.ttf'
Y = (255, 206, 0); R = (210, 30, 45); WH = (255, 255, 255); K = (8, 10, 16); ICE = (150, 200, 235); NAVY = (10, 18, 34)
def ca(s):
    f = ImageFont.truetype(CA, s, layout_engine=ImageFont.Layout.RAQM)
    try: f.set_variation_by_name('Black')
    except Exception: pass
    return f
def tj(s): return ImageFont.truetype(TJ, s, layout_engine=ImageFont.Layout.RAQM)
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def eob(x, s=1.6): x = max(0, min(1, x)) - 1; return x * x * ((s + 1) * x + s) + 1
os.makedirs('shots', exist_ok=True); os.makedirs('ov', exist_ok=True)
L = json.load(open('lines.json'))

# ---------------- plan ----------------
P = {
0: (['v:19298575', 'v:29888681'], [('date', '1 فبراير 1959'), ('label', 'جبال الأورال الشمالية')]),
1: (['v:15390975', 'v:20395853'], [('big', '−40°')]),
2: (['a:1', 'a:2'], []),
3: (['v:6453507', 'v:11839732'], []),
4: (['v:19627257'], []),
5: (['p:00'], [('label', 'الخيمة كما وجدها المنقذون — 1959')]),
6: (['d:06', 'g:title'], []),
7: (['p:03'], [('chapter', 'الملف')]),
8: (['p:13'], [('label', 'إيغور دياتلوف — قائد المجموعة')]),
9: (['g:members'], []),
10: (['g:map', 'v:35045294'], []),
11: (['p:15', 'p:14'], [('label', 'دياتلوف ورفاقه في رحلة شتوية — 1958')]),
12: (['v:11618451'], [('date', '28 يناير'), ('label', 'يوري يودين — الناجي الوحيد')]),
13: (['v:6766947', 'v:30123240'], []),
14: (['v:19642768'], []),
15: (['v:29620844', 'v:16236611', 'v:7593100'], []),
16: (['v:39365722', 'v:30584166'], [('chapter', 'الخيمة'), ('label', 'جبل خولات سياخل')]),
17: (['v:8778194', 'v:36111065'], [('label', 'آخر صورة: الحفر في الثلج')]),
18: (['v:2750099', 'v:33068304'], [('date', 'قبل 12 فبراير')]),
19: (['v:19791476'], []),
20: (['p:12'], [('date', '20 فبراير'), ('label', 'بداية البحث')]),
21: (['a:6', 'v:35793378'], []),
22: (['p:00', 'v:11447869'], [('date', '26 فبراير')]),
23: (['v:11112318'], []),
24: (['v:6453507', 'v:8778194', 'v:7000725'], []),
25: (['v:15390975', 'v:11354012'], []),
26: (['a:3'], []),
27: (['g:scheme1', 'v:15237622'], [('chapter', 'الشجرة')]),
28: (['a:4'], []),
29: (['v:5878222', 'v:6650190'], [('big', '5 م')]),
30: (['g:scheme2'], []),
31: (['v:11112318'], []),
32: (['v:7000725'], [('big', '5 / 9')]),
33: (['v:19627257'], []),
34: (['v:16236611', 'p:01'], [('chapter', 'الوادي'), ('date', '4 مايو')]),
35: (['p:01', 'g:scheme3'], []),
36: (['v:30123240'], []),
37: (['d:08', 'd:09', 'd:05'], [('label', 'من ملف التحقيق الأصلي — 1959'), ('face', 'thibeaux:نيكولاي تيبو-بريينول', 0), ('face', 'dubinina:لودميلا دوبينينا', 1), ('face', 'zolotaryov:سيميون زولوتاريوف', 2)]),
38: (['d:04'], []),
39: (['v:6650190', 'v:19642768'], []),
40: (['d:10'], [('label', 'قرار بفحص الإشعاع على الملابس')]),
41: (['d:07', 'g:quote'], [('date', 'مايو 1959')]),
42: (['d:06', 'v:2750099'], []),
43: (['v:19450621'], [('chapter', 'الفرضيات')]),
44: (['v:29620844', 'v:6416727'], [('hyp', 'الفرضية 1|هجوم من السكان المحليين|مستبعدة')]),
45: (['v:31733343', 'v:19450622'], [('hyp', 'الفرضية 2|تجربة عسكرية سرية|غير مثبتة')]),
46: (['v:29888681', 'g:wave'], [('hyp', 'الفرضية 3|موجات صوتية لا تُسمع|صعبة الإثبات')]),
47: (['v:15628486', 'v:36715106'], [('hyp', 'الفرضية 4|رياح جليدية عنيفة|ممكنة')]),
48: (['v:20395853'], []),
49: (['v:19298575'], []),
50: (['v:33068304'], [('chapter', 'الانعطافة'), ('date', '2019')]),
51: (['v:3590790'], [('date', '2020'), ('label', 'النيابة الروسية: انهيار ثلجي')]),
52: (['v:39365714', 'v:36393314'], []),
53: (['v:36510380'], [('date', '2021'), ('label', 'يوهان غوم وألكسندر بوزرين')]),
54: (['g:sim', 'v:35742076', 'v:36274550'], []),
55: (['g:slope'], []),
56: (['g:slope28', 'v:11354012'], []),
57: (['a:5'], []),
58: (['v:30584166'], [('big', 'كتلة بحجم سيارة')]),
59: (['v:35793378', 'v:6766947'], []),
60: (['v:11792113'], []),
61: (['v:11839715', 'v:11792116'], []),
62: (['v:11839716', 'v:11839732'], [('quote', 'كان صراعًا بطوليًا… لم يكن هناك ذعر')]),
63: (['v:35763506', 'v:15237622'], []),
64: (['v:7456038'], [('chapter', 'الحكم')]),
65: (['g:verdict1'], []),
66: (['g:verdict2'], []),
67: (['v:37219534'], []),
68: (['v:36111065'], []),
69: (['p:16'], [('label', 'مقبرة ميخايلوفسكوي — يكاترينبورغ')]),
70: (['p:17', 'p:02'], [('label', 'النصب التذكاري — يكاترينبورغ')]),
71: (['v:30659945'], []),
72: (['g:end'], []),
}
# ---------------- helpers ----------------
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())
VD = {}
used = {}
def next_ss(vid, d):
    if vid not in VD: VD[vid] = dur(f'v/{vid}.mp4')
    D = VD[vid]; u = used.get(vid, 0.5)
    if u + d > D - 0.2: u = max(0, (u + 1.3) % max(0.1, D - d - 0.2))
    used[vid] = u + d + 0.4
    return u, D
GRADE = "eq=contrast=1.08:saturation=0.82:brightness=-0.03,colorbalance=bs=0.06:bm=0.03:bh=-0.02"
def enc(args, out):
    subprocess.run(['ffmpeg', '-y', '-v', 'error'] + args + ['-r', str(FPS), '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-an', out], check=True)
def shot_video(vid, d, out):
    ss, D = next_ss(vid, d)
    speed = 1.0
    if D - ss < d: speed = max(0.5, (D - ss - 0.1) / d)
    vf = f"setpts={1/speed:.4f}*PTS,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{GRADE},fps={FPS}"
    enc(['-ss', f'{ss:.2f}', '-i', f'v/{vid}.mp4', '-t', f'{d:.3f}', '-vf', vf], out)
def kb(img, d, out, mode=0, bw=False, tag=None):
    im = Image.open(img).convert('RGB')
    if bw: im = im.convert('L').convert('RGB')
    # fit as cover on 2400x1350 canvas; tall documents -> blurred bg + centered page
    cw, ch = 2400, 1350
    if im.width / im.height < 1.2:
        bg = im.resize((cw, int(cw * im.height / im.width))).crop((0, 0, cw, ch)).filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg).enhance(0.35)
        pg = im.copy(); sc = (ch * 1.5) / pg.height; pg = pg.resize((int(pg.width * sc), int(pg.height * sc)), Image.LANCZOS)
        can = bg.copy(); can.paste(pg, ((cw - pg.width) // 2, 60))
        im = can
    else:
        s = max(cw / im.width, ch / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        im = im.crop(((im.width - cw) // 2, (im.height - ch) // 2, (im.width - cw) // 2 + cw, (im.height - ch) // 2 + ch))
    p = f'/tmp/kb_{os.getpid()}.jpg'; im.save(p, quality=93)
    n = int(d * FPS) + 1
    z0, z1 = [(1.0, 1.12), (1.12, 1.0), (1.0, 1.1), (1.05, 1.15)][mode % 4]
    px = ['(iw-iw/zoom)/2', '(iw-iw/zoom)*on/%d' % n, '(iw-iw/zoom)*(1-on/%d)' % n, '(iw-iw/zoom)/2'][mode % 4]
    py = ['(ih-ih/zoom)/2', '(ih-ih/zoom)/2', '(ih-ih/zoom)/3', '(ih-ih/zoom)*on/%d' % n][mode % 4]
    vf = f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':x='{px}':y='{py}':d={n}:s={W}x{H}:fps={FPS},{GRADE}"
    enc(['-loop', '1', '-i', p, '-t', f'{d:.3f}', '-vf', vf], out)
# ---------------- overlays (transparent PNG) ----------------
def ov_png(kind, text, name):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == 'date':
        f = ca(64); tw = f.getlength(text)
        d.rectangle([1590 - tw - 60, 150, 1590, 250], fill=(0, 0, 0, 170)); d.rectangle([1590 - 10, 150, 1590, 250], fill=R)
        d.text((1590 - 40, 200), text, font=f, fill=Y, anchor='rm', direction='rtl')
    elif kind == 'label':
        f = tj(44); tw = f.getlength(text)
        d.rectangle([1860 - tw - 50, 930, 1860, 1004], fill=(0, 0, 0, 175)); d.rectangle([1852, 930, 1860, 1004], fill=Y)
        d.text((1860 - 28, 968), text, font=f, fill=WH, anchor='rm', direction='rtl')
    elif kind == 'big':
        f = ca(210)
        d.text((960, 560), text, font=f, fill=WH, anchor='mm', direction='rtl', stroke_width=10, stroke_fill=(0, 0, 0))
    elif kind == 'chapter':
        f = ca(120); tw = f.getlength(text)
        d.rectangle([0, 430, W, 650], fill=(0, 0, 0, 150))
        d.rectangle([960 - tw / 2 - 40, 640, 960 + tw / 2 + 40, 650], fill=R)
        d.text((960, 535), text, font=f, fill=Y, anchor='mm', direction='rtl')
    elif kind == 'quote':
        f = ca(76)
        d.rectangle([140, 400, 1780, 680], fill=(0, 0, 0, 165)); d.rectangle([140, 400, 152, 680], fill=Y)
        d.text((1700, 540), '«' + text + '»', font=f, fill=WH, anchor='rm', direction='rtl')
    elif kind == 'hyp':
        a, b, c = text.split('|')
        d.rounded_rectangle([1000, 170, 1590, 470], 24, fill=(5, 10, 20, 215), outline=Y, width=4)
        d.text((1550, 235), a, font=ca(58), fill=Y, anchor='rm', direction='rtl')
        d.text((1550, 330), b, font=tj(46), fill=WH, anchor='rm', direction='rtl')
        col = R if c in ('مستبعدة',) else ((255, 150, 0) if c != 'ممكنة' else (60, 190, 110))
        f = ca(48); tw = f.getlength(c)
        d.rounded_rectangle([1550 - tw - 40, 380, 1550, 450], 12, outline=col, width=5)
        d.text((1550 - 20, 414), c, font=f, fill=col, anchor='rm', direction='rtl')
    elif kind == 'face':
        import gfx2
        k, nm = text.split(':')
        pr = gfx2.portrait(k, 230)
        x0, y0 = 210, 300
        g = Image.new('RGBA', (pr.width + 70, pr.height + 70), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([0, 0, g.width - 1, g.height - 1], fill=(0, 0, 0, 160)); g = g.filter(ImageFilter.GaussianBlur(18))
        im.alpha_composite(g, (x0 - 35, y0 - 35)); im.alpha_composite(pr, (x0, y0))
        f = tj(46); tw = f.getlength(nm); cx = x0 + pr.width / 2
        d.rounded_rectangle([cx - tw / 2 - 24, y0 + pr.height + 20, cx + tw / 2 + 24, y0 + pr.height + 92], 12, fill=(0, 0, 0, 200))
        d.rectangle([cx - tw / 2 - 24, y0 + pr.height + 20, cx - tw / 2 - 16, y0 + pr.height + 92], fill=Y)
        d.text((cx, y0 + pr.height + 56), nm, font=f, fill=WH, anchor='mm', direction='rtl')
    elif kind == 'aitag':
        f = tj(34); t = 'إعادة تمثيل'; tw = f.getlength(t)
        d.rounded_rectangle([60, 960, 60 + tw + 50, 1020], 10, fill=(0, 0, 0, 150))
        d.text((60 + tw + 25, 990), t, font=f, fill=(230, 230, 230), anchor='rm', direction='rtl')
    im.save(f'ov/{name}.png')
def pastille():
    # Logo officiel Rawi Zone (brand/watermark_video.png) en haut à droite, 85 % d'opacité
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lg = Image.open('/home/claude/dy/brand/watermark_video.png').convert('RGBA')
    lw = 250; lg = lg.resize((lw, int(lg.size[1] * lw / lg.size[0])), Image.LANCZOS)
    lg.putalpha(lg.getchannel('A').point(lambda v: v * 85 // 100))
    im.alpha_composite(lg, (W - lw - 30, 26))
    im.save('ov/pastille.png')
# ---------------- graphics (frame-rendered) ----------------
def bgdark():
    im = Image.new('RGB', (W, H), NAVY); d = ImageDraw.Draw(im)
    for y in range(0, H, 4): d.line([(0, y), (W, y)], fill=(10 + y // 60, 18 + y // 50, 34 + y // 30))
    return im
BG = None
def gtext(d, xy, s, size, col=WH, anchor='rm', font=None):
    d.text(xy, s, font=font or tj(size), fill=col, anchor=anchor, direction='rtl')
def gframe(name, t, D):
    import gfx2
    gfx2.B.BG = BG
    if name == 'map': return gfx2.g_map(t, D)
    if name == 'members': return gfx2.g_members(t, D)
    if name in ('scheme1','scheme2','scheme3'): return gfx2.g_topo(name, t, D)
    im = BG.copy(); d = ImageDraw.Draw(im)
    a = ease(t / 0.6)
    if name == 'title':
        im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
        k = eob(t / 0.8); f = ca(150)
        d.text((960, 470), 'ممرّ دياتلوف', font=f, fill=tuple(int(c * ease(t / 0.5)) for c in WH), anchor='mm', direction='rtl')
        w = int(700 * ease((t - 0.4) / 0.6)); d.rectangle([960 - w // 2, 590, 960 + w // 2, 598], fill=R)
        if t > 0.8: d.text((960, 680), 'لغزُ تسعةِ متسلّقين… منذ 1959', font=tj(56), fill=(200, 200, 200), anchor='mm', direction='rtl')
    elif name == 'members':
        names = ['إيغور دياتلوف 23', 'زينايدا كولموغوروفا 22', 'لودميلا دوبينينا 20', 'يوري دوروشينكو 21', 'يوري كريفونيشينكو 23',
                 'روستم سلوبودين 23', 'ألكسندر كوليفاتوف 24', 'نيكولاي تيبو-بريينول 23', 'سيميون زولوتاريوف 38', 'يوري يودين 21 — عاد']
        gtext(d, (1590, 120), 'المجموعة: 10 طلاب ومرشد', 70, Y, font=ca(70))
        for i, n in enumerate(names):
            k = ease((t - 0.3 - i * 0.35) / 0.4)
            if k <= 0: continue
            col, cx = (i % 2, i // 2)
            x = 1590 - col * 720 + int((1 - k) * 60); y = 260 + cx * 140
            fill = (120, 120, 120) if i == 9 else WH
            d.rounded_rectangle([x - 640, y - 50, x, y + 50], 14, fill=(20, 32, 56), outline=(Y if i == 0 else (60, 80, 110)), width=3)
            gtext(d, (x - 30, y), n, 46, fill)
    elif name == 'map':
        gtext(d, (1590, 120), 'الطريق إلى جبل أوتورتن', 70, Y, font=ca(70))
        pts = [(1500, 900, 'سفيردلوفسك'), (1180, 640, 'إيفديل'), (960, 520, 'فيجاي'), (620, 300, 'خولات سياخل'), (520, 200, 'أوتورتن')]
        k = ease(t / (D * 0.7)) * (len(pts) - 1)
        for i in range(len(pts) - 1):
            seg = max(0, min(1, k - i))
            if seg <= 0: break
            x0, y0, _ = pts[i]; x1, y1, _ = pts[i + 1]
            d.line([(x0, y0), (x0 + (x1 - x0) * seg, y0 + (y1 - y0) * seg)], fill=(255, 120, 60) if i == 3 else Y, width=10)
        for i, (x, y, n) in enumerate(pts):
            if k + 0.05 >= i:
                c = R if n == 'خولات سياخل' else WH
                d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=c, outline=K, width=3)
                gtext(d, (x - 30, y), n, 44, c, anchor='rm' if x > 700 else 'lm') if x > 700 else gtext(d, (x + 30, y), n, 44, c, anchor='lm')
        if t > D * 0.6: gtext(d, (1590, 1000), '≈ 300 كم على الزلاجات', 54, ICE)
    elif name in ('scheme1', 'scheme2', 'scheme3'):
        gtext(d, (1590, 110), {'scheme1': 'من الخيمة إلى الشجرة', 'scheme2': 'أين وُجد الخمسة الأوائل', 'scheme3': 'الوادي: 4 مايو 1959'}[name], 64, Y, font=ca(64))
        d.polygon([(0, 260), (W, 860), (W, H), (0, H)], fill=(225, 232, 240))
        d.line([(0, 260), (W, 860)], fill=(255, 255, 255), width=4)
        tent = (300, 340); tree = (1560, 760)
        d.polygon([(tent[0] - 50, tent[1] + 20), (tent[0], tent[1] - 40), (tent[0] + 50, tent[1] + 20)], fill=(70, 60, 50))
        gtext(d, (tent[0], tent[1] - 70), 'الخيمة', 42, K, anchor='mm')
        d.polygon([(tree[0], tree[1] - 200), (tree[0] - 70, tree[1]), (tree[0] + 70, tree[1])], fill=(30, 70, 45))
        gtext(d, (tree[0], tree[1] - 230), 'شجرة الصنوبر', 42, K, anchor='mm')
        k = ease(t / 2.0)
        for i in range(9):
            px = tent[0] + 60 + (tree[0] - tent[0] - 100) * k
            for s in range(0, int(18 * k)):
                fx = tent[0] + 60 + (tree[0] - tent[0] - 100) * s / 18; fy = tent[1] + 30 + (tree[1] - tent[1] - 40) * s / 18 + (i - 4) * 6
                d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=(90, 100, 120))
        if name == 'scheme1':
            if t > 1.5: gtext(d, (930, 470), '≈ 1.5 كم', 70, R, anchor='mm', font=ca(70))
            if t > 3:
                for j, dx in enumerate((-30, 30)): d.ellipse([tree[0] + dx - 14, tree[1] + 6, tree[0] + dx + 14, tree[1] + 34], fill=R)
                gtext(d, (tree[0] - 120, tree[1] + 80), 'كريفونيشينكو ودوروشينكو', 40, R)
        if name == 'scheme2':
            for j, (m, n) in enumerate([(300, 'دياتلوف — 300 م'), (480, 'كولموغوروفا — 480 م'), (630, 'سلوبودين — 630 م')]):
                if t > 0.8 + j * 1.6:
                    f = 1 - m / 1500; x = tent[0] + (tree[0] - tent[0]) * f; y = tent[1] + (tree[1] - tent[1]) * f
                    d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=R)
                    gtext(d, (x, y - 50), n, 38, R, anchor='mm')
        if name == 'scheme3':
            rx = tree[0] - 160; ry = tree[1] + 120
            d.ellipse([rx - 140, ry - 40, rx + 140, ry + 50], fill=(150, 170, 190))
            if t > 1: gtext(d, (rx, ry - 70), 'الوادي — 75 م من الشجرة', 40, R, anchor='mm')
            if t > 2.2:
                for j in range(4): d.ellipse([rx - 60 + j * 40 - 12, ry - 6, rx - 60 + j * 40 + 12, ry + 18], fill=R)
                gtext(d, (rx, ry + 90), 'تحت 4 أمتار من الثلج', 40, K, anchor='mm')
    elif name == 'quote':
        im = Image.new('RGB', (W, H), (14, 12, 10)); d = ImageDraw.Draw(im)
        gtext(d, (960, 300), 'خلاصة التحقيق — مايو 1959', 54, (200, 190, 170), anchor='mm')
        k = ease(t / 0.8)
        d.text((960, 520), '«قوةٌ طبيعيةٌ قاهرة»', font=ca(120), fill=tuple(int(c * k) for c in Y), anchor='mm', direction='rtl')
        if t > 1.2:
            st = Image.new('RGBA', (560, 150), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle([5, 5, 554, 144], 16, outline=R, width=10); sd.text((280, 76), 'أُغلِق الملف', font=ca(80), fill=R, anchor='mm', direction='rtl')
            st = st.rotate(-8, expand=True); im.paste(st, (680, 640), st)
    elif name == 'wave':
        gtext(d, (1590, 120), 'موجات تحت سمعية؟', 70, Y, font=ca(70))
        for i in range(0, W, 6):
            amp = 160 * math.sin(i / 90 + t * 3) * math.exp(-((i - 960) / 900) ** 2) * ease(t / 1)
            d.line([(i, 560 - amp), (i + 6, 560 - amp)], fill=ICE, width=6)
        gtext(d, (1590, 900), 'أقل من 20 هرتز — لا تسمعها الأذن', 50, WH)
    elif name == 'sim':
        gtext(d, (1590, 120), 'دراسة 2021: محاكاة الانهيار', 66, Y, font=ca(66))
        for i in range(260):
            r = random.Random(i); x = r.uniform(300, 1700); y0 = r.uniform(300, 600)
            y = y0 + (r.uniform(150, 420)) * ease((t - 0.3 - i * 0.004) / 2)
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(200 + r.randint(0, 55), 220 + r.randint(0, 35), 255))
        d.line([(200, 300), (1720, 800)], fill=(120, 140, 170), width=3)
        gtext(d, (1590, 980), 'نماذج حاسوبية + بيانات اختبارات اصطدام السيارات', 46, WH)
    elif name in ('slope', 'slope28'):
        gtext(d, (1590, 110), 'المنحدر فوق الخيمة', 66, Y, font=ca(66))
        d.polygon([(150, 300), (1100, 760), (1100, 840), (1800, 840), (1800, H), (150, H)], fill=(220, 228, 238))
        d.rectangle([1100, 760, 1500, 840], fill=(200, 210, 222))
        d.polygon([(1180, 838), (1300, 770), (1420, 838)], fill=(70, 60, 50))
        gtext(d, (1300, 880), 'الخيمة', 42, K, anchor='mm')
        if name == 'slope':
            k = ease((t - 0.5) / 1)
            d.line([(1100, 760), (1100, 760 - 0)], fill=R, width=8)
            d.rectangle([1090, 760 - int(120 * k), 1110, 760], fill=R)
            if t > 1.2: gtext(d, (1060, 600), 'حفروا في المنحدر', 48, R, anchor='rm')
        else:
            k = ease(t / 3)
            th = int(140 * k)
            d.polygon([(500, 470), (1100, 760), (1100, 760 - th), (500, 470 - th * 0.6)], fill=(250, 252, 255), outline=(160, 180, 200))
            d.arc([60, 210, 440, 590], 0, 26, fill=Y, width=6)
            gtext(d, (500, 380), '28°', 90, Y, anchor='mm', font=ca(90))
            gtext(d, (800, 300), 'الرياح تراكم الثلج', 46, ICE, anchor='mm')
            for i in range(12):
                x = (i * 140 + t * 300) % 1500 + 100; d.line([(x, 220 + i * 8), (x + 80, 250 + i * 8)], fill=ICE, width=4)
    elif name in ('verdict1', 'verdict2'):
        items = (['الخيمة شُقّت من الداخل', 'الأقدام مشت ولم تركض', 'البرد قتل خمسة', 'الإصابات البالغة للأربعة في الوادي']
                 if name == 'verdict1' else ['أثر الإشعاع', 'الكرات البرتقالية', 'كيف أُصيب الأربعة بالضبط'])
        gtext(d, (1590, 130), 'ما هو ثابت' if name == 'verdict1' else 'ما زال مفتوحًا', 80, (60, 200, 120) if name == 'verdict1' else (255, 150, 0), font=ca(80))
        for i, s in enumerate(items):
            k = ease((t - 0.4 - i * 1.0) / 0.5)
            if k <= 0: continue
            y = 300 + i * 170; x = 1590 + int((1 - k) * 80)
            d.rounded_rectangle([x - 1100, y - 60, x, y + 60], 16, fill=(20, 32, 56))
            mk = '✓' if name == 'verdict1' else '؟'
            d.text((x - 40, y), mk, font=ca(70), fill=(60, 200, 120) if name == 'verdict1' else (255, 150, 0), anchor='rm')
            gtext(d, (x - 130, y), s, 52, WH)
    elif name == 'end':
        im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
        k = ease(t / 0.8)
        f = ca(150); d.text((960, 430), 'Rawi', font=f, fill=tuple(int(c * k) for c in Y), anchor='rm'); d.text((990, 430), 'Zone', font=f, fill=tuple(int(c * k) for c in WH), anchor='lm')
        if t > 0.8:
            d.text((960, 620), 'اشتركوا وفعّلوا الجرس', font=tj(64), fill=WH, anchor='mm', direction='rtl')
            d.text((960, 720), 'التحقيق القادم قريبًا', font=tj(48), fill=(180, 180, 180), anchor='mm', direction='rtl')
    return im
def shot_graphic(name, d, out):
    n = int(d * FPS) + 1
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', out], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(gframe(name, i / FPS, d).tobytes())
    p.stdin.close(); p.wait()
# ---------------- build ----------------
if __name__ == '__main__':
    BG = bgdark(); pastille()
    only = set(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else None
    seq = []; aic = 0; n = 0; mode = 0
    for i, l in enumerate(L):
        vis, ovs = P[i]
        s, e = l['s'], l['e']
        nxt = L[i + 1]['s'] if i + 1 < len(L) else e + 1.5
        total = nxt - s
        k = len(vis); w = [1.0] * k
        if k > 1 and vis[0].startswith('g:'): w[0] = 1.6
        ds = [total * x / sum(w) for x in w]
        for j, (v, d) in enumerate(zip(vis, ds)):
            out = f'shots/{i:02d}_{j}.mp4'; seq.append((out, i, j, d, v, [x for x in ovs if (len(x) == 3 and x[2] == j) or (len(x) == 2 and (j == 0 or x[0] == 'label'))]))
            if only is not None and i not in only: continue
            if os.path.exists(out) and only is None: continue
            t, x = v.split(':')
            if t == 'v': shot_video(x, d, out)
            elif t == 'p': kb(f'real/p{x}.jpg', d, out, mode); mode += 1
            elif t == 'd': kb(f'real/p{x}.jpg', d, out, 3)
            elif t == 'a': kb(f'ai/ai{x}.jpg', d, out, mode); mode += 1
            elif t == 'g': shot_graphic(x, d, out)
    json.dump([(a, b, c, d, e, f) for a, b, c, d, e, f in seq], open('seq.json', 'w'), ensure_ascii=False)
    print('shots', len(seq))
