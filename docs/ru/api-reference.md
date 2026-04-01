# API Reference

Справочник по всем методам SDK. Если вы только начинаете — лучше начните с раздела «Быстрый старт».

## Класс Scraper

HTTP-скрейпер — быстрое извлечение контента со страниц без запуска браузера.
Использует TLS-fingerprinting для обхода антибот-защит.

### Создание клиента

```python
from dawg_baas import Scraper

scraper = Scraper(api_key="ваш_ключ")
```

Параметры:
- `api_key` — ваш API-ключ (обязательно)
- `base_url` — URL сервиса (по умолчанию `https://dawgswarm.ru`)
- `timeout` — таймаут HTTP-запросов в секундах (по умолчанию 60)

### Методы

#### `scrape(url, format="markdown", ...)`

Скрейпит одну страницу и возвращает `ScrapeResult`.

```python
result = scraper.scrape("https://example.com", format="markdown")
print(result.content)       # чистый markdown
print(result.metadata)      # {"title": "...", "word_count": 42, ...}
```

Параметры:
- `url` — URL страницы
- `format` — формат вывода: `"markdown"`, `"text"`, `"html"` (по умолчанию `"markdown"`)
- `main_content` — убрать навигацию, футер, рекламу (по умолчанию `False`)
- `include_links` — включить список найденных ссылок (по умолчанию `False`)
- `headers` — кастомные HTTP-заголовки (dict)
- `timeout_ms` — таймаут загрузки страницы в мс (по умолчанию 30000)

Возвращает `ScrapeResult`:
- `success` — успешно ли
- `content` — извлечённый контент в запрошенном формате
- `metadata` — `{"title", "description", "language", "word_count"}`
- `links` — список ссылок (если `include_links=True`)
- `final_url` — финальный URL после редиректов
- `status_code` — HTTP-статус целевой страницы
- `elapsed_ms` — время выполнения

#### `crawl(url, max_depth=2, max_pages=50, ...)`

Рекурсивный обход сайта по ссылкам. Возвращает `ScrapeJob` — задачу, которая выполняется в фоне.

```python
job = scraper.crawl("https://example.com", max_depth=2, max_pages=20)
job.wait()  # ждём завершения

for page in job.pages:
    print(page.url, page.metadata.get("title"))
```

Параметры:
- `url` — стартовый URL
- `format` — формат контента (по умолчанию `"markdown"`)
- `max_depth` — глубина обхода (по умолчанию 2, макс 5)
- `max_pages` — максимум страниц (по умолчанию 50, макс 200)
- `concurrency` — параллельные запросы (по умолчанию 3, макс 10)
- `include_patterns` — glob-паттерны URL для включения
- `exclude_patterns` — glob-паттерны URL для исключения
- `main_content` — убрать шаблонные элементы
- `timeout_ms` — таймаут на каждую страницу

#### `batch(urls, concurrency=5, ...)`

Параллельный скрейпинг списка URL. Возвращает `ScrapeJob`.

```python
job = scraper.batch([
    "https://example.com",
    "https://httpbin.org/html",
], format="text")
job.wait()

for page in job.pages:
    print(f"{page.url}: {len(page.content)} символов")
```

Параметры:
- `urls` — список URL (макс 100)
- `format`, `concurrency`, `timeout_ms`, `main_content` — аналогично crawl

#### `get_job(job_id)` / `cancel_job(job_id)`

Получить статус задачи или отменить её.

### Работа с задачами (ScrapeJob)

Методы `crawl()` и `batch()` возвращают `ScrapeJob`:

```python
job = scraper.crawl("https://example.com")

# Дождаться завершения (поллинг каждые 2 секунды)
job.wait(timeout=300, poll_interval=2.0)

# Или проверить статус вручную
job.refresh()
print(job.status)      # "running" | "completed" | "failed" | "cancelled"
print(job.progress)    # {"completed": 5, "total": 10, "errors": 0}

# Отменить
job.cancel()
```

### Рекомендуемый способ: with

