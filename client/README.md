# Автоматический скриншотер

Модульная система для автоматического создания скриншотов с кликом мыши каждые 15 секунд.

## Установка

```bash
pip install -r requirements.txt
```

### Установка зависимостей

#### Автоматическая установка Tesseract:

```bash
./install_tesseract.sh
```

#### Ручная установка Tesseract:

**macOS:**

```bash
brew install tesseract
```

**Ubuntu/Debian:**

```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Скачайте и установите Tesseract с https://github.com/UB-Mannheim/tesseract/wiki

#### Установка Python зависимостей:

```bash
pip install -r requirements.txt
```

**Примечание:** Система автоматически найдет Tesseract или использует fallback метод

## Тестирование

Для проверки работоспособности OCR на последнем скриншоте:

```bash
python test_last_screenshot.py
```

## Запуск

```bash
python main.py
```

## Функциональность

- Клик левой кнопкой мыши в текущей позиции курсора
- Захват области 100x40 пикселей вокруг позиции мыши
- Рабочий OCR с Tesseract для распознавания белого текста на черном фоне в формате HH:MM:SS
- Вывод распознанного тайминга в консоль
- Сохранение скриншота с таймстемпом в папку `screenshots/`
- Автоматическое выполнение каждые 15 секунд

## Архитектура

- `mouse_controller.py` - управление мышью
- `screenshot_capture.py` - захват скриншота
- `image_processor.py` - обработка изображений
- `working_ocr_detector.py` - OCR с Tesseract для распознавания тайминга
- `file_manager.py` - управление файлами
- `screenshot_workflow.py` - объединение всех операций
- `scheduler.py` - планировщик задач
- `main.py` - главная точка входа
- `test_last_screenshot.py` - тест на последнем скриншоте

## Остановка

Нажмите `Ctrl+C` для корректного завершения работы.
