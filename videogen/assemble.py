import subprocess, json, os
A = '/home/claude/aud'
B = '/home/claude/build'
FONTS = '/home/claude/fonts/Amiri-1.000'
W, H, FPS = 1280, 720, 25
GAP, LEAD, TAIL = 0.4, 0.5, 0.6

def dur(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))

lines = json.load(open('/home/claude/markaz-alhusna.github.io/videogen/job.json'))['speech']['lines']
names = {'ahmad': 'أَحْمَدُ', 'omar': 'عُمَرُ'}
audio = {}
for i, l in enumerate(lines):
    f = f"{A}/kid_line{i:02d}-{l['who']}.wav"
    audio[i] = (f, dur(f))

# segment: source, kind, lines, motion
segs = [
    ('s1.png', 'img', [0], 'in'),
    ('v2.mp4', 'vid', [1, 2], None),
    ('s3.png', 'img', [3, 4], 'out'),
    ('s6.png', 'img', [5, 6], 'in'),
    ('s4.png', 'img', [7], 'in'),
    ('s5.png', 'img', [8], 'in'),
    ('s4.png', 'img', [9], 'left'),
    ('s5.png', 'img', [10], 'right'),
    ('s4.png', 'img', [11], 'out'),
    ('v7.mp4', 'vid', [12, 13], None),
]

t = 0.0
parts, events, subs = [], [], []
for k, (src, kind, ls, motion) in enumerate(segs):
    start = t
    cur = t + LEAD
    for i in ls:
        f, d = audio[i]
        events.append((f, cur))
        if i > 0:
            subs.append((cur - 0.1, cur + d + 0.25, f"{names[lines[i]['who']]}: {lines[i]['text']}"))
        else:
            subs.append(('title', start, None))
        cur += d + GAP
    seglen = cur - start - GAP + TAIL
    if k == len(segs) - 1:
        seglen += 1.0
    out = f'{B}/seg{k:02d}.mp4'
    n = int(round(seglen * FPS))
    if kind == 'img':
        z = {'in': ("1+0.07*on/{n}", 'iw/2-(iw/zoom/2)', 'ih/2-(ih/zoom/2)'),
             'out': ("1.07-0.07*on/{n}", 'iw/2-(iw/zoom/2)', 'ih/2-(ih/zoom/2)'),
             'left': ("1.08", '(iw-iw/zoom)*(1-on/{n})', 'ih/2-(ih/zoom/2)'),
             'right': ("1.08", '(iw-iw/zoom)*on/{n}', 'ih/2-(ih/zoom/2)')}[motion]
        zz, xx, yy = [s.replace('{n}', str(n)) for s in z]
        vf = (f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
              f"zoompan=z='{zz}':x='{xx}':y='{yy}':d={n}:s={W}x{H}:fps={FPS},format=yuv420p")
        cmd = ['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', f'{B}/{src}', '-vf', vf, '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', out]
    else:
        vd = dur(f'{B}/{src}')
        factor = max(1.0, seglen / vd)
        vf = f"setpts={factor:.4f}*PTS,fps={FPS},scale={W}:{H},tpad=stop_mode=clone:stop_duration=3,format=yuv420p"
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', f'{B}/{src}', '-an', '-vf', vf, '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', out]
    if not os.path.exists(out): subprocess.run(cmd, check=True)
    parts.append(out)
    t += n / FPS
total = t

# concat with short crossfade-free cuts
with open(f'{B}/list.txt', 'w') as fh:
    for p in parts:
        fh.write(f"file '{p}'\n")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{B}/list.txt', '-c', 'copy', f'{B}/video_raw.mp4'], check=True)

# audio mix
inputs, filt = [], []
for j, (f, st) in enumerate(events):
    inputs += ['-i', f]
    ms = int(st * 1000)
    filt.append(f"[{j}:a]adelay={ms}|{ms},aformat=channel_layouts=stereo[a{j}]")
mix = ''.join(f'[a{j}]' for j in range(len(events)))
filt.append(f"{mix}amix=inputs={len(events)}:normalize=0,apad=whole_dur={total:.2f}[aout]")
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[aout]', '-t', f'{total:.2f}', '-ar', '48000', f'{B}/audio.wav'], check=True)

# ASS subtitles
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"
ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Line,Amiri,62,&H00FFFFFF,&H00FFFFFF,&H00301A0A,&H90000000,1,0,0,0,175,175,0,0,1,4,3,2,60,60,30,1
Style: Title,Amiri,104,&H00FFFFFF,&H00FFFFFF,&H00402818,&H80000000,1,0,0,0,160,160,0,0,1,4,2,8,60,60,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
title_end = audio[0][1] + LEAD + TAIL + 0.2
for s in subs:
    if s[0] == 'title':
        ass += f"Dialogue: 0,{ts(0.2)},{ts(title_end)},Title,,0,0,0,,{{\\fad(400,300)}}{lines[0]['text']}\n"
    else:
        ass += f"Dialogue: 0,{ts(s[0])},{ts(s[1])},Line,,0,0,0,,{{\\fad(150,150)}}{s[2]}\n"
open(f'{B}/subs.ass', 'w').write(ass)

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{B}/video_raw.mp4', '-i', f'{B}/audio.wav',
                '-vf', f"subtitles={B}/subs.ass:fontsdir={FONTS},fade=t=in:st=0:d=0.5,fade=t=out:st={total-0.8:.2f}:d=0.8",
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', f'{B}/al-husna-dialog-taaruf.mp4'], check=True)
print('total', round(total, 2))
