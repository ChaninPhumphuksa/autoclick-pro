# -*- coding: utf-8 -*-
"""
gui/app.py
==========
หน้าต่างหลักของโปรแกรม Auto Clicker Pro
ประกอบร่างจาก core.engine (ตรรกะการทำงาน) + core.tray + core.startup + core.config
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from pynput import mouse, keyboard
except ImportError:
    mouse = None
    keyboard = None

from core.engine import AutoClicker, MacroRecorder, MacroPlayer
from core.config import load_config, save_config, MACRO_LIBRARY_DIR, ensure_dirs
from core.logger import get_logger
from core.tray import TrayIcon
from core import startup as win_startup
from .theme import apply_theme, ACCENT
from .dialogs import StepDialog, AboutDialog

VERSION = "2.0.0"
FUNCTION_KEYS = [f"f{i}" for i in range(1, 13)]

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
ICON_PNG = os.path.join(ASSETS_DIR, "icon.png")
ICON_ICO = os.path.join(ASSETS_DIR, "icon.ico")

log = get_logger()


class App:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        ensure_dirs()

        root.title("Auto Clicker Pro")
        root.geometry(self.config.get("window_geometry") or "600x780")
        root.minsize(560, 700)

        self._set_window_icon()
        apply_theme(root, mode=self.config.get("theme", "dark"))

        self.hotkey_click_var = tk.StringVar(value=self.config.get("hotkey_click", "f6"))
        self.hotkey_play_var = tk.StringVar(value=self.config.get("hotkey_play", "f7"))
        self.hotkey_record_var = tk.StringVar(value=self.config.get("hotkey_record", "f8"))
        self.start_with_windows_var = tk.BooleanVar(value=self.config.get("start_with_windows", False))
        self.minimize_to_tray_var = tk.BooleanVar(value=self.config.get("minimize_to_tray_on_close", True))

        self.clicker = AutoClicker(self.get_click_settings, self.set_status)
        self.recorder = MacroRecorder(self.set_status, on_change=self.refresh_macro_list)
        self.player = MacroPlayer(lambda: self.recorder.events, self.get_macro_settings, self.set_status)

        self.tray = TrayIcon(
            icon_path=ICON_PNG,
            on_show=self._show_window,
            on_toggle_click=self.clicker.toggle,
            on_toggle_play=self.player.toggle,
            on_stop_all=self.stop_all,
            on_exit=self._exit_app,
        )

        self._build_menu_bar()
        self._build_ui()
        self._setup_global_hotkeys()
        self._refresh_library_list()

        root.protocol("WM_DELETE_WINDOW", self._on_close_button)

        if self.tray.available():
            self.tray.start()

        if pyautogui is None or mouse is None:
            messagebox.showwarning(
                "ขาดไลบรารีที่จำเป็น",
                "กรุณาติดตั้งไลบรารีก่อนใช้งาน:\n\npip install -r requirements.txt"
            )
        log.info("Application started")

    # ------------------------------------------------------------------
    def _set_window_icon(self):
        try:
            if sys.platform.startswith("win") and os.path.exists(ICON_ICO):
                self.root.iconbitmap(ICON_ICO)
            elif os.path.exists(ICON_PNG):
                img = tk.PhotoImage(file=ICON_PNG)
                self.root.iconphoto(True, img)
                self._icon_img_ref = img  # keep a reference
        except Exception:
            log.exception("Failed to set window icon")

    # ------------------------------------------------------------------
    def _build_menu_bar(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="นำเข้ามาโคร (.json)...", command=self.load_macro_file)
        file_menu.add_command(label="ส่งออกมาโคร (.json)...", command=self.save_macro_file)
        file_menu.add_separator()
        file_menu.add_command(label="ย่อลงถาด (System Tray)", command=self._hide_to_tray)
        file_menu.add_command(label="ออกจากโปรแกรม", command=self._exit_app)
        menubar.add_cascade(label="ไฟล์", menu=file_menu)

        control_menu = tk.Menu(menubar, tearoff=0)
        control_menu.add_command(label="เริ่ม/หยุด Auto Click", command=self.clicker.toggle)
        control_menu.add_command(label="เริ่ม/หยุด เล่นมาโคร", command=self.player.toggle)
        control_menu.add_command(label="เริ่ม/หยุด อัดมาโคร", command=self.recorder.toggle)
        control_menu.add_separator()
        control_menu.add_command(label="⛔ หยุดทั้งหมดทันที", command=self.stop_all)
        menubar.add_cascade(label="ควบคุม", menu=control_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="เกี่ยวกับโปรแกรม", command=lambda: AboutDialog(self.root, VERSION))
        menubar.add_cascade(label="ช่วยเหลือ", menu=help_menu)

        self.root.config(menu=menubar)

    # ------------------------------------------------------------------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # ---- Header: brand + emergency stop (always visible, above tabs) ----
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=14, pady=(12, 6))
        ttk.Label(header, text="⚡ Auto Clicker Pro", font=("Segoe UI", 14, "bold")).pack(side="left")

        self.stop_all_btn = tk.Button(
            header, text="⛔  หยุดทั้งหมด (Emergency Stop)", command=self.stop_all,
            bg="#DC2626", fg="white", activebackground="#B91C1C", activeforeground="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=14, pady=6, cursor="hand2",
        )
        self.stop_all_btn.pack(side="right")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=(0, 0))

        # ================= Tab 1: Auto Click =================
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Auto Click")

        ttk.Label(tab1, text="ความถี่ในการคลิก", font=("Segoe UI", 11, "bold")).pack(**pad, anchor="w")
        freq_frame = ttk.Frame(tab1)
        freq_frame.pack(**pad, anchor="w")
        self.hours_var = tk.StringVar(value="0")
        self.mins_var = tk.StringVar(value="0")
        self.secs_var = tk.StringVar(value="0")
        self.ms_var = tk.StringVar(value="200")
        for label, var in [("ชม.", self.hours_var), ("นาที", self.mins_var),
                            ("วินาที", self.secs_var), ("มิลลิวินาที", self.ms_var)]:
            box = ttk.Frame(freq_frame)
            box.pack(side="left", padx=6)
            ttk.Entry(box, textvariable=var, width=6).pack()
            ttk.Label(box, text=label).pack()

        jitter_frame = ttk.Frame(tab1)
        jitter_frame.pack(**pad, anchor="w")
        ttk.Label(jitter_frame, text="สุ่มความหน่วงเวลา ±").pack(side="left")
        self.jitter_ms_var = tk.StringVar(value="0")
        ttk.Entry(jitter_frame, textvariable=self.jitter_ms_var, width=6).pack(side="left", padx=4)
        ttk.Label(jitter_frame, text="มิลลิวินาที").pack(side="left")

        ttk.Label(tab1, text="ปุ่มเมาส์", font=("Segoe UI", 11, "bold")).pack(**pad, anchor="w")
        self.button_var = tk.StringVar(value="left")
        btn_frame = ttk.Frame(tab1)
        btn_frame.pack(**pad, anchor="w")
        for text, val in [("ซ้าย", "left"), ("ขวา", "right"), ("กลาง", "middle")]:
            ttk.Radiobutton(btn_frame, text=text, value=val, variable=self.button_var).pack(side="left", padx=8)
        self.double_click_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab1, text="ดับเบิลคลิก", variable=self.double_click_var).pack(**pad, anchor="w")

        ttk.Label(tab1, text="ตำแหน่งคลิก", font=("Segoe UI", 11, "bold")).pack(**pad, anchor="w")
        self.fixed_pos_var = tk.BooleanVar(value=False)
        ttk.Radiobutton(tab1, text="คลิกที่ตำแหน่งเมาส์ปัจจุบัน", value=False,
                         variable=self.fixed_pos_var).pack(**pad, anchor="w")
        fixed_row = ttk.Frame(tab1)
        fixed_row.pack(**pad, anchor="w")
        ttk.Radiobutton(fixed_row, text="คลิกที่ตำแหน่งคงที่:", value=True,
                         variable=self.fixed_pos_var).pack(side="left")
        self.fixed_x_var = tk.StringVar(value="0")
        self.fixed_y_var = tk.StringVar(value="0")
        ttk.Label(fixed_row, text="X").pack(side="left", padx=(8, 2))
        ttk.Entry(fixed_row, textvariable=self.fixed_x_var, width=6).pack(side="left")
        ttk.Label(fixed_row, text="Y").pack(side="left", padx=(8, 2))
        ttk.Entry(fixed_row, textvariable=self.fixed_y_var, width=6).pack(side="left")
        ttk.Button(fixed_row, text="จับตำแหน่ง (3 วิ)", command=self._capture_fixed_position).pack(side="left", padx=8)

        ttk.Label(tab1, text="จำนวนครั้ง", font=("Segoe UI", 11, "bold")).pack(**pad, anchor="w")
        self.limited_var = tk.BooleanVar(value=False)
        ttk.Radiobutton(tab1, text="ไม่จำกัด (จนกว่าจะกด หยุด)", value=False,
                         variable=self.limited_var).pack(**pad, anchor="w")
        limited_row = ttk.Frame(tab1)
        limited_row.pack(**pad, anchor="w")
        ttk.Radiobutton(limited_row, text="จำกัดจำนวน:", value=True, variable=self.limited_var).pack(side="left")
        self.click_count_var = tk.StringVar(value="10")
        ttk.Entry(limited_row, textvariable=self.click_count_var, width=8).pack(side="left", padx=6)
        ttk.Label(limited_row, text="ครั้ง").pack(side="left")

        ttk.Separator(tab1).pack(fill="x", padx=10, pady=10)
        self.click_toggle_btn = ttk.Button(tab1, text="▶ เริ่ม Auto Click", style="Accent.TButton",
                                            command=self.clicker.toggle)
        self.click_toggle_btn.pack(padx=20, pady=6, fill="x")

        # ================= Tab 2: Macro =================
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Macro")

        ttk.Label(tab2, text="อัดมาโครจากการใช้งานจริง", font=("Segoe UI", 10, "bold")).pack(**pad, anchor="w")
        self.record_toggle_btn = ttk.Button(tab2, text="⏺ เริ่มอัดมาโคร", command=self.recorder.toggle)
        self.record_toggle_btn.pack(padx=20, pady=6, fill="x")

        ttk.Separator(tab2).pack(fill="x", padx=10, pady=6)
        ttk.Label(tab2, text="สร้าง/แก้ไขมาโครเอง (Custom)", font=("Segoe UI", 10, "bold")).pack(**pad, anchor="w")

        columns = ("no", "type", "detail", "delay")
        self.step_tree = ttk.Treeview(tab2, columns=columns, show="headings", height=7)
        for col, text, width in [("no", "#", 30), ("type", "ประเภท", 80),
                                  ("detail", "รายละเอียด", 220), ("delay", "ดีเลย์ (วิ)", 80)]:
            self.step_tree.heading(col, text=text)
            self.step_tree.column(col, width=width, anchor="center" if col != "detail" else "w")
        self.step_tree.pack(padx=20, pady=4, fill="x")

        step_btns1 = ttk.Frame(tab2)
        step_btns1.pack(padx=20, pady=2, fill="x")
        ttk.Button(step_btns1, text="+ คลิก", command=lambda: self._add_step_dialog("click")).pack(side="left", padx=2)
        ttk.Button(step_btns1, text="+ กดปุ่ม", command=lambda: self._add_step_dialog("key")).pack(side="left", padx=2)
        ttk.Button(step_btns1, text="+ ดีเลย์", command=lambda: self._add_step_dialog("wait")).pack(side="left", padx=2)
        ttk.Button(step_btns1, text="แก้ไข", command=self._edit_selected_step).pack(side="left", padx=2)
        ttk.Button(step_btns1, text="ลบ", command=self._remove_selected_step).pack(side="left", padx=2)

        step_btns2 = ttk.Frame(tab2)
        step_btns2.pack(padx=20, pady=2, fill="x")
        ttk.Button(step_btns2, text="▲ เลื่อนขึ้น", command=lambda: self._move_selected_step(-1)).pack(side="left", padx=2)
        ttk.Button(step_btns2, text="▼ เลื่อนลง", command=lambda: self._move_selected_step(1)).pack(side="left", padx=2)
        ttk.Button(step_btns2, text="ล้างทั้งหมด", command=self._clear_steps).pack(side="left", padx=2)

        ttk.Separator(tab2).pack(fill="x", padx=10, pady=6)
        ttk.Label(tab2, text="การเล่นซ้ำ", font=("Segoe UI", 10, "bold")).pack(**pad, anchor="w")
        self.loop_macro_var = tk.BooleanVar(value=False)
        ttk.Radiobutton(tab2, text="วนซ้ำไม่จำกัด (จนกว่าจะกด หยุด)", value=True,
                         variable=self.loop_macro_var).pack(**pad, anchor="w")
        rep_row = ttk.Frame(tab2)
        rep_row.pack(**pad, anchor="w")
        ttk.Radiobutton(rep_row, text="เล่นซ้ำ:", value=False, variable=self.loop_macro_var).pack(side="left")
        self.macro_repeat_var = tk.StringVar(value="1")
        ttk.Entry(rep_row, textvariable=self.macro_repeat_var, width=8).pack(side="left", padx=6)
        ttk.Label(rep_row, text="รอบ").pack(side="left")

        self.play_toggle_btn = ttk.Button(tab2, text="▶ เริ่มเล่นมาโคร", style="Accent.TButton",
                                           command=self.player.toggle)
        self.play_toggle_btn.pack(padx=20, pady=6, fill="x")

        ttk.Separator(tab2).pack(fill="x", padx=10, pady=6)
        ttk.Label(tab2, text="คลังมาโคร (บันทึก/โหลดแบบตั้งชื่อ)", font=("Segoe UI", 10, "bold")).pack(**pad, anchor="w")
        lib_row = ttk.Frame(tab2)
        lib_row.pack(padx=20, pady=6, fill="x")
        self.library_var = tk.StringVar()
        self.library_combo = ttk.Combobox(lib_row, textvariable=self.library_var, state="readonly", width=28)
        self.library_combo.pack(side="left", padx=(0, 6))
        ttk.Button(lib_row, text="โหลด", command=self._load_from_library).pack(side="left", padx=2)
        ttk.Button(lib_row, text="ลบ", command=self._delete_from_library).pack(side="left", padx=2)

        save_row = ttk.Frame(tab2)
        save_row.pack(padx=20, pady=6, fill="x")
        ttk.Label(save_row, text="ชื่อมาโคร:").pack(side="left")
        self.save_name_var = tk.StringVar()
        ttk.Entry(save_row, textvariable=self.save_name_var, width=20).pack(side="left", padx=6)
        ttk.Button(save_row, text="บันทึกลงคลัง", command=self._save_to_library).pack(side="left", padx=2)

        # ================= Tab 3: Settings =================
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="ตั้งค่า")

        ttk.Label(tab3, text="กำหนด Hotkey เอง", font=("Segoe UI", 11, "bold")).pack(**pad, anchor="w")
        for label, var in [("Auto Click เริ่ม/หยุด:", self.hotkey_click_var),
                            ("เล่นมาโคร เริ่ม/หยุด:", self.hotkey_play_var),
                            ("อัดมาโคร เริ่ม/หยุด:", self.hotkey_record_var)]:
            row = ttk.Frame(tab3)
            row.pack(padx=20, pady=6, anchor="w", fill="x")
            ttk.Label(row, text=label, width=20).pack(side="left")
            combo = ttk.Combobox(row, textvariable=var, values=FUNCTION_KEYS, state="readonly", width=8)
            combo.pack(side="left")
            combo.bind("<<ComboboxSelected>>", lambda e: self._persist_config())
        ttk.Label(tab3, text="* ปุ่ม ESC ถูกกำหนดตายตัวไว้เป็นปุ่มหยุดฉุกเฉินเสมอ",
                  foreground="gray").pack(padx=20, pady=6, anchor="w")

        ttk.Separator(tab3).pack(fill="x", padx=10, pady=10)
        ttk.Label(tab3, text="ระบบ / Windows", font=("Segoe UI", 11, "bold")).pack(**pad, anchor="w")

        startup_row = ttk.Frame(tab3)
        startup_row.pack(padx=20, pady=6, anchor="w", fill="x")
        startup_check = ttk.Checkbutton(startup_row, text="เปิดโปรแกรมอัตโนมัติเมื่อ Windows เริ่มทำงาน",
                                         variable=self.start_with_windows_var,
                                         command=self._on_toggle_start_with_windows)
        startup_check.pack(side="left")
        if not win_startup.is_windows():
            startup_check.config(state="disabled")
            ttk.Label(tab3, text="(ใช้ได้เฉพาะบน Windows)", foreground="gray").pack(anchor="w", padx=40)

        ttk.Checkbutton(tab3, text="ย่อหน้าต่างลงถาด (System Tray) เมื่อกดปิดหน้าต่าง แทนการปิดโปรแกรม",
                         variable=self.minimize_to_tray_var,
                         command=self._persist_config).pack(padx=20, pady=6, anchor="w")

        if not self.tray.available():
            ttk.Label(tab3, text="* ยังไม่ได้ติดตั้ง pystray/Pillow — ระบบ tray จะไม่ทำงาน (pip install pystray pillow)",
                      foreground="orange").pack(padx=20, pady=6, anchor="w")

        ttk.Separator(tab3).pack(fill="x", padx=10, pady=10)
        ttk.Label(tab3, text="ประวัติการทำงาน (Log)", font=("Segoe UI", 11, "bold")).pack(**pad, anchor="w")
        self.log_text = scrolledtext.ScrolledText(tab3, height=10, width=60, state="disabled", wrap="word")
        self.log_text.pack(padx=20, pady=4, fill="both", expand=True)
        ttk.Button(tab3, text="ล้าง Log", command=self._clear_log).pack(padx=20, pady=4, anchor="e")

        # ---------------- Status bar ----------------
        self.status_var = tk.StringVar(value="พร้อมทำงาน")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(fill="x", side="bottom")
        self.hint_var = tk.StringVar()
        ttk.Label(self.root, textvariable=self.hint_var, foreground="gray").pack(side="bottom", pady=2)
        self._update_hint()

    def _update_hint(self):
        self.hint_var.set(
            f"Hotkeys: {self.hotkey_click_var.get().upper()}=Auto Click | "
            f"{self.hotkey_play_var.get().upper()}=เล่นมาโคร | "
            f"{self.hotkey_record_var.get().upper()}=อัดมาโคร | ESC=หยุดทั้งหมด"
        )
        self.root.after(500, self._update_hint)

    # ------------------------------------------------------------------
    # Emergency stop / window / tray lifecycle
    # ------------------------------------------------------------------
    def stop_all(self):
        self.clicker.stop()
        self.player.stop()
        self.recorder.stop()
        log.info("Emergency stop triggered")
        self.set_status("⛔ หยุดการทำงานทั้งหมดแล้ว (Emergency Stop)")

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _hide_to_tray(self):
        if self.tray.available():
            self.root.withdraw()
            self.set_status("ย่อโปรแกรมลงถาดแล้ว (คลิกไอคอนถาดเพื่อเปิดกลับมา)")
        else:
            messagebox.showinfo("ไม่รองรับ", "ยังไม่ได้ติดตั้ง pystray/Pillow จึงย่อลงถาดไม่ได้")

    def _on_close_button(self):
        if self.minimize_to_tray_var.get() and self.tray.available():
            self._hide_to_tray()
        else:
            self._exit_app()

    def _exit_app(self):
        self._persist_config(save_geometry=True)
        self.stop_all()
        self.tray.stop()
        log.info("Application exiting")
        self.root.after(200, self.root.destroy)

    # ------------------------------------------------------------------
    def _on_toggle_start_with_windows(self):
        enabled = self.start_with_windows_var.get()
        ok = win_startup.set_enabled(enabled)
        if not ok and enabled:
            messagebox.showerror("ไม่สำเร็จ", "ไม่สามารถตั้งค่าเริ่มพร้อม Windows ได้")
            self.start_with_windows_var.set(False)
        self._persist_config()
        self.set_status("ตั้งค่าเริ่มพร้อม Windows: " + ("เปิดใช้งาน" if self.start_with_windows_var.get() else "ปิดใช้งาน"))

    def _persist_config(self, save_geometry=False):
        self.config.update({
            "hotkey_click": self.hotkey_click_var.get(),
            "hotkey_play": self.hotkey_play_var.get(),
            "hotkey_record": self.hotkey_record_var.get(),
            "start_with_windows": self.start_with_windows_var.get(),
            "minimize_to_tray_on_close": self.minimize_to_tray_var.get(),
        })
        if save_geometry:
            try:
                self.config["window_geometry"] = self.root.geometry()
            except Exception:
                pass
        save_config(self.config)

    # ------------------------------------------------------------------
    # Settings getters
    # ------------------------------------------------------------------
    def get_click_settings(self):
        try:
            hours = float(self.hours_var.get() or 0)
            mins = float(self.mins_var.get() or 0)
            secs = float(self.secs_var.get() or 0)
            ms = float(self.ms_var.get() or 0)
        except ValueError:
            hours = mins = secs = 0
            ms = 200
        interval = hours * 3600 + mins * 60 + secs + ms / 1000.0
        try:
            click_count = int(self.click_count_var.get() or 1)
        except ValueError:
            click_count = 1
        try:
            jitter_seconds = float(self.jitter_ms_var.get() or 0) / 1000.0
        except ValueError:
            jitter_seconds = 0.0
        fixed = self.fixed_pos_var.get()
        try:
            fx = int(float(self.fixed_x_var.get())) if fixed else None
            fy = int(float(self.fixed_y_var.get())) if fixed else None
        except ValueError:
            fx = fy = None
        return {
            "interval_seconds": interval, "jitter_seconds": jitter_seconds,
            "button": self.button_var.get(), "double_click": self.double_click_var.get(),
            "limited_count": self.limited_var.get(), "click_count": click_count,
            "fixed_position": fixed, "fixed_x": fx, "fixed_y": fy,
        }

    def get_macro_settings(self):
        try:
            repeat = int(self.macro_repeat_var.get() or 1)
        except ValueError:
            repeat = 1
        return {"loop_macro": self.loop_macro_var.get(), "macro_repeat_count": max(1, repeat)}

    def _capture_fixed_position(self):
        def countdown(n):
            if n > 0:
                self.set_status(f"จับตำแหน่งใน {n} วินาที... ย้ายเมาส์ไปตำแหน่งที่ต้องการ")
                self.root.after(1000, lambda: countdown(n - 1))
            else:
                if pyautogui:
                    x, y = pyautogui.position()
                    self.fixed_x_var.set(str(x))
                    self.fixed_y_var.set(str(y))
                    self.set_status(f"จับตำแหน่งคงที่แล้ว: ({x}, {y})")
        countdown(3)

    # ------------------------------------------------------------------
    # Macro step editor helpers
    # ------------------------------------------------------------------
    def refresh_macro_list(self):
        def _update():
            self.step_tree.delete(*self.step_tree.get_children())
            for i, ev in enumerate(self.recorder.events):
                if ev["type"] == "click":
                    detail = f"({ev['x']}, {ev['y']})  ปุ่ม={ev.get('button', 'left')}"
                    type_label = "คลิก"
                elif ev["type"] == "key":
                    detail = f"ปุ่ม: {ev['key']}"
                    type_label = "กดปุ่ม"
                else:
                    detail = "-"
                    type_label = "ดีเลย์"
                self.step_tree.insert("", "end", iid=str(i),
                                       values=(i + 1, type_label, detail, f"{ev.get('delay', 0):.2f}"))
        try:
            self.root.after(0, _update)
        except Exception:
            pass

    def _selected_step_index(self):
        sel = self.step_tree.selection()
        return int(sel[0]) if sel else None

    def _add_step_dialog(self, step_type):
        dialog = StepDialog(self.root, step_type)
        self.root.wait_window(dialog)
        if dialog.result:
            idx = self._selected_step_index()
            insert_at = idx + 1 if idx is not None else None
            self.recorder.add_step(dialog.result, index=insert_at)
            self.set_status("เพิ่มขั้นตอนมาโครแล้ว")

    def _edit_selected_step(self):
        idx = self._selected_step_index()
        if idx is None:
            messagebox.showinfo("ยังไม่ได้เลือก", "กรุณาเลือกขั้นตอนที่ต้องการแก้ไขก่อน")
            return
        existing = self.recorder.events[idx]
        dialog = StepDialog(self.root, existing["type"], existing=existing)
        self.root.wait_window(dialog)
        if dialog.result:
            self.recorder.update_step(idx, dialog.result)
            self.set_status("แก้ไขขั้นตอนมาโครแล้ว")

    def _remove_selected_step(self):
        idx = self._selected_step_index()
        if idx is None:
            messagebox.showinfo("ยังไม่ได้เลือก", "กรุณาเลือกขั้นตอนที่ต้องการลบก่อน")
            return
        self.recorder.remove_step(idx)
        self.set_status("ลบขั้นตอนมาโครแล้ว")

    def _move_selected_step(self, direction):
        idx = self._selected_step_index()
        if idx is None:
            return
        new_idx = self.recorder.move_step(idx, direction)
        self.step_tree.selection_set(str(new_idx))

    def _clear_steps(self):
        if not self.recorder.events:
            return
        if messagebox.askyesno("ยืนยัน", "ล้างขั้นตอนมาโครทั้งหมดหรือไม่?"):
            self.recorder.clear()
            self.set_status("ล้างมาโครทั้งหมดแล้ว")

    # ------------------------------------------------------------------
    # Macro library
    # ------------------------------------------------------------------
    def _refresh_library_list(self):
        files = sorted(f[:-5] for f in os.listdir(MACRO_LIBRARY_DIR) if f.endswith(".json"))
        self.library_combo["values"] = files
        if files and not self.library_var.get():
            self.library_var.set(files[0])

    def _save_to_library(self):
        name = self.save_name_var.get().strip()
        if not name:
            messagebox.showinfo("ระบุชื่อ", "กรุณาตั้งชื่อมาโครก่อนบันทึก")
            return
        if not self.recorder.events:
            messagebox.showinfo("ไม่มีข้อมูล", "ยังไม่มีขั้นตอนมาโครให้บันทึก")
            return
        safe_name = "".join(c for c in name if c.isalnum() or c in " _-").strip() or "macro"
        path = os.path.join(MACRO_LIBRARY_DIR, f"{safe_name}.json")
        self.recorder.save(path)
        self._refresh_library_list()
        self.library_var.set(safe_name)
        self.set_status(f"บันทึกมาโคร '{safe_name}' ลงคลังแล้ว")

    def _load_from_library(self):
        name = self.library_var.get()
        if not name:
            return
        path = os.path.join(MACRO_LIBRARY_DIR, f"{name}.json")
        try:
            self.recorder.load(path)
            self.set_status(f"โหลดมาโคร '{name}' จากคลังแล้ว ({len(self.recorder.events)} ขั้นตอน)")
        except Exception as e:
            messagebox.showerror("โหลดไม่สำเร็จ", str(e))

    def _delete_from_library(self):
        name = self.library_var.get()
        if not name:
            return
        if messagebox.askyesno("ยืนยัน", f"ลบมาโคร '{name}' ออกจากคลังหรือไม่?"):
            path = os.path.join(MACRO_LIBRARY_DIR, f"{name}.json")
            try:
                os.remove(path)
                self._refresh_library_list()
                self.library_var.set("")
                self.set_status(f"ลบมาโคร '{name}' แล้ว")
            except Exception as e:
                messagebox.showerror("ลบไม่สำเร็จ", str(e))

    def save_macro_file(self):
        if not self.recorder.events:
            messagebox.showinfo("ไม่มีข้อมูล", "ยังไม่มีมาโครให้ส่งออก")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Macro JSON", "*.json")])
        if path:
            self.recorder.save(path)
            self.set_status(f"ส่งออกมาโครแล้ว: {path}")

    def load_macro_file(self):
        path = filedialog.askopenfilename(filetypes=[("Macro JSON", "*.json")])
        if path:
            try:
                self.recorder.load(path)
                self.set_status(f"นำเข้ามาโครแล้ว ({len(self.recorder.events)} ขั้นตอน)")
            except Exception as e:
                messagebox.showerror("นำเข้าไม่สำเร็จ", str(e))

    # ------------------------------------------------------------------
    def set_status(self, text):
        def _update():
            self.status_var.set(text)
            self.click_toggle_btn.config(text=("⏹ หยุด Auto Click" if self.clicker.running else "▶ เริ่ม Auto Click"))
            self.play_toggle_btn.config(text=("⏹ หยุดเล่นมาโคร" if self.player.running else "▶ เริ่มเล่นมาโคร"))
            self.record_toggle_btn.config(text=("⏹ หยุดอัดมาโคร" if self.recorder.recording else "⏺ เริ่มอัดมาโคร"))
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_text.config(state="normal")
            self.log_text.insert("end", f"[{ts}] {text}\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        try:
            self.root.after(0, _update)
        except Exception:
            pass

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # ------------------------------------------------------------------
    def _setup_global_hotkeys(self):
        if keyboard is None:
            return

        def on_press(key):
            try:
                name = getattr(key, "name", None)
                if name == self.hotkey_click_var.get():
                    self.clicker.toggle()
                elif name == self.hotkey_play_var.get():
                    self.player.toggle()
                elif name == self.hotkey_record_var.get():
                    self.recorder.toggle()
                elif key == keyboard.Key.esc:
                    self.stop_all()
            except Exception:
                log.exception("Error in global hotkey handler")

        self._hotkey_listener = keyboard.Listener(on_press=on_press)
        self._hotkey_listener.start()
