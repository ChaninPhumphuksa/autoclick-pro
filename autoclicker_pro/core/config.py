# -*- coding: utf-8 -*-
"""
core/config.py
==============
จัดการการตั้งค่าที่ต้องคงอยู่ข้ามการเปิด-ปิดโปรแกรม (persistent settings)
เก็บไว้ที่โฟลเดอร์โปรไฟล์ผู้ใช้ ~/.autoclicker_pro/config.json
เพื่อให้ทำงานได้ถูกต้องแม้ติดตั้งโปรแกรมเป็น .exe ในโฟลเดอร์ที่เขียนไฟล์ไม่ได้ (เช่น Program Files)
"""

import json
import os

APP_DIR = os.path.join(os.path.expanduser("~"), ".autoclicker_pro")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
MACRO_LIBRARY_DIR = os.path.join(APP_DIR, "saved_macros")
LOG_DIR = os.path.join(APP_DIR, "logs")

DEFAULT_CONFIG = {
    "hotkey_click": "f6",
    "hotkey_play": "f7",
    "hotkey_record": "f8",
    "hotkey_capture": "f9",
    "theme": "dark",              # "dark" หรือ "light"
    "start_with_windows": False,
    "minimize_to_tray_on_close": True,
    "window_geometry": None,      # เก็บขนาด/ตำแหน่งหน้าต่างล่าสุด
    "background_mode": False,             # ทำงานเบื้องหลังกับโปรแกรมเป้าหมายโดยไม่ขโมยโฟกัส
    "background_target_title": None,      # ชื่อหน้าต่างเป้าหมายล่าสุดที่เลือกไว้
    "background_target_process": None,    # ชื่อโปรแกรม (.exe) ของเป้าหมายล่าสุด
}


def ensure_dirs():
    os.makedirs(APP_DIR, exist_ok=True)
    os.makedirs(MACRO_LIBRARY_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def load_config():
    ensure_dirs()
    if not os.path.exists(CONFIG_PATH):
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(config: dict):
    ensure_dirs()
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
