# Подготовка ролика к сборке: python scripts/prepare.py queue/<ролик>
# 1) голос: склейка абзацев (тишина по краям срезана, хук +3 дБ), время слов Whisper под слова сценария
#    -> voice.mp3, abzacy.json, slova.json (перенос _общее/голос.py);
# 2) кадры: стоп-кадр каждого клипа смотрит Gemini; «не то» - замена из запаса абзаца (POOL в plan.json);
# 3) data.ts для Remotion (перенос _общее/данные.py) + Shorts по абзацам из plan.json.
# plan.json: {"PLAN": [[абзац, ["клип" | "клип@сек" | "~клип" - фон без проверки]]], "POOL": {"абзац": [запасные клипы]},
#   "SUBJ": {"абзац": "что в кадре"} (по умолчанию - заголовок абзаца до точки),
#   "CHAPTERS": [[абзац, "Глава"]], "COVER": {...}, "SHORTS": [{"id", "abz": [с, по], "title", "text"}]}
import difflib, json, re, subprocess, sys, time, pathlib
from common import audio16k, ROOT, looks_like, paragraphs, run, save_state, state, tg
from stock import download

Q = (ROOT / sys.argv[1]).resolve()
T = ROOT / 'tmp' / Q.name
T.mkdir(parents=True, exist_ok=True)
ABZ = paragraphs(Q)
PL = json.loads((Q / 'plan.json').read_text(encoding='utf-8'))
GAP, HOOK_GAP, HOOK_DB = 0.5, 0.7, 3.0


def ff(*a):
    run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *a)


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                capture_output=True, text=True).stdout)


# ---------- 1. голос ----------
parts = []
trim = ('silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,'
        'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse')
for i in range(1, len(ABZ) + 1):
    out = T / f'abz{i:02d}.wav'
    ff('-i', str(Q / 'voice' / f'{i:02d}.mp3'), '-af', trim + (f',volume={HOOK_DB}dB' if i == 1 else ''),
       '-ar', '48000', '-ac', '1', str(out))
    parts.append(out)
sil = {g: T / f'sil{g}.wav' for g in (GAP, HOOK_GAP)}
for g, p in sil.items():
    ff('-f', 'lavfi', '-t', str(g), '-i', 'anullsrc=r=48000:cl=mono', str(p))
lst, t, abzacy = [], 0.0, []
for i, p in enumerate(parts, 1):
    d = dur(p)
    abzacy.append({'n': i, 's': round(t, 3), 'e': round(t + d, 3), 'text': ABZ[i - 1]})
    lst.append(p); t += d
    if i < len(parts):
        g = HOOK_GAP if i == 1 else GAP
        lst.append(sil[g]); t += g
(T / 'spisok.txt').write_text(''.join(f"file '{p.as_posix()}'\n" for p in lst), encoding='utf-8')
ff('-f', 'concat', '-safe', '0', '-i', str(T / 'spisok.txt'), '-af', 'loudnorm=I=-15:TP=-1.5:LRA=9',
   '-ar', '48000', '-ac', '1', '-b:a', '192k', str(Q / 'voice.mp3'))

from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cpu', compute_type='int8')


def norm(s):
    return re.sub(r'[^а-яёa-z0-9]', '', s.lower().replace('ё', 'е'))


W = []
for i, p in enumerate(parts, 1):
    segs, _ = model.transcribe(audio16k(p), language='ru', word_timestamps=True)
    hyp = [[w.start, w.end, w.word.strip()] for s in segs for w in s.words]
    off = abzacy[i - 1]['s']
    rr = []
    for w in ABZ[i - 1].replace(' - ', ' — ').split():
        w = w.replace('—', '-')
        if w == '-' and rr: rr[-1] += ' -'
        else: rr.append(w)
    a, b = [norm(w) for w in rr], [norm(h[2]) for h in hyp]
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal':
            out += [{'w': rr[i1 + k], 's': hyp[j1 + k][0], 'e': hyp[j1 + k][1]} for k in range(i2 - i1)]
        elif op == 'replace' and any(re.search(r'\d', hyp[j][2]) for j in range(j1, j2)):
            tail = re.sub(r'^.*?([.,!?:;]*)$', r'\1', rr[i2 - 1])
            ws = [{'w': hyp[j][2].rstrip('.,!?:;'), 's': hyp[j][0], 'e': hyp[j][1]} for j in range(j1, j2)]
            ws[-1]['w'] += tail
            out += ws
        elif op in ('replace', 'delete'):
            s0 = hyp[j1][0] if op == 'replace' else (out[-1]['e'] if out else 0.0)
            e0 = hyp[j2 - 1][1] if op == 'replace' else (hyp[j1][0] if j1 < len(hyp) else s0 + 0.3 * (i2 - i1))
            ln = [max(1, len(norm(w))) for w in rr[i1:i2]]
            tot, acc = sum(ln), s0
            for w, l in zip(rr[i1:i2], ln):
                d = (e0 - s0) * l / tot
                out.append({'w': w, 's': acc, 'e': acc + d}); acc += d
    for k in range(len(out) - 1, 0, -1):
        if (re.match(r'^-\d', out[k]['w']) and re.search(r'\d$', out[k - 1]['w'])) or out[k]['w'] == '%':
            out[k - 1]['w'] += out[k]['w']; out[k - 1]['e'] = out[k]['e']; del out[k]
    for w in out:
        W.append({'w': w['w'], 's': round(w['s'] + off, 3), 'e': round(w['e'] + off, 3), 'p': i})
    print('whisper', i, flush=True)
