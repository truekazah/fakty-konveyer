# Сборка ролика: python scripts/build.py queue/<ролик> [--bez-shorts]
# Берёт из папки очереди data.ts, abzacy.json, slova.json, voice.mp3 (их делает prepare.py), stock.json, meta.json.
# Режет клипы Pexels под абзацы (как _общее/нарезка.py), собирает обложку, ролик 16:9, Shorts, описание.
# Выход: out/<ролик>/ - <ролик>.mp4, oblozhka.png, opisanie.txt, Short-<id>.mp4 (латиница: GitHub портит кириллицу
# в именах файлов релиза; имя длинного = имя папки, с ним Руслан грузит черновик, по нему publish.py его находит).
import json, re, shutil, subprocess, sys, time
from common import ROOT, run
from stock import download

Q = (ROOT / sys.argv[1]).resolve()
R = ROOT / 'remotion'
OUT = ROOT / 'out' / Q.name
OUT.mkdir(parents=True, exist_ok=True)
VF = 'scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1,fps=30,format=yuv420p'
t0 = time.time()


def log(*a):
    print(f'[{time.time() - t0:6.0f} c]', *a, flush=True)


for f in ('data.ts', 'abzacy.json', 'slova.json'):
    shutil.copy(Q / f, R / 'src' / f)
run('ffmpeg', '-v', 'error', '-y', '-i', Q / 'voice.mp3', '-ar', '48000', '-ac', '1', R / 'public' / 'voice.wav')

# ---------- сток ----------
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
shutil.rmtree(out, ignore_errors=True)
out.mkdir(parents=True)
for (name, ss), d in need.items():
    src = download(name, Q)
    srcdur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(src)],
                                  capture_output=True, text=True).stdout)
    slow = max(1.0, d / max(0.5, srcdur - ss - 0.1))
    vf = (f'setpts={slow:.3f}*PTS,' if slow > 1.0 else '') + VF
    run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', ss, '-i', src, '-t', f'{d / slow:.2f}',
        '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', out / f'{name}_{ss:g}.mp4')
log('сток готов:', len(need), 'кусков')


# ---------- рендер (как _общее/рендер.py) ----------
def rem(*a):
    run('npx', 'remotion', *a, '--log=error', cwd=R)


def loud(src, dst):
    ch = 'alimiter=limit=0.7:level=false,loudnorm=I=-14:TP=-1.5:LRA=11'
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(src), '-vn', '-af', ch + ':print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True, encoding='utf-8', errors='ignore').stderr
    j = json.loads(err[err.rindex('{'):err.rindex('}') + 1])
    flt = (ch + f":measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
           f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-c:v', 'copy', '-af', flt,
        '-ar', '48000', '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', dst)
    src.unlink()


rem('still', 'src/index.ts', 'Oblozhka', OUT / 'oblozhka.png')
log('обложка готова')
rem('render', 'src/index.ts', 'Rolik', OUT / 'сборка.mp4', '--codec=h264', '--crf=18', '--audio-bitrate=256k')
loud(OUT / 'сборка.mp4', OUT / f'{Q.name}.mp4')
log('ролик готов:', round((OUT / f'{Q.name}.mp4').stat().st_size / 2**20, 1), 'МБ')
if '--bez-shorts' not in sys.argv:
    asks = set(re.findall(r"id: '(Short-[^']+)'[^}]*ask: '", data))  # с вопросом зрителю плашка 3,8 сек
    for sid in re.findall(r"id: '(Short-[^']+)'", data):
        rem('render', 'src/index.ts', sid, OUT / f'{sid}-s.mp4', '--codec=h264', '--crf=18', '--audio-bitrate=256k')
        # тишина под плашкой «Полное видео»: глушилка в Film.tsx не срабатывает в Shorts - там слышно
        # начало следующего абзаца (тест 18.10.2026, Whisper: «Вот такие они»), поэтому глушим здесь
        d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                  str(OUT / f'{sid}-s.mp4')], capture_output=True, text=True).stdout)
        run('ffmpeg', '-v', 'error', '-y', '-i', OUT / f'{sid}-s.mp4', '-c:v', 'copy',
            '-af', f'volume=0:enable=gte(t\\,{d - (3.9 if sid in asks else 1.9):.2f})', '-c:a', 'aac', '-b:a', '256k', OUT / f'{sid}-m.mp4')
        (OUT / f'{sid}-s.mp4').unlink()
        loud(OUT / f'{sid}-m.mp4', OUT / f'{sid}.mp4')
        log(sid, 'готов')

# ---------- описание с главами (как _общее/описание.py) ----------
meta = json.loads((Q / 'meta.json').read_text(encoding='utf-8'))
chapters = [(int(p), t) for p, t in re.findall(r"\[(\d+),\s*'([^']+)'\]", data[data.index('export const CHAPTERS'):])]
tc = lambda s: f'{int(s) // 60}:{int(s) % 60:02d}'
lines = ['0:00 Вступление'] + [f"{tc(ABZ[p - 1]['s'])} {t}" for p, t in chapters] + [f"{tc(ABZ[-1]['s'])} Итог"]
(OUT / 'opisanie.txt').write_text(f"{meta['intro']}\n\nГлавы:\n" + '\n'.join(lines) + '\n\n#факты #интересныефакты #наука\n',
                                  encoding='utf-8')
log('описание готово')
