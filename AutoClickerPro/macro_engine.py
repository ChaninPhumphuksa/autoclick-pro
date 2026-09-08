"""
macro_engine.py
- ClickerEngine   : ระบบ Auto Click พื้นฐาน (interval, ตำแหน่ง, ปุ่มเมาส์, จำนวนครั้ง)
- MacroRecorder   : บันทึกการกระทำเมาส์ + คีย์บอร์ดจริงของผู้ใช้ พร้อม timestamp
- MacroPlayer     : เล่นย้อนสิ่งที่บันทึกไว้ ปรับความเร็ว/humanizer ได้
"""

import time
import threading
from pynput import mouse, keyboard as pkeyboard
from pynput.mouse import Button

from humanizer import Humanizer


class ClickerEngine:
    """
    การตั้งค่า (settings dict):
      interval_seconds : ระยะเวลาหน่วงระหว่างคลิกแต่ละครั้ง (วินาที)
      button           : "left" | "right" | "middle"
      click_type       : จำนวนคลิกต่อครั้ง (1=single, 2=double, 3=triple)
      position_mode    : "cursor" | "fixed"
      fixed_pos        : (x, y) ใช้เมื่อ position_mode == "fixed"
      repeat_mode      : "until_stopped" | "count"
      repeat_count     : จำนวนครั้งที่จะคลิกเมื่อ repeat_mode == "count"
      humanizer        : dict การตั้งค่า Humanizer
    """

    def __init__(self, settings: dict, on_click=None, on_stop=None):
        self.settings = settings
        self.on_click = on_click
        self.on_stop = on_stop
        self.mouse = mouse.Controller()
        self._stop_event = threading.Event()
        self._thread = None
        self.click_count = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self.click_count = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        s = self.settings
        hum = Humanizer.from_dict(s.get("humanizer"))
        button = {"left": Button.left, "right": Button.right,
                  "middle": Button.middle}.get(s.get("button", "left"), Button.left)
        clicks = int(s.get("click_type", 1))
        interval = float(s.get("interval_seconds", 0.1))
        position_mode = s.get("position_mode", "cursor")
        fixed_pos = s.get("fixed_pos")
        repeat_mode = s.get("repeat_mode", "until_stopped")
        repeat_count = int(s.get("repeat_count", 1))

        while not self._stop_event.is_set():
            if position_mode == "fixed" and fixed_pos:
                cur = self.mouse.position
                jx, jy = hum.jitter_point(*fixed_pos)
                for px, py in hum.movement_path(cur, (jx, jy)):
                    if self._stop_event.is_set():
                        break
                    self.mouse.position = (px, py)
                    time.sleep(0.004)

            if hum.should_misclick():
                mx, my = self.mouse.position
                self.mouse.position = (mx + 3, my + 3)
                self.mouse.click(button, 1)
                time.sleep(0.04)
                self.mouse.position = (mx, my)

            self.mouse.click(button, clicks)
            self.click_count += 1
            if self.on_click:
                self.on_click(self.click_count)

            if repeat_mode == "count" and self.click_count >= repeat_count:
                break

            hum.sleep(interval)

        if self.on_stop:
            self.on_stop(self.click_count)


class MacroRecorder:
    """บันทึกเหตุการณ์เมาส์ + คีย์บอร์ดจริงพร้อม timestamp สัมพัทธ์ (วินาทีจากจุดเริ่ม)"""

    def __init__(self):
        self.events = []
        self._start_time = None
        self._mouse_listener = None
        self._kb_listener = None
        self._recording = False

    def start(self, record_mouse_move=False):
        self.events = []
        self._start_time = time.time()
        self._recording = True

        def t():
            return time.time() - self._start_time

        def on_move(x, y):
            if self._recording and record_mouse_move:
                self.events.append({"t": t(), "type": "move", "x": x, "y": y})

        def on_click(x, y, button, pressed):
            if self._recording:
                self.events.append({
                    "t": t(), "type": "click", "x": x, "y": y,
                    "button": button.name, "pressed": pressed
                })

        def on_scroll(x, y, dx, dy):
            if self._recording:
                self.events.append({"t": t(), "type": "scroll", "x": x, "y": y, "dx": dx, "dy": dy})

        def on_press(key):
            if self._recording:
                self.events.append({"t": t(), "type": "key", "key": _key_to_str(key), "pressed": True})

        def on_release(key):
            if self._recording:
                self.events.append({"t": t(), "type": "key", "key": _key_to_str(key), "pressed": False})

        self._mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        self._kb_listener = pkeyboard.Listener(on_press=on_press, on_release=on_release)
        self._mouse_listener.start()
        self._kb_listener.start()

    def stop(self):
        self._recording = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._kb_listener:
            self._kb_listener.stop()
        return self.events

    def to_script(self, name="Recorded Macro"):
        """แปลง events ที่บันทึกได้ ให้เป็นรูปแบบ script DSL เดียวกับ ScriptEngine (ใช้ wait แทน timestamp)"""
        actions = []
        last_t = 0.0
        for e in self.events:
            gap = e["t"] - last_t
            if gap > 0.005:
                actions.append({"type": "wait", "min": round(gap, 3), "max": round(gap, 3)})
            if e["type"] == "click" and e["pressed"]:
                actions.append({"type": "click", "button": e["button"], "x": e["x"], "y": e["y"], "clicks": 1})
            elif e["type"] == "move":
                actions.append({"type": "move", "x": e["x"], "y": e["y"]})
            elif e["type"] == "scroll":
                actions.append({"type": "scroll", "dx": e["dx"], "dy": e["dy"]})
            elif e["type"] == "key" and e["pressed"]:
                actions.append({"type": "key", "key": e["key"], "action": "tap"})
            last_t = e["t"]
        return {
            "name": name,
            "hotkey": None,
            "repeat": 1,
            "humanizer": Humanizer(enabled=True, delay_variance=0.15, position_jitter=2).to_dict(),
            "actions": actions,
        }


def _key_to_str(key):
    try:
        return key.char
    except AttributeError:
        return key.name
