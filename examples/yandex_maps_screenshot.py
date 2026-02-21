"""Скриншот Яндекс Карт с геолокацией Бердска."""

import os
from dawg_baas import Baas
import time
from playwright.sync_api import sync_playwright

API_KEY = "api_key"

baas = Baas(api_key=API_KEY)

try:
    # Создаём браузер с геолокацией Бердска
    print("Создаём браузер с geo='moskva'...")
    ws_url = baas.create(geo="moskva")
    print(f"Браузер готов: {baas.browser_id}")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        # Открываем Яндекс Карты
        print("Открываем Яндекс Карты...")
        page.goto("https://yandex.ru/maps", wait_until="networkidle", timeout=60000)

        # Ждём загрузку карты
        #print("Ждём 10 сек перед нажатием на кнопку геолокации...")
        #time.sleep(1)

        # Нажимаем кнопку "Моё местоположение" (ищем по внутреннему классу иконки)
        geo_btn = page.locator(".map-geolocation-control__icon").first
        geo_btn.click(timeout=10000)
        print("Кнопка геолокации нажата, ждём перемещение карты...")

        # Ждём пока карта переместится к геолокации
        time.sleep(2)

        # Делаем скриншот
        page.screenshot(path="yandex_maps_moskva.png")
        print("Скриншот сохранён: yandex_maps_moskva.png")

        browser.close()

finally:
    baas.release()
    print("Готово!")
