# -*- coding: utf-8 -*-
"""
core/engine.py
==============
เอนจินหลักของโปรแกรม: AutoClicker, MacroRecorder (บันทึก+แก้ไขมาโครเอง), MacroPlayer
แยกออกจากชั้น GUI โดยเด็ดขาด (separation of concerns) เพื่อให้ทดสอบและดูแลรักษาง่าย
"""

import json
import random
import threading
import time

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import mouse, keyboard
except ImportError:
    mouse = None
    keyboard = None

from .logger import get_logger

log = get_logger()

if pyautogui:
    pyautogui.FAILSAFE = False


class AutoClicker:
    def __init__(self, get_settings_fn, status_cb):
        self.get_settings = get_settings_fn
        self.status_cb = status_cb
        self._thread = None
        self._stop_event = threading.Event()
        self.running = False

    def start(self):
        if self.running or pyautogui is None:
            return
        self._stop_event.clear()
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        log.info("Auto Click started")
        self.status_cb("คลิกอัตโนมัติ: กำลังทำงาน...")

    def stop(self):
        if not self.running:
            return
        self._stop_event.set()
        self.running = False
        log.info("Auto Click stop requested")
        self.status_cb("คลิกอัตโนมัติ: หยุดแล้ว")

    def toggle(self):
        self.stop() if self.running else self.start()

    def _run(self):
        s = self.get_settings()
        base_interval = max(0.001, s["interval_seconds"])
        jitter = max(0.0, s.get("jitter_seconds", 0.0))
        button = s["button"]
        double = s["double_click"]
        limited = s["limited_count"]
        max_clicks = s["click_count"]
        fixed = s.get("fixed_position", False)
        fx, fy = s.get("fixed_x"), s.get("fixed_y")
        count = 0
        try:
            while not self._stop_event.is_set():
                kwargs = {"button": button}
                if double:
                    kwargs["clicks"] = 2
                    kwargs["interval"] = 0.05
                if fixed and fx is not None and fy is not None:
                    kwargs["x"] = fx
                    kwargs["y"] = fy
                pyautogui.click(**kwargs)
                count += 1
                if limited and count >= max_clicks:
                    break
                wait_time = base_interval
                if jitter:
                    wait_time = max(0.001, base_interval + random.uniform(-jitter, jitter))
                self._stop_event.wait(wait_time)
        except Exception:
            log.exception("Error in AutoClicker loop")
        self.running = False
        log.info(f"Auto Click stopped, total clicks={count}")
        self.status_cb(f"คลิกอัตโนมัติ: หยุดแล้ว (คลิกไปทั้งหมด {count} ครั้ง)")


