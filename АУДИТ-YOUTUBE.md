# Заявка на аудит YouTube API (чтобы длинные ролики тоже выходили сами)

Зачем: без аудита всё, что программа загружает на YouTube, навсегда остаётся приватным. Поэтому
сейчас длинные ролики перетаскиваете вы. Одобрят - перетаскивать не придётся.
Срок - обычно несколько недель, одобрение не гарантировано. Бесплатно.

**Сначала** закончите шаг 2 из `ШАГИ-РУСЛАНА.md` (Branding + Publish app) - без него форму могут отклонить.

## Как подать

1. Откройте форму: https://support.google.com/youtube/contact/yt_api_form
2. Войдите аккаунтом truekazah123@gmail.com.
3. Если спросят, что вам нужно, выберите **«Audit»** / **«I want to have my API client audited»**
   (не «quota extension»).
4. Заполняйте поля текстом ниже - копируйте английский текст как есть. В скобках - перевод для вас.

| Поле формы | Что вставить |
|---|---|
| First name / Last name (имя, фамилия) | Ruslan / Abenov |
| Email | truekazah123@gmail.com |
| Organization name (организация) | RUSI4 |
| Organization website (сайт) | https://rusi4.kz |
| Google Cloud project number (номер проекта) | 417497273851 |
| API client name (название программы) | Da nu pravda konveyer |
| Link to API client / website | https://github.com/truekazah/fakty-konveyer |
| Privacy policy | https://rusi4.kz/politika-konfidencialnosti |
| How many users? (сколько пользователей) | 1 (only the channel owner) |
| YouTube channel (канал) | https://www.youtube.com/channel/UClDTlKwNV1e_fKzZxaaf1hQ |

**Describe your API client / use case** (опишите программу - вставить целиком):

```
This is a private internal tool used only by the owner of a single YouTube channel
("Da nu, pravda?!", channel UClDTlKwNV1e_fKzZxaaf1hQ) to publish his own original
educational videos about animals and science facts. The videos are produced by the
channel owner (own scripts, own voice-over, licensed Pexels stock footage).

The tool uses the YouTube Data API v3 only on the owner's own channel, authorized via
OAuth by the owner himself:
- videos.insert - upload the owner's finished videos to his channel;
- videos.update - set title, description, tags, category and privacy of his own videos;
- thumbnails.set - set the custom thumbnail;
- playlists / playlistItems - keep his own playlists in order.

No other users, no third-party channels, no data collection, no data sharing.
The code is open: https://github.com/truekazah/fakty-konveyer
We request an audit so that uploaded videos are not locked to private mode.
```

(Перевод: это внутренний инструмент владельца одного канала. Загружает его собственные
ролики, ставит название, описание, обложку и плейлисты только на его канале. Других
пользователей нет, данные никуда не уходят. Просим аудит, чтобы загрузки не были приватными.)

5. Отправьте форму (**Submit**). Если форма попросит видео-демонстрацию или скриншоты -
   не отправляйте, пришлите мне скриншот, подготовлю.
6. Ответ придёт на почту, обычно на английском - перешлите мне.
