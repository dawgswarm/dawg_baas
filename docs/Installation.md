# Установка

dawg-baas — это Python SDK для работы с DAWG Browser-as-a-Service.
Позволяет управлять удалёнными браузерами через простой API.

## Требования

- Python 3.9 или выше
- pip (менеджер пакетов Python)

## Установка через pip

```bash
pip install dawg-baas
```

## Зависимости

SDK автоматически установит следующие зависимости:

- `httpx` — для асинхронных HTTP-запросов
- `requests` — для синхронных HTTP-запросов

## Дополнительные библиотеки

Для работы с браузером рекомендуем установить одну из библиотек автоматизации:

```bash
# Playwright (рекомендуется)
pip install playwright
playwright install chromium

# Или Selenium
pip install selenium
```

## Проверка установки

```python
from dawg_baas import Baas

print("dawg-baas установлен успешно!")
```
