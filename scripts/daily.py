# Ежедневный прогон, 12:15 по Астане (сразу после сброса лимита Gemini): python scripts/daily.py
# 1) озвучка (voice.py); 2) один ролик с готовым голосом: подготовка, сборка, выгрузка в релиз GitHub;
# 3) сообщение Руслану: ссылка на файл, который надо перетащить в Studio.
import datetime as dt, json, os, subprocess, sys
from common import ROOT, git_commit, run, save_state, state, tg, videos

PY = sys.executable
REPO = os.environ.get('GITHUB_REPOSITORY', 'truekazah/fakty-konveyer')

subprocess.run([PY, ROOT / 'scripts' / 'voice.py'], check=False)
ready = videos('ready') + videos('prepared')
if not ready:
    sys.exit()
q = ready[0]
rel = f'queue/{q.name}'
try:
    if state(q)['stage'] == 'ready':
        run(PY, ROOT / 'scripts' / 'prepare.py', rel)
        git_commit(f'Подготовлен {q.name}')
    run(PY, ROOT / 'scripts' / 'build.py', rel)
    out = ROOT / 'out' / q.name
    files = sorted(str(f) for f in out.iterdir())
    meta = json.loads((q / 'meta.json').read_text(encoding='utf-8'))
    subprocess.run(['gh', 'release', 'delete', q.name, '-y', '-R', REPO], capture_output=True)
    run('gh', 'release', 'create', q.name, *files, '-R', REPO, '--title', meta['title'], '--notes', 'Собрано конвейером')
except subprocess.CalledProcessError as e:
    tg(f'Конвейер: сборка {q.name} упала ({e.cmd[1] if len(e.cmd) > 1 else e.cmd}). Завтра попробую снова; лог - во вкладке Actions репозитория.')
    raise
st = state(q)
st.update(stage='built', built=dt.datetime.now(dt.timezone.utc).isoformat())
save_state(q, st)
git_commit(f'Собран {q.name}')
notes = ''.join(f'\n- {n}' for n in st.get('notes', []))
tg(f'Конвейер: собран ролик «{meta["title"]}».\n\n'
   f'1. Скачай: https://github.com/{REPO}/releases/download/{q.name}/{q.name}.mp4\n'
   f'2. Перетащи файл в YouTube Studio, ничего не заполняй - название «{q.name}» оставь как есть.\n'
   f'Дальше всё сделаю сам в течение часа.'
   + (f'\n\nЗамены кадров после проверки Gemini:{notes}' if notes else ''))
