"""
profile_manager.py
จัดการบันทึก/โหลดโปรไฟล์การตั้งค่า Auto Clicker และไฟล์มาโคร/สคริปต์ (.json)
เก็บไว้ในโฟลเดอร์ profiles/ และ macros/ ข้าง ๆ ตัวโปรแกรม
"""

import json
import os
import sys


def _base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


PROFILES_DIR = os.path.join(_base_dir(), "profiles")
MACROS_DIR = os.path.join(_base_dir(), "macros")

os.makedirs(PROFILES_DIR, exist_ok=True)
os.makedirs(MACROS_DIR, exist_ok=True)


def list_files(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(f[:-5] for f in os.listdir(folder) if f.endswith(".json"))


def save_json(folder, name, data):
    safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip() or "untitled"
    path = os.path.join(folder, f"{safe_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_json(folder, name):
    path = os.path.join(folder, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_json(folder, name):
    path = os.path.join(folder, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)


# ---- ทางลัดสำหรับโปรไฟล์ auto-clicker ----
def list_profiles():
    return list_files(PROFILES_DIR)


def save_profile(name, settings):
    return save_json(PROFILES_DIR, name, settings)


def load_profile(name):
    return load_json(PROFILES_DIR, name)


def delete_profile(name):
    delete_json(PROFILES_DIR, name)


# ---- ทางลัดสำหรับมาโคร/สคริปต์ ----
def list_macros():
    return list_files(MACROS_DIR)


def save_macro(name, script):
    return save_json(MACROS_DIR, name, script)


def load_macro(name):
    return load_json(MACROS_DIR, name)


def delete_macro(name):
    delete_json(MACROS_DIR, name)
