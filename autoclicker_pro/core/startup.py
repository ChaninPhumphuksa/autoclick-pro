# -*- coding: utf-8 -*-
"""
core/startup.py
================
จัดการ "เปิดโปรแกรมอัตโนมัติเมื่อ Windows เริ่มทำงาน" ผ่าน Registry
(HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run)

ทำงานเฉพาะบน Windows เท่านั้น — บน macOS/Linux ฟังก์ชันจะคืนค่า False และไม่ทำอะไร
"""

import sys
import os

APP_NAME = "AutoClickerPro"


def is_windows():
    return sys.platform.startswith("win")


def _get_target_command():
    """คืนคำสั่งที่จะให้ Windows รันตอน startup (รองรับทั้งโหมด .py และ .exe ที่แพ็กแล้ว)"""
    if getattr(sys, "frozen", False):
        # กรณีถูกแพ็กเป็น .exe ด้วย PyInstaller แล้ว sys.executable คือตัว .exe เอง
        return f'"{sys.executable}"'
    else:
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        return f'"{pythonw}" "{main_script}"'


def is_enabled():
    if not is_windows():
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def set_enabled(enabled: bool):
    if not is_windows():
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Run",
                              0, winreg.KEY_SET_VALUE)
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_target_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False
