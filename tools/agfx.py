# Animated graphics for الراوي (dynamic cards, counters, gauges) + paper/whoosh SFX.
# render(scene, d, out) -> list of (t, sfx) events relative to the shot start.
import math, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import reportage_gfx as g

W, H, FPS = 1920, 1080, 25

def eo_back(x, s=1.7):
    x = min(max(x, 0), 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2
def eo_cubic(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3

def shadowed(card, blur=16, off=(10, 14), alpha=120, angle=0):
    """Return RGBA image of card with drop shadow (padded)."""
    pad = 50
    c = card.convert('RGBA')
    if angle: c = c.rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', (c.width + 2 * pad, c.height + 2 * pad), (0, 0, 0, 0))
    m = Image.new('L', c.size, 0); m.paste(c.split()[3])
    s = Image.new('RGBA', c.size, (0, 0, 0, alpha)); s.putalpha(m.point(lambda v: v * alpha // 255))
    sh.alpha_composite(s, (pad + off[0], pad + off[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.alpha_composite(c, (pad, pad))
    return sh

class Layer:
    """An element appearing at time t0 with an entry animation."""
    def __init__(self, img, cx, cy, t0=0.0, anim='drop', dur=0.55, sfx='paper', shadow=True, angle=0):
        self.img = shadowed(img, angle=angle) if shadow else img.convert('RGBA')
        self.cx, self.cy, self.t0, self.anim, self.dur, self.sfx = cx, cy, t0, anim, dur, sfx
    def place(self, frame, t):
        if t < self.t0: return
        p = (t - self.t0) / self.dur
        im = self.img; x, y = self.cx, self.cy; a = 1.0
        if self.anim == 'drop':
            y = self.cy - (1 - eo_back(p)) * 700; a = min(1, p * 3)
        elif self.anim == 'slide':
            x = self.cx + (1 - eo_back(p, 1.2)) * 1100
        elif self.anim == 'slidel':
            x = self.cx - (1 - eo_back(p, 1.2)) * 1100
        elif self.anim in ('pop', 'stamp'):
            k = (2.2 - 1.2 * eo_back(p, 2.5)) if self.anim == 'stamp' else (0.4 + 0.6 * eo_back(p, 2.2))
            if abs(k - 1) > 0.01 and p < 1:
                im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BILINEAR)
            a = min(1, p * 2.5)
        elif self.anim == 'fade':
            a = eo_cubic(p)
        if a < 1:
            im = im.copy(); al = im.split()[3].point(lambda v: int(v * a)); im.putalpha(al)
        frame.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

class Dyn:
    """Per-frame drawn element: fn(t) -> RGBA image (or None); centered at cx, cy."""
    def __init__(self, fn, cx, cy, t0=0.0, sfx=None):
        self.fn, self.cx, self.cy, self.t0, self.sfx = fn, cx, cy, t0, sfx
    def place(self, frame, t):
        if t < self.t0: return
        im = self.fn(t - self.t0)
        if im is not None:
            frame.alpha_composite(im, (int(self.cx - im.width / 2), int(self.cy - im.height / 2)))

def text_img(txt, size, fill, font=None, stroke=0, stroke_fill=(0, 0, 0)):
    f = g.F(font or g.FB, size)
    d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    rtl = any('؀' <= c <= 'ۿ' for c in txt)
    bb = d0.textbbox((0, 0), txt, font=f, stroke_width=stroke, direction='rtl' if rtl else None)
    im = Image.new('RGBA', (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill,
                            direction='rtl' if rtl else None)
    return im

def render(bg, items, d, out, zoom=(1.0, 1.06), drift=(0, 0)):
    """bg: RGB/RGBA 1920x1080 (or callable t->image). items: Layer/Dyn list. Writes out mp4, returns sfx events."""
    n = int(round(d * FPS))
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    base = bg.convert('RGBA') if not callable(bg) else None
    for i in range(n):
        t = i / FPS
        fr = (bg(t).convert('RGBA') if callable(bg) else base.copy())
        for it in items: it.place(fr, t)
        z = zoom[0] + (zoom[1] - zoom[0]) * (i / max(1, n - 1))
        if z != 1.0:
            cw, ch = W / z, H / z
            ox = (W - cw) / 2 + drift[0] * (i / max(1, n - 1)); oy = (H - ch) / 2 + drift[1] * (i / max(1, n - 1))
            fr = fr.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + cw, oy + ch))
        p.stdin.write(fr.convert('RGB').tobytes())
    p.stdin.close(); p.wait()
    ev = []
    for it in items:
        if getattr(it, 'sfx', None) and it.t0 < d - 0.1: ev.append((it.t0, it.sfx))
    return ev

# ---------- SFX synthesis ----------
SR = 48000
def _bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def sfx(kind, seed=0):
    rng = np.random.default_rng(seed)
    if kind == 'paper':      # card slides/lands: crinkle + soft thump
        n = int(0.42 * SR); t = np.arange(n) / SR
        crin = _bp(rng.standard_normal(n), 1800, 7000) * np.exp(-t * 9) * (0.6 + 0.4 * (rng.random(n) > 0.97))
        thump = np.sin(2 * np.pi * (90 + 60 * np.exp(-t * 40)) * t) * np.exp(-t * 28) * 0.8
        x = crin / (np.abs(crin).max() + 1e-9) * 0.55 + thump * 0.6
    elif kind == 'flip':     # page turn
        n = int(0.35 * SR); t = np.arange(n) / SR
        env = np.sin(np.pi * np.minimum(t / 0.3, 1)) ** 2
        x = _bp(rng.standard_normal(n), 1200, 6000) * env; x /= np.abs(x).max() + 1e-9; x *= 0.6
    elif kind == 'stamp':
        n = int(0.3 * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * (70 + 80 * np.exp(-t * 50)) * t) * np.exp(-t * 18) + _bp(rng.standard_normal(n), 300, 3000) * np.exp(-t * 40) * 0.4
        x /= np.abs(x).max(); x *= 0.9
    elif kind == 'whoosh':
        n = int(0.5 * SR); t = np.arange(n) / SR
        env = np.sin(np.pi * t / 0.5) ** 2
        x = _bp(rng.standard_normal(n), 300, 3500) * env; x /= np.abs(x).max() + 1e-9; x *= 0.45
    elif kind == 'tick':
        n = int(0.06 * SR); t = np.arange(n) / SR
        x = _bp(rng.standard_normal(n), 2500, 9000) * np.exp(-t * 90); x /= np.abs(x).max() + 1e-9; x *= 0.35
    else:
        return np.zeros(1)
    return x

def sfx_track(events, total, path, gain=0.55):
    out = np.zeros(int(total * SR) + SR)
    for k, (t, kind) in enumerate(events):
        s = sfx(kind, k); i = int(t * SR)
        if i < len(out): out[i:i + len(s)] += s[:len(out) - i]
    out = np.clip(out * gain, -1, 1)
    st = np.stack([out, out], 1)
    import wave
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
