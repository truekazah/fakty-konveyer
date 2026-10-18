# Клипы Pexels по номеру: stock.json в папке ролика - {"имя-клипа": номер_на_Pexels}.
# Скачанные лежат в cache/ (в облаке кэш между запусками не живёт - это нормально, качается за 2-3 минуты).
import json, os, shutil, sys, urllib.request
from common import ROOT

CACHE = ROOT / 'cache'


def download(name, q):
    CACHE.mkdir(exist_ok=True)
    dst = CACHE / f'{name}.mp4'
    if dst.exists():
        return dst
    stock = json.loads((q / 'stock.json').read_text(encoding='utf-8'))
    h = {'Authorization': os.environ['PEXELS_KEY'], 'User-Agent': 'fakty-konveyer'}
    info = json.load(urllib.request.urlopen(urllib.request.Request(
        f'https://api.pexels.com/videos/videos/{stock[name]}', headers=h), timeout=60))
    files = [f for f in info['video_files'] if (f.get('width') or 0) > (f.get('height') or 0)] or info['video_files']
    best = sorted(files, key=lambda f: abs(1920 - (f.get('width') or 0)))[0]
    if not best['link'].startswith('https://'):
        sys.exit(f'странная ссылка Pexels у {name}: {best["link"][:60]}')
    with urllib.request.urlopen(urllib.request.Request(best['link'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=300) as r, \
            open(dst, 'wb') as w:
        shutil.copyfileobj(r, w)
    return dst
