# Геолокация

Подмена GPS-координат в браузере. Сайты, использующие `navigator.geolocation`, получат указанные вами координаты вместо реальных.

## Использование

Передайте параметр `geo` при создании браузера. Можно указать slug города или точные координаты.

### По названию города

```python
from dawg_baas import Baas

baas = Baas(api_key="ваш_ключ")
ws_url = baas.create(geo="novosibirsk")

# Браузер будет отдавать координаты Новосибирска
browser = playwright.chromium.connect_over_cdp(ws_url)
# ...
baas.release()
```

### По координатам

```python
# Точные координаты (lat, lon)
ws_url = baas.create(geo=(55.7558, 37.6173))  # Москва

# Или по slug:
ws_url = baas.create(geo="moskva")
```

### Async-клиент

```python
from dawg_baas import AsyncBaas

baas = AsyncBaas(api_key="ваш_ключ")
ws_url = await baas.create(geo="moskva")
# ...
await baas.release()
```

### Комбинация с прокси

```python
# Прокси + геолокация
ws_url = baas.create(
    proxy="socks5://user:pass@host:port",
    geo="kazan"
)
```

## Параметр `geo`

| Тип | Пример | Описание |
|-----|--------|----------|
| `str` | `"moskva"` | Slug города из таблицы ниже. Координаты подставляются автоматически |
| `tuple[float, float]` | `(55.75, 37.61)` | Явные координаты `(широта, долгота)` |

## Как это работает

- При создании браузера Manager вызывает `Emulation.setGeolocationOverride` через CDP
- Разрешение `geolocation` автоматически выдается через `Browser.grantPermissions`
- Геолокация применяется ко всем вкладкам, включая открытые позже
- Координаты видны через `navigator.geolocation.getCurrentPosition()`

## Проверка

```python
from playwright.sync_api import sync_playwright
from dawg_baas import Baas

baas = Baas(api_key="ваш_ключ")
ws_url = baas.create(geo="moskva")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(ws_url)
    page = browser.new_page()

    coords = page.evaluate("""
        () => new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                pos => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude}),
                err => reject(err.message)
            )
        })
    """)
    print(f"Координаты: {coords}")
    # -> {'lat': 55.755833333333, 'lon': 37.617777777778}

    browser.close()

baas.release()
```

## Доступные города

1134 города России. Полный список с возможностью поиска доступен на странице документации: **Документация → Геолокация**.

Список также доступен через API:

```
GET https://dawgswarm.ru/api/geo/cities
```

### Популярные города

| Город | Slug | Широта | Долгота |
|-------|------|--------|---------|
| Москва | `moskva` | 55.7558 | 37.6178 |
| Санкт-Петербург | `sankt-peterburg` | 59.9500 | 30.3167 |
| Новосибирск | `novosibirsk` | 55.0167 | 82.9167 |
| Екатеринбург | `yekaterinburg` | 56.8333 | 60.5833 |
| Казань | `kazan` | 55.7833 | 49.1000 |
| Нижний Новгород | `nizhniy-novgorod` | 56.3167 | 44.0000 |
| Красноярск | `krasnoyarsk` | 56.0167 | 92.8667 |
| Самара | `samara` | 53.1833 | 50.1000 |
| Ростов-на-Дону | `rostov-na-donu` | 47.2333 | 39.7000 |
| Владивосток | `vladivostok` | 43.1000 | 131.8667 |
