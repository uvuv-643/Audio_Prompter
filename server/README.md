# Screenshot Server with Telegram Bot

Сервер для управления клиентами скриншотов через WebSocket соединения с Telegram ботом для инициации команд.

## Установка

### Автоматическая установка

```bash
./install.sh
```

### Ручная установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите сервер
python main.py
```

## Конфигурация

### Сервер

- Host: 0.0.0.0 (все интерфейсы)
- Port: 8765

### Telegram Bot

Создайте файл `.env` в директории сервера:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8765
```

### Настройка Telegram Bot

1. Создайте бота через @BotFather в Telegram
2. Получите токен бота
3. Добавьте токен в файл .env

## Архитектура

- `main.py` - точка входа для запуска сервера
- `server.py` - основной сервер с WebSocket поддержкой
- `telegram_bot.py` - Telegram бот для управления
- `requirements.txt` - зависимости
- `.env` - конфигурация бота
- `install.sh` - скрипт установки

## Управление

### Запуск/остановка

```bash
# Запуск
python main.py

# Остановка
Ctrl+C
```

### Логи

```bash
# Логи в консоли и файле
tail -f screenshot_server.log
```

## Telegram Bot Команды

- `/start` - главное меню с кнопкой
- `/pause` - поставить на паузу (аналог кнопки)

### Кнопки в меню

- ⏸️ **Поставить на паузу** - отправить команду перевода всем клиентам

## Протокол

Сервер использует WebSocket для связи с клиентами:

### Сообщения от сервера к клиенту

1. `connection_established` - подтверждение подключения
2. `execute_screenshot` - команда выполнить скриншот
3. `heartbeat_ack` - подтверждение heartbeat

### Сообщения от клиента к серверу

1. `screenshot_completed` - результат выполнения скриншота
2. `screenshot_error` - ошибка при выполнении
3. `heartbeat` - проверка соединения

## Масштабирование

Сервер поддерживает множественные подключения клиентов. Каждый клиент получает команды одновременно.
