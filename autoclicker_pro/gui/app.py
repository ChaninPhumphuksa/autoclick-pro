import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import pyautogui

# --- Dictionary ระบบ 2 ภาษา ---
LOCALES = {
    "TH": {
        "title": "AutoClicker Pro",
        "start": "เริ่มทำงาน",
        "stop": "หยุดทำงาน",
        "status_idle": "สถานะ: พร้อมใช้งาน",
        "status_running": "สถานะ: กำลังคลิก...",
        "settings": "ตั้งค่าการทำงาน",
        "hotkey_label": "ปุ่มลัด (Hotkey):",
        "press_key": "กดปุ่มที่ต้องการ...",
        "interval_label": "ระยะห่างการคลิก (วินาที):",
        "click_type": "ประเภทการคลิก:",
        "left": "คลิกซ้าย",
        "right": "คลิกขวา",
        "lang_btn": "English",
        "pos_mode_label": "ตำแหน่งการคลิก:",
        "pos_current": "ตำแหน่งเมาส์ปัจจุบัน",
        "pos_custom": "ระบุพิกัด (X, Y)",
        "pick_btn": "🎯 เลือกพิกัดบนจอ",
        "picking_msg": "คลิกจุดที่ต้องการบนหน้าจอ..."
    },
    "EN": {
        "title": "AutoClicker Pro",
        "start": "Start",
        "stop": "Stop",
        "status_idle": "Status: Idle",
        "status_running": "Status: Running...",
        "settings": "Settings",
        "hotkey_label": "Custom Hotkey:",
        "press_key": "Press any key...",
        "interval_label": "Click Interval (sec):",
        "click_type": "Click Button:",
        "left": "Left Click",
        "right": "Right Click",
        "lang_btn": "ไทย",
        "pos_mode_label": "Click Position:",
        "pos_current": "Current Location",
        "pos_custom": "Fixed Location (X, Y)",
        "pick_btn": "🎯 Pick Location",
        "picking_msg": "Click anywhere on screen..."
    }
}

