# Общее для скриптов конвейера: пути, состояние роликов, Gemini, Telegram.
# Ключи - переменные окружения (в облаке это секреты репозитория):
#   GEMINI_KEY, PEXELS_KEY, BUFFER_KEY, TG_TOKEN, TG_CHAT, YT_CLIENT_JSON, YT_TOKEN_JSON
import base64, json, os, pathlib, subprocess, sys, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / 'queue'
TZ = '+05:00'  # Астана


def paragraphs(q):
    return [a.strip() for a in (q / 'script.txt').read_text(encoding='utf-8').split('\n\n') if a.strip()]


def state(q):
    f = q / 'state.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {'stage': 'voice'}


def save_state(q, st):
    (q / 'state.json').write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding='utf-8')


def videos(stage=None):
    # ролики очереди по порядку имени папки (01-..., 02-...)
    out = [q for q in sorted(QUEUE.iterdir()) if (q / 'script.txt').exists()]
    return [q for q in out if stage is None or state(q)['stage'] == stage]


def run(*a, **k):
    subprocess.run([str(x) for x in a], check=True, **k)


def http_json(url, body=None, headers=None, timeout=300):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Content-Type': 'application/json', **(headers or {})})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


# ---------- Gemini ----------
class DayLimit(Exception):
    pass


def gemini(model, parts, config=None):
    body = {'contents': [{'parts': parts}]}
    if config:
        body['generationConfig'] = config
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    for attempt in range(5):
        try:
            return http_json(url, body, {'x-goog-api-key': os.environ['GEMINI_KEY']}, timeout=600)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            if 'PerDay' in msg:
                raise DayLimit(model)
            if e.code != 429 and e.code < 500:
                raise RuntimeError(f'Gemini {e.code}: {msg[:300]}')
            time.sleep(65)
    raise RuntimeError('Gemini не ответил 5 раз')


STIL = {True: 'Прочитай по-русски живо, с удивлением, как ведущий научно-популярного канала начинает ролик:',
        False: 'Прочитай по-русски спокойно и с интересом, как ведущий научно-популярного канала:'}


def tts(text, hook, mp3):
    # голос Orus, выбран Русланом 17.10.2026; по абзацу за запрос - пачки сбоили (4 из 9)
    r = gemini('gemini-2.5-flash-preview-tts', [{'text': STIL[hook] + '\n\n' + text}],
               {'responseModalities': ['AUDIO'],
                'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': 'Orus'}}}})
    parts = r['candidates'][0]['content']['parts']
    pcm = b''.join(base64.b64decode(p['inlineData']['data']) for p in parts if 'inlineData' in p)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', '-',
                    '-b:a', '128k', str(mp3)], input=pcm, check=True)


# Проверка кадров 18.10.2026 на 12 кадрах с известным ответом: 3.5-flash-lite 11 из 12, 3.1-flash-lite 10 из 12,
# 3.8-flash точнее, но бесплатно всего ~25 картинок в день (кончился на подготовке одного ролика), gemma-4 - ошибки 500.
VISION = ['gemini-3.5-flash-lite', 'gemini-3.1-flash-lite', 'gemini-3.8-flash']
_vision_dead = set()


def looks_like(jpg, word):
    # Gemini смотрит стоп-кадр: подходит ли он к слову диктора. Все 4 подмены из 4 (ослы вместо гиены и т.п.) пойманы.
    img = base64.b64encode(pathlib.Path(jpg).read_bytes()).decode()
    prompt = (f'Это стоп-кадр стокового видео для научно-популярного ролика. Когда диктор говорит «{word}», '
              'на экране должен быть именно этот объект, узнаваемый. Если он виден и узнаётся - ДА, даже если в кадре '
              'не целиком, их несколько или рядом есть что-то ещё. НЕТ - если на кадре другое животное или предмет, '
              'или объекта не разглядеть. Первое слово ответа - ДА или НЕТ, дальше одной фразой, что на кадре на самом деле.')
    for model in VISION:
        if model in _vision_dead:
            continue
        try:
            r = gemini(model, [{'inline_data': {'mime_type': 'image/jpeg', 'data': img}}, {'text': prompt}])
        except DayLimit:
            _vision_dead.add(model)
            continue
        parts = r['candidates'][0]['content']['parts']
        a = ' '.join(p.get('text', '') for p in parts if not p.get('thought')).strip().lstrip('*').strip()
        return a.upper().startswith('ДА'), a
    return True, 'проверка пропущена: у всех моделей кончился дневной лимит'


# ---------- Telegram ----------
def tg(text):
    tok, chat = os.environ.get('TG_TOKEN'), os.environ.get('TG_CHAT')
    if not tok or not chat:
        print('TG:', text)
        return
    try:
        http_json(f'https://api.telegram.org/bot{tok}/sendMessage',
                  {'chat_id': chat, 'text': text, 'disable_web_page_preview': True}, timeout=30)
    except Exception as e:  # сообщение не главное - сборку из-за него не роняем
        print('TG не ушло:', e)


def git_commit(msg):
    run('git', 'add', '-A', 'queue', 'chain.json', cwd=ROOT)
    if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT).returncode:
        run('git', 'commit', '-q', '-m', msg, cwd=ROOT)
        run('git', 'pull', '-q', '--rebase', cwd=ROOT)  # публикатор и сборка пишут в один репозиторий
        run('git', 'push', '-q', cwd=ROOT)