(Q / 'slova.json').write_text(json.dumps(W, ensure_ascii=False, indent=0), encoding='utf-8')
(Q / 'abzacy.json').write_text(json.dumps(abzacy, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'голос {t:.1f} сек, слов {len(W)}', flush=True)

# ---------- 2. кадры ----------
subj = {int(k): v for k, v in PL.get('SUBJ', {}).items()}
pool = {int(k): list(v) for k, v in PL.get('POOL', {}).items()}
checked, notes = {}, []


def frame_ok(clip, word):
    if clip in checked:
        return checked[clip]
    name, _, ss = clip.partition('@')
    src = download(name, Q)
    jpg = T / f'{clip.replace("@", "_")}.jpg'
    ff('-ss', str(float(ss or 0) + 1.0), '-i', str(src), '-frames:v', '1', '-vf', 'scale=-2:480', str(jpg))
    good, answer = looks_like(jpg, word)
    time.sleep(7)  # бесплатный Gemini - около 10 запросов в минуту
    checked[clip] = good
    print(clip, '->', 'ok' if good else 'НЕТ', '|', answer[:90], flush=True)
    return good


plan = []
for p, clips in PL['PLAN']:
    word = subj.get(p) or ABZ[p - 1].split('.')[0][:40]
    keep = []
    for c in clips:
        if c.startswith('~'):  # «~клип» - фон (льды, волны, небо): животного там нет и не должно быть, не проверяем
            keep.append(c[1:])
            continue
        if frame_ok(c, word):
            keep.append(c)
            continue
        while pool.get(p):
            alt = pool[p].pop(0)
            if frame_ok(alt, word):
                keep.append(alt); notes.append(f'абзац {p}: {c} -> {alt}')
                break
        else:
            notes.append(f'абзац {p}: {c} убран, замены нет')
    if not keep:
        keep = [clips[0].lstrip('~')]
        notes.append(f'абзац {p}: ни один клип не прошёл проверку, оставлен {clips[0]}')
        tg(f'Конвейер {Q.name}: в абзаце {p} («{word}») Gemini забраковал все кадры. Ролик соберу, но проверь этот кусок.')
    plan.append([p, keep])
(Q / 'plan-final.json').write_text(json.dumps({'PLAN': plan, 'notes': notes}, ensure_ascii=False, indent=1), encoding='utf-8')

# ---------- 3. data.ts ----------
key = lambda c: c.replace('@', '_')
plan_ts = ',\n'.join('\t[%d, [%s]]' % (p, ', '.join(f"'{x}'" for x in c)) for p, c in plan)
chap = ',\n'.join(f"\t\t[{p}, '{t}']" for p, t in PL['CHAPTERS'])
c = PL['COVER']
shorts = []
for s in PL.get('SHORTS', []):
    a, b = s['abz']
    # последние 1,8 сек - плашка «Полное видео - на канале», звук в ней глушится (Film.tsx, tail),
    # поэтому начало следующего абзаца не слышно; с вопросом зрителю (ask) плашка висит 3,8 сек
    ask = s.get('ask', '').replace("'", '’')
    shorts.append("{id: 'Short-%s', from: %.2f, to: %.2f, title: '%s', outro: 'Полное видео - на канале'%s}" % (
        s['id'], max(0, abzacy[a - 1]['s'] - 0.15), abzacy[b - 1]['e'] + (3.9 if ask else 1.9), s['title'],
        f", ask: '{ask}'" if ask else ''))
ts = f"""// Таймлайн ролика {Q.name}. Сгенерировано scripts/prepare.py - править plan.json, не этот файл.
import slova from './slova.json';
import abzacy from './abzacy.json';

export const FPS = 30;
export type Word = {{w: string; s: number; e: number; p: number}};
export const WORDS: Word[] = slova as Word[];
const ABZ = abzacy as {{n: number; s: number; e: number}}[];
export const VOICE_SEC = ABZ[ABZ.length - 1].e;
const at = (p: number) => ABZ[p - 1].s;

export const PLAN: [number, string[]][] = [
{plan_ts},
];
const key = (c: string) => c.replace('@', '_');
export const SHOTS: [string, number][] = PLAN.flatMap(([p, clips]) => {{
	const a = at(p);
	const b = p < ABZ.length ? at(p + 1) : VOICE_SEC;
	return clips.map((c, i) => [key(c.includes('@') ? c : c + '@0'), a + ((b - a) * i) / clips.length] as [string, number]);
}});

export const CHAPTERS = (
	[
{chap},
	] as [number, string][]
).map(([p, title]) => ({{p, title, at: at(p) + 0.1}}));

export const PLATES = [1, ABZ.length];

export const SHORTS: {{id: string; from: number; to: number; title: string; outro?: string; ask?: string}}[] = [{', '.join(shorts)}];

export const COVER = {{clip: '{c['clip']}', sec: {c['sec']}, small: '{c['small']}', big: '{c['big']}'}};
"""
(Q / 'data.ts').write_text(ts, encoding='utf-8')
st = state(Q); st['stage'] = 'prepared'; st['notes'] = notes; save_state(Q, st)
print('готово к сборке:', len(plan), 'абзацев,', sum(len(x) for _, x in plan), 'клипов, замен', len(notes))
