# Публикатор, раз в час: python scripts/publish.py
# 1) YouTube: ролик собран (stage built) -> ищет черновик с названием = имя файла (<папка>.mp4, его грузит Руслан),
#    ставит название, описание, обложку, плейлисты, открывает; встраивает в цепочку «Следующее видео» (chain.json).
# 2) Buffer: Shorts по 3 в день одной пачкой подряд (с 10:00 по Астане; если сегодня ещё не было - сразу),
#    в очереди Buffer не больше 9 (бесплатно - 10).
#    Shorts ролика ставятся, когда длинный вышел (в описании ссылка на него) или через 2 дня после сборки.
import datetime as dt, json, os, pathlib, sys, tempfile, urllib.request
from common import ROOT, TZ, git_commit, http_json, save_state, state, tg, videos

NOW = dt.datetime.now(dt.timezone.utc)
ASTANA = dt.timezone(dt.timedelta(hours=5))
BATCH_HOUR = 10  # пачка Shorts на день
PER_DAY = 3
MAX_QUEUE = 9
TAGS = ['интересные факты', 'факты', 'это интересно', 'наука', 'познавательное', 'да ну правда']
REPO = os.environ.get('GITHUB_REPOSITORY', 'truekazah/fakty-konveyer')
BUFFER_YT = '6ab4262dea19ca0bdeca1b4d'  # канал YouTube в Buffer


def yt():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    t = json.loads(os.environ['YT_TOKEN_JSON'])
    cr = Credentials.from_authorized_user_info(t, t.get('scopes'))
    cr.refresh(Request())
    return build('youtube', 'v3', credentials=cr, cache_discovery=False)


def uploads(y):
    up = y.channels().list(part='contentDetails', mine=True).execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    out, tok = [], None
    while True:
        r = y.playlistItems().list(part='snippet,status', playlistId=up, maxResults=50, pageToken=tok).execute()
        out += r['items']; tok = r.get('nextPageToken')
        if not tok:
            return out


def playlist_id(y, title, cache={}):
    if not cache:
        tok = None
        while True:
            r = y.playlists().list(part='snippet', mine=True, maxResults=50, pageToken=tok).execute()
            cache.update({p['snippet']['title']: p['id'] for p in r['items']}); tok = r.get('nextPageToken')
            if not tok:
                break
    if title not in cache:
        p = y.playlists().insert(part='snippet,status', body={
            'snippet': {'title': title, 'defaultLanguage': 'ru'}, 'status': {'privacyStatus': 'public'}}).execute()
        cache[title] = p['id']
    return cache[title]


def chain(y):
    # перенос tools/youtube/цепочка.py: плейлист по порядку + строка «Следующее видео» в начале описания
    PL, MARK = 'Все выпуски по порядку', '▶ Следующее видео:'
    order = json.loads((ROOT / 'chain.json').read_text(encoding='utf-8'))
    pub = [v for v in uploads(y) if v['status']['privacyStatus'] == 'public']
    ch = []
    for k in order:
        m = [v for v in pub if k in v['snippet']['title']]
        if m:
            ch.append((m[0]['snippet']['resourceId']['videoId'], m[0]['snippet']['title']))
    pid = playlist_id(y, PL)
    items, tok = [], None
    while True:
        r = y.playlistItems().list(part='snippet', playlistId=pid, maxResults=50, pageToken=tok).execute()
        items += r['items']; tok = r.get('nextPageToken')
        if not tok:
            break
    have = {i['snippet']['resourceId']['videoId']: i for i in items}
    for pos, (vid, _) in enumerate(ch):
        body = {'snippet': {'playlistId': pid, 'position': pos, 'resourceId': {'kind': 'youtube#video', 'videoId': vid}}}
        if vid in have:
            if have[vid]['snippet'].get('position') == pos:
                continue
            body['id'] = have[vid]['id']
            y.playlistItems().update(part='snippet', body=body).execute()
        else:
            y.playlistItems().insert(part='snippet', body=body).execute()
    for i, (vid, _) in enumerate(ch):
        nvid, ntitle = ch[(i + 1) % len(ch)]
        line = f'{MARK} {ntitle}\nhttps://www.youtube.com/watch?v={nvid}&list={pid}'
        s = y.videos().list(part='snippet', id=vid).execute()['items'][0]['snippet']
        desc = s.get('description', '')
        if desc.startswith(line):
            continue
        if desc.startswith(MARK):
            desc = desc.split('\n\n', 1)[1] if '\n\n' in desc else ''
        s['description'] = line + '\n\n' + desc
        s.pop('thumbnails', None); s.pop('localized', None)
        y.videos().update(part='snippet', body={'id': vid, 'snippet': s}).execute()
    print('цепочка:', len(ch), 'роликов')


def asset(q, name):
    return f'https://github.com/{REPO}/releases/download/{q.name}/{name}'


