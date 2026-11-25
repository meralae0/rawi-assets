import json, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
os.chdir('/home/claude/dy')
L = json.load(open('lines.json'))
W, H, FPS = 1080, 1920, 30
TJ = ImageFont.truetype('/root/.fonts/Tajawal-ExtraBold.ttf', 74, layout_engine=ImageFont.Layout.RAQM)
SH = {'s1': [0, 2, 3, 4, 5], 's2': [35, 36, 37, 40]}
subprocess.run(['python3', '/home/claude/rawi-assets/tools/endcards.py', '.', 'تحقيقات'], check=True)
def run(a): subprocess.run(['ffmpeg', '-y', '-v', 'error'] + a, check=True)
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())
def cap_frames(words, t0, t1, tag):
    """karaoke caption pngs: list of (start,end,png) ; words timed by char length; chunks <= 5 words"""
    out = []; n = len(words)
    tot = sum(len(w) + 1 for w in words); t = t0; times = []
    for w in words:
        d = (t1 - t0) * (len(w) + 1) / tot; times.append((t, t + d)); t += d
    for c0 in range(0, n, 4):
        chunk = words[c0:c0 + 4]
        for k in range(len(chunk)):
            im = Image.new('RGBA', (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            full = ' '.join(chunk)
            wfull = TJ.getlength(full, direction='rtl'); xr = W / 2 + wfull / 2
            x = xr
            for j, w in enumerate(chunk):
                ww = TJ.getlength(w, direction='rtl')
                col = (255, 214, 0) if j == k else (255, 255, 255)
                d.text((x, 130), w, font=TJ, fill=col, anchor='rm', direction='rtl', stroke_width=8, stroke_fill=(0, 0, 0))
                x -= ww + TJ.getlength(' ')
            p = f'vt/{tag}_{c0 + k:03d}.png'; im.save(p)
            out.append((times[c0 + k][0], times[c0 + k][1], p))
    return out
os.makedirs('vt', exist_ok=True)
for tag, idx in SH.items():
    segs = []; tcur = 0.0; caps = []; parts = []
    for n, i in enumerate(idx):
        s = L[i]['s'] - (0.15 if n else 0.0); e = L[i]['e'] + 0.25
        if i == 4: e = L[i]['e'] + 0.6
        d = e - s
        v = f'vt/{tag}_{n}.mp4'
        fc = (f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bg];"
              f"[0:v]scale=1080:-2[fg];[bg][fg]overlay=0:560,setsar=1,fps={FPS}")
        run(['-ss', f'{s:.3f}', '-i', 'body2.mp4', '-t', f'{d:.3f}', '-filter_complex', fc, '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', v])
        run(['-i', 'voice.wav', '-ss', f'{s:.3f}', '-t', f'{d:.3f}', '-ar', '48000', '-ac', '2', f'vt/{tag}_{n}.wav'])
        caps += cap_frames(L[i]['text'].split(), tcur + (L[i]['s'] - s), tcur + (L[i]['e'] - s), f'{tag}{n}')
        parts.append((v, d)); tcur += d
    # end card 2.5 s
    run(['-loop', '1', '-i', 'endv.png', '-t', '2.5', '-vf', f'fps={FPS},format=yuv420p,fade=in:st=0:d=0.3', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', f'vt/{tag}_end.mp4'])
    run(['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', '2.5', f'vt/{tag}_end.wav'])
    parts.append((f'vt/{tag}_end.mp4', 2.5))
    # concat video with quick xfade(slide) between parts
    ins = []; fc = []; last = '[0:v]'; off = 0.0
    for k, (p, d) in enumerate(parts): ins += ['-i', p]
    for k in range(1, len(parts)):
        off += parts[k - 1][1] - 0.3
        tr = 'slideleft' if k < len(parts) - 1 else 'fadewhite'
        fc.append(f"{last}[{k}:v]xfade=transition={tr}:duration=0.3:offset={off:.3f}[x{k}]"); last = f'[x{k}]'
    run(ins + ['-filter_complex', ';'.join(fc), '-map', last, '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', f'vt/{tag}_v.mp4'])
    # voice: concat wavs with 0.3 overlap compensation (acrossfade)
    ains = []; afc = []; al = '[0:a]'
    wavs = [p.replace('.mp4', '.wav') for p, _ in parts]
    for p in wavs: ains += ['-i', p]
    for k in range(1, len(wavs)):
        afc.append(f"{al}[{k}:a]acrossfade=d=0.3[a{k}]"); al = f'[a{k}]'
    run(ains + ['-filter_complex', ';'.join(afc), '-map', al, f'vt/{tag}_voice.wav'])
    # shift caption times for xfade overlap: each boundary removes 0.3 s
    bounds = []; acc = 0
    for k, (p, d) in enumerate(parts): bounds.append(acc); acc += d
    def shift(t):
        k = sum(1 for b in bounds[1:] if t >= b); return t - 0.3 * k
    caps = [(shift(a), shift(b), p) for a, b, p in caps]
    # overlays: captions + progress bar (RTL fill)
    vd = dur(f'vt/{tag}_v.mp4')
    ins = ['-i', f'vt/{tag}_v.mp4']; fc = []; last = '[0:v]'
    for k, (a, b, p) in enumerate(caps):
        ins += ['-i', p]
        fc.append(f"{last}[{k + 1}:v]overlay=0:1290:enable='between(t,{a:.3f},{b:.3f})'[c{k}]"); last = f'[c{k}]'
    fc.append(f"color=c=0xFFD600:s=1080x12:d={vd:.3f}[bar];{last}[bar]overlay=x='W-W*t/{vd:.3f}':y=0[vo]")
    open(f'vt/{tag}_fc.txt', 'w').write(';'.join(fc))
    run(ins + ['-filter_complex_script', f'vt/{tag}_fc.txt', '-map', '[vo]', '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', f'vt/{tag}_vc.mp4'])
    subprocess.run(['python3', '/home/claude/rawi-assets/tools/mix.py', f'vt/{tag}_vc.mp4', f'vt/{tag}_voice.wav', f'short_{tag}.mp4',
                    '--track', '/home/claude/rawi-assets/music/mystere_darkness-mystery.mp3', '--music-db', '-17'], check=True)
    print(tag, dur(f'short_{tag}.mp4'))
