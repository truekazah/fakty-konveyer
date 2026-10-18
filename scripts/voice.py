# Ежедневная озвучка: python scripts/voice.py
# Берёт ролики очереди со стадией voice по порядку и озвучивает недостающие абзацы (voice/NN.mp3),
# пока Gemini не скажет «дневной лимит» (~12 запросов, сброс в 12:00 по Астане).
# Каждый новый абзац сразу слушает Whisper: повтор или пропуск фразы - файл удаляется, завтра переозвучка.
# Все абзацы есть - стадия ready, дальше сборка.
import difflib, re
from common import audio16k, DayLimit, git_commit, paragraphs, save_state, state, tg, tts, videos

_model = None


def heard(mp3):
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel('small', device='cpu', compute_type='int8')
    segs, _ = _model.transcribe(audio16k(mp3), language='ru', vad_filter=True)  # без VAD Whisper сочиняет титры на тишине
    return ' '.join(s.text for s in segs)


def words(t):
    return re.findall(r'[а-яёa-z]+', t.lower().replace('ё', 'е'))


def ok(text, mp3):
    # числа Whisper пишет цифрами, поэтому сравниваем только слова из букв
    a, b = words(text), words(heard(mp3))
    sim = difflib.SequenceMatcher(None, a, b).ratio()
    return sim >= 0.75 and len(b) <= len(a) * 1.15 + 2, sim, len(a), len(b)


done = 0
try:
    for q in videos('voice'):
        st = state(q)
        abz = paragraphs(q)
        (q / 'voice').mkdir(exist_ok=True)
        for i, text in enumerate(abz, 1):
            mp3 = q / 'voice' / f'{i:02d}.mp3'
            if mp3.exists():
                continue
            tts(text, i == 1, mp3)
            try:
                good, sim, na, nb = ok(text, mp3)
            except Exception as e:  # проверка упала - абзац оставляем, запрос лимита не теряем
                print(q.name, f'{i:02d}', 'проверка Whisper не сработала:', e, flush=True)
                good, sim, na, nb = True, 0, 0, 0
            print(q.name, f'{i:02d}', 'ok' if good else 'ПЕРЕОЗВУЧИТЬ', f'сходство {sim:.2f}, слов {na} -> {nb}', flush=True)
            if not good:
                mp3.unlink()
                st['bad'] = st.get('bad', 0) + 1
                if st['bad'] in (3, 6):
                    tg(f'Конвейер: абзац {i} ролика {q.name} не озвучивается чисто уже {st["bad"]} раз. Проверь текст.')
            done += 1
            save_state(q, st)
        if all((q / 'voice' / f'{i:02d}.mp3').exists() for i in range(1, len(abz) + 1)):
            st['stage'] = 'ready'
            print(q.name, 'голос готов', flush=True)
        save_state(q, st)
except DayLimit:
    print('дневной лимит Gemini, продолжу завтра', flush=True)
if not videos('voice') and not videos('ready'):
    tg('Конвейер: в очереди кончились сценарии. Пора готовить новую пачку.')
print('озвучено абзацев:', done)
git_commit(f'Озвучка: {done} абзацев')
