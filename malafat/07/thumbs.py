import sys
sys.path.insert(0, '/home/claude/rawi-assets/tools')
import reportage_gfx as g
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W, H = 1280, 720
def outline_text(d, xy, t, f, fill, ow=8, anchor='mm'):
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            if dx * dx + dy * dy <= ow * ow:
                d.text((xy[0] + dx, xy[1] + dy), t, font=f, fill=(0, 0, 0), anchor=anchor, direction='rtl')
    d.text(xy, t, font=f, fill=fill, anchor=anchor, direction='rtl')
# 16:9
bg = Image.open('src/14.jpg').convert('RGB')
bg = bg.resize((int(bg.width * H / bg.height * 1.6), int(H * 1.6))).crop((300, 250, 300 + W, 250 + H))
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(3))).enhance(0.45)
sk = Image.open('src/01.jpg').convert('RGB'); sk = sk.resize((int(sk.width * 640 / sk.height), 640))
fr = Image.new('RGB', (sk.width + 20, sk.height + 20), (250, 246, 236)); fr.paste(sk, (10, 10))
g.shadow_paste(bg, fr, (W - fr.width - 50, 40), angle=-3)
d = ImageDraw.Draw(bg)
outline_text(d, (380, 150), 'قفز ومعه', g.F(g.FB, 110), (255, 255, 255))
outline_text(d, (380, 290), '200,000$', g.F(g.FB, 130), g.YEL)
outline_text(d, (380, 430), '…واختفى!', g.F(g.FB, 120), (255, 255, 255))
d.rounded_rectangle((40, 30, 200, 90), 12, fill=g.RED); d.text((120, 62), 'ملفات', font=g.F(g.FB, 40), fill=(255, 255, 255), anchor='mm', direction='rtl')
bg.save('thumbA.jpg', quality=92)
# vertical cover 1080x1920
V = Image.new('RGB', (1080, 1920))
b2 = Image.open('src/14.jpg').convert('RGB'); b2 = b2.resize((int(b2.width * 1920 / b2.height), 1920)).crop((1500, 0, 2580, 1920))
V.paste(ImageEnhance.Brightness(b2.filter(ImageFilter.GaussianBlur(6))).enhance(0.4), (0, 0))
sk2 = Image.open('src/01.jpg').convert('RGB'); sk2 = sk2.resize((760, int(sk2.height * 760 / sk2.width)))
fr2 = Image.new('RGB', (sk2.width + 24, sk2.height + 24), (250, 246, 236)); fr2.paste(sk2, (12, 12))
g.shadow_paste(V, fr2, (140, 700), angle=2)
d = ImageDraw.Draw(V)
outline_text(d, (540, 300), 'قفز من الطائرة', g.F(g.FB, 110), (255, 255, 255))
outline_text(d, (540, 470), '…واختفى!', g.F(g.FB, 140), g.YEL)
d.rounded_rectangle((60, 80, 260, 160), 14, fill=g.RED); d.text((160, 122), 'ملفات', font=g.F(g.FB, 52), fill=(255, 255, 255), anchor='mm', direction='rtl')
V.save('cover-v.jpg', quality=92)
