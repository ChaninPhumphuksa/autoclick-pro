# -*- coding: utf-8 -*-
"""
core/positions.py
==================
จัดเก็บ "ตำแหน่งบนหน้าจอ" ที่ผู้ใช้บันทึกไว้เป็นชื่อที่จำง่าย (Position Picker)
เพื่อให้เลือกใช้ซ้ำได้ทั้งในหน้า Auto Click และตอนสร้างขั้นตอนคลิกในชุดคำสั่ง
โดยไม่ต้องจิ้มตำแหน่งใหม่ทุกครั้ง

เก็บไว้ที่ ~/.autoclicker_pro/positions.json
"""

import json
import os

from .config import APP_DIR, ensure_dirs

POSITIONS_PATH = os.path.join(APP_DIR, "positions.json")


def load_positions():
    """คืน dict รูปแบบ {"ชื่อตำแหน่ง": {"x": int, "y": int}, ...}"""
    ensure_dirs()
    if not os.path.exists(POSITIONS_PATH):
        return {}
    try:
        with open(POSITIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def save_positions(data):
    ensure_dirs()
    try:
        with open(POSITIONS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def add_or_update_position(name, x, y):
    data = load_positions()
    data[name] = {"x": int(x), "y": int(y)}
    save_positions(data)
    return data


def delete_position(name):
    data = load_positions()
    if name in data:
        del data[name]
        save_positions(data)
    return data
