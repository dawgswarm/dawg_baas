# Changelog

## 0.4.0 — 2026-08-03

- `Baas.list_sessions()` / `AsyncBaas.list_sessions()` — server-side list of the
  account's live sessions (`ACTIVE` + `IDLE`), including ones created by other
  processes.
- `release(session_id=None)` now accepts an explicit session id, so a session
  whose id was lost (crashed worker, restarted process) can be found via
  `list_sessions()` and killed instead of burning minutes until the farm's
  inactivity timeout.

## 0.3.0 — 2026-05-16

**BREAKING:** Package renamed from `dawg-baas` to `dawg-sdk-python`.

- PyPI package name: `dawg-baas` → `dawg-sdk-python`
- Import path: `from dawg_baas import ...` → `from dawg_sdk import ...`
- GitHub repository: `dawgswarm/dawg_baas` → `dawgswarm/dawg-sdk-python`

The old `dawg-baas` package remains frozen on PyPI at 0.2.1 and will not receive further updates. Migrate by installing the new package and updating imports — the public API is otherwise unchanged.

```bash
pip uninstall dawg-baas
pip install dawg-sdk-python
```

```python
# before
from dawg_baas import Baas, AsyncBaas, Scraper

# after
from dawg_sdk import Baas, AsyncBaas, Scraper
```
