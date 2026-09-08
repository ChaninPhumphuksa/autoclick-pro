"""
main.py
AutoClicker Pro - โปรแกรม Auto Click มืออาชีพ
=================================================
Tabs:
  1) Auto Clicker   - คลิกอัตโนมัติ ตั้งค่า interval / ปุ่มเมาส์ / ตำแหน่ง / hotkey ปุ่มไหนก็ได้
  2) Macro Recorder - บันทึกการกระทำจริงแล้วเล่นซ้ำ
  3) Script Editor  - เขียนสคริปต์มาโครแบบ custom เอง (JSON DSL) + บันทึก/โหลด
  4) Settings       - ธีม, Failsafe, จัดการโปรไฟล์, About

รันด้วย: python main.py
แพ็กเป็น .exe ด้วย: build.bat (ดู README.md)
"""

import json
import threading
import time

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pynput import keyboard as pkeyboard

from humanizer import Humanizer
from macro_engine import ClickerEngine, MacroRecorder
from script_engine import ScriptEngine
from hotkey_manager import HotkeyManager, capture_next_key, key_to_str
import profile_manager as pm

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

APP_TITLE = "AutoClicker Pro"
FAILSAFE_KEY = "esc"  # ปุ่มฉุกเฉิน หยุดทุกอย่างทันที เสมอ


