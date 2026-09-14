# -*- coding: utf-8 -*-
"""
core/windows_target.py
=======================
ทำให้ "คลิกอัตโนมัติ" ทำงานกับโปรแกรมเป้าหมายที่เลือกไว้ได้ โดยไม่ต้องสลับหน้าต่างมาโฟกัส
(ไม่ขโมย focus) ผู้ใช้จึงไปทำงานโปรแกรมอื่นต่อได้ในระหว่างที่คลิกอัตโนมัติทำงานอยู่เบื้องหลัง

วิธีการ: ใช้ Windows API ส่งข้อความคลิกเมาส์ (WM_LBUTTONDOWN/UP ฯลฯ) ตรงไปยังหน้าต่าง
เป้าหมายผ่าน PostMessage แทนการขยับเมาส์จริงบนจอ

*** ข้อจำกัดสำคัญที่ต้องรู้ก่อนใช้ ***
เทคนิคนี้ใช้ได้เฉพาะบน Windows เท่านั้น และได้ผลดีกับโปรแกรม Windows ทั่วไป
(เช่นโปรแกรมออฟฟิศ, เว็บเบราว์เซอร์บางส่วน) แต่ "อาจใช้ไม่ได้" กับ:
- เกมส่วนใหญ่ (โดยเฉพาะเกมที่ใช้ DirectInput/RawInput หรือมีระบบป้องกันการโกง)
- โปรแกรมบางตัวที่ตรวจสอบว่าหน้าต่างต้อง "ใช้งานอยู่จริง" (foreground) ก่อนถึงจะรับคลิก
ถ้าคลิกเบื้องหลังไม่ได้ผลกับโปรแกรมเป้าหมายของคุณ ให้ใช้โหมดคลิกปกติ (ต้องเปิดหน้าต่าง
โปรแกรมนั้นค้างไว้ด้านหน้า) แทน
"""

import sys
import time
import ctypes
from ctypes import wintypes

IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEMOVE = 0x0200
MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002
MK_MBUTTON = 0x0010

BUTTON_MESSAGES = {
    "left": (WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON),
    "right": (WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON),
    "middle": (WM_MBUTTONDOWN, WM_MBUTTONUP, MK_MBUTTON),
}

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def is_windows():
    return IS_WINDOWS


def _get_process_name(pid):
    if not IS_WINDOWS or pid == 0:
        return ""
    try:
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_process:
            return ""
        try:
            buffer = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            ok = kernel32.QueryFullProcessImageNameW(h_process, 0, buffer, ctypes.byref(size))
            if ok:
                full_path = buffer.value
                return full_path.split("\\")[-1]
            return ""
        finally:
            kernel32.CloseHandle(h_process)
    except Exception:
        return ""


def list_target_windows(exclude_title_contains=None):
    """
    คืนลิสต์หน้าต่างที่เปิดอยู่และมองเห็นได้ (มีชื่อ) รูปแบบ
    [{"hwnd": int, "title": str, "process": str}, ...]
    ไม่รวมหน้าต่างของโปรแกรมนี้เอง (กรองด้วย exclude_title_contains)
    """
    if not IS_WINDOWS:
        return []

    results = []
    seen_titles = set()

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value.strip()
        if not title:
            return True
        if exclude_title_contains and exclude_title_contains in title:
            return True
        key = title
        if key in seen_titles:
            return True
        seen_titles.add(key)

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process_name = _get_process_name(pid.value)

        results.append({"hwnd": int(hwnd), "title": title, "process": process_name})
        return True

    user32.EnumWindows(enum_proc, 0)
    return results


