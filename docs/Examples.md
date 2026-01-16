# Примеры

Базовые примеры использования SDK для различных сценариев.

## Синхронный клиент

Простой пример без контекст-менеджера:

```python
from dawg_baas import Baas

baas = Baas(api_key="ваш_api_ключ")

try:
    # Создаём браузер
    ws_url = baas.create()
    print(f"Браузер готов: {ws_url}")

    # Здесь ваш код работы с браузером
    # ...

finally:
    # Обязательно возвращаем браузер в пул
    baas.release()
```

## Асинхронный клиент

```python
import asyncio
from dawg_baas import AsyncBaas

async def main():
    baas = AsyncBaas(api_key="ваш_api_ключ")

    try:
        ws_url = await baas.create()
        print(f"Браузер готов: {ws_url}")

        # Здесь ваш асинхронный код
        # ...

    finally:
        # Обязательно возвращаем браузер в пул
        await baas.release()

asyncio.run(main())
```

## С контекст-менеджером

Рекомендуемый способ — браузер автоматически освобождается:

```python
from dawg_baas import Baas

with Baas(api_key="ваш_api_ключ") as ws_url:
    print(f"Браузер готов: {ws_url}")
    # Работаем с браузером
    # ...

# Браузер автоматически возвращён в пул
```

## С прокси

Поддерживаются SOCKS5 и HTTP прокси. При использовании прокси нужно
управлять браузером вручную (контекст-менеджер `with` не поддерживает прокси):

```python
from dawg_baas import Baas

# Форматы: socks5://user:pass@host:port или http://user:pass@host:port
PROXY = "http://user:pass@proxy.example.com:8080"

baas = Baas(api_key="ваш_api_ключ")

try:
    ws_url = baas.create(proxy=PROXY)
    # Работа с браузером...
finally:
    baas.release()
```

## С Playwright

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

with Baas(api_key="ваш_api_ключ") as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://example.com")
        print(page.title())

        browser.close()
```

## Обработка ошибок

```python
from dawg_baas import (
    Baas,
    BaasError,
    AuthError,
    RateLimitError,
    BrowserNotReadyError
)
import time

def run_with_retry(api_key: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            with Baas(api_key=api_key) as ws_url:
                print(f"Подключено: {ws_url}")
                # Ваш код здесь
                return True

        except AuthError:
            print("Ошибка: неверный API-ключ")
            return False

        except RateLimitError as e:
            print(f"Лимит превышен. Ждём {e.retry_after} сек...")
            time.sleep(e.retry_after)

        except BrowserNotReadyError:
            print(f"Попытка {attempt + 1}: браузер не готов")
            time.sleep(5)

        except BaasError as e:
            print(f"Ошибка: {e.message}")
            return False

    return False

run_with_retry("ваш_api_ключ")
```

## Параллельные браузеры

```python
import asyncio
from dawg_baas import AsyncBaas

async def process_url(api_key: str, url: str):
    async with AsyncBaas(api_key=api_key) as ws_url:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]
            await page.goto(url)
            title = await page.title()
            await browser.close()
            return title

async def main():
    api_key = "ваш_api_ключ"
    urls = [
        "https://example.com",
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com"
    ]

    # Запускаем параллельно
    tasks = [process_url(api_key, url) for url in urls]
    results = await asyncio.gather(*tasks)

    for url, title in zip(urls, results):
        print(f"{url}: {title}")

asyncio.run(main())
```
