# Cookbook

Практические рецепты для решения типичных задач с браузерной автоматизацией.

> **Два способа использования SDK:**
> - **with (контекст-менеджер)** — автоматическое освобождение браузера, без прокси
> - **Ручное управление** — полный контроль, поддержка прокси

## Работа с прокси

Использование SOCKS5/HTTP прокси для обхода гео-ограничений и ротации IP.

### Ручное управление (с прокси)

```python
import json
import re
import time
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"

# Форматы прокси:
# SOCKS5: "socks5://user:pass@host:port"
# HTTP:   "http://user:pass@host:port"
PROXY = "http://username:password@proxy.example.com:8080"

baas = Baas(api_key=API_KEY)

try:
    # Создаём браузер с прокси
    print("Создаём браузер с прокси...")
    ws_url = baas.create(proxy=PROXY)
    print(f"Браузер создан: {baas.browser_id}")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        time.sleep(2)  # Ждём инициализации

        page = browser.contexts[0].pages[0]

        # Проверяем IP через прокси
        print("Проверяем IP...")
        page.goto("https://api.ipify.org?format=json", wait_until="networkidle", timeout=60000)

        content = page.content()
        match = re.search(r'\{[^}]+\}', content)
        if match:
            data = json.loads(match.group())
            print(f"IP через прокси: {data.get('ip')}")

        # Открываем сайт
        page.goto("https://example.com", wait_until="networkidle")
        print(f"Заголовок: {page.title()}")

        browser.close()

finally:
    baas.release()
    print("Готово!")
```

### with (без прокси)

> **Примечание:** Контекст-менеджер `with Baas(...) as ws_url` не поддерживает передачу прокси.
> Для работы с прокси используйте ручное управление.

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

# Без прокси — можно использовать with
with Baas(api_key="ваш_api_ключ") as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://api.ipify.org?format=json")
        print(page.content())

        browser.close()
# Браузер автоматически освобождён
```

---

## Скриншоты разных разрешений

Создание скриншотов для desktop, tablet и mobile.

### with

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://example.com"

VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        for device, viewport in VIEWPORTS.items():
            page.set_viewport_size(viewport)
            page.goto(URL, wait_until="networkidle")
            page.screenshot(path=f"screenshot_{device}.png")
            print(f"Сохранён: screenshot_{device}.png")

        browser.close()
```

### Ручное управление

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://example.com"

VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}

baas = Baas(api_key=API_KEY)

try:
    ws_url = baas.create()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        for device, viewport in VIEWPORTS.items():
            page.set_viewport_size(viewport)
            page.goto(URL, wait_until="networkidle")
            page.screenshot(path=f"screenshot_{device}.png")
            print(f"Сохранён: screenshot_{device}.png")

        browser.close()

finally:
    baas.release()
```

---

## Извлечение данных из таблиц

Извлечение данных из HTML-таблиц (например, Wikipedia).

### with

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://en.wikipedia.org/wiki/List_of_countries_by_population"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")

        # Находим таблицу
        table = page.query_selector("table.wikitable")
        rows = table.query_selector_all("tr")[1:11]  # Первые 10 строк

        print("Топ-10 стран по населению:")
        for i, row in enumerate(rows, 1):
            cells = row.query_selector_all("td")
            if cells:
                country = cells[0].inner_text().strip()
                print(f"{i}. {country}")

        browser.close()
```

### Ручное управление

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://en.wikipedia.org/wiki/List_of_countries_by_population"

baas = Baas(api_key=API_KEY)

try:
    ws_url = baas.create()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")

        table = page.query_selector("table.wikitable")
        rows = table.query_selector_all("tr")[1:11]

        print("Топ-10 стран по населению:")
        for i, row in enumerate(rows, 1):
            cells = row.query_selector_all("td")
            if cells:
                country = cells[0].inner_text().strip()
                print(f"{i}. {country}")

        browser.close()

finally:
    baas.release()
```

---

## Заполнение форм

Автоматическое заполнение и отправка форм.

### with

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://httpbin.org/forms/post"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")

        # Заполняем поля
        page.fill('input[name="custname"]', "Иван Иванов")
        page.fill('input[name="custtel"]', "+7-999-123-4567")
        page.fill('input[name="custemail"]', "ivan@example.com")

        # Выбираем опции
        page.click('input[name="size"][value="medium"]')
        page.check('input[name="topping"][value="bacon"]')
        page.check('input[name="topping"][value="cheese"]')

        # Отправляем форму
        with page.expect_response(lambda r: "post" in r.url) as response:
            page.click('button[type="submit"]')

        print(f"Статус: {response.value.status}")

        browser.close()
```

### Ручное управление

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://httpbin.org/forms/post"

