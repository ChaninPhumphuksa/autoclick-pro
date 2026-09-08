"""
hotkey_manager.py
ระบบดักจับปุ่มคีย์บอร์ด "แบบไหนก็ได้" (any key) ทั้งสำหรับ:
  1. capture_next_key(): จับปุ่มถัดไปที่ผู้ใช้กด เพื่อนำไปตั้งเป็น hotkey (ตอนกด "Set Hotkey")
  2. HotkeyManager: ฟังปุ่มลัดหลายตัวพร้อมกันแบบ global (ทำงานได้แม้โปรแกรมไม่ได้โฟกัสอยู่)
     รองรับทั้งปุ่มเดี่ยว (เช่น F6) และคีย์ผสม (เช่น ctrl+alt+s)
"""

import threading
from pynput import keyboard as pkeyboard


def key_to_str(key) -> str:
    try:
        return key.char
    except AttributeError:
        return str(key).replace("Key.", "")


def capture_next_key(callback, timeout=None):
    """
    เริ่มฟังปุ่มถัดไปที่ผู้ใช้กด (ปุ่มเดียว) แล้วเรียก callback(key_str) หนึ่งครั้ง
    ใช้ตอนผู้ใช้กดปุ่ม "ตั้งค่า Hotkey" ในหน้า UI แล้วรอให้กดปุ่มจริงบนคีย์บอร์ด
    """
    listener_holder = {}

    def on_press(key):
        name = key_to_str(key)
        callback(name)
        listener_holder["listener"].stop()
        return False  # หยุด listener

    listener = pkeyboard.Listener(on_press=on_press)
    listener_holder["listener"] = listener
    listener.start()
    return listener


class HotkeyManager:
    """
    ลงทะเบียน hotkey หลายตัว แต่ละตัวมี callback ของตัวเอง
    hotkeys: dict {"f6": callback_fn, "ctrl+alt+s": callback_fn, ...}
    """

    def __init__(self):
        self._bindings = {}  # normalized_str -> callback
        self._pressed = set()
        self._listener = None
        self._lock = threading.Lock()

    def register(self, hotkey_str: str, callback):
        with self._lock:
            self._bindings[self._normalize(hotkey_str)] = callback

    def unregister(self, hotkey_str: str):
        with self._lock:
            self._bindings.pop(self._normalize(hotkey_str), None)

    def clear(self):
        with self._lock:
            self._bindings.clear()

    @staticmethod
    def _normalize(hotkey_str: str) -> str:
        parts = [p.strip().lower() for p in hotkey_str.split("+")]
        return "+".join(sorted(parts))

    def start(self):
        if self._listener:
            return

        def on_press(key):
            name = key_to_str(key).lower()
            self._pressed.add(name)
            combo = self._normalize("+".join(self._pressed))
            with self._lock:
                cb = self._bindings.get(combo)
            if cb:
                cb()

        def on_release(key):
            name = key_to_str(key).lower()
            self._pressed.discard(name)

        self._listener = pkeyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._pressed.clear()
