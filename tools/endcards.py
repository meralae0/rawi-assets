"""End card + cut card for vertical shorts (1080x1920). Always show the real handle @rawizonetv.
Usage: python3 endcards.py OUTDIR SERIES   (e.g. ملفات / تحقيقات / أرشيف / ترند)"""
import sys
from PIL import Image, ImageDraw, ImageFont
F = lambda s: ImageFont.truetype('/root/.fonts/Tajawal-ExtraBold.ttf', s, layout_engine=ImageFont.Layout.RAQM)
HANDLE = '@rawizonetv'
def draw(path, rows):
    im = Image.new('RGB', (1080, 1920), (14, 14, 16)); d = ImageDraw.Draw(im)
    for txt, size, col, y, box, rtl in rows:
        f = F(size); kw = {'direction': 'rtl'} if rtl else {}
        w = d.textlength(txt, font=f, **kw)
        if box:
            d.rounded_rectangle([540 - w / 2 - 36, y - 14, 540 + w / 2 + 36, y + size + 24], radius=16, fill=box)
        d.text((540 - w / 2, y), txt, font=f, fill=col, **kw)
    im.save(path)
out, series = sys.argv[1], sys.argv[2]
full = 'التحقيق الكامل' if series == 'تحقيقات' else 'الملفّ الكامل' if series == 'ملفات' else 'القصّة الكاملة'
draw(f'{out}/endv.png', [(full, 110, (255, 215, 0), 640, None, True), ('على يوتيوب', 70, (255, 255, 255), 790, None, True),
                         (HANDLE, 92, (255, 255, 255), 960, (200, 26, 26), False), ('ابحثوا عن', 52, (190, 190, 190), 1130, None, True),
                         (f'{series} | Rawi Zone', 54, (255, 215, 0), 1210, None, True)])
draw(f'{out}/cut.png', [(f'مقتطف من {full}', 80, (255, 215, 0), 820, None, True), ('على يوتيوب', 56, (255, 255, 255), 950, None, True),
                        (HANDLE, 62, (255, 255, 255), 1050, (200, 26, 26), False)])