baas = Baas(api_key=API_KEY)

try:
    ws_url = baas.create()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")

        page.fill('input[name="custname"]', "Иван Иванов")
        page.fill('input[name="custtel"]', "+7-999-123-4567")
        page.fill('input[name="custemail"]', "ivan@example.com")

        page.click('input[name="size"][value="medium"]')
        page.check('input[name="topping"][value="bacon"]')
        page.check('input[name="topping"][value="cheese"]')

        with page.expect_response(lambda r: "post" in r.url) as response:
            page.click('button[type="submit"]')

        print(f"Статус: {response.value.status}")

        browser.close()

finally:
    baas.release()
```

---

## Генерация PDF

Создание PDF через Chrome DevTools Protocol.

### with

```python
import base64
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://example.com"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")

        # Используем CDP для генерации PDF
        cdp = page.context.new_cdp_session(page)
        result = cdp.send("Page.printToPDF", {
            "printBackground": True,
            "preferCSSPageSize": True,
            "marginTop": 0.5,
            "marginBottom": 0.5,
            "marginLeft": 0.5,
            "marginRight": 0.5,
        })

        # Сохраняем PDF
        pdf_data = base64.b64decode(result["data"])
        with open("output.pdf", "wb") as f:
            f.write(pdf_data)

        print("PDF сохранён: output.pdf")
        browser.close()
```

### Ручное управление

```python
import base64
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://example.com"

baas = Baas(api_key=API_KEY)

try:
    ws_url = baas.create()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")

        cdp = page.context.new_cdp_session(page)
        result = cdp.send("Page.printToPDF", {
            "printBackground": True,
            "preferCSSPageSize": True,
            "marginTop": 0.5,
            "marginBottom": 0.5,
            "marginLeft": 0.5,
            "marginRight": 0.5,
        })

        pdf_data = base64.b64decode(result["data"])
        with open("output.pdf", "wb") as f:
            f.write(pdf_data)

        print("PDF сохранён: output.pdf")
        browser.close()

finally:
    baas.release()
```

---

## Работа с SPA (JavaScript)

Работа с динамическим контентом Single Page Applications.

### with

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://quotes.toscrape.com/js/"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL)

        # Ждём загрузки динамического контента
        page.wait_for_selector(".quote", timeout=10000)

        # Извлекаем данные через JavaScript (быстрее)
        quotes = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.quote')).map(q => ({
                text: q.querySelector('.text')?.innerText || '',
                author: q.querySelector('.author')?.innerText || '',
                tags: Array.from(q.querySelectorAll('.tag')).map(t => t.innerText)
            }));
        }""")

        print(f"Найдено цитат: {len(quotes)}")
        for quote in quotes[:3]:
            print(f"\n{quote['text']}")
            print(f"  — {quote['author']}")
            print(f"  Теги: {', '.join(quote['tags'])}")

        browser.close()
```

### Ручное управление

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"
URL = "https://quotes.toscrape.com/js/"

baas = Baas(api_key=API_KEY)

try:
    ws_url = baas.create()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL)
        page.wait_for_selector(".quote", timeout=10000)

        quotes = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.quote')).map(q => ({
                text: q.querySelector('.text')?.innerText || '',
                author: q.querySelector('.author')?.innerText || '',
                tags: Array.from(q.querySelectorAll('.tag')).map(t => t.innerText)
            }));
        }""")

        print(f"Найдено цитат: {len(quotes)}")
        for quote in quotes[:3]:
            print(f"\n{quote['text']}")
            print(f"  — {quote['author']}")
            print(f"  Теги: {', '.join(quote['tags'])}")

        browser.close()

finally:
    baas.release()
```

---

## Перехват сетевых запросов

Мониторинг HTTP-запросов.

### with

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        # Перехватываем запросы
        def handle_request(request):
            if request.resource_type in ["image", "font"]:
                return
            print(f"[{request.method}] {request.url[:80]}")

        def handle_response(response):
            if response.status >= 400:
                print(f"[ОШИБКА {response.status}] {response.url[:80]}")

        page.on("request", handle_request)
        page.on("response", handle_response)

        page.goto("https://httpbin.org/anything")

        browser.close()
```

### Ручное управление

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "ваш_api_ключ"

baas = Baas(api_key=API_KEY)

try:
    ws_url = baas.create()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        def handle_request(request):
            if request.resource_type in ["image", "font"]:
                return
            print(f"[{request.method}] {request.url[:80]}")

        def handle_response(response):
            if response.status >= 400:
                print(f"[ОШИБКА {response.status}] {response.url[:80]}")

        page.on("request", handle_request)
        page.on("response", handle_response)

        page.goto("https://httpbin.org/anything")

        browser.close()

finally:
    baas.release()
```
