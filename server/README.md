# Screenshot Server

Сервер для управления клиентами скриншотов через WebSocket соединения.

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

Сервер по умолчанию запускается на:

- Host: 0.0.0.0 (все интерфейсы)
- Port: 8765
- Интервал: 15 секунд

## Архитектура

- `server.py` - основной сервер с WebSocket поддержкой
- `systemd_service.py` - создание systemd сервиса
- `requirements.txt` - зависимости

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
