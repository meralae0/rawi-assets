"""Pro audio mix for Rawi videos (rule §13).

Usage:
  python3 tools/mix.py VIDEO_IN VOICE_WAV OUT [--mood tension] [--track file.mp3]
                       [--sfx sfx.wav] [--lead 0.6] [--music-db -16]

- One continuous music bed from rawi-assets/music (never cut at shot boundaries;
  looped with 2 s crossfades if shorter than the video).
- Sidechain ducking under the voice (music drops ~10 dB while speaking, comes back in pauses).
- Optional sfx track mixed on top.
- Fade in 1 s / fade out 2 s, loudness normalised to -14 LUFS, true peak -1 dBTP.
Video stream is copied (no re-encode).
"""
import argparse, json, os, random, subprocess

LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'music')


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode())


def pick(mood, track):
    if track:
        return track if os.path.isabs(track) else os.path.join(LIB, track)
    idx = json.load(open(os.path.join(LIB, 'index.json')))
    c = [t for t in idx if t['mood'] == mood] or idx
    c.sort(key=lambda t: -t['dl'])
    return os.path.join(LIB, random.Random(mood).choice(c[:2])['file'])


def music_bed(src, total, out):
    """Loop src with 2 s crossfades until it covers total seconds."""
    d = dur(src)
    n = max(1, int(total // (d - 2)) + 1)
    if n == 1:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-t', f'{total:.3f}', '-ar', '48000', '-ac', '2', out], check=True)
        return
    ins, fc, last = [], [], '[0:a]'
    for i in range(n):
        ins += ['-i', src]
    for i in range(1, n):
        o = f'[x{i}]'
        fc.append(f'{last}[{i}:a]acrossfade=d=2:c1=tri:c2=tri{o}')
        last = o
    fc.append(f'{last}atrim=0:{total:.3f}[m]')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex', ';'.join(fc), '-map', '[m]', '-ar', '48000', '-ac', '2', out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('voice'); ap.add_argument('out')
    ap.add_argument('--mood', default='tension'); ap.add_argument('--track')
    ap.add_argument('--sfx'); ap.add_argument('--lead', type=float, default=0.0)
    ap.add_argument('--music-db', type=float, default=-16.0)
    a = ap.parse_args()
    total = dur(a.video)
    bed = a.out + '.bed.wav'
    music_bed(pick(a.mood, a.track), total, bed)
    ms = int(a.lead * 1000)
    fc = [f'[1:a]adelay={ms}|{ms},apad,atrim=0:{total:.3f},aresample=48000,aformat=channel_layouts=stereo,asplit[v][sc]',
          f'[2:a]volume={a.music_db}dB[mraw]',
          '[mraw][sc]sidechaincompress=threshold=0.03:ratio=8:attack=60:release=450:makeup=1[mduck]']
    mix_in, n = '[v][mduck]', 2
    ins = ['-i', a.video, '-i', a.voice, '-i', bed]
    if a.sfx:
        ins += ['-i', a.sfx]
        fc.append('[3:a]aresample=48000,aformat=channel_layouts=stereo[s]')
        mix_in += '[s]'; n = 3
    fc.append(f'{mix_in}amix=inputs={n}:normalize=0:duration=first,'
              f'afade=t=in:st=0:d=1,afade=t=out:st={max(0, total - 2):.3f}:d=2,'
              'loudnorm=I=-14:TP=-1:LRA=9[aout]')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[aout]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', a.out], check=True)
    os.remove(bed)


if __name__ == '__main__':
    main()
