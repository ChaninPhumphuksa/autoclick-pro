# -*- coding: utf-8 -*-
"""
core/stats.py
=============
เก็บสถิติการใช้งานแบบง่าย ๆ (คลิกไปทั้งหมดกี่ครั้ง, วันนี้กี่ครั้ง, รันชุดคำสั่งไปกี่ครั้ง)
บันทึกไว้ที่ ~/.autoclicker_pro/stats.json
"""

import json
import os
import threading
from datetime import date

from .config import APP_DIR, ensure_dirs

STATS_PATH = os.path.join(APP_DIR, "stats.json")

DEFAULT_STATS = {
    "total_clicks": 0,
    "total_macro_runs": 0,
    "today_date": "",
    "today_clicks": 0,
}

_lock = threading.Lock()
_stats = None


def _load():
    ensure_dirs()
    if not os.path.exists(STATS_PATH):
        return dict(DEFAULT_STATS)
    try:
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_STATS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_STATS)


def _save():
    ensure_dirs()
    try:
        with open(STATS_PATH, "w", encoding="utf-8") as f:
            json.dump(_stats, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _ensure_today():
    today_str = date.today().isoformat()
    if _stats.get("today_date") != today_str:
        _stats["today_date"] = today_str
        _stats["today_clicks"] = 0


def get_stats():
    global _stats
    with _lock:
        if _stats is None:
            _stats = _load()
        _ensure_today()
        return dict(_stats)


def record_click(count=1):
    global _stats
    with _lock:
        if _stats is None:
            _stats = _load()
        _ensure_today()
        _stats["total_clicks"] += count
        _stats["today_clicks"] += count
        _save()


def record_macro_run():
    global _stats
    with _lock:
        if _stats is None:
            _stats = _load()
        _stats["total_macro_runs"] += 1
        _save()


def reset_stats():
    global _stats
    with _lock:
        _stats = dict(DEFAULT_STATS)
        _ensure_today()
        _save()
