# API Reference

Справочник по всем методам SDK. Если вы только начинаете — лучше начните с раздела «Быстрый старт».

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
