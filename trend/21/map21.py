# Cartes ترند 21 : Méditerranée (Maroc entier, Sahara compris, sans frontière interne)
import re, cairosvg, io, sys, math
sys.path.insert(0, '/home/claude/rawi-assets/trend/11')
from gfx import T, eo, W, H, RED, YEL, WH
from PIL import Image, ImageDraw
svgsrc = open('/usr/local/lib/python3.13/site-packages/pygal_maps_world/worldmap.svg').read()
# paths par pays : <g class="country ma"> ... <path d="..."/> ou <path class="country ma" d=...>
D = {}
for m in re.finditer(r'<path[^>]*?(?:class="([^"]*)")?[^>]*?\bd="([^"]+)"[^>]*?/?>', svgsrc):
    pass
for g in re.finditer(r'<g class="([a-z]{2}) country[^"]*">(.*?)</g>', svgsrc, re.S):
    D.setdefault(g.group(1), []).extend(re.findall(r'\bd="([^"]+)"', g.group(2)))
for p in re.finditer(r'<path[^>]*class="country ([a-z]{2})"[^>]*>', svgsrc):
    dd = re.search(r'\bd="([^"]+)"', p.group(0))
    if dd: D.setdefault(p.group(1), []).append(dd.group(1))
VW = 510.0; VX = 1035.0; VY = 222.0; VH = VW * 9 / 16
SC = 4
def lonlat(lon, lat): return (1203.9 + 7.615 * lon, 374.2 + (35.92 - lat) * 8.63)
COL = {'ma': '#c9a227', 'eh': '#c9a227', 'ly': '#2a7f7a', 'ua': '#2f5fb3', 'ru': '#7a2630', 'tr': '#3b4766'}
paths = []
for k, v in D.items():
    c = COL.get(k, '#25324d'); s = c if k in ('ma', 'eh') else '#3a4b70'
    for p in v: paths.append(f'<path d="{p}" fill="{c}" stroke="{s}" stroke-width="0.4"/>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VX} {VY} {VW} {VH}" width="{W*SC//2}" height="{H*SC//2}"><rect x="{VX}" y="{VY}" width="{VW}" height="{VH}" fill="#0b1830"/>{"".join(paths)}</svg>'
BASE = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGB').resize((W, H), Image.LANCZOS)
P = {'od': (1415.3, 283.5), 'bg': (1351.7, 406.6), 'bo': (1411.0, 329.3), 'gb': (1162.0, 374.0),
     'at': (1104.9, 291.6), 'pt': (1129.3, 352.0), 'al': (1219.0, 361.0), 'si': (1287.7, 363.8)}
def px(k):
    x, y = P[k]; return ((x - VX) / VW * W, (y - VY) / VH * H)
def dline(d, pts, k, col, w=8, dash=26):
    # polyline animée en pointillés, k in [0,1]
    seg = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = [math.dist(a, b) for a, b in seg]; tot = sum(L) * k; acc = 0
    for (a, b), l in zip(seg, L):
        if acc >= tot: break
        f = min(1, (tot - acc) / l); n = int(l * f / dash)
        for j in range(n + 1):
            t0 = j * dash / l; t1 = min(f, (j * dash + dash * 0.6) / l)
            if t0 > f: break
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=col, width=w)
        acc += l
def pin(d, p, r, col):
    x, y = p; d.ellipse([x - r - 5, y - r - 5, x + r + 5, y + r + 5], fill=(0, 0, 0)); d.ellipse([x - r, y - r, x + r, y + r], fill=col)
def g_dist(t, Dur, a):
    im = BASE.copy(); d = ImageDraw.Draw(im)
    od = px('od'); bg = px('bg')
    T(d, (50, 330), 'من أوكرانيا', 60, WH, 'lm', stroke=4); T(d, (50, 410), 'إلى بنغازي', 60, WH, 'lm', stroke=4)
    if t > 0.3: pin(d, od, 14, YEL); T(d, (od[0] - 30, od[1] - 10), 'أوديسا', 46, WH, 'rm', stroke=4)
    if t > 0.6: pin(d, bg, 14, RED); T(d, (bg[0], bg[1] + 50), 'بنغازي', 46, WH, stroke=4)
    k = eo((t - 0.8) / 1.6)
    if k > 0: dline(d, [od, bg], k, YEL)
    if k >= 1:
        mx, my = (od[0] + bg[0]) / 2, (od[1] + bg[1]) / 2
        d.rounded_rectangle([mx + 30, my - 45, mx + 330, my + 45], 14, fill=RED); T(d, (mx + 180, my + 2), '≈ 2000 كم', 52)
    return im
def g_route(t, Dur, a):
    im = BASE.copy(); d = ImageDraw.Draw(im)
    T(d, (W - 40, 760), 'طريق السفن', 56, WH, 'rm', stroke=5); T(d, (W - 40, 835), 'الحربية الروسية', 56, WH, 'rm', stroke=5)
    bo = px('bo')
    if t > 0.3:
        x, y = bo; r = 26; d.line([x - r, y - r, x + r, y + r], fill=RED, width=12); d.line([x - r, y + r, x + r, y - r], fill=RED, width=12)
        T(d, (x + 40, y - 30), 'المضائق التركية مغلقة', 42, WH, 'lm', stroke=4)
    pts = [px(k) for k in ('at', 'pt', 'gb', 'al', 'si', 'bg')]
    k = eo((t - 1.0) / 3.0)
    if k > 0: dline(d, pts, k, YEL)
    gb = px('gb')
    if t > 2.2:
        d.ellipse([gb[0] - 34, gb[1] - 34, gb[0] + 34, gb[1] + 34], outline=RED, width=7)
        T(d, (gb[0] + 10, gb[1] + 70), 'مضيق جبل طارق', 46, YEL, stroke=4)
    if k >= 1: b = px('bg'); pin(d, b, 14, RED); T(d, (b[0], b[1] + 50), 'بنغازي', 44, WH, stroke=4)
    return im
def frames_map(kind, dur):
    fn = g_dist if kind == 'dist' else g_route
    for i in range(int(round(dur * 25))): yield fn(i / 25, dur, {})
if __name__ == '__main__':
    print(sorted(k for k in D if k in ('ma', 'eh', 'ly', 'ua', 'ru', 'tr')), len(D))
    s = Image.new('RGB', (W, H // 2 * 2)); s.paste(g_dist(4, 5, {}).resize((W // 2, H // 2)), (0, 0)); s.paste(g_route(6, 9, {}).resize((W // 2, H // 2)), (W // 2, 0)); s.crop((0, 0, W, H // 2)).save('/tmp/maps.jpg')
