# -*- coding: utf-8 -*-
"""
gui/theme.py
============
ทำให้หน้าตาโปรแกรมดูทันสมัย เข้าใจง่าย ใช้ธีม Sun Valley (sv_ttk) ถ้าติดตั้งไว้
(pip install sv-ttk) มิฉะนั้น fallback ไปใช้ ttk 'clam' พร้อมปรับสีเอง ให้ยังดูดีอยู่
ใช้ฟอนต์ Prompt เป็นหลัก (ดู gui/fonts.py)
"""

from tkinter import ttk

from .fonts import ui_font, apply_default_font

try:
    import sv_ttk
except ImportError:
    sv_ttk = None

ACCENT = "#4F46E5"       # สีหลักของแบรนด์ (โทนม่วง-น้ำเงิน ตรงกับไอคอน)
ACCENT_DARK = "#4338CA"
DANGER = "#DC2626"        # สีแดง สำหรับปุ่มหยุดฉุกเฉิน
DANGER_DARK = "#B91C1C"
SUCCESS = "#16A34A"
SUCCESS_DARK = "#15803D"
NEUTRAL = "#6B7280"

# สีประจำแต่ละแท็บ ให้แต่ละหน้าดูมีเอกลักษณ์ของตัวเอง
TAB_AUTOCLICK = "#3B82F6"   # ฟ้า
TAB_AUTOCLICK_DARK = "#2563EB"
TAB_MACRO = "#8B5CF6"       # ม่วง
TAB_MACRO_DARK = "#7C3AED"
TAB_SETTINGS = "#14B8A6"    # เขียวอมฟ้า
TAB_SETTINGS_DARK = "#0F9488"

RAINBOW_STRIPE = ["#3B82F6", "#8B5CF6", "#EC4899", "#F59E0B", "#14B8A6", "#22C55E"]


def apply_theme(root, mode="dark"):
    """ใช้ธีมทันสมัยกับหน้าต่างหลัก คืนค่า True หากใช้ sv_ttk ได้จริง"""
    used_sv_ttk = False
    if sv_ttk is not None:
        try:
            sv_ttk.set_theme(mode)
            used_sv_ttk = True
        except Exception:
            used_sv_ttk = False

    style = ttk.Style()
    if not used_sv_ttk:
        try:
            style.theme_use("clam")
        except Exception:
            pass
        bg = "#1E1E2E" if mode == "dark" else "#F5F5F7"
        fg = "#EAEAEA" if mode == "dark" else "#1A1A1A"
        root.configure(bg=bg)
        style.configure(".", background=bg, foreground=fg)
        style.configure("TButton", padding=8)
        style.configure("TNotebook.Tab", padding=(16, 10))

    # ตั้งฟอนต์ Prompt (หรือฟอนต์สำรองที่อ่านง่าย) ให้ทั้งโปรแกรม — ทำหลังตั้งธีมเสมอ
    # เพื่อให้ฟอนต์ที่เราต้องการมีผลเหนือกว่าฟอนต์ที่มากับธีม
    apply_default_font(root, size=11)

    # ปุ่มเน้นสี ขนาดใหญ่ขึ้น กดง่าย เห็นชัด
    style.configure("Accent.TButton", font=ui_font(11, "bold"), padding=10)
    style.configure("Danger.TButton", font=ui_font(12, "bold"), padding=10)
    style.configure("TNotebook.Tab", font=ui_font(11))
    try:
        style.map("Danger.TButton",
                  background=[("!disabled", DANGER), ("active", DANGER_DARK)],
                  foreground=[("!disabled", "#FFFFFF")])
    except Exception:
        pass

    # สไตล์แถบสถานะด้านล่าง สลับสีตามสถานะการทำงาน (เขียว=กำลังทำงาน, เทา=ว่าง)
    style.configure("StatusIdle.TLabel", background=NEUTRAL, foreground="#FFFFFF", padding=(10, 4))
    style.configure("StatusRunning.TLabel", background=SUCCESS, foreground="#FFFFFF", padding=(10, 4))

    return used_sv_ttk