def resolve_window(title, process=None):
    """
    หา hwnd ปัจจุบันของหน้าต่างที่ตรงกับชื่อ (และโปรแกรมถ้าระบุ) ที่สุด
    ต้องเรียกใหม่ทุกครั้งก่อนคลิก เพราะ hwnd อาจเปลี่ยนได้ถ้าโปรแกรมเป้าหมายถูกปิดแล้วเปิดใหม่
    """
    if not IS_WINDOWS or not title:
        return None
    candidates = list_target_windows()
    for w in candidates:
        if w["title"] == title and (not process or w["process"] == process):
            return w["hwnd"]
    # หาไม่เจอแบบตรงเป๊ะ ลองแบบคร่าว ๆ (ชื่อหน้าต่างขึ้นต้นเหมือนกัน)
    for w in candidates:
        if w["title"].startswith(title[:20]) and (not process or w["process"] == process):
            return w["hwnd"]
    return None


def screen_to_client(hwnd, screen_x, screen_y):
    """แปลงพิกัดบนจอ ให้เป็นพิกัดสัมพัทธ์กับพื้นที่เนื้อหาของหน้าต่าง (client area)"""
    if not IS_WINDOWS:
        return screen_x, screen_y
    point = wintypes.POINT(int(screen_x), int(screen_y))
    user32.ScreenToClient(hwnd, ctypes.byref(point))
    return point.x, point.y


def is_window_valid(hwnd):
    if not IS_WINDOWS or not hwnd:
        return False
    try:
        return bool(user32.IsWindow(hwnd))
    except Exception:
        return False


def post_click(hwnd, client_x, client_y, button="left", double=False):
    """
    ส่งคลิกเมาส์ตรงไปยังหน้าต่างเป้าหมาย (พิกัดอ้างอิงจากมุมซ้ายบนของพื้นที่เนื้อหาหน้าต่าง)
    โดยไม่ขยับเมาส์จริงบนจอ และไม่ทำให้หน้าต่างเป้าหมายถูกดึงมาอยู่ด้านหน้า
    คืนค่า True หากส่งสำเร็จ (ไม่ได้แปลว่าโปรแกรมเป้าหมายตอบสนองเสมอไป ขึ้นกับตัวโปรแกรมนั้น)
    """
    if not IS_WINDOWS or not is_window_valid(hwnd):
        return False
    down_msg, up_msg, mk_flag = BUTTON_MESSAGES.get(button, BUTTON_MESSAGES["left"])
    lparam = (int(client_y) << 16) | (int(client_x) & 0xFFFF)
    try:
        repeats = 2 if double else 1
        for _ in range(repeats):
            user32.PostMessageW(hwnd, down_msg, mk_flag, lparam)
            user32.PostMessageW(hwnd, up_msg, 0, lparam)
        return True
    except Exception:
        return False


def post_drag(hwnd, x1, y1, x2, y2, button="left", duration=0.3, steps=12):
    """
    ส่งการ "ลากเมาส์" (กดค้าง-ขยับ-ปล่อย) ไปยังหน้าต่างเป้าหมายโดยไม่ขโมยโฟกัส
    พิกัดทั้งหมดอ้างอิงจากพื้นที่เนื้อหาของหน้าต่าง (client area) เช่นเดียวกับ post_click
    """
    if not IS_WINDOWS or not is_window_valid(hwnd):
        return False
    down_msg, up_msg, mk_flag = BUTTON_MESSAGES.get(button, BUTTON_MESSAGES["left"])
    try:
        lparam_start = (int(y1) << 16) | (int(x1) & 0xFFFF)
        user32.PostMessageW(hwnd, down_msg, mk_flag, lparam_start)

        steps = max(2, int(steps))
        step_delay = max(0.01, duration / steps)
        for i in range(1, steps + 1):
            ix = int(x1 + (x2 - x1) * i / steps)
            iy = int(y1 + (y2 - y1) * i / steps)
            lparam = (iy << 16) | (ix & 0xFFFF)
            user32.PostMessageW(hwnd, WM_MOUSEMOVE, mk_flag, lparam)
            time.sleep(step_delay)

        lparam_end = (int(y2) << 16) | (int(x2) & 0xFFFF)
        user32.PostMessageW(hwnd, up_msg, 0, lparam_end)
        return True
    except Exception:
        return False
