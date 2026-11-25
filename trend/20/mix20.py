import json,subprocess
sfx=json.load(open('sfx.json')); SF='/home/claude/rawi-assets/sfx/'
inputs=['-i','body.mp4','-i','voice.wav','-stream_loop','-1','-i','/home/claude/rawi-assets/music/enquete_mystery-detective-investigation-music.mp3','-loop','1','-i','ov/wm.png']
fc=['[0:v][3:v]overlay=0:0:shortest=1[v]','[2:a]volume=0.16,aresample=48000,aformat=channel_layouts=stereo[m]','[1:a]aresample=48000,aformat=channel_layouts=stereo,apad=pad_dur=1.2,asplit=2[vo][sc]','[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md]']
mix=['[vo]','[md]']
for i,(f,t) in enumerate(sfx):
    inputs+=['-i',SF+f]; k=4+i; vol=0.35 if 'page' in f else 0.5
    fc.append(f'[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={int(t*1000)}|{int(t*1000)}[s{i}]'); mix.append(f'[s{i}]')
fc.append(''.join(mix)+f'amix=inputs={len(mix)}:normalize=0:duration=first,afade=t=out:st=139.8:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11[a]')
subprocess.run(['ffmpeg','-y','-v','error']+inputs+['-filter_complex',';'.join(fc),'-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','141.3','-movflags','+faststart','t20.mp4'],check=True)