```python
with Scraper(api_key="ваш_ключ") as s:
    result = s.scrape("https://example.com")
    print(result.content)
# HTTP-сессия автоматически закрыта
```

### Асинхронный клиент: AsyncScraper

```python
from dawg_baas import AsyncScraper

async with AsyncScraper(api_key="ваш_ключ") as s:
    result = await s.scrape("https://example.com")

    job = await s.crawl("https://example.com", max_pages=10)
    await job.wait()
```

---

## Класс Baas

Основной класс для работы с сервисом. Позволяет получить браузер из облака
и подключиться к нему через Playwright, Puppeteer или любой другой инструмент с поддержкой CDP.

### Создание клиента

```python
from dawg_baas import Baas

baas = Baas(api_key="ваш_ключ")
```

Дополнительные параметры (обычно не нужны):

- `timeout` — сколько секунд ждать запуска браузера (по умолчанию 60)
- `poll_interval` — как часто проверять готовность браузера (по умолчанию 2 сек)

### Методы

#### `create(proxy=None)`

Запрашивает браузер из пула и возвращает URL для подключения.
Этот URL передаётся в Playwright/Puppeteer для управления браузером.

```python
# Получаем URL для подключения к браузеру
ws_url = baas.create()

# Или с прокси (браузер будет ходить в интернет через ваш прокси)
ws_url = baas.create(proxy="http://user:pass@proxy.com:8080")
```

#### `release()`

**Важно вызывать после завершения работы!** Сообщает сервису, что вы закончили
использовать браузер. Браузер возвращается в пул и может быть выдан другому пользователю.

Если не вызвать — браузер будет считаться занятым до таймаута (несколько минут),
и вы будете тратить лимиты впустую.

```python
# Закончили работу — освобождаем браузер
baas.release()
```

### Рекомендуемый способ: with

Чтобы не забыть вызвать `release()`, используйте конструкцию `with` —
браузер освободится автоматически:

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

with Baas(api_key="ваш_ключ") as ws_url:
    # ws_url — это URL для подключения
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://example.com")
        print(page.title())

        browser.close()

# Браузер автоматически освобождён
```

> **Ограничение with:** при использовании `with` нельзя передать прокси.
> Если нужен прокси — используйте `baas.create(proxy=...)` напрямую.

### Свойства

- `baas.browser_id` — ID браузера (для отладки)
- `baas.session_id` — ID сессии (для отладки)

---

## Асинхронный клиент: AsyncBaas

Если ваш код асинхронный (используете `async/await`),
используйте `AsyncBaas` — он работает точно так же:

```python
from dawg_baas import AsyncBaas
from playwright.async_api import async_playwright

async def main():
    async with AsyncBaas(api_key="ваш_ключ") as ws_url:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]

            await page.goto("https://example.com")
            print(await page.title())

            await browser.close()

# Запуск
import asyncio
asyncio.run(main())
```

---

## Обработка ошибок

SDK выбрасывает понятные исключения, которые можно обработать:

### `AuthError`

Неверный API-ключ. Проверьте, что ключ скопирован правильно.

### `RateLimitError`

Превышен лимит запросов вашего тарифа.
Свойство `retry_after` показывает, через сколько секунд можно повторить.

### `BrowserNotReadyError`

Браузер не успел запуститься за отведённое время. Попробуйте ещё раз.

### `BaasError`

Базовый класс для всех ошибок. Ловите его, если хотите обработать любую ошибку SDK.

### Пример

```python
from dawg_baas import Baas, AuthError, RateLimitError, BrowserNotReadyError
import time

baas = Baas(api_key="ваш_ключ")

try:
    ws_url = baas.create()
    # ... работа с браузером ...

except AuthError:
    print("Ошибка: неверный API-ключ")

except RateLimitError as e:
    print(f"Лимит исчерпан. Подождите {e.retry_after} секунд")
    time.sleep(e.retry_after)
    # Можно повторить запрос

except BrowserNotReadyError:
    print("Браузер не запустился, попробуйте ещё раз")

finally:
    baas.release()
```
