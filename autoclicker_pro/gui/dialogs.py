# -*- coding: utf-8 -*-
"""
gui/dialogs.py
==============
กล่องโต้ตอบสำหรับเพิ่ม/แก้ไขขั้นตอนของชุดคำสั่งทีละรายการ ใช้ภาษาที่เข้าใจง่าย
ไม่ใช้ศัพท์เทคนิค
"""

import tkinter as tk
from tkinter import ttk, messagebox

from .fonts import ui_font

try:
    import pyautogui
except ImportError:
    pyautogui = None

# แปลชื่อปุ่มพิเศษเป็นภาษาไทยให้ผู้ใช้เห็น แต่ค่าที่เก็บจริงยังเป็นชื่อปุ่มมาตรฐาน
SPECIAL_KEY_LABELS = {
    "": "— ไม่เลือก —",
    "space": "เว้นวรรค (Space)",
    "enter": "ตอบตกลง (Enter)",
    "tab": "แท็บ (Tab)",
    "backspace": "ลบถอยหลัง (Backspace)",
    "up": "ลูกศรขึ้น",
    "down": "ลูกศรลง",
    "left": "ลูกศรซ้าย",
    "right": "ลูกศรขวา",
    "shift": "Shift",
    "ctrl": "Ctrl",
    "alt": "Alt",
}
SPECIAL_KEY_VALUES = {v: k for k, v in SPECIAL_KEY_LABELS.items()}


