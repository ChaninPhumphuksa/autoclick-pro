"""
script_engine.py
Custom Script Engine - ให้ผู้ใช้เขียนสคริปต์มาโครเองแบบละเอียด (JSON DSL)
รองรับ: click, move, key press/release, wait (random range), type_text,
        loop (จำกัดจำนวน หรือ infinite), if_running (เงื่อนไขหยุด)

ตัวอย่างสคริปต์ 1 action:
{
  "type": "click", "button": "left", "x": 500, "y": 500, "clicks": 1
}

โครงสร้างสคริปต์ทั้งไฟล์:
{
  "name": "My Script",
  "hotkey": "f6",
  "repeat": 0,              # 0 = วนไม่จำกัด, N = วน N รอบ
  "humanizer": {...},
  "actions": [ ... ]
}
"""

import time
import threading
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyController, Key

from humanizer import Humanizer

_MOUSE_BUTTONS = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}

_SPECIAL_KEYS = {k.name: k for k in Key}


def _resolve_key(name: str):
    if name is None:
        return None
    if len(name) == 1:
        return name
    return _SPECIAL_KEYS.get(name.lower(), name)


class ScriptEngine:
    """
    รันสคริปต์ JSON DSL แบบ stack-based เพื่อรองรับ loop ซ้อนกันได้
    เรียกใช้ผ่าน .run(script_dict, stop_event, on_step=None)
    """

    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyController()

    def validate(self, script: dict):
        """ตรวจสอบโครงสร้างสคริปต์คร่าว ๆ ก่อนรัน คืน (ok, error_message)"""
        if not isinstance(script, dict):
            return False, "สคริปต์ต้องเป็น JSON object"
        actions = script.get("actions")
        if not isinstance(actions, list) or len(actions) == 0:
            return False, "ต้องมี 'actions' เป็น list และมีอย่างน้อย 1 คำสั่ง"

        depth = 0
        for i, act in enumerate(actions):
            if "type" not in act:
                return False, f"action ลำดับที่ {i} ไม่มีฟิลด์ 'type'"
            t = act["type"]
            if t == "loop_start":
                depth += 1
            elif t == "loop_end":
                depth -= 1
                if depth < 0:
                    return False, f"action ลำดับที่ {i}: loop_end ไม่มี loop_start คู่กัน"
            elif t not in (
                "click", "move", "key", "wait", "type_text", "scroll",
            ):
                return False, f"action ลำดับที่ {i}: type '{t}' ไม่รู้จัก"
        if depth != 0:
            return False, "จำนวน loop_start กับ loop_end ไม่เท่ากัน"
        return True, ""

    def _do_click(self, act, hum: Humanizer):
        x, y = act.get("x"), act.get("y")
        if x is not None and y is not None:
            cur = self.mouse.position
            jx, jy = hum.jitter_point(x, y)
            for px, py in hum.movement_path(cur, (jx, jy)):
                self.mouse.position = (px, py)
                time.sleep(0.004)
        button = _MOUSE_BUTTONS.get(act.get("button", "left"), Button.left)
        clicks = int(act.get("clicks", 1))
        if hum.should_misclick():
            mx, my = self.mouse.position
            self.mouse.position = (mx + 4, my + 4)
            self.mouse.click(button, 1)
            time.sleep(0.05)
            self.mouse.position = (mx, my)
        self.mouse.click(button, clicks)

    def _do_move(self, act, hum: Humanizer):
        x, y = act.get("x", 0), act.get("y", 0)
        cur = self.mouse.position
        jx, jy = hum.jitter_point(x, y)
        for px, py in hum.movement_path(cur, (jx, jy)):
            self.mouse.position = (px, py)
            time.sleep(0.004)

    def _do_key(self, act):
        key = _resolve_key(act.get("key", ""))
        action = act.get("action", "tap")
        if action == "press":
            self.keyboard.press(key)
        elif action == "release":
            self.keyboard.release(key)
        else:
            self.keyboard.press(key)
            self.keyboard.release(key)

    def _do_wait(self, act, hum: Humanizer):
        lo = float(act.get("min", act.get("seconds", 0.1)))
        hi = float(act.get("max", lo))
        if hi < lo:
            hi = lo
        import random
        base = random.uniform(lo, hi)
        hum.sleep(base)

    def _do_type_text(self, act):
        text = act.get("text", "")
        self.keyboard.type(text)

    def _do_scroll(self, act):
        dx = int(act.get("dx", 0))
        dy = int(act.get("dy", 0))
        self.mouse.scroll(dx, dy)

    def run(self, script: dict, stop_event: threading.Event, on_step=None, speed=1.0):
        """
        รันสคริปต์จนกว่า stop_event จะถูก set หรือครบจำนวนรอบที่กำหนด (repeat)
        on_step(index, action) จะถูกเรียกทุกครั้งก่อนรัน action นั้น ๆ (ใช้ทำ UI highlight)
        speed: ตัวคูณความเร็ว (>1 = เร็วขึ้น, <1 = ช้าลง) มีผลกับ wait เท่านั้น
        """
        ok, err = self.validate(script)
        if not ok:
            raise ValueError(err)

        hum = Humanizer.from_dict(script.get("humanizer"))
        actions = script["actions"]
        repeat = int(script.get("repeat", 0))

        round_count = 0
        while not stop_event.is_set():
            i = 0
            loop_stack = []  # (loop_start_index, remaining_count or None=infinite)
            while i < len(actions):
                if stop_event.is_set():
                    return
                act = actions[i]
                t = act["type"]
                if on_step:
                    on_step(i, act)

                if t == "loop_start":
                    count = act.get("count")  # None = infinite
                    loop_stack.append([i, count])
                elif t == "loop_end":
                    if loop_stack:
                        start_i, count = loop_stack[-1]
                        if count is None:
                            i = start_i
                            continue
                        else:
                            count -= 1
                            if count > 0:
                                loop_stack[-1][1] = count
                                i = start_i
                                continue
                            else:
                                loop_stack.pop()
                else:
                    if t == "click":
                        self._do_click(act, hum)
                    elif t == "move":
                        self._do_move(act, hum)
                    elif t == "key":
                        self._do_key(act)
                    elif t == "wait":
                        act2 = dict(act)
                        if speed and speed != 1.0:
                            act2["min"] = float(act2.get("min", act2.get("seconds", 0.1))) / speed
                            act2["max"] = float(act2.get("max", act2.get("min"))) / speed
                        self._do_wait(act2, hum)
                    elif t == "type_text":
                        self._do_type_text(act)
                    elif t == "scroll":
                        self._do_scroll(act)
                i += 1

            round_count += 1
            if repeat and round_count >= repeat:
                return
