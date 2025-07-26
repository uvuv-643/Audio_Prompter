# VTT Subtitles Integration with TTS

Добавлена поддержка работы с .vtt файлами субтитров для автоматического определения текущей реплики по времени с озвучкой и автоматическим кликом.

## Возможности

- Загрузка .vtt файлов с URL или локального файла
- Автоматическое определение субтитров по времени из скриншота
- Вывод текущей реплики в консоль вместе с таймингом
- **Озвучка субтитров с помощью Microsoft Edge TTS (высокое качество)**
- **Автоматический клик мышью после завершения озвучки**
- Поддержка форматов времени HH:MM:SS и HH:MM:SS.mmm
- Автоматическое определение кодировки файлов (UTF-8, CP1251, Windows-1251)
- Поддержка русских и других Unicode символов
- Многопоточная обработка для плавной работы
- Естественное звучание с русским голосом Svetlana

## Использование

### Основной workflow (main.py)

```bash
# С VTT файлом по URL и TTS
python main.py --vtt-url "https://example.com/subtitles.vtt" --interval 15

# С локальным VTT файлом и TTS
python main.py --vtt-url "file:///path/to/subtitles.vtt" --interval 10

# Без TTS (только субтитры)
python main.py --vtt-url "https://example.com/subtitles.vtt" --no-tts --interval 15

# Без VTT файла (только тайминг)
python main.py --interval 15
```

### Клиент (client.py)

```bash
# С VTT файлом и TTS
python client.py --vtt-url "https://example.com/subtitles.vtt" --host localhost --port 8765

# С локальным файлом и TTS
python client.py --vtt-url "file:///path/to/subtitles.vtt"

# Без TTS (только субтитры)
python client.py --vtt-url "https://example.com/subtitles.vtt" --no-tts
```

## Формат вывода

При обнаружении тайминга и соответствующего субтитра:

```
🎬 0:01:26
💬 0:01:26 | - Привет.
- Привет. 25 фунтов?
🎤 Starting speech synthesis for: - Привет.
- Привет. 25 фунтов?
🖱️ Speech completed, performing mouse click...
✅ Mouse click completed
```

При обнаружении тайминга без субтитра:

```
🎬 0:00:24
🔍 0:00:24 | No subtitle found
```

## Структура VTT файла

Поддерживается стандартный формат WebVTT:

```
WEBVTT

00:00:23.189 --> 00:00:25.160

00:00:41.527 --> 00:00:44.331
Все в порядке...

00:00:51.914 --> 00:00:55.152
Тсс...
```

## Тестирование

```bash
# Тест TTS
python test_tts.py
```

## Зависимости

Добавлены зависимости:

- `requests>=2.31.0` - для загрузки VTT файлов по URL
- `edge-tts>=6.1.9` - для высококачественного синтеза речи
- `aiohttp>=3.8.0` - для асинхронных HTTP запросов

## TTS Модель

Используется **Microsoft Edge TTS** - высококачественный движок синтеза речи:

- Естественное звучание с русским голосом Svetlana
- Высокое качество озвучки
- Поддержка эмоций и интонаций
- Быстрая генерация речи
- Кроссплатформенная поддержка
