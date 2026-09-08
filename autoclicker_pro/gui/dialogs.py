# -*- coding: utf-8 -*-
"""
gui/dialogs.py
==============
กล่องโต้ตอบสำหรับเพิ่ม/แก้ไขขั้นตอนของชุดคำสั่งทีละรายการ ใช้ภาษาที่เข้าใจง่าย
ไม่ใช้ศัพท์เทคนิค
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from .fonts import ui_font
from core.positions import load_positions, add_or_update_position, delete_position

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_keyboard = None

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
            capture_row = ttk.Frame(self)
            capture_row.grid(row=row, column=0, columnspan=2, **pad)
            ttk.Button(capture_row, text="📍 จิ้มตำแหน่งจากเมาส์ (3 วิ)",
                       command=self._start_capture).pack(side="left", padx=(0, 6))
            ttk.Button(capture_row, text="🗂 เลือกจากที่บันทึกไว้",
                       command=self._open_position_picker).pack(side="left")
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

    def _open_position_picker(self):
        dialog = PositionPickerDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            x, y = dialog.result
            self.x_var.set(str(x))
            self.y_var.set(str(y))
            self.capture_status.set(f"เลือกตำแหน่งแล้ว ✓ ({x}, {y})")

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


class PositionPickerDialog(tk.Toplevel):
    """
    ตัวช่วยจับพิกัด (Position Picker)
    ให้ผู้ใช้บันทึกตำแหน่งบนหน้าจอไว้เป็นชื่อที่จำง่าย แล้วเรียกใช้ซ้ำได้
    ทั้งจากหน้า Auto Click และตอนสร้างขั้นตอนคลิกในชุดคำสั่ง
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.result = None  # จะถูกตั้งเป็น (x, y) เมื่อผู้ใช้กด "ใช้ตำแหน่งนี้"
        self.title("🗂 ตัวช่วยจับพิกัด")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.geometry("420x380")

        ttk.Label(self, text="บันทึกตำแหน่งบนหน้าจอไว้เป็นชื่อที่จำง่าย แล้วเลือกใช้ซ้ำได้ทุกที่ในโปรแกรม",
                  font=ui_font(9), foreground="gray", wraplength=380, justify="left").pack(
            padx=14, pady=(14, 8), anchor="w")

        columns = ("name", "x", "y")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        self.tree.heading("name", text="ชื่อตำแหน่ง")
        self.tree.heading("x", text="X")
        self.tree.heading("y", text="Y")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("x", width=60, anchor="center")
        self.tree.column("y", width=60, anchor="center")
        self.tree.pack(padx=14, pady=4, fill="both", expand=True)

        btn_row1 = ttk.Frame(self)
        btn_row1.pack(padx=14, pady=6, fill="x")
        ttk.Button(btn_row1, text="➕ จับตำแหน่งใหม่", command=self._capture_new).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row1, text="ลบ", command=self._delete_selected).pack(side="left")

        btn_row2 = ttk.Frame(self)
        btn_row2.pack(padx=14, pady=(4, 14), fill="x")
        ttk.Button(btn_row2, text="✓ ใช้ตำแหน่งนี้", style="Accent.TButton",
                   command=self._use_selected).pack(side="left", padx=(0, 6))
        ttk.Button(btn_row2, text="ปิด", command=self.destroy).pack(side="left")

        self._refresh_list()

    def _refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        positions = load_positions()
        for name, coord in sorted(positions.items()):
            self.tree.insert("", "end", iid=name, values=(name, coord.get("x", 0), coord.get("y", 0)))

    def _capture_new(self):
        if pyautogui is None:
            messagebox.showinfo("ยังใช้งานไม่ได้", "ฟีเจอร์นี้ต้องติดตั้งตัวช่วยเพิ่มเติมก่อน")
            return

        status_win = tk.Toplevel(self)
        status_win.title("กำลังจับตำแหน่ง")
        status_win.resizable(False, False)
        status_win.transient(self)
        status_win.grab_set()
        status_var = tk.StringVar(value="เตรียมตัว...")
        ttk.Label(status_win, textvariable=status_var, font=ui_font(11), padding=20).pack()

        def countdown(n):
            if n > 0:
                status_var.set(f"ย้ายเมาส์ไปตำแหน่งที่ต้องการ... อีก {n} วินาที")
                status_win.after(1000, lambda: countdown(n - 1))
            else:
                x, y = pyautogui.position()
                status_win.destroy()
                self._prompt_name_and_save(x, y)

        countdown(3)

    def _prompt_name_and_save(self, x, y):
        name = simpledialog.askstring(
            "ตั้งชื่อตำแหน่ง",
            f"จับตำแหน่งได้แล้ว: ({x}, {y})\nตั้งชื่อตำแหน่งนี้ (เช่น ปุ่มยืนยัน):",
            parent=self,
        )
        if name:
            name = name.strip()
        if not name:
            return
        add_or_update_position(name, x, y)
        self._refresh_list()

    def _selected_name(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _delete_selected(self):
        name = self._selected_name()
        if not name:
            messagebox.showinfo("ยังไม่ได้เลือก", "กรุณาเลือกตำแหน่งจากรายการก่อน")
            return
        if messagebox.askyesno("ยืนยัน", f"ลบตำแหน่ง '{name}' ทิ้งหรือไม่?"):
            delete_position(name)
            self._refresh_list()

    def _use_selected(self):
        name = self._selected_name()
        if not name:
            messagebox.showinfo("ยังไม่ได้เลือก", "กรุณาเลือกตำแหน่งจากรายการก่อน")
            return
        positions = load_positions()
        coord = positions.get(name)
        if coord:
            self.result = (coord["x"], coord["y"])
            self.destroy()


class HotkeyCaptureDialog(tk.Toplevel):
    """
    กล่องโต้ตอบสำหรับ "ตั้งปุ่มลัดเอง" — รอรับการกดปุ่มใด ๆ บนคีย์บอร์ดจริง
    ไม่จำกัดแค่ F1-F12 เหมือนก่อนหน้า รองรับตัวอักษร ตัวเลข และปุ่มพิเศษส่วนใหญ่
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("ตั้งปุ่มลัดเอง")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self._listener = None

        frame = ttk.Frame(self, padding=24)
        frame.pack()
        ttk.Label(frame, text="⌨", font=ui_font(28)).pack()
        self.status_var = tk.StringVar(value="กดปุ่มที่ต้องการตั้งเป็นปุ่มลัด...")
        ttk.Label(frame, textvariable=self.status_var, font=ui_font(11)).pack(pady=(6, 14))
        ttk.Button(frame, text="ยกเลิก", command=self._cancel).pack()

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.after(150, self._start_listening)

    def _start_listening(self):
        if pynput_keyboard is None:
            self.status_var.set("ฟีเจอร์นี้ต้องติดตั้งตัวช่วยเพิ่มเติมก่อน")
            return

        def on_press(key):
            try:
                if key == pynput_keyboard.Key.esc:
                    # ESC สงวนไว้เป็นปุ่มหยุดฉุกเฉินเสมอ ใช้ตั้งเป็นปุ่มลัดอื่นไม่ได้
                    self.after(0, self._reject_esc)
                    return
                name = getattr(key, "name", None)
                if name:
                    value = name
                else:
                    ch = getattr(key, "char", None)
                    value = ch.lower() if ch else None
                if value:
                    self.after(0, lambda: self._accept(value))
            except Exception:
                pass

        self._listener = pynput_keyboard.Listener(on_press=on_press)
        self._listener.start()

    def _reject_esc(self):
        self.status_var.set("ปุ่ม ESC สงวนไว้แล้ว กรุณากดปุ่มอื่น")

    def _accept(self, value):
        self.result = value
        self._stop_listener()
        self.destroy()

    def _cancel(self):
        self._stop_listener()
        self.destroy()

    def _stop_listener(self):
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None


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