# ---------- 1. длинные ролики ----------
built = videos('built')
if built:
    y = yt()
    # Studio берёт название из имени файла и меняет «-» на пробел: «01-skorost» -> «01 skorost»
    key = lambda t: ' '.join(t.lower().replace('-', ' ').replace('_', ' ').split())
    drafts = {key(v['snippet']['title']): v['snippet']['resourceId']['videoId'] for v in uploads(y)
              if v['status']['privacyStatus'] != 'public'}
    for q in built:
        st, meta = state(q), json.loads((q / 'meta.json').read_text(encoding='utf-8'))
        vid = drafts.get(key(q.name))
        if not vid:
            continue
        desc = urllib.request.urlopen(asset(q, 'opisanie.txt'), timeout=60).read().decode('utf-8')
        y.videos().update(part='snippet,status', body={'id': vid, 'snippet': {
            'title': meta['title'], 'description': desc, 'tags': TAGS + meta.get('tags', []), 'categoryId': '27',
            'defaultLanguage': 'ru', 'defaultAudioLanguage': 'ru'},
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False, 'license': 'youtube', 'embeddable': True,
                       'publicStatsViewable': True, 'containsSyntheticMedia': False}}).execute()
        from googleapiclient.http import MediaFileUpload
        with tempfile.TemporaryDirectory() as d:
            png = pathlib.Path(d) / 'cover.png'
            png.write_bytes(urllib.request.urlopen(asset(q, 'oblozhka.png'), timeout=60).read())
            y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(png), mimetype='image/png')).execute()
        for pl in meta.get('playlists', []) + ['Интересные факты']:
            y.playlistItems().insert(part='snippet', body={'snippet': {
                'playlistId': playlist_id(y, pl), 'resourceId': {'kind': 'youtube#video', 'videoId': vid}}}).execute()
        order = json.loads((ROOT / 'chain.json').read_text(encoding='utf-8'))
        if meta['chain_key'] not in order:
            order.append(meta['chain_key'])
            (ROOT / 'chain.json').write_text(json.dumps(order, ensure_ascii=False, indent=1), encoding='utf-8')
        st.update(stage='published', yt_id=vid, published=NOW.isoformat())
        save_state(q, st)
        chain(y)
        tg(f'Конвейер: вышел «{meta["title"]}»\nhttps://youtu.be/{vid}\nОсталось поставить конечную заставку в Studio.')
        print('опубликован', q.name, vid)

# ---------- 2. Shorts в Buffer ----------
plan = []  # (ролик, short) - ещё не поставленные, по порядку
future = []
dues = []  # все Shorts, и вышедшие, - чтобы считать по 3 в день
for q in videos():
    st = state(q)
    for s in st.get('shorts', {}).values():
        if s.get('due'):
            dues.append(dt.datetime.fromisoformat(s['due']))
            if dues[-1] > NOW:
                future.append(dues[-1])
    if st['stage'] not in ('built', 'published'):
        continue
    ready = st['stage'] == 'published' or NOW - dt.datetime.fromisoformat(st['built']) > dt.timedelta(days=2)
    if not ready:
        continue
    for s in json.loads((q / 'plan.json').read_text(encoding='utf-8')).get('SHORTS', []):
        if s['id'] not in st.get('shorts', {}):
            plan.append((q, s))


def next_slot(dues):
    # первый день, где Shorts меньше PER_DAY; в пачке подряд, с разницей в минуту
    d = NOW.astimezone(ASTANA)
    for k in range(0, 30):
        day = (d + dt.timedelta(days=k)).date()
        n = sum(1 for t in dues if t.astimezone(ASTANA).date() == day)
        if n >= PER_DAY:
            continue
        start = dt.datetime(day.year, day.month, day.day, BATCH_HOUR, tzinfo=ASTANA)
        if start < d + dt.timedelta(minutes=5):
            start = d + dt.timedelta(minutes=5)
        later = [t for t in dues if t.astimezone(ASTANA).date() == day]
        return max([start] + [t + dt.timedelta(minutes=1) for t in later])


M = ('mutation($input: CreatePostInput!){ createPost(input:$input){ __typename '
     '... on PostActionSuccess { post { id dueAt status } } ... on MutationError { message } } }')
for q, s in plan:
    if len(future) >= MAX_QUEUE:
        break
    st = state(q)
    due = next_slot(dues)
    link = f"\n\nПолное видео: https://youtu.be/{st['yt_id']}" if st.get('yt_id') else '\n\nПолное видео - на канале.'
    input_ = {'channelId': BUFFER_YT, 'text': s['text'] + link + '\n\n' + s.get('tags', '#факты #интересныефакты #shorts'),
              'assets': [{'video': {'url': asset(q, f"Short-{s['id']}.mp4"), 'metadata': {'thumbnailOffset': 1000}}}],
              'metadata': {'youtube': {'title': s['yt_title'], 'privacy': 'public', 'categoryId': '27', 'madeForKids': False,
                                       'notifySubscribers': True, 'isAiGenerated': False}},
              'mode': 'customScheduled', 'dueAt': due.isoformat(), 'schedulingType': 'automatic', 'needsApproval': False}
    j = http_json('https://api.buffer.com', {'query': M, 'variables': {'input': input_}},
                  {'Authorization': 'Bearer ' + os.environ['BUFFER_KEY']}, timeout=60)
    res = (j.get('data') or {}).get('createPost') or {}
    if not res.get('post'):
        tg(f'Конвейер: Buffer не принял Short {q.name}/{s["id"]}: {json.dumps(res or j.get("errors"), ensure_ascii=False)[:300]}')
        break
    st.setdefault('shorts', {})[s['id']] = {'buffer': res['post']['id'], 'due': due.isoformat()}
    save_state(q, st)
    future.append(due); dues.append(due)
    print('Short в Buffer:', q.name, s['id'], due.isoformat())

git_commit('Публикация')