class StepDialog(tk.Toplevel):
    def __init__(self, parent, step_type, existing=None):
        super().__init__(parent)
        self.result = None
        self.step_type = step_type
        titles = {"click": "เพิ่มขั้นตอน: คลิกที่ตำแหน่งนี้",
                  "key": "เพิ่มขั้นตอน: กดปุ่มนี้",
                  "wait": "เพิ่มขั้นตอน: รอสักครู่"}
        self.title(titles[step_type])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(padx=4, pady=4)

        existing = existing or {}
        pad = {"padx": 12, "pady": 8}
        row = 0

        ttk.Label(self, text="รอกี่วินาทีก่อนทำขั้นตอนนี้:", font=ui_font(10)).grid(
            row=row, column=0, sticky="w", **pad)
        self.delay_var = tk.StringVar(value=str(existing.get("delay", 0.5)))
        ttk.Entry(self, textvariable=self.delay_var, width=10, font=ui_font(10)).grid(
            row=row, column=1, **pad)
        row += 1

        if step_type == "click":
            ttk.Label(self, text="ตำแหน่งแนวนอน (X):", font=ui_font(10)).grid(
                row=row, column=0, sticky="w", **pad)
            self.x_var = tk.StringVar(value=str(existing.get("x", 0)))
            ttk.Entry(self, textvariable=self.x_var, width=10, font=ui_font(10)).grid(
                row=row, column=1, **pad)
            row += 1

            ttk.Label(self, text="ตำแหน่งแนวตั้ง (Y):", font=ui_font(10)).grid(
                row=row, column=0, sticky="w", **pad)
            self.y_var = tk.StringVar(value=str(existing.get("y", 0)))
            ttk.Entry(self, textvariable=self.y_var, width=10, font=ui_font(10)).grid(
                row=row, column=1, **pad)
            row += 1

            ttk.Label(self, text="ปุ่มเมาส์:", font=ui_font(10)).grid(row=row, column=0, sticky="w", **pad)
            self.button_var = tk.StringVar(value=existing.get("button", "left"))
            btn_frame = ttk.Frame(self)
            btn_frame.grid(row=row, column=1, sticky="w")
            for text, val in [("ซ้าย", "left"), ("ขวา", "right"), ("กลาง", "middle")]:
                ttk.Radiobutton(btn_frame, text=text, value=val, variable=self.button_var).pack(side="left")
            row += 1

            self.capture_status = tk.StringVar(value="")
            ttk.Button(self, text="📍 จิ้มตำแหน่งจากเมาส์ (นับถอยหลัง 3 วิ)",
                       command=self._start_capture).grid(row=row, column=0, columnspan=2, **pad)
            row += 1
            ttk.Label(self, textvariable=self.capture_status, foreground="gray", font=ui_font(9)).grid(
                row=row, column=0, columnspan=2)
            row += 1

        elif step_type == "key":
            existing_key = existing.get("key", "a")
            existing_is_special = existing_key in SPECIAL_KEY_LABELS and existing_key != ""

            ttk.Label(self, text="พิมพ์ตัวอักษรที่ต้องการกด (เช่น a, 1):", font=ui_font(10)).grid(
                row=row, column=0, sticky="w", **pad)
            self.key_var = tk.StringVar(value="" if existing_is_special else existing_key)
            ttk.Entry(self, textvariable=self.key_var, width=10, font=ui_font(10)).grid(
                row=row, column=1, **pad)
            row += 1

            ttk.Label(self, text="หรือเลือกปุ่มพิเศษ:", font=ui_font(10)).grid(
                row=row, column=0, sticky="w", **pad)
            initial_label = SPECIAL_KEY_LABELS.get(existing_key, SPECIAL_KEY_LABELS[""]) if existing_is_special else SPECIAL_KEY_LABELS[""]
            self.special_display_var = tk.StringVar(value=initial_label)
            ttk.Combobox(self, textvariable=self.special_display_var,
                         values=list(SPECIAL_KEY_LABELS.values()),
                         state="readonly", width=18, font=ui_font(10)).grid(row=row, column=1, **pad)
            row += 1

        ttk.Separator(self).grid(row=row, column=0, columnspan=2, sticky="ew", pady=8)
        row += 1
        btns = ttk.Frame(self)
        btns.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="บันทึก", style="Accent.TButton", command=self._on_save).pack(side="left", padx=6)
        ttk.Button(btns, text="ยกเลิก", command=self.destroy).pack(side="left", padx=6)

    def _start_capture(self):
        def countdown(n):
            if n > 0:
                self.capture_status.set(f"เตรียมตัว... อีก {n} วินาที (ย้ายเมาส์ไปตำแหน่งที่ต้องการไว้ก่อน)")
                self.after(1000, lambda: countdown(n - 1))
            else:
                if pyautogui:
                    x, y = pyautogui.position()
                    self.x_var.set(str(x))
                    self.y_var.set(str(y))
                    self.capture_status.set(f"จิ้มตำแหน่งแล้ว ✓ ({x}, {y})")
        countdown(3)

    def _on_save(self):
        try:
            delay = float(self.delay_var.get())
        except ValueError:
            messagebox.showerror("กรอกไม่ถูกต้อง", "ช่องเวลารอ ต้องเป็นตัวเลขเท่านั้น")
            return

        if self.step_type == "click":
            try:
                x = int(float(self.x_var.get()))
                y = int(float(self.y_var.get()))
            except ValueError:
                messagebox.showerror("กรอกไม่ถูกต้อง", "ตำแหน่ง X และ Y ต้องเป็นตัวเลขเท่านั้น")
                return
            self.result = {"type": "click", "x": x, "y": y, "button": self.button_var.get(), "delay": delay}
        elif self.step_type == "key":
            special_val = SPECIAL_KEY_VALUES.get(self.special_display_var.get(), "")
            key_val = special_val or self.key_var.get().strip()
            if not key_val:
                messagebox.showerror("กรอกไม่ถูกต้อง", "กรุณาระบุปุ่มที่ต้องการกด")
                return
            self.result = {"type": "key", "key": key_val, "delay": delay}
        else:
            self.result = {"type": "wait", "delay": delay}
        self.destroy()


class AboutDialog(tk.Toplevel):
    def __init__(self, parent, version):
        super().__init__(parent)
        self.title("เกี่ยวกับโปรแกรม")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        frame = ttk.Frame(self, padding=24)
        frame.pack()
        ttk.Label(frame, text="⚡ คลิกอัตโนมัติ", font=ui_font(18, "bold")).pack(pady=(0, 4))
        ttk.Label(frame, text=f"เวอร์ชัน {version}", font=ui_font(10)).pack()
        ttk.Label(frame, text="โปรแกรมช่วยคลิกอัตโนมัติ และสร้างชุดคำสั่งอัตโนมัติของคุณเอง",
                  foreground="gray", font=ui_font(10)).pack(pady=(8, 14))
        ttk.Label(frame,
                  text="ปุ่มลัด: ตั้งค่าได้ในหน้า 'ตั้งค่า'\nปุ่ม ESC = หยุดทุกอย่างทันที",
                  justify="left", font=ui_font(10)).pack(pady=(0, 14))
        ttk.Button(frame, text="ปิด", command=self.destroy).pack()
