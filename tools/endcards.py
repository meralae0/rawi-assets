"""End card + cut card for vertical shorts (1080x1920). Always show the real handle @rawizonetv.
Usage: python3 endcards.py OUTDIR SERIES   (e.g. ملفات / تحقيقات / أرشيف / ترند)"""
import sys
from PIL import Image, ImageDraw, ImageFont
F = lambda s: ImageFont.truetype('/root/.fonts/Tajawal-ExtraBold.ttf', s, layout_engine=ImageFont.Layout.RAQM)
HANDLE = '@rawizonetv'
POP = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
SEGS = [('@', (130, 130, 130)), ('rawi', (255, 196, 0)), ('zone', (255, 255, 255)), ('tv', (0, 190, 255))]  # choix C d'Alae, 17 nov.
NAME = [('Rawi ', (255, 196, 0)), ('Zone', (255, 255, 255))]  # nom trouvable sur Google (17 nov.)
def wordmark(d, y, size, segs=SEGS):
    f = ImageFont.truetype(POP, size); ws = [d.textlength(t, font=f) for t, _ in segs]; x = 540 - sum(ws) / 2
    for (t, c), w in zip(segs, ws): d.text((x, y), t, font=f, fill=c); x += w
def draw(path, rows):
    im = Image.new('RGB', (1080, 1920), (14, 14, 16)); d = ImageDraw.Draw(im)
    for txt, size, col, y, box, rtl in rows:
        if txt == HANDLE: wordmark(d, y, size); continue
        if txt == 'NAME': wordmark(d, y, size, NAME); continue
        f = F(size); kw = {'direction': 'rtl'} if rtl else {}
        w = d.textlength(txt, font=f, **kw)
        if box:
            d.rounded_rectangle([540 - w / 2 - 36, y - 14, 540 + w / 2 + 36, y + size + 24], radius=16, fill=box)
        d.text((540 - w / 2, y), txt, font=f, fill=col, **kw)
    im.save(path)
out, series = sys.argv[1], sys.argv[2]
full = 'التحقيق الكامل' if series == 'تحقيقات' else 'الملفّ الكامل' if series == 'ملفات' else 'القصّة الكاملة'
draw(f'{out}/endv.png', [(full, 110, (255, 215, 0), 620, None, True), ('على يوتيوب ابحثوا عن', 64, (255, 255, 255), 780, None, True),
                         ('NAME', 150, None, 900, None, False), (HANDLE, 64, None, 1110, None, False)])
draw(f'{out}/cut.png', [(f'مقتطف من {full}', 80, (255, 215, 0), 800, None, True), ('على يوتيوب', 56, (255, 255, 255), 930, None, True),
                        ('NAME', 104, None, 1020, None, False), (HANDLE, 50, None, 1170, None, False)])
