# Screenshot Server with Telegram Bot

Сервер для управления клиентами скриншотов через WebSocket соединения с Telegram ботом для инициации команд.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

### Ручной запуск

```bash
python server.py
```

### Автоматический запуск через systemd (Ubuntu)

```bash
sudo python systemd_service.py
sudo systemctl start screenshot-server
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

- `server.py` - основной сервер с WebSocket поддержкой
- `telegram_bot.py` - Telegram бот для управления
- `systemd_service.py` - создание systemd сервиса
- `requirements.txt` - зависимости
- `.env` - конфигурация бота

## Управление

### Systemd команды

```bash
sudo systemctl start screenshot-server
sudo systemctl stop screenshot-server
sudo systemctl status screenshot-server
sudo systemctl enable screenshot-server
sudo systemctl disable screenshot-server
```

### Логи

```bash
journalctl -u screenshot-server -f
```

## Telegram Bot Команды

- `/start` - главное меню с кнопкой
- `/pause` - выполнить скриншот (аналог кнопки)

### Кнопки в меню

- 📸 **Take Screenshot** - отправить команду скриншота всем клиентам

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