class MacroRecorder:
    """
    บันทึกเหตุการณ์เมาส์/คีย์บอร์ดจากการอัดจริง และรองรับแก้ไข/เพิ่ม/ลบ/เรียงลำดับเอง

    event: {"type": "click", "x", "y", "button", "delay"}
           {"type": "key", "key", "delay"}
           {"type": "wait", "delay"}
    """

    def __init__(self, status_cb, on_change=None):
        self.status_cb = status_cb
        self.on_change = on_change or (lambda: None)
        self.events = []
        self._recording = False
        self._last_time = None
        self._mouse_listener = None
        self._keyboard_listener = None

    @property
    def recording(self):
        return self._recording

    def start(self):
        if self._recording or mouse is None:
            return
        self.events = []
        self._recording = True
        self._last_time = time.time()
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self._mouse_listener.start()
        self._keyboard_listener.start()
        log.info("Macro recording started")
        self.status_cb("กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว 0 ขั้นตอน)")
        self.on_change()

    def stop(self):
        if not self._recording:
            return
        self._recording = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        log.info(f"Macro recording stopped, {len(self.events)} events")
        self.status_cb(f"หยุดบันทึกชุดคำสั่งแล้ว (ได้ {len(self.events)} ขั้นตอน)")
        self.on_change()

    def toggle(self):
        self.stop() if self._recording else self.start()

    def _record_delay(self):
        now = time.time()
        delay = now - self._last_time
        self._last_time = now
        return delay

    def _on_click(self, x, y, button, pressed):
        if not self._recording or not pressed:
            return
        delay = self._record_delay()
        self.events.append({
            "type": "click", "x": x, "y": y,
            "button": str(button).replace("Button.", ""), "delay": delay,
        })
        self.status_cb(f"กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว {len(self.events)} ขั้นตอน)")
        self.on_change()

    def _on_key_press(self, key):
        if not self._recording:
            return
        if key == keyboard.Key.esc:
            return
        delay = self._record_delay()
        try:
            key_repr = key.char
        except AttributeError:
            key_repr = str(key)
        self.events.append({"type": "key", "key": key_repr, "delay": delay})
        self.status_cb(f"กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว {len(self.events)} ขั้นตอน)")
        self.on_change()

    # ---- manual editing (custom macro) ----
    def add_step(self, step, index=None):
        if index is None or index >= len(self.events):
            self.events.append(step)
        else:
            self.events.insert(index, step)
        self.on_change()

    def update_step(self, index, step):
        if 0 <= index < len(self.events):
            self.events[index] = step
            self.on_change()

    def remove_step(self, index):
        if 0 <= index < len(self.events):
            del self.events[index]
            self.on_change()

    def move_step(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.events) and 0 <= index < len(self.events):
            self.events[index], self.events[new_index] = self.events[new_index], self.events[index]
            self.on_change()
            return new_index
        return index

    def clear(self):
        self.events = []
        self.on_change()

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
        log.info(f"Macro saved to {path}")

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.events = json.load(f)
        log.info(f"Macro loaded from {path} ({len(self.events)} events)")
        self.on_change()


class MacroPlayer:
    def __init__(self, get_events_fn, get_settings_fn, status_cb):
        self.get_events = get_events_fn
        self.get_settings = get_settings_fn
        self.status_cb = status_cb
        self._thread = None
        self._stop_event = threading.Event()
        self.running = False

    def start(self):
        events = self.get_events()
        if self.running or pyautogui is None:
            return
        if not events:
            self.status_cb("ยังไม่มีชุดคำสั่งให้เล่น กรุณาบันทึกหรือสร้างชุดคำสั่งก่อน")
            return
        self._stop_event.clear()
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        log.info("Macro playback started")
        self.status_cb("กำลังเล่นชุดคำสั่ง...")

    def stop(self):
        if not self.running:
            return
        self._stop_event.set()
        self.running = False
        log.info("Macro playback stop requested")
        self.status_cb("เล่นชุดคำสั่ง: หยุดแล้ว")

    def toggle(self):
        self.stop() if self.running else self.start()

    def _run(self):
        settings = self.get_settings()
        loop = settings["loop_macro"]
        repeat_count = settings["macro_repeat_count"]
        kb_controller = keyboard.Controller() if keyboard else None
        runs = 0
        try:
            while not self._stop_event.is_set():
                for ev in self.get_events():
                    if self._stop_event.is_set():
                        break
                    wait_time = max(0.0, ev.get("delay", 0))
                    if self._stop_event.wait(wait_time):
                        break
                    if ev["type"] == "click":
                        pyautogui.click(x=ev["x"], y=ev["y"], button=ev.get("button", "left"))
                    elif ev["type"] == "key" and kb_controller:
                        k = ev["key"]
                        try:
                            if len(k) == 1:
                                kb_controller.press(k)
                                kb_controller.release(k)
                            else:
                                special = getattr(keyboard.Key, k.replace("Key.", ""), None)
                                if special:
                                    kb_controller.press(special)
                                    kb_controller.release(special)
                        except Exception:
                            log.exception("Error sending key event")
                    elif ev["type"] == "wait":
                        pass
                runs += 1
                if not loop and runs >= repeat_count:
                    break
        except Exception:
            log.exception("Error in MacroPlayer loop")
        self.running = False
        log.info(f"Macro playback stopped after {runs} run(s)")
        self.status_cb(f"เล่นชุดคำสั่ง: หยุดแล้ว (เล่นไปทั้งหมด {runs} รอบ)")
