# -*- coding: utf-8 -*-
"""
core/notify.py
==============
เล่นเสียงแจ้งเตือนสั้น ๆ เมื่อคลิกอัตโนมัติ/ชุดคำสั่งทำงานจน "เสร็จตามที่ตั้งไว้" เอง
(ไม่เล่นตอนผู้ใช้กดหยุดเอง) ทำงานได้ทั้ง Windows/macOS/Linux แบบไม่ต้องติดตั้งไลบรารีเพิ่ม
"""

import sys


def play_completion_sound():
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif sys.platform == "darwin":
            import os
            os.system("afplay /System/Library/Sounds/Glass.aiff >/dev/null 2>&1 &")
        else:
            # เตือนด้วยเสียง bell ของเทอร์มินัล/ระบบเป็นทางเลือกสุดท้ายที่ไม่ต้องพึ่งไลบรารีเพิ่ม
            print("\a", end="", flush=True)
    except Exception:
        pass