class HotkeyCaptureButton(ctk.CTkButton):
    """ปุ่มที่กดแล้วเข้าสู่โหมด 'รอรับปุ่มถัดไป' เพื่อกำหนด hotkey แบบ 'ปุ่มไหนก็ได้'"""

    def __init__(self, master, initial="f6", on_change=None, **kwargs):
        self.value = initial
        self.on_change = on_change
        super().__init__(master, text=self._label(), command=self._capture, **kwargs)

    def _label(self):
        return f"⌨ {self.value.upper()}  (คลิกเพื่อเปลี่ยน)"

    def _capture(self):
        self.configure(text="กดปุ่มที่ต้องการ...", state="disabled")

        def done(key_str):
            self.value = key_str
            self.after(0, lambda: self.configure(text=self._label(), state="normal"))
            if self.on_change:
                self.on_change(key_str)

        capture_next_key(done)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x680")
        self.minsize(860, 600)

        # --- engines / state ---
        self.clicker = None
        self.script_engine = ScriptEngine()
        self.recorder = MacroRecorder()
        self.recorded_script = None
        self.hotkeys = HotkeyManager()
        self.script_stop_event = threading.Event()
        self.script_thread = None
        self.is_recording = False

        self._build_ui()
        self._start_global_failsafe()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        self.tabs = ctk.CTkTabview(self, width=960, height=660)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_click = self.tabs.add("🖱  Auto Clicker")
        self.tab_record = self.tabs.add("⏺  Macro Recorder")
        self.tab_script = self.tabs.add("📝  Script Engine")
        self.tab_settings = self.tabs.add("⚙  Settings")

        self._build_clicker_tab()
        self._build_recorder_tab()
        self._build_script_tab()
        self._build_settings_tab()

    # ============================================================ TAB 1
    def _build_clicker_tab(self):
        t = self.tab_click
        left = ctk.CTkFrame(t)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        right = ctk.CTkFrame(t, width=280)
        right.pack(side="right", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left, text="ระยะเวลาระหว่างคลิก", font=("", 15, "bold")).pack(anchor="w", pady=(5, 0))
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.pack(anchor="w", pady=5)
        self.ent_h = ctk.CTkEntry(row, width=55, placeholder_text="ชม.")
        self.ent_m = ctk.CTkEntry(row, width=55, placeholder_text="นาที")
        self.ent_s = ctk.CTkEntry(row, width=55, placeholder_text="วินาที")
        self.ent_ms = ctk.CTkEntry(row, width=65, placeholder_text="มิลลิวิ")
        for e, default in [(self.ent_h, "0"), (self.ent_m, "0"), (self.ent_s, "0"), (self.ent_ms, "100")]:
            e.insert(0, default)
            e.pack(side="left", padx=3)

        ctk.CTkLabel(left, text="ปุ่มเมาส์ & รูปแบบคลิก", font=("", 15, "bold")).pack(anchor="w", pady=(15, 0))
        row2 = ctk.CTkFrame(left, fg_color="transparent")
        row2.pack(anchor="w", pady=5)
        self.opt_button = ctk.CTkOptionMenu(row2, values=["left", "right", "middle"])
        self.opt_button.pack(side="left", padx=3)
        self.opt_clicktype = ctk.CTkOptionMenu(row2, values=["1 (single)", "2 (double)", "3 (triple)"])
        self.opt_clicktype.pack(side="left", padx=3)

        ctk.CTkLabel(left, text="ตำแหน่งคลิก", font=("", 15, "bold")).pack(anchor="w", pady=(15, 0))
        self.opt_position = ctk.CTkOptionMenu(left, values=["ตำแหน่งเมาส์ปัจจุบัน", "ตำแหน่งคงที่ (Fixed XY)"],
                                               command=self._on_position_mode_change)
        self.opt_position.pack(anchor="w", pady=5)
        row3 = ctk.CTkFrame(left, fg_color="transparent")
        row3.pack(anchor="w")
        self.ent_x = ctk.CTkEntry(row3, width=80, placeholder_text="X")
        self.ent_y = ctk.CTkEntry(row3, width=80, placeholder_text="Y")
        self.btn_pick_pos = ctk.CTkButton(row3, text="🎯 จับตำแหน่งจากเมาส์ (กด F8)", command=self._pick_position)
        self.ent_x.pack(side="left", padx=3)
        self.ent_y.pack(side="left", padx=3)
        self.btn_pick_pos.pack(side="left", padx=6)

        ctk.CTkLabel(left, text="จำนวนรอบ", font=("", 15, "bold")).pack(anchor="w", pady=(15, 0))
        row4 = ctk.CTkFrame(left, fg_color="transparent")
        row4.pack(anchor="w", pady=5)
        self.opt_repeat = ctk.CTkOptionMenu(row4, values=["คลิกไปเรื่อย ๆ จนกว่าจะหยุด", "คลิกจำนวนจำกัด"])
        self.opt_repeat.pack(side="left", padx=3)
        self.ent_repeat_count = ctk.CTkEntry(row4, width=90, placeholder_text="จำนวนครั้ง")
        self.ent_repeat_count.insert(0, "10")
        self.ent_repeat_count.pack(side="left", padx=3)

        # --- Humanizer ---
        hum_frame = ctk.CTkFrame(left)
        hum_frame.pack(fill="x", pady=(20, 5))
        ctk.CTkLabel(hum_frame, text="🛡 Anti-Ban Humanizer", font=("", 15, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        self.chk_hum_enabled = ctk.CTkCheckBox(hum_frame, text="เปิดใช้งาน (สุ่มหน่วงเวลา + สุ่มตำแหน่งเล็กน้อย)")
        self.chk_hum_enabled.select()
        self.chk_hum_enabled.pack(anchor="w", padx=10, pady=5)

        self.sld_variance = self._labeled_slider(hum_frame, "ความสุ่มของเวลาหน่วง (delay variance)", 0, 100, 20)
        self.sld_jitter = self._labeled_slider(hum_frame, "สุ่มขยับตำแหน่งคลิก (pixel jitter)", 0, 20, 3)
        self.sld_misclick = self._labeled_slider(hum_frame, "โอกาสคลิกพลาดเล็กน้อยก่อนคลิกจริง (%)", 0, 20, 0)

        # --- right: hotkey + start/stop + stats ---
        ctk.CTkLabel(right, text="Hotkey เริ่ม/หยุด", font=("", 15, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(right, text="(กำหนดเป็นปุ่มไหนก็ได้บนคีย์บอร์ด)", font=("", 11)).pack()
        self.hotkey_btn = HotkeyCaptureButton(right, initial="f6", on_change=self._rebind_clicker_hotkey)
        self.hotkey_btn.pack(pady=8)

        self.btn_start_stop = ctk.CTkButton(right, text="▶ เริ่มคลิก (Start)", height=45,
                                             fg_color="#1f9d55", hover_color="#178a49",
                                             command=self._toggle_clicker)
        self.btn_start_stop.pack(pady=20, fill="x", padx=20)

        self.lbl_status = ctk.CTkLabel(right, text="สถานะ: หยุดทำงาน", font=("", 13, "bold"))
        self.lbl_status.pack(pady=5)
        self.lbl_count = ctk.CTkLabel(right, text="จำนวนคลิก: 0")
        self.lbl_count.pack(pady=5)

        ctk.CTkLabel(right, text="⛔ กด ESC เพื่อหยุดฉุกเฉินได้ทุกเมื่อ", text_color="#e0a030").pack(pady=(30, 5))

        # profile save/load
        prof_frame = ctk.CTkFrame(right, fg_color="transparent")
        prof_frame.pack(pady=10, fill="x", padx=15)
        ctk.CTkButton(prof_frame, text="💾 บันทึกโปรไฟล์", command=self._save_profile).pack(fill="x", pady=3)
        ctk.CTkButton(prof_frame, text="📂 โหลดโปรไฟล์", command=self._load_profile).pack(fill="x", pady=3)

        self._on_position_mode_change(self.opt_position.get())
        self._rebind_clicker_hotkey(self.hotkey_btn.value)

    def _labeled_slider(self, parent, label, frm, to, default):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", padx=10, pady=4)
        lbl = ctk.CTkLabel(wrap, text=f"{label}: {default}")
        lbl.pack(anchor="w")
        sld = ctk.CTkSlider(wrap, from_=frm, to=to, number_of_steps=max(1, to - frm))
        sld.set(default)
        sld.configure(command=lambda v: lbl.configure(text=f"{label}: {int(v)}"))
        sld.pack(fill="x")
        return sld

    def _on_position_mode_change(self, value):
        fixed = value.startswith("ตำแหน่งคงที่")
        state = "normal" if fixed else "disabled"
        self.ent_x.configure(state=state)
        self.ent_y.configure(state=state)
        self.btn_pick_pos.configure(state=state)

    def _pick_position(self):
        messagebox.showinfo("จับตำแหน่ง", "ย้ายเมาส์ไปยังตำแหน่งที่ต้องการ แล้วกดปุ่ม F8 บนคีย์บอร์ด")
        from pynput.mouse import Controller as MouseController

        def on_press(key):
            if key_to_str(key).lower() == "f8":
                x, y = MouseController().position
                self.ent_x.delete(0, "end")
                self.ent_x.insert(0, str(x))
                self.ent_y.delete(0, "end")
                self.ent_y.insert(0, str(y))
                return False

        pkeyboard.Listener(on_press=on_press).start()

    def _gather_clicker_settings(self):
        try:
            h = float(self.ent_h.get() or 0)
            m = float(self.ent_m.get() or 0)
            s = float(self.ent_s.get() or 0)
            ms = float(self.ent_ms.get() or 0)
        except ValueError:
            h = m = s = 0
            ms = 100
        interval = h * 3600 + m * 60 + s + ms / 1000.0
        interval = max(0.01, interval)

        click_type = int(self.opt_clicktype.get().split()[0])
        position_mode = "fixed" if self.opt_position.get().startswith("ตำแหน่งคงที่") else "cursor"
        fixed_pos = None
        if position_mode == "fixed":
            try:
                fixed_pos = (int(self.ent_x.get()), int(self.ent_y.get()))
            except ValueError:
                fixed_pos = None
        repeat_mode = "count" if self.opt_repeat.get() == "คลิกจำนวนจำกัด" else "until_stopped"
        try:
            repeat_count = int(self.ent_repeat_count.get())
        except ValueError:
            repeat_count = 10

        humanizer = {
            "enabled": bool(self.chk_hum_enabled.get()),
            "delay_variance": self.sld_variance.get() / 100.0,
            "position_jitter": int(self.sld_jitter.get()),
            "misclick_chance": self.sld_misclick.get() / 100.0,
            "move_curve": True,
        }

        return {
            "interval_seconds": interval,
            "button": self.opt_button.get(),
            "click_type": click_type,
            "position_mode": position_mode,
            "fixed_pos": fixed_pos,
            "repeat_mode": repeat_mode,
            "repeat_count": repeat_count,
            "humanizer": humanizer,
            "hotkey": self.hotkey_btn.value,
        }

    def _apply_clicker_settings(self, s):
        self.ent_h.delete(0, "end"); self.ent_h.insert(0, "0")
        total = s.get("interval_seconds", 0.1)
        self.ent_m.delete(0, "end"); self.ent_m.insert(0, "0")
        self.ent_s.delete(0, "end"); self.ent_s.insert(0, str(int(total)))
        self.ent_ms.delete(0, "end"); self.ent_ms.insert(0, str(int((total - int(total)) * 1000)))
        self.opt_button.set(s.get("button", "left"))
        ct = s.get("click_type", 1)
        ct_label = "single" if ct == 1 else ("double" if ct == 2 else "triple")
        self.opt_clicktype.set(f"{ct} ({ct_label})")
        if s.get("position_mode") == "fixed":
            self.opt_position.set("ตำแหน่งคงที่ (Fixed XY)")
            if s.get("fixed_pos"):
                self.ent_x.delete(0, "end"); self.ent_x.insert(0, str(s["fixed_pos"][0]))
                self.ent_y.delete(0, "end"); self.ent_y.insert(0, str(s["fixed_pos"][1]))
        else:
            self.opt_position.set("ตำแหน่งเมาส์ปัจจุบัน")
        self._on_position_mode_change(self.opt_position.get())
        self.opt_repeat.set("คลิกจำนวนจำกัด" if s.get("repeat_mode") == "count" else "คลิกไปเรื่อย ๆ จนกว่าจะหยุด")
        self.ent_repeat_count.delete(0, "end"); self.ent_repeat_count.insert(0, str(s.get("repeat_count", 10)))
        hum = s.get("humanizer", {})
        if hum.get("enabled", True):
            self.chk_hum_enabled.select()
        else:
            self.chk_hum_enabled.deselect()
        self.sld_variance.set(hum.get("delay_variance", 0.2) * 100)
        self.sld_jitter.set(hum.get("position_jitter", 3))
        self.sld_misclick.set(hum.get("misclick_chance", 0) * 100)
        if s.get("hotkey"):
            self.hotkey_btn.value = s["hotkey"]
            self.hotkey_btn.configure(text=self.hotkey_btn._label())
            self._rebind_clicker_hotkey(s["hotkey"])

    def _toggle_clicker(self):
        if self.clicker and self.clicker.is_running():
            self.clicker.stop()
        else:
            settings = self._gather_clicker_settings()
            self.clicker = ClickerEngine(settings, on_click=self._on_click_tick, on_stop=self._on_clicker_stopped)
            self.clicker.start()
            self.btn_start_stop.configure(text="■ หยุด (Stop)", fg_color="#c0392b", hover_color="#a93226")
            self.lbl_status.configure(text="สถานะ: กำลังคลิก...")

    def _on_click_tick(self, count):
        self.after(0, lambda: self.lbl_count.configure(text=f"จำนวนคลิก: {count}"))

    def _on_clicker_stopped(self, count):
        def upd():
            self.btn_start_stop.configure(text="▶ เริ่มคลิก (Start)", fg_color="#1f9d55", hover_color="#178a49")
            self.lbl_status.configure(text="สถานะ: หยุดทำงาน")
            self.lbl_count.configure(text=f"จำนวนคลิก: {count}")
        self.after(0, upd)

    def _rebind_clicker_hotkey(self, key_str):
        self.hotkeys.unregister(self._last_clicker_hotkey) if hasattr(self, "_last_clicker_hotkey") else None
        self._last_clicker_hotkey = key_str
        self.hotkeys.register(key_str, lambda: self.after(0, self._toggle_clicker))

    def _save_profile(self):
        name = ctk.CTkInputDialog(text="ตั้งชื่อโปรไฟล์:", title="บันทึกโปรไฟล์").get_input()
        if not name:
            return
        pm.save_profile(name, self._gather_clicker_settings())
        messagebox.showinfo("สำเร็จ", f"บันทึกโปรไฟล์ '{name}' แล้ว")

    def _load_profile(self):
        names = pm.list_profiles()
        if not names:
            messagebox.showwarning("ไม่มีโปรไฟล์", "ยังไม่มีโปรไฟล์ที่บันทึกไว้")
            return
        self._show_pick_list("เลือกโปรไฟล์", names, lambda n: self._apply_clicker_settings(pm.load_profile(n)))

    def _show_pick_list(self, title, names, on_pick):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("300x400")
        for n in names:
            ctk.CTkButton(win, text=n, command=lambda n=n: (on_pick(n), win.destroy())).pack(fill="x", padx=10, pady=4)

    # ============================================================ TAB 2
    def _build_recorder_tab(self):
        t = self.tab_record
        top = ctk.CTkFrame(t)
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="บันทึกการกระทำเมาส์ + คีย์บอร์ดจริง แล้วเล่นซ้ำได้ทันที",
                     font=("", 14, "bold")).pack(anchor="w", pady=5)

        row = ctk.CTkFrame(top, fg_color="transparent")
        row.pack(anchor="w", pady=5)
        self.chk_record_move = ctk.CTkCheckBox(row, text="บันทึกการเคลื่อนเมาส์ด้วย (ไฟล์จะใหญ่ขึ้น)")
        self.chk_record_move.pack(side="left", padx=5)

        self.btn_record = ctk.CTkButton(top, text="⏺ เริ่มบันทึก (Hotkey: F9)", height=40,
                                         fg_color="#c0392b", command=self._toggle_record)
        self.btn_record.pack(pady=10, fill="x")
        self.lbl_record_status = ctk.CTkLabel(top, text="สถานะ: ไม่ได้บันทึก | 0 เหตุการณ์")
        self.lbl_record_status.pack()

        mid = ctk.CTkFrame(t)
        mid.pack(fill="both", expand=True, padx=10, pady=10)
        self.record_list = ctk.CTkTextbox(mid, height=300)
        self.record_list.pack(fill="both", expand=True, padx=5, pady=5)

        bottom = ctk.CTkFrame(t)
        bottom.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(bottom, text="▶ เล่นซ้ำ 1 รอบ", command=lambda: self._play_recorded(1)).pack(side="left", padx=5)
        ctk.CTkButton(bottom, text="🔁 เล่นซ้ำวนไม่จำกัด", command=lambda: self._play_recorded(0)).pack(side="left", padx=5)
        ctk.CTkButton(bottom, text="⏹ หยุดเล่น", command=self._stop_script).pack(side="left", padx=5)
        ctk.CTkButton(bottom, text="💾 บันทึกเป็นไฟล์มาโคร", command=self._save_recorded_as_macro).pack(side="left", padx=5)

        self.hotkeys.register("f9", lambda: self.after(0, self._toggle_record))

    def _toggle_record(self):
        if not self.is_recording:
            self.recorder.start(record_mouse_move=bool(self.chk_record_move.get()))
            self.is_recording = True
            self.btn_record.configure(text="⏹ หยุดบันทึก (Hotkey: F9)")
            self.lbl_record_status.configure(text="สถานะ: 🔴 กำลังบันทึก...")
            self._tick_record_status()
        else:
            events = self.recorder.stop()
            self.is_recording = False
            self.btn_record.configure(text="⏺ เริ่มบันทึก (Hotkey: F9)")
            self.lbl_record_status.configure(text=f"สถานะ: บันทึกเสร็จ | {len(events)} เหตุการณ์")
            self.recorded_script = self.recorder.to_script()
            self.record_list.delete("1.0", "end")
            self.record_list.insert("1.0", json.dumps(self.recorded_script, ensure_ascii=False, indent=2))

    def _tick_record_status(self):
        if self.is_recording:
            self.lbl_record_status.configure(text=f"สถานะ: 🔴 กำลังบันทึก... | {len(self.recorder.events)} เหตุการณ์")
            self.after(200, self._tick_record_status)

    def _play_recorded(self, repeat):
        if not self.recorded_script:
            messagebox.showwarning("ไม่มีข้อมูล", "ยังไม่มีมาโครที่บันทึกไว้")
            return
        script = dict(self.recorded_script)
        script["repeat"] = repeat
        self._run_script_async(script)

    def _save_recorded_as_macro(self):
        if not self.recorded_script:
            messagebox.showwarning("ไม่มีข้อมูล", "ยังไม่มีมาโครที่บันทึกไว้")
            return
        name = ctk.CTkInputDialog(text="ตั้งชื่อไฟล์มาโคร:", title="บันทึกมาโคร").get_input()
        if not name:
            return
        pm.save_macro(name, self.recorded_script)
        messagebox.showinfo("สำเร็จ", f"บันทึกมาโคร '{name}' แล้ว")

    # ============================================================ TAB 3
    def _build_script_tab(self):
        t = self.tab_script
        top = ctk.CTkFrame(t)
        top.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top, text="Custom Script Engine — เขียนมาโครเองแบบละเอียด (JSON DSL)",
                     font=("", 14, "bold")).pack(anchor="w")

        btn_row = ctk.CTkFrame(t, fg_color="transparent")
        btn_row.pack(fill="x", padx=10)
        ctk.CTkButton(btn_row, text="📄 ตัวอย่างสคริปต์", command=self._insert_example_script).pack(side="left", padx=3)
        ctk.CTkButton(btn_row, text="✅ ตรวจสอบ", command=self._validate_script).pack(side="left", padx=3)
        ctk.CTkButton(btn_row, text="▶ รันสคริปต์", fg_color="#1f9d55", command=self._run_editor_script).pack(side="left", padx=3)
        ctk.CTkButton(btn_row, text="⏹ หยุด", fg_color="#c0392b", command=self._stop_script).pack(side="left", padx=3)
        ctk.CTkButton(btn_row, text="💾 บันทึก", command=self._save_editor_script).pack(side="left", padx=3)
        ctk.CTkButton(btn_row, text="📂 เปิดไฟล์", command=self._load_editor_script).pack(side="left", padx=3)

        self.script_editor = ctk.CTkTextbox(t, height=380, font=("Consolas", 12))
        self.script_editor.pack(fill="both", expand=True, padx=10, pady=10)
        self._insert_example_script()

        self.lbl_script_status = ctk.CTkLabel(t, text="")
        self.lbl_script_status.pack(anchor="w", padx=10)

        help_txt = ("รองรับคำสั่ง (action.type): click, move, key, wait, type_text, scroll, "
                    "loop_start{count|ไม่ใส่=วนไม่จำกัด}, loop_end")
        ctk.CTkLabel(t, text=help_txt, text_color="#888").pack(anchor="w", padx=10, pady=(0, 5))

    def _insert_example_script(self):
        example = {
            "name": "ตัวอย่าง: คลิกสลับ 2 จุด 5 รอบ",
            "hotkey": "f7",
            "repeat": 1,
            "humanizer": Humanizer(enabled=True, delay_variance=0.2, position_jitter=3).to_dict(),
            "actions": [
                {"type": "loop_start", "count": 5},
                {"type": "click", "x": 400, "y": 400, "button": "left", "clicks": 1},
                {"type": "wait", "min": 0.2, "max": 0.5},
                {"type": "click", "x": 600, "y": 400, "button": "left", "clicks": 1},
                {"type": "wait", "min": 0.2, "max": 0.5},
                {"type": "loop_end"},
                {"type": "type_text", "text": "เสร็จแล้ว!"},
            ],
        }
        self.script_editor.delete("1.0", "end")
        self.script_editor.insert("1.0", json.dumps(example, ensure_ascii=False, indent=2))

    def _get_editor_script(self):
        raw = self.script_editor.get("1.0", "end")
        return json.loads(raw)

    def _validate_script(self):
        try:
            script = self._get_editor_script()
            ok, err = self.script_engine.validate(script)
            if ok:
                self.lbl_script_status.configure(text="✅ สคริปต์ถูกต้อง", text_color="#2ecc71")
            else:
                self.lbl_script_status.configure(text=f"❌ {err}", text_color="#e74c3c")
        except json.JSONDecodeError as e:
            self.lbl_script_status.configure(text=f"❌ JSON ผิดรูปแบบ: {e}", text_color="#e74c3c")

    def _run_editor_script(self):
        try:
            script = self._get_editor_script()
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON ผิดรูปแบบ", str(e))
            return
        self._run_script_async(script)

    def _run_script_async(self, script):
        self._stop_script()
        self.script_stop_event = threading.Event()

        def target():
            try:
                self.script_engine.run(script, self.script_stop_event)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("เกิดข้อผิดพลาด", str(e)))

        self.script_thread = threading.Thread(target=target, daemon=True)
        self.script_thread.start()
        self.lbl_script_status.configure(text="▶ กำลังรันสคริปต์... (กด ESC เพื่อหยุดฉุกเฉิน)", text_color="#3498db")

    def _stop_script(self):
        self.script_stop_event.set()
        if self.script_thread and self.script_thread.is_alive():
            self.script_thread.join(timeout=0.5)
        self.lbl_script_status.configure(text="⏹ หยุดแล้ว", text_color="#888")

    def _save_editor_script(self):
        try:
            script = self._get_editor_script()
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON ผิดรูปแบบ", str(e))
            return
        name = ctk.CTkInputDialog(text="ตั้งชื่อไฟล์สคริปต์:", title="บันทึกสคริปต์").get_input()
        if not name:
            return
        pm.save_macro(name, script)
        messagebox.showinfo("สำเร็จ", f"บันทึกสคริปต์ '{name}' แล้ว")

    def _load_editor_script(self):
        names = pm.list_macros()
        if not names:
            messagebox.showwarning("ไม่มีไฟล์", "ยังไม่มีไฟล์มาโคร/สคริปต์ที่บันทึกไว้")
            return
        def apply(n):
            script = pm.load_macro(n)
            self.script_editor.delete("1.0", "end")
            self.script_editor.insert("1.0", json.dumps(script, ensure_ascii=False, indent=2))
        self._show_pick_list("เลือกไฟล์สคริปต์", names, apply)

    # ============================================================ TAB 4
    def _build_settings_tab(self):
        t = self.tab_settings
        ctk.CTkLabel(t, text="ธีม", font=("", 15, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkOptionMenu(t, values=["Dark", "Light", "System"],
                          command=lambda v: ctk.set_appearance_mode(v)).pack(anchor="w", padx=15)

        ctk.CTkLabel(t, text="Failsafe", font=("", 15, "bold")).pack(anchor="w", padx=15, pady=(20, 5))
        ctk.CTkLabel(t, text=f"ปุ่ม {FAILSAFE_KEY.upper()} จะหยุดการคลิก/มาโคร/สคริปต์ทั้งหมดทันที (เปิดใช้งานถาวร)"
                     ).pack(anchor="w", padx=15)

        ctk.CTkLabel(t, text="จัดการโปรไฟล์และไฟล์มาโคร", font=("", 15, "bold")).pack(anchor="w", padx=15, pady=(20, 5))
        row = ctk.CTkFrame(t, fg_color="transparent")
        row.pack(anchor="w", padx=15)
        ctk.CTkButton(row, text="เปิดโฟลเดอร์โปรไฟล์", command=lambda: self._open_folder(pm.PROFILES_DIR)).pack(side="left", padx=3)
        ctk.CTkButton(row, text="เปิดโฟลเดอร์มาโคร", command=lambda: self._open_folder(pm.MACROS_DIR)).pack(side="left", padx=3)

        ctk.CTkLabel(t, text="เกี่ยวกับ", font=("", 15, "bold")).pack(anchor="w", padx=15, pady=(20, 5))
        about = ("AutoClicker Pro\n"
                 "รองรับ: Auto Click ปุ่มไหนก็ได้ / Macro Recorder / Custom Script Engine / "
                 "Anti-Ban Humanizer / Failsafe / Profile Manager\n"
                 "สร้างด้วย Python + customtkinter + pynput")
        ctk.CTkLabel(t, text=about, justify="left").pack(anchor="w", padx=15)

    def _open_folder(self, path):
        import os, subprocess, sys as _sys
        try:
            if _sys.platform.startswith("win"):
                os.startfile(path)
            elif _sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showinfo("โฟลเดอร์", f"{path}\n({e})")

    # ================================================================ core
    def _start_global_failsafe(self):
        def emergency_stop():
            if self.clicker:
                self.clicker.stop()
            self.script_stop_event.set()
            if self.is_recording:
                self._toggle_record()

        self.hotkeys.register(FAILSAFE_KEY, lambda: self.after(0, emergency_stop))
        self.hotkeys.start()

    def on_close(self):
        try:
            if self.clicker:
                self.clicker.stop()
            self.script_stop_event.set()
            self.hotkeys.stop()
        finally:
            self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
