# Сборка длинного ролика в облаке: python scripts/build.py queue/<ролик>
# Берёт из папки очереди data.ts, abzacy.json, slova.json, voice.mp3, stock.json (клип -> номер Pexels),
# скачивает клипы с Pexels, режет их под абзацы (как _общее/нарезка.py), собирает обложку и ролик.
# Выход: out/<ролик>/ролик.mp4, out/<ролик>/обложка.png. Ключ Pexels - переменная PEXELS_KEY.
import json, os, re, shutil, subprocess, sys, time, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
Q = (ROOT / sys.argv[1]).resolve()
R = ROOT / 'remotion'
OUT = ROOT / 'out' / Q.name
OUT.mkdir(parents=True, exist_ok=True)
CACHE = ROOT / 'cache'
CACHE.mkdir(exist_ok=True)
VF = 'scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1,fps=30,format=yuv420p'
t0 = time.time()

def log(*a):
    print(f'[{time.time() - t0:6.0f} c]', *a, flush=True)

def run(*a, **k):
    subprocess.run(a, check=True, **k)

for f in ('data.ts', 'abzacy.json', 'slova.json'):
    shutil.copy(Q / f, R / 'src' / f)
run('ffmpeg', '-v', 'error', '-y', '-i', str(Q / 'voice.mp3'), '-ar', '48000', '-ac', '1', str(R / 'public' / 'voice.wav'))

# ---------- сток: скачать с Pexels и нарезать ----------
stock = json.loads((Q / 'stock.json').read_text(encoding='utf-8'))
H = {'Authorization': os.environ['PEXELS_KEY'], 'User-Agent': 'fakty-konveyer'}

def download(name):
    dst = CACHE / f'{name}.mp4'
    if dst.exists():
        return dst
    info = json.load(urllib.request.urlopen(urllib.request.Request(
        f'https://api.pexels.com/videos/videos/{stock[name]}', headers=H), timeout=60))
    files = [f for f in info['video_files'] if (f.get('width') or 0) > (f.get('height') or 0)] or info['video_files']
    best = sorted(files, key=lambda f: abs(1920 - (f.get('width') or 0)))[0]
    if not best['link'].startswith('https://'):
        sys.exit(f'странная ссылка Pexels у {name}: {best["link"][:60]}')
    req = urllib.request.Request(best['link'], headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=300) as r, open(dst, 'wb') as w:
        shutil.copyfileobj(r, w)
    return dst

ABZ = json.loads((Q / 'abzacy.json').read_text(encoding='utf-8'))
data = (Q / 'data.ts').read_text(encoding='utf-8')
plan = data[data.index('export const PLAN'):]
plan = plan[:plan.index('];')]
need = {}
for p, clips in re.findall(r'\[(\d+),\s*\[([^\]]*)\]\]', plan):
    p = int(p)
    a = ABZ[p - 1]['s']
    b = ABZ[p]['s'] if p < len(ABZ) else ABZ[-1]['e'] + 3 + 13  # +13 - финальная заставка (END_SEC в Film.tsx)
    clips = re.findall(r"'([^']+)'", clips)
    for c in clips:
        name, _, ss = c.partition('@')
        k = (name, float(ss or 0))
        need[k] = max(need.get(k, 0), (b - a) / len(clips) + 1.0)
cov = re.search(r"COVER = \{clip: '([a-z0-9-]+)_([\d.]+)'", data)
need.setdefault((cov.group(1), float(cov.group(2))), 5.0)

out = R / 'public' / 'stock'
out.mkdir(parents=True, exist_ok=True)
for (name, ss), d in need.items():
    src = download(name)
    srcdur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(src)],
                                  capture_output=True, text=True).stdout)
    slow = max(1.0, d / max(0.5, srcdur - ss - 0.1))
    vf = (f'setpts={slow:.3f}*PTS,' if slow > 1.0 else '') + VF
    run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(ss), '-i', str(src), '-t', f'{d / slow:.2f}',
        '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', str(out / f'{name}_{ss:g}.mp4'))
log('сток готов:', len(need), 'кусков из', len(stock), 'клипов')

# ---------- обложка и ролик (как _общее/рендер.py) ----------
def rem(*a):
    run('npx', 'remotion', *a, '--log=error', cwd=R)

def loud(src, dst):
    ch = 'alimiter=limit=0.7:level=false,loudnorm=I=-14:TP=-1.5:LRA=11'
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(src), '-vn', '-af', ch + ':print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True, encoding='utf-8', errors='ignore').stderr
    j = json.loads(err[err.rindex('{'):err.rindex('}') + 1])
    flt = (ch + f":measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
           f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(src), '-c:v', 'copy', '-af', flt,
        '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(dst))

rem('still', 'src/index.ts', 'Oblozhka', str(OUT / 'обложка.png'))
log('обложка готова')
rem('render', 'src/index.ts', 'Rolik', str(OUT / 'сборка.mp4'), '--codec=h264', '--crf=18', '--audio-bitrate=256k')
loud(OUT / 'сборка.mp4', OUT / 'ролик.mp4')
(OUT / 'сборка.mp4').unlink()
log('ролик готов:', round((OUT / 'ролик.mp4').stat().st_size / 2**20, 1), 'МБ')
