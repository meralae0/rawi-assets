# Carte animée : Maroc entier (Sahara compris, sans frontière interne) + zones industrielles de défense
import json, cairosvg, io, sys
sys.path.insert(0, '/home/claude/rawi-assets/trend/11')
from gfx import T, eo, W, H, RED, YEL, WH, MU
from PIL import Image, ImageDraw
D = json.load(open('/home/claude/t19/mapd.json'))
VW = 360.0; VX, VY = 1135 - VW / 2, 440 - VW * 9 / 32  # viewBox (16:9)
VH = VW * 9 / 16
SC = 6  # rendu 6x pour pouvoir zoomer
def lonlat(lon, lat): return (1203.9 + 7.615 * lon, 374.2 + (35.92 - lat) * 8.63)
paths = []
for k, v in D.items():
    if k in ('ma', 'eh'): continue
    for p in v: paths.append(f'<path d="{p}" fill="#25324d" stroke="#3a4b70" stroke-width="0.4"/>')
for k in ('ma', 'eh'):
    for p in D[k]: paths.append(f'<path d="{p}" fill="#c9a227" stroke="#c9a227" stroke-width="0.6"/>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VX} {VY} {VW} {VH}" width="{W*SC//2}" height="{H*SC//2}"><rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" fill="#0b1830"/>{"".join(paths)}</svg>'
BASE = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGB')
BW, BH = BASE.size
def to_px(lon, lat):
    x, y = lonlat(lon, lat); return ((x - VX) / VW * BW, (y - VY) / VH * BH)
Z = [('النواصر', -7.58, 33.37, 0), ('سيدي يحيى الغرب', -6.30, 34.31, 0), ('بنجرير', -7.95, 32.24, 1), ('بنسليمان', -7.12, 33.62, 1)]
def g_map(t, Dur, a):
    # 0-1.2 s : Maroc entier ; 1.2-2.6 s : zoom vers le nord-ouest ; puis épingles
    z = 1 + 2.6 * eo((t - 1.2) / 1.4)
    cx0, cy0 = BW / 2, BH / 2; tx, ty = to_px(-7.0, 33.2)
    k = eo((t - 1.2) / 1.4); cx = cx0 + (tx - cx0) * k; cy = cy0 + (ty - cy0) * k
    w, h = BW / z, BH / z
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    im = BASE.crop(tuple(int(v) for v in box)).resize((W, H), Image.LANCZOS); d = ImageDraw.Draw(im)
    def sc(p): return ((p[0] - box[0]) / w * W, (p[1] - box[1]) / h * H)
    T(d, (W - 160, 120), 'مناطق صناعية للدفاع', 62, WH, 'rm', stroke=3)
    for i, (n, lon, lat, new) in enumerate(Z):
        st = 2.8 + 0.55 * i
        if t < st: continue
        kk = eo((t - st) / 0.35); x, y = sc(to_px(lon, lat)); r = 18 * kk
        col = YEL if new else RED
        d.ellipse([x - r - 6, y - r - 6, x + r + 6, y + r + 6], fill=(0, 0, 0)); d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        if kk > 0.6:
            off = -40 if i in (1, 3) else 40
            T(d, (x - 34, y + off), n, 46, WH, 'rm', stroke=4)
    if t > 5.2:
        d.rounded_rectangle([140, 900, 520, 980], 14, fill=RED); T(d, (330, 942), 'منطقة قائمة', 42)
        d.rounded_rectangle([560, 900, 1000, 980], 14, fill=YEL); T(d, (780, 942), 'منطقة جديدة', 42, (20, 20, 30))
    return im
if __name__ == '__main__':
    for tt in (0.5, 2.0, 6.5):
        g_map(tt, 8, {}).save(f'/tmp/map_{tt}.jpg')
