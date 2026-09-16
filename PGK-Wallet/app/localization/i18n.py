"""
PGK Wallet - simple JSON-based i18n loader.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DIR = Path(__file__).resolve().parent
_CACHE: dict[str, dict[str, str]] = {}


def _load(lang: str) -> dict[str, str]:
    if lang not in _CACHE:
        path = _DIR / f"{lang}.json"
        if not path.exists():
            path = _DIR / "en.json"
        with open(path, "r", encoding="utf-8") as f:
            _CACHE[lang] = json.load(f)
    return _CACHE[lang]


def t(lang: str, key: str, **kwargs: Any) -> str:
    """Translate `key` for `lang`, falling back to Persian then the raw key."""
    lang = lang if lang in ("fa", "en") else "fa"
    strings = _load(lang)
    text = strings.get(key)
    if text is None:
        text = _load("fa").get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
