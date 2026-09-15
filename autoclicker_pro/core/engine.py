# -*- coding: utf-8 -*-
"""
core/engine.py
==============
เอนจินหลักของโปรแกรม: AutoClicker, MacroRecorder (บันทึก+แก้ไขมาโครเอง), MacroPlayer, MultiMacroRunner
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
    import pydirectinput
except ImportError:
    pydirectinput = None

try:
    from pynput import mouse, keyboard
except ImportError:
    mouse = None
    keyboard = None

from .logger import get_logger
from . import windows_target

log = get_logger()

if pyautogui:
    pyautogui.FAILSAFE = False
if pydirectinput:
    try:
        pydirectinput.FAILSAFE = False
    except Exception:
        pass


def is_directinput_available():
    return pydirectinput is not None


def _get_backend(input_backend):
    """เลือกโมดูลที่จะใช้คลิก/ลาก: 'directinput' (เข้ากันได้กับเกม) หรือ pyautogui ปกติ"""
    if input_backend == "directinput" and pydirectinput is not None:
        return pydirectinput
    return pyautogui

MODIFIER_KEY_MAP = {
    "ctrl": None,   # เติมค่าจริงด้านล่างหลัง import keyboard สำเร็จ (แพลตฟอร์มขึ้นกับ pynput)
    "alt": None,
    "shift": None,
}
if keyboard:
    MODIFIER_KEY_MAP = {
        "ctrl": keyboard.Key.ctrl,
        "alt": keyboard.Key.alt,
        "shift": keyboard.Key.shift,
    }


class AutoClicker:
    def __init__(self, get_settings_fn, status_cb, on_click_cb=None, on_finished_cb=None):
        self.get_settings = get_settings_fn
        self.status_cb = status_cb
        self.on_click_cb = on_click_cb or (lambda: None)
        self.on_finished_cb = on_finished_cb or (lambda: None)
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

        start_delay = max(0.0, s.get("start_delay_seconds", 0))
        if start_delay > 0:
            self.status_cb(f"คลิกอัตโนมัติ: จะเริ่มในอีก {start_delay:.0f} วินาที...")
            if self._stop_event.wait(start_delay):
                self.running = False
                self.status_cb("คลิกอัตโนมัติ: ยกเลิกก่อนถึงเวลาเริ่ม")
                return

        self.status_cb("คลิกอัตโนมัติ: กำลังทำงาน...")

        base_interval = max(0.001, s["interval_seconds"])
        jitter = max(0.0, s.get("jitter_seconds", 0.0))
        pos_jitter = max(0, int(s.get("position_jitter_pixels", 0)))
        button = s["button"]
        double = s["double_click"]
        limited = s["limited_count"]
        max_clicks = s["click_count"]
        fixed = s.get("fixed_position", False)
        fx, fy = s.get("fixed_x"), s.get("fixed_y")
        backend = _get_backend(s.get("input_backend", "pyautogui"))

        background_mode = s.get("background_mode", False) and windows_target.is_windows()
        target_title = s.get("background_target_title")
        target_process = s.get("background_target_process")
        hwnd = None
        if background_mode:
            hwnd = windows_target.resolve_window(target_title, target_process)
            if hwnd is None:
                self.running = False
                self.status_cb(f"หาโปรแกรมเป้าหมาย '{target_title}' ไม่เจอ กรุณาเปิดโปรแกรมนั้นไว้ก่อนแล้วลองใหม่")
                return

        count = 0
        finished_naturally = False
        try:
            while not self._stop_event.is_set():
                click_x, click_y = fx, fy
                if pos_jitter and click_x is not None and click_y is not None:
                    click_x += random.randint(-pos_jitter, pos_jitter)
                    click_y += random.randint(-pos_jitter, pos_jitter)

                if background_mode:
                    if not windows_target.is_window_valid(hwnd):
                        hwnd = windows_target.resolve_window(target_title, target_process)
                        if hwnd is None:
                            self.status_cb(f"โปรแกรมเป้าหมาย '{target_title}' ถูกปิดไปแล้ว หยุดคลิกอัตโนมัติ")
                            break
                    windows_target.post_click(hwnd, click_x or 0, click_y or 0, button=button, double=double)
                else:
                    kwargs = {"button": button}
                    if double:
                        kwargs["clicks"] = 2
                        kwargs["interval"] = 0.05
                    if fixed and click_x is not None and click_y is not None:
                        kwargs["x"] = click_x
                        kwargs["y"] = click_y
                    backend.click(**kwargs)
                count += 1
                self.on_click_cb()
                if limited and count >= max_clicks:
                    finished_naturally = True
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
        if finished_naturally:
            self.on_finished_cb()


class MacroRecorder:
    """
    บันทึกเหตุการณ์เมาส์/คีย์บอร์ดจากการอัดจริง และรองรับแก้ไข/เพิ่ม/ลบ/เรียงลำดับ/ทำซ้ำเอง

    event: {"type": "click", "x", "y", "button", "delay"}
           {"type": "drag", "x1", "y1", "x2", "y2", "button", "duration", "delay"}
           {"type": "key", "key", "modifiers": ["ctrl", ...], "delay"}
           {"type": "type", "text", "delay"}
           {"type": "wait", "delay"}
           {"type": "wait_pixel", "x", "y", "color", "match", "timeout", "delay"}
           {"type": "loop_start", "repeat", "delay"}
           {"type": "loop_end", "delay"}
    """

    DRAG_DISTANCE_THRESHOLD = 5  # ลากเมาส์ไกลกว่ากี่พิกเซลถึงจะนับเป็น "ลาก" แทน "คลิก"
    MODIFIER_KEYS = {"ctrl", "alt", "shift"}

    def __init__(self, status_cb, on_change=None):
        self.status_cb = status_cb
        self.on_change = on_change or (lambda: None)
        self.events = []
        self._recording = False
        self._last_time = None
        self._pending_press = None
        self._held_modifiers = set()
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
        self._pending_press = None
        self._held_modifiers = set()
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
        self._mouse_listener.start()
        self._keyboard_listener.start()
        log.info("Macro recording started")
        self.status_cb("กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว 0 ขั้นตอน)")
        self.on_change()

    def stop(self):
        if not self._recording:
            return
        self._recording = False
        self._pending_press = None
        self._held_modifiers = set()
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
        if not self._recording:
            return
        btn_name = str(button).replace("Button.", "")

        if pressed:
            self._pending_press = {"x": x, "y": y, "time": time.time(), "button": btn_name}
            return

        press = self._pending_press
        self._pending_press = None
        if press is None or press["button"] != btn_name:
            return

        release_time = time.time()
        delay = max(0.0, press["time"] - self._last_time)
        self._last_time = release_time

        dx = x - press["x"]
        dy = y - press["y"]
        distance = (dx * dx + dy * dy) ** 0.5

        if distance > self.DRAG_DISTANCE_THRESHOLD:
            duration = max(0.05, round(release_time - press["time"], 2))
            self.events.append({
                "type": "drag", "x1": press["x"], "y1": press["y"],
                "x2": x, "y2": y, "button": btn_name,
                "duration": duration, "delay": delay,
            })
        else:
            self.events.append({
                "type": "click", "x": press["x"], "y": press["y"],
                "button": btn_name, "delay": delay,
            })

        self.status_cb(f"กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว {len(self.events)} ขั้นตอน)")
        self.on_change()

    def _key_name(self, key):
        if key == keyboard.Key.esc:
            return None
        try:
            return key.char
        except AttributeError:
            return str(key).replace("Key.", "")

    def _on_key_press(self, key):
        if not self._recording:
            return
        name = self._key_name(key)
        if name is None:
            return
        if name in self.MODIFIER_KEYS:
            self._held_modifiers.add(name)
            return
        delay = self._record_delay()
        self.events.append({
            "type": "key", "key": name,
            "modifiers": sorted(self._held_modifiers),
            "delay": delay,
        })
        self.status_cb(f"กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว {len(self.events)} ขั้นตอน)")
        self.on_change()

    def _on_key_release(self, key):
        if not self._recording:
            return
        name = self._key_name(key)
        if name in self.MODIFIER_KEYS:
            self._held_modifiers.discard(name)

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

    def duplicate_step(self, index):
        if 0 <= index < len(self.events):
            self.events.insert(index + 1, dict(self.events[index]))
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
    def __init__(self, get_events_fn, get_settings_fn, status_cb, on_click_cb=None, on_finished_cb=None):
        self.get_events = get_events_fn
        self.get_settings = get_settings_fn
        self.status_cb = status_cb
        self.on_click_cb = on_click_cb or (lambda: None)
        self.on_finished_cb = on_finished_cb or (lambda: None)
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

    def _press_key_by_name(self, kb_controller, name):
        try:
            if len(name) == 1:
                kb_controller.press(name)
                kb_controller.release(name)
            else:
                special = getattr(keyboard.Key, name, None)
                if special:
                    kb_controller.press(special)
                    kb_controller.release(special)
        except Exception:
            log.exception("Error sending key event")

    def _execute_event(self, ev, hwnd, background_mode, kb_controller, backend):
        """รันหนึ่งขั้นตอน (ไม่รวม loop_start/loop_end ซึ่งจัดการที่ตัว interpreter หลัก)"""
        etype = ev["type"]
        if etype == "click":
            if background_mode:
                windows_target.post_click(hwnd, ev["x"], ev["y"], button=ev.get("button", "left"))
            else:
                backend.click(x=ev["x"], y=ev["y"], button=ev.get("button", "left"))
            self.on_click_cb()

        elif etype == "drag":
            if background_mode:
                windows_target.post_drag(hwnd, ev["x1"], ev["y1"], ev["x2"], ev["y2"],
                                          button=ev.get("button", "left"),
                                          duration=max(0.05, ev.get("duration", 0.3)))
            else:
                backend.moveTo(ev["x1"], ev["y1"])
                backend.dragTo(ev["x2"], ev["y2"],
                                duration=max(0.05, ev.get("duration", 0.3)),
                                button=ev.get("button", "left"))
            self.on_click_cb()

        elif etype == "key" and kb_controller:
            # การกดปุ่มคีย์บอร์ดยังต้องให้หน้าต่างเป้าหมายอยู่ด้านหน้าเท่านั้น (ไม่รองรับโหมดเบื้องหลัง)
            modifiers = ev.get("modifiers") or []
            mod_keys = [MODIFIER_KEY_MAP[m] for m in modifiers if m in MODIFIER_KEY_MAP and MODIFIER_KEY_MAP[m]]
            try:
                for mk in mod_keys:
                    kb_controller.press(mk)
                self._press_key_by_name(kb_controller, ev["key"])
            finally:
                for mk in reversed(mod_keys):
                    try:
                        kb_controller.release(mk)
                    except Exception:
                        pass

        elif etype == "type" and kb_controller:
            text = ev.get("text", "")
            try:
                kb_controller.type(text)
            except Exception:
                log.exception("Error typing text")

        elif etype == "wait_pixel":
            if pyautogui is None:
                return
            x, y = ev.get("x", 0), ev.get("y", 0)
            target_color = tuple(ev.get("color", (0, 0, 0)))
            want_match = ev.get("match", True)
            timeout = max(0.1, ev.get("timeout", 5))
            deadline = time.time() + timeout
            while time.time() < deadline and not self._stop_event.is_set():
                try:
                    current = pyautogui.pixel(x, y)
                except Exception:
                    break
                is_match = (current == target_color)
                if is_match == want_match:
                    break
                self._stop_event.wait(0.2)

        elif etype == "wait":
            pass

    def _run(self):
        settings = self.get_settings()
        loop = settings["loop_macro"]
        repeat_count = settings["macro_repeat_count"]
        kb_controller = keyboard.Controller() if keyboard else None
        backend = _get_backend(settings.get("input_backend", "pyautogui"))

        background_mode = settings.get("background_mode", False) and windows_target.is_windows()
        target_title = settings.get("background_target_title")
        target_process = settings.get("background_target_process")
        hwnd = None
        if background_mode:
            hwnd = windows_target.resolve_window(target_title, target_process)
            if hwnd is None:
                self.running = False
                self.status_cb(f"หาโปรแกรมเป้าหมาย '{target_title}' ไม่เจอ กรุณาเปิดโปรแกรมนั้นไว้ก่อนแล้วลองใหม่")
                return

        runs = 0
        finished_naturally = False
        try:
            while not self._stop_event.is_set():
                if background_mode and not windows_target.is_window_valid(hwnd):
                    hwnd = windows_target.resolve_window(target_title, target_process)
                    if hwnd is None:
                        self.status_cb(f"โปรแกรมเป้าหมาย '{target_title}' ถูกปิดไปแล้ว หยุดเล่นชุดคำสั่ง")
                        break

                events = self.get_events()
                i = 0
                loop_stack = []  # แต่ละชั้น: [start_index, เหลืออีกกี่รอบ]
                while i < len(events) and not self._stop_event.is_set():
                    ev = events[i]

                    if ev["type"] == "loop_start":
                        loop_stack.append([i, max(1, int(ev.get("repeat", 1)))])
                        i += 1
                        continue
                    if ev["type"] == "loop_end":
                        if loop_stack:
                            start_idx, remaining = loop_stack[-1]
                            remaining -= 1
                            if remaining > 0:
                                loop_stack[-1][1] = remaining
                                i = start_idx + 1
                                continue
                            else:
                                loop_stack.pop()
                        i += 1
                        continue

                    wait_time = max(0.0, ev.get("delay", 0))
                    if self._stop_event.wait(wait_time):
                        break
                    self._execute_event(ev, hwnd, background_mode, kb_controller, backend)
                    i += 1

                runs += 1
                if not loop and runs >= repeat_count:
                    finished_naturally = True
                    break
        except Exception:
            log.exception("Error in MacroPlayer loop")
        self.running = False
        log.info(f"Macro playback stopped after {runs} run(s)")
        self.status_cb(f"เล่นชุดคำสั่ง: หยุดแล้ว (เล่นไปทั้งหมด {runs} รอบ)")
        if finished_naturally:
            self.on_finished_cb()


def load_macro_file(path):
    """โหลดขั้นตอนชุดคำสั่งจากไฟล์ .json ตรง ๆ โดยไม่ยุ่งกับ MacroRecorder (ใช้เล่นแบบขนานได้)"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class MultiMacroRunner:
    """
    ตัวจัดการเล่นชุดคำสั่งที่บันทึกไว้ "หลายชุดพร้อมกัน" โดยแต่ละชุดมี MacroPlayer อิสระของตัวเอง
    ทำงานคู่ขนานกันในเธรดของตัวเอง แยกต่างหากจาก MacroPlayer หลักที่ใช้กับชุดคำสั่งที่กำลังแก้ไขอยู่
    """

    def __init__(self, status_cb, on_click_cb=None):
        self.status_cb = status_cb
        self.on_click_cb = on_click_cb or (lambda: None)
        self._players = {}  # ชื่อชุดคำสั่ง -> MacroPlayer

    def running_names(self):
        return [name for name, p in self._players.items() if p.running]

    def is_running(self, name):
        p = self._players.get(name)
        return bool(p and p.running)

    def start(self, name, events, get_settings_fn):
        if self.is_running(name) or not events:
            return
        def cb(msg):
            self.status_cb(f"[{name}] {msg}")
        player = MacroPlayer(lambda: events, get_settings_fn, cb, on_click_cb=self.on_click_cb)
        self._players[name] = player
        player.start()

    def stop(self, name):
        p = self._players.get(name)
        if p:
            p.stop()

    def stop_all(self):
        for p in self._players.values():
            p.stop()
