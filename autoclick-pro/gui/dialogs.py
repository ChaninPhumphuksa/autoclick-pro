# -*- coding: utf-8 -*-
"""
gui/dialogs.py
==============
กล่องโต้ตอบสำหรับเพิ่ม/แก้ไขขั้นตอนมาโครทีละรายการ (custom macro step editor)
"""

import tkinter as tk
from tkinter import ttk, messagebox

try:
    import pyautogui
except ImportError:
    pyautogui = None


class StepDialog(tk.Toplevel):
    def __init__(self, parent, step_type, existing=None):
        super().__init__(parent)
        self.result = None
        self.step_type = step_type
        titles = {"click": "ขั้นตอน: คลิกเมาส์", "key": "ขั้นตอน: กดปุ่ม", "wait": "ขั้นตอน: หน่วงเวลา"}
        self.title(titles[step_type])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        existing = existing or {}
        pad = {"padx": 10, "pady": 6}
        row = 0

        ttk.Label(self, text="ดีเลย์ก่อนขั้นตอนนี้ (วินาที):").grid(row=row, column=0, sticky="w", **pad)
        self.delay_var = tk.StringVar(value=str(existing.get("delay", 0.5)))
        ttk.Entry(self, textvariable=self.delay_var, width=10).grid(row=row, column=1, **pad)
        row += 1

        if step_type == "click":
            ttk.Label(self, text="ตำแหน่ง X:").grid(row=row, column=0, sticky="w", **pad)
            self.x_var = tk.StringVar(value=str(existing.get("x", 0)))
            ttk.Entry(self, textvariable=self.x_var, width=10).grid(row=row, column=1, **pad)
            row += 1

            ttk.Label(self, text="ตำแหน่ง Y:").grid(row=row, column=0, sticky="w", **pad)
            self.y_var = tk.StringVar(value=str(existing.get("y", 0)))
            ttk.Entry(self, textvariable=self.y_var, width=10).grid(row=row, column=1, **pad)
            row += 1

            ttk.Label(self, text="ปุ่มเมาส์:").grid(row=row, column=0, sticky="w", **pad)
            self.button_var = tk.StringVar(value=existing.get("button", "left"))
            btn_frame = ttk.Frame(self)
            btn_frame.grid(row=row, column=1, sticky="w")
            for text, val in [("ซ้าย", "left"), ("ขวา", "right"), ("กลาง", "middle")]:
                ttk.Radiobutton(btn_frame, text=text, value=val, variable=self.button_var).pack(side="left")
            row += 1

            self.capture_status = tk.StringVar(value="")
            ttk.Button(self, text="จับตำแหน่งเมาส์ปัจจุบัน (นับถอยหลัง 3 วิ)",
                       command=self._start_capture).grid(row=row, column=0, columnspan=2, **pad)
            row += 1
            ttk.Label(self, textvariable=self.capture_status, foreground="gray").grid(
                row=row, column=0, columnspan=2)
            row += 1

        elif step_type == "key":
            ttk.Label(self, text="ปุ่ม (พิมพ์ตัวอักษรเดียว เช่น a, 1)").grid(row=row, column=0, sticky="w", **pad)
            self.key_var = tk.StringVar(value=existing.get("key", "a"))
            ttk.Entry(self, textvariable=self.key_var, width=10).grid(row=row, column=1, **pad)
            row += 1

            ttk.Label(self, text="หรือเลือกปุ่มพิเศษ:").grid(row=row, column=0, sticky="w", **pad)
            special_keys = ["", "space", "enter", "tab", "backspace",
                            "up", "down", "left", "right", "shift", "ctrl", "alt"]
            self.special_var = tk.StringVar(value="")
            ttk.Combobox(self, textvariable=self.special_var, values=special_keys,
                         state="readonly", width=10).grid(row=row, column=1, **pad)
            row += 1

        ttk.Separator(self).grid(row=row, column=0, columnspan=2, sticky="ew", pady=6)
        row += 1
        btns = ttk.Frame(self)
        btns.grid(row=row, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="บันทึก", style="Accent.TButton", command=self._on_save).pack(side="left", padx=6)
        ttk.Button(btns, text="ยกเลิก", command=self.destroy).pack(side="left", padx=6)

    def _start_capture(self):
        def countdown(n):
            if n > 0:
                self.capture_status.set(f"เตรียมตัว... จับตำแหน่งใน {n} วินาที (ย้ายเมาส์ไปตำแหน่งที่ต้องการ)")
                self.after(1000, lambda: countdown(n - 1))
            else:
                if pyautogui:
                    x, y = pyautogui.position()
                    self.x_var.set(str(x))
                    self.y_var.set(str(y))
                    self.capture_status.set(f"จับตำแหน่งแล้ว: ({x}, {y})")
        countdown(3)

    def _on_save(self):
        try:
            delay = float(self.delay_var.get())
        except ValueError:
            messagebox.showerror("ข้อมูลไม่ถูกต้อง", "ดีเลย์ต้องเป็นตัวเลข")
            return

        if self.step_type == "click":
            try:
                x = int(float(self.x_var.get()))
                y = int(float(self.y_var.get()))
            except ValueError:
                messagebox.showerror("ข้อมูลไม่ถูกต้อง", "ตำแหน่ง X, Y ต้องเป็นตัวเลข")
                return
            self.result = {"type": "click", "x": x, "y": y, "button": self.button_var.get(), "delay": delay}
        elif self.step_type == "key":
            key_val = self.special_var.get().strip() or self.key_var.get().strip()
            if not key_val:
                messagebox.showerror("ข้อมูลไม่ถูกต้อง", "กรุณาระบุปุ่ม")
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
        frame = ttk.Frame(self, padding=20)
        frame.pack()
        ttk.Label(frame, text="Auto Clicker Pro", font=("Segoe UI", 16, "bold")).pack(pady=(0, 4))
        ttk.Label(frame, text=f"เวอร์ชัน {version}").pack()
        ttk.Label(frame, text="โปรแกรม Auto Click และเครื่องมือมาโครแบบกำหนดเอง",
                  foreground="gray").pack(pady=(6, 12))
        ttk.Label(frame, text="Hotkeys: ตั้งค่าได้ในแท็บ 'ตั้งค่า'\nESC = หยุดทั้งหมดทันที (ตายตัว)",
                  justify="left").pack(pady=(0, 12))
        ttk.Button(frame, text="ปิด", command=self.destroy).pack()
