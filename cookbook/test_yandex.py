#!/usr/bin/env python3
"""
Тест stealth браузера через BaaS кластер: открывает Яндекс, делает поиск.

Usage:
    python cookbook/test_yandex.py
"""

import time
from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"

# Селекторы капчи Яндекса
CAPTCHA_SELECTORS = [
    'input.CheckboxCaptcha-Button',
    '.CheckboxCaptcha',
    '.SmartCaptcha',
    'img[src*="captcha"]',
    '[class*="Captcha"]',
]

# Селекторы поля поиска
SEARCH_SELECTORS = [
    'input[name="text"]',
    'input.search3__input',
    'input.mini-suggest__input',
    '#text',
    'input[aria-label*="запрос"]',
]


def check_captcha(page) -> str | None:
    """Проверяет наличие капчи, возвращает селектор если найдена."""
    for sel in CAPTCHA_SELECTORS:
        el = page.query_selector(sel)
        if el and el.is_visible():
            return sel
    return None


def find_search_input(page):
    """Ищет поле поиска по разным селекторам."""
    for sel in SEARCH_SELECTORS:
        try:
            el = page.wait_for_selector(sel, timeout=3000)
            if el:
                print(f"    Найдено поле: {sel}")
                return el
        except:
            continue
    return None


with Baas(api_key=API_KEY) as ws_url:
    print(f"[0] Браузер получен: {ws_url[:50]}...")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        # Открываем Яндекс
        print("[1] Открываю ya.ru...")
        page.goto("https://ya.ru", wait_until="networkidle", timeout=30000)
        page.screenshot(path="/tmp/baas_yandex_1_main.png", full_page=True)
        print("    Скриншот: /tmp/baas_yandex_1_main.png")

        time.sleep(2)

        # Проверяем капчу
        print("[2] Проверяю капчу...")
        captcha = check_captcha(page)
        if captcha:
            print(f"    ⚠️  КАПЧА ОБНАРУЖЕНА! ({captcha})")
            page.screenshot(path="/tmp/baas_yandex_captcha.png", full_page=True)
            print("    Скриншот: /tmp/baas_yandex_captcha.png")
            browser.close()
            exit(1)
        print("    Капчи нет ✓")

        # Ищем поле поиска
        print("[3] Ввожу поисковый запрос...")
        search_input = find_search_input(page)
        if not search_input:
            print("    ❌ Поле поиска не найдено")
            page.screenshot(path="/tmp/baas_yandex_no_input.png", full_page=True)
            browser.close()
            exit(1)

        # Вводим запрос
        search_query = "playwright browser automation"
        search_input.click()
        time.sleep(0.5)
        search_input.fill(search_query)
        page.screenshot(path="/tmp/baas_yandex_2_typed.png", full_page=True)
        print("    Скриншот: /tmp/baas_yandex_2_typed.png")

        # Отправляем поиск
        print("[4] Отправляю поиск...")
        page.keyboard.press("Enter")

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass
        time.sleep(3)

        # Проверяем капчу после поиска
        captcha = check_captcha(page)
        if captcha:
            print(f"    ⚠️  КАПЧА ПОСЛЕ ПОИСКА! ({captcha})")
            page.screenshot(path="/tmp/baas_yandex_captcha_search.png", full_page=True)
            print("    Скриншот: /tmp/baas_yandex_captcha_search.png")
            browser.close()
            exit(1)

        # Финальный скриншот
        page.screenshot(path="/tmp/baas_yandex_3_results.png", full_page=True)
        print("[5] Готово!")
        print("    Скриншот результатов: /tmp/baas_yandex_3_results.png")
        print(f"    Текущий URL: {page.url}")

        browser.close()

print("\n[OK] Тест завершён успешно!")