class ColorfulAutoClicker:
    def __init__(self, root):
        self.root = root
        self.current_lang = "TH"
        
        # ลบ Toolbar/Titlebar เดิม
        self.root.overrideredirect(True)
        self.root.geometry("380x600")
        
        # สถานะการทำงาน
        self.is_running = False
        self.hotkey = "f6"
        self.click_interval = 0.1
        self.click_button = "left"
        self.use_custom_pos = tk.BooleanVar(value=False)
        self.custom_x = 0
        self.custom_y = 0
        
        # Palette สี Colorful & Vibrant
        self.colors = {
            "bg": "#1e1e2e",
            "card": "#2a2a3c",
            "primary": "#8a2be2",
            "accent": "#00f2fe",
            "text": "#ffffff",
            "text_sub": "#a6adc8",
            "danger": "#ff4976",
            "success": "#00e676"
        }
        
        self.root.configure(bg=self.colors["bg"])
        self.setup_ui()
        self.bind_hotkeys()

    def setup_ui(self):
        # Header แบบ Custom (ไม่มี Toolbar ระบบ)
        header = tk.Frame(self.root, bg=self.colors["primary"], height=40)
        header.pack(fill="x", side="top")
        
        title_lbl = tk.Label(header, text="✨ AutoClicker Pro", bg=self.colors["primary"], fg="#fff", font=("Helvetica", 12, "bold"))
        title_lbl.pack(side="left", padx=15, pady=8)
        
        close_btn = tk.Button(header, text="✕", bg=self.colors["primary"], fg="#fff", bd=0, font=("Helvetica", 12, "bold"), command=self.root.destroy, activebackground=self.colors["danger"])
        close_btn.pack(side="right", padx=10)

        # สวิตช์เปลี่ยนภาษา (TH/EN)
        self.lang_btn = tk.Button(header, text=LOCALES[self.current_lang]["lang_btn"], bg=self.colors["accent"], fg="#000", bd=0, font=("Helvetica", 9, "bold"), command=self.toggle_language)
        self.lang_btn.pack(side="right", padx=5)

        # Main Container Panel
        main_card = tk.Frame(self.root, bg=self.colors["card"], bd=0)
        main_card.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Section: Custom Hotkey ---
        self.lbl_hotkey_title = tk.Label(main_card, text=LOCALES[self.current_lang]["hotkey_label"], bg=self.colors["card"], fg=self.colors["text_sub"], font=("Helvetica", 10))
        self.lbl_hotkey_title.pack(anchor="w", padx=15, pady=(10, 3))
        
        self.btn_set_hotkey = tk.Button(main_card, text=self.hotkey.upper(), bg=self.colors["primary"], fg="#fff", bd=0, font=("Helvetica", 10, "bold"), height=2, command=self.capture_custom_hotkey)
        self.btn_set_hotkey.pack(fill="x", padx=15)

        # --- Section: Interval ---
        self.lbl_interval = tk.Label(main_card, text=LOCALES[self.current_lang]["interval_label"], bg=self.colors["card"], fg=self.colors["text_sub"], font=("Helvetica", 10))
        self.lbl_interval.pack(anchor="w", padx=15, pady=(10, 3))
        
        self.entry_interval = tk.Entry(main_card, bg=self.colors["bg"], fg=self.colors["accent"], bd=1, insertbackground="#fff", font=("Helvetica", 11, "bold"), justify="center")
        self.entry_interval.insert(0, "0.1")
        self.entry_interval.pack(fill="x", padx=15)

        # --- Section: Location Picker (เพิ่มใหม่) ---
        self.lbl_pos_title = tk.Label(main_card, text=LOCALES[self.current_lang]["pos_mode_label"], bg=self.colors["card"], fg=self.colors["text_sub"], font=("Helvetica", 10))
        self.lbl_pos_title.pack(anchor="w", padx=15, pady=(10, 3))

        self.rb_current = tk.Radiobutton(main_card, text=LOCALES[self.current_lang]["pos_current"], variable=self.use_custom_pos, value=False, bg=self.colors["card"], fg=self.colors["text"], selectcolor=self.colors["bg"], font=("Helvetica", 9), command=self.toggle_pos_inputs)
        self.rb_current.pack(anchor="w", padx=20)

        self.rb_custom = tk.Radiobutton(main_card, text=LOCALES[self.current_lang]["pos_custom"], variable=self.use_custom_pos, value=True, bg=self.colors["card"], fg=self.colors["text"], selectcolor=self.colors["bg"], font=("Helvetica", 9), command=self.toggle_pos_inputs)
        self.rb_custom.pack(anchor="w", padx=20)

        pos_frame = tk.Frame(main_card, bg=self.colors["card"])
        pos_frame.pack(fill="x", padx=15, pady=5)

        self.entry_x = tk.Entry(pos_frame, bg=self.colors["bg"], fg="#fff", bd=1, width=6, font=("Helvetica", 10), justify="center", state="disabled")
        self.entry_x.pack(side="left", padx=(5, 5))
        self.entry_x.insert(0, "0")

        self.entry_y = tk.Entry(pos_frame, bg=self.colors["bg"], fg="#fff", bd=1, width=6, font=("Helvetica", 10), justify="center", state="disabled")
        self.entry_y.pack(side="left", padx=(0, 10))
        self.entry_y.insert(0, "0")

        self.btn_pick_pos = tk.Button(pos_frame, text=LOCALES[self.current_lang]["pick_btn"], bg=self.colors["accent"], fg="#000", bd=0, font=("Helvetica", 9, "bold"), state="disabled", command=self.pick_location)
        self.btn_pick_pos.pack(side="right", fill="x", expand=True)

        # --- Status & Control Action ---
        self.lbl_status = tk.Label(main_card, text=LOCALES[self.current_lang]["status_idle"], bg=self.colors["card"], fg=self.colors["accent"], font=("Helvetica", 11, "bold"))
        self.lbl_status.pack(pady=15)

        self.btn_action = tk.Button(main_card, text=LOCALES[self.current_lang]["start"], bg=self.colors["success"], fg="#000", bd=0, font=("Helvetica", 12, "bold"), height=2, command=self.toggle_clicking)
        self.btn_action.pack(fill="x", padx=15, side="bottom", pady=15)

    def toggle_pos_inputs(self):
        state = "normal" if self.use_custom_pos.get() else "disabled"
        self.entry_x.config(state=state)
        self.entry_y.config(state=state)
        self.btn_pick_pos.config(state=state)

    def pick_location(self):
        self.root.withdraw()  # ซ่อนหน้าต่างชั่วคราวเพื่อเลือกจุดบนจอ
        time.sleep(0.3)
        
        # รอกดคลิกเลือกตำแหน่ง
        def on_click(x, y, button, pressed):
            if pressed:
                self.custom_x = x
                self.custom_y = y
                return False  # หยุดฟัง event

        from pynput import mouse
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

        # อัปเดตพิกัดกลับเข้าช่องกรอก
        self.entry_x.config(state="normal")
        self.entry_y.config(state="normal")
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(self.custom_x))
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(self.custom_y))
        
        self.root.deiconify()  # แสดงหน้าต่างกลับมา

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "TH" else "TH"
        loc = LOCALES[self.current_lang]
        
        self.lang_btn.config(text=loc["lang_btn"])
        self.lbl_hotkey_title.config(text=loc["hotkey_label"])
        self.lbl_interval.config(text=loc["interval_label"])
        self.lbl_pos_title.config(text=loc["pos_mode_label"])
        self.rb_current.config(text=loc["pos_current"])
        self.rb_custom.config(text=loc["pos_custom"])
        self.btn_pick_pos.config(text=loc["pick_btn"])
        self.btn_action.config(text=loc["stop"] if self.is_running else loc["start"])
        self.lbl_status.config(text=loc["status_running"] if self.is_running else loc["status_idle"])

    def capture_custom_hotkey(self):
        self.btn_set_hotkey.config(text=LOCALES[self.current_lang]["press_key"], bg=self.colors["accent"], fg="#000")
        self.root.update()
        
        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            self.hotkey = event.name
            self.btn_set_hotkey.config(text=self.hotkey.upper(), bg=self.colors["primary"], fg="#fff")
            self.bind_hotkeys()

    def bind_hotkeys(self):
        keyboard.unhook_all()
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

    def toggle_clicking(self):
        self.is_running = not self.is_running
        loc = LOCALES[self.current_lang]
        
        if self.is_running:
            self.btn_action.config(text=loc["stop"], bg=self.colors["danger"], fg="#fff")
            self.lbl_status.config(text=loc["status_running"], fg=self.colors["danger"])
            threading.Thread(target=self.run_auto_click, daemon=True).start()
        else:
            self.btn_action.config(text=loc["start"], bg=self.colors["success"], fg="#000")
            self.lbl_status.config(text=loc["status_idle"], fg=self.colors["accent"])

    def run_auto_click(self):
        try:
            interval = float(self.entry_interval.get())
        except ValueError:
            interval = 0.1

        use_custom = self.use_custom_pos.get()
        if use_custom:
            try:
                x = int(self.entry_x.get())
                y = int(self.entry_y.get())
            except ValueError:
                x, y = pyautogui.position()
            
        while self.is_running:
            if use_custom:
                pyautogui.click(x=x, y=y, button=self.click_button)
            else:
                pyautogui.click(button=self.click_button)
            time.sleep(interval)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorfulAutoClicker(root)
    root.mainloop()
