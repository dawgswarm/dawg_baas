# Быстрый старт

Начните работу с DAWG BaaS за несколько минут. Получите API-ключ в личном кабинете
и используйте примеры ниже.

## Получение API-ключа

1. Зарегистрируйтесь на сайте
2. Перейдите в раздел «API ключи» в панели управления
3. Создайте новый ключ

## Минимальный пример

Самый простой способ — использовать контекст-менеджер:

```python
from dawg_baas import Baas

# Контекст-менеджер автоматически освободит браузер
with Baas(api_key="ваш_api_ключ") as ws_url:
    print(f"WebSocket URL: {ws_url}")
    # Подключайтесь к браузеру через ws_url
```

## Пример с Playwright

Интеграция с Playwright для автоматизации браузера:

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        # Подключаемся к удалённому браузеру
        browser = p.chromium.connect_over_cdp(ws_url)

        # Получаем страницу
        page = browser.contexts[0].pages[0]

        # Работаем с браузером
        page.goto("https://example.com")
        print(f"Заголовок: {page.title()}")

        # Делаем скриншот
        page.screenshot(path="screenshot.png")

        browser.close()

print("Готово!")
```

## Асинхронный пример

Для асинхронного кода используйте `AsyncBaas`:

```python
import asyncio
from dawg_baas import AsyncBaas
from playwright.async_api import async_playwright

async def main():
    async with AsyncBaas(api_key="ваш_api_ключ") as ws_url:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]

            await page.goto("https://example.com")
            print(f"Заголовок: {await page.title()}")

            await browser.close()

asyncio.run(main())
```

> **Важно:** Браузер автоматически возвращается в пул при выходе
> из контекст-менеджера. Это позволяет эффективно переиспользовать ресурсы.
