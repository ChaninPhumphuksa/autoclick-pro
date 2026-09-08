# -*- coding: utf-8 -*-
"""
gui/theme.py
============
ทำให้หน้าตาโปรแกรมดูทันสมัยแบบมืออาชีพ ใช้ธีม Sun Valley (sv_ttk) ถ้าติดตั้งไว้
(pip install sv-ttk) มิฉะนั้น fallback ไปใช้ ttk 'clam' พร้อมปรับสีเอง ให้ยังดูดีอยู่
"""

from tkinter import ttk

try:
    import sv_ttk
except ImportError:
    sv_ttk = None

ACCENT = "#4F46E5"      # indigo-600 — ใช้เป็นสีหลักของแบรนด์ (ตรงกับไอคอน)
ACCENT_DARK = "#4338CA"
DANGER = "#DC2626"       # แดง สำหรับปุ่มหยุดฉุกเฉิน
DANGER_DARK = "#B91C1C"
SUCCESS = "#16A34A"


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
        style.configure(".", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("TButton", padding=6)
        style.configure("TNotebook.Tab", padding=(14, 8))

    # ปุ่มเน้นสี (ใช้ได้ทั้งสองธีม เพราะกำหนดสีตรง ๆ)
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
    style.configure("Danger.TButton", font=("Segoe UI", 12, "bold"))
    try:
        style.map("Danger.TButton",
                  background=[("!disabled", DANGER), ("active", DANGER_DARK)],
                  foreground=[("!disabled", "#FFFFFF")])
    except Exception:
        pass

    return used_sv_ttk
