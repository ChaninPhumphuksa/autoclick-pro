# -*- coding: utf-8 -*-
"""
gui/i18n.py
===========
ระบบสองภาษา (ไทย/อังกฤษ) ของโปรแกรม เรียกใช้ผ่านฟังก์ชัน t("คีย์", ตัวแปร=...)
สลับภาษาได้ทันทีระหว่างใช้งานด้วยปุ่ม TH/EN โดยไม่ต้องปิดโปรแกรมใหม่
"""

LANG_TH = "th"
LANG_EN = "en"

_current_lang = LANG_TH

TRANSLATIONS = {
    # ---------- ทั่วไป / หัวโปรแกรม ----------
    "window_title": {"th": "คลิกอัตโนมัติ", "en": "Auto Clicker"},
    "header_title": {"th": " คลิกอัตโนมัติ", "en": " Auto Clicker"},
    "stop_all": {"th": "⛔  หยุดทุกอย่างทันที", "en": "⛔  Stop Everything"},
    "status_ready": {"th": "พร้อมใช้งาน", "en": "Ready"},
    "hint_bar": {
        "th": "ปุ่มลัด:  {click} คลิกอัตโนมัติ   |   {play} เล่นชุดคำสั่ง   |   {record} บันทึกชุดคำสั่ง   |   ESC หยุดทั้งหมด",
        "en": "Shortcuts:  {click} Auto Click   |   {play} Play Set   |   {record} Record Set   |   ESC Stop All",
    },
    "not_ready_title": {"th": "ยังใช้งานไม่ได้เต็มรูปแบบ", "en": "Not Fully Ready"},
    "not_ready_msg": {"th": "โปรแกรมต้องการตัวช่วยเพิ่มเติมก่อนใช้งาน กรุณาติดตั้งตามคู่มือที่แนบมา",
                       "en": "A few components still need installing — see the included setup guide."},

    # ---------- แท็บ ----------
    "tab_autoclick": {"th": "  คลิกอัตโนมัติ  ", "en": "  Auto Click  "},
    "tab_macro": {"th": "  ชุดคำสั่ง  ", "en": "  Command Set  "},
    "tab_settings": {"th": "  ตั้งค่า  ", "en": "  Settings  "},

    # ---------- แท็บคลิกอัตโนมัติ ----------
    "sec_frequency": {"th": "⏱  คลิกถี่แค่ไหน", "en": "⏱  Click Frequency"},
    "unit_hours": {"th": "ชั่วโมง", "en": "hr"},
    "unit_minutes": {"th": "นาที", "en": "min"},
    "unit_seconds": {"th": "วินาที", "en": "sec"},
    "unit_ms": {"th": "มิลลิวินาที", "en": "ms"},
    "jitter_label": {"th": "ให้จังหวะคลิกดูเป็นธรรมชาติ ไม่ตรงเป๊ะทุกครั้ง (บวกลบ):",
                      "en": "Make click timing feel natural, not exact every time (±):"},

    "sec_button": {"th": "🖱  ใช้ปุ่มเมาส์ไหน", "en": "🖱  Mouse Button"},
    "mouse_left": {"th": "ปุ่มซ้าย", "en": "Left"},
    "mouse_right": {"th": "ปุ่มขวา", "en": "Right"},
    "mouse_middle": {"th": "ปุ่มกลาง", "en": "Middle"},
    "double_click": {"th": "คลิกสองครั้งติดกัน (ดับเบิลคลิก)", "en": "Double-click"},

    "sec_position": {"th": "📍  คลิกที่ตรงไหน", "en": "📍  Click Location"},
    "pos_current": {"th": "คลิกตรงที่เมาส์อยู่ตอนกดเริ่ม", "en": "Click wherever the mouse is when started"},
    "pos_fixed": {"th": "คลิกตำแหน่งเดิมทุกครั้ง:", "en": "Always click this exact spot:"},
    "capture_button": {"th": "📍 จิ้มตำแหน่งจากเมาส์ (3 วิ)", "en": "📍 Grab from mouse (3s)"},
    "position_picker_btn": {"th": "🗂 ตัวช่วยจับพิกัด", "en": "🗂 Position Picker"},
    "save_position_btn": {"th": "💾 บันทึกตำแหน่งนี้ไว้ใช้อีก", "en": "💾 Save this position"},

    "sec_count": {"th": "🔢  คลิกกี่ครั้ง", "en": "🔢  Click Count"},
    "count_unlimited": {"th": "คลิกไปเรื่อย ๆ จนกว่าจะกดหยุดเอง", "en": "Keep clicking until I stop it"},
    "count_limited": {"th": "คลิกแค่จำนวนนี้แล้วหยุดเอง:", "en": "Stop automatically after this many:"},
    "unit_times": {"th": "ครั้ง", "en": "clicks"},

    "start_autoclick": {"th": "▶  เริ่มคลิกอัตโนมัติ", "en": "▶  Start Auto Click"},
    "stop_autoclick": {"th": "⏹  หยุดคลิกอัตโนมัติ", "en": "⏹  Stop Auto Click"},

    # ---------- แท็บชุดคำสั่ง ----------
    "macro_intro": {"th": "ชุดคำสั่งคือลำดับการคลิก/ลากเมาส์/กดปุ่มที่คุณตั้งไว้ล่วงหน้า แล้วให้โปรแกรมทำซ้ำให้ทีหลัง",
                     "en": "A command set is a sequence of clicks/drags/keys you set up once, then replay anytime."},
    "macro_step1": {"th": "① บันทึกจากสิ่งที่คุณทำจริง", "en": "① Record what you actually do"},
    "start_recording": {"th": "⏺  เริ่มบันทึก", "en": "⏺  Start Recording"},
    "stop_recording": {"th": "⏹  หยุดบันทึก", "en": "⏹  Stop Recording"},
    "macro_step2": {"th": "② หรือสร้าง/แก้ไขเองทีละขั้นตอน", "en": "② Or build/edit it step by step"},
    "col_order": {"th": "ลำดับ", "en": "#"},
    "col_action": {"th": "ทำอะไร", "en": "Action"},
    "col_detail": {"th": "รายละเอียด", "en": "Detail"},
    "col_delay": {"th": "รอกี่วิ", "en": "Wait (s)"},
    "add_click": {"th": "+ คลิก", "en": "+ Click"},
    "add_drag": {"th": "+ ลาก", "en": "+ Drag"},
    "add_key": {"th": "+ กดปุ่ม", "en": "+ Key"},
    "add_wait": {"th": "+ รอ", "en": "+ Wait"},
    "edit": {"th": "แก้ไข", "en": "Edit"},
    "delete": {"th": "ลบ", "en": "Delete"},
    "move_up": {"th": "▲ เลื่อนขึ้น", "en": "▲ Move Up"},
    "move_down": {"th": "▼ เลื่อนลง", "en": "▼ Move Down"},
    "clear_all": {"th": "ล้างทั้งหมด", "en": "Clear All"},
    "type_click": {"th": "คลิก", "en": "Click"},
    "type_drag": {"th": "ลาก", "en": "Drag"},
    "type_key": {"th": "กดปุ่ม", "en": "Key"},
    "type_wait": {"th": "รอ", "en": "Wait"},
    "button_label_short": {"th": "ปุ่ม", "en": "btn"},
    "key_label_short": {"th": "กดปุ่ม", "en": "Press"},

    "macro_step3": {"th": "③ เล่นซ้ำกี่รอบ", "en": "③ How many times to repeat"},
    "loop_unlimited": {"th": "วนเล่นไปเรื่อย ๆ จนกว่าจะกดหยุดเอง", "en": "Loop forever until I stop it"},
    "loop_limited": {"th": "เล่นแค่:", "en": "Play only:"},
    "unit_rounds": {"th": "รอบ", "en": "times"},
    "start_play": {"th": "▶  เริ่มเล่นชุดคำสั่ง", "en": "▶  Play Command Set"},
    "stop_play": {"th": "⏹  หยุดเล่นชุดคำสั่ง", "en": "⏹  Stop Playing"},
    "macro_step4": {"th": "④ ชุดคำสั่งที่เคยบันทึกไว้", "en": "④ Saved command sets"},
    "open_selected": {"th": "เปิดใช้", "en": "Open"},
    "delete_selected": {"th": "ลบทิ้ง", "en": "Delete"},
    "name_this_set": {"th": "ตั้งชื่อชุดคำสั่งนี้:", "en": "Name this set:"},
    "save_for_later": {"th": "บันทึกไว้ใช้ทีหลัง", "en": "Save for later"},
    "import_from_file": {"th": "📂 นำเข้าจากไฟล์", "en": "📂 Import from file"},
    "export_to_file": {"th": "💾 ส่งออกเป็นไฟล์", "en": "💾 Export to file"},

    # ---------- แท็บตั้งค่า ----------
    "sec_hotkeys": {"th": "⌨  ปุ่มลัดบนคีย์บอร์ด", "en": "⌨  Keyboard Shortcuts"},
    "hotkeys_desc": {"th": "กดปุ่ม \"ตั้งปุ่มเอง\" แล้วกดปุ่มบนคีย์บอร์ดที่ต้องการ ใช้ปุ่มไหนก็ได้ตามใจ",
                      "en": "Click \"Set custom key\", then press any key on your keyboard."},
    "hotkey_click_label": {"th": "เริ่ม/หยุด คลิกอัตโนมัติ:", "en": "Start/Stop Auto Click:"},
    "hotkey_play_label": {"th": "เริ่ม/หยุด เล่นชุดคำสั่ง:", "en": "Start/Stop Playing:"},
    "hotkey_record_label": {"th": "เริ่ม/หยุด บันทึกชุดคำสั่ง:", "en": "Start/Stop Recording:"},
    "set_custom_key": {"th": "🖊 ตั้งปุ่มเอง", "en": "🖊 Set custom key"},
    "esc_note": {"th": "* ปุ่ม ESC ใช้หยุดทุกอย่างฉุกเฉินได้เสมอ ไม่สามารถเปลี่ยนได้",
                 "en": "* ESC always works as the emergency stop and can't be changed."},

    "sec_language": {"th": "🌐  ภาษา", "en": "🌐  Language"},
    "language_desc": {"th": "เลือกภาษาที่ใช้แสดงผลในโปรแกรม", "en": "Choose the display language for the app"},

    "sec_system": {"th": "🖥  การเปิด-ปิดโปรแกรม", "en": "🖥  Startup & Closing"},
    "start_with_windows": {"th": "เปิดโปรแกรมนี้ให้อัตโนมัติทุกครั้งที่เปิดเครื่อง",
                            "en": "Launch this program automatically when Windows starts"},
    "windows_only_note": {"th": "(ใช้ได้เฉพาะเครื่อง Windows เท่านั้น)", "en": "(Windows only)"},
    "minimize_to_tray": {"th": "เมื่อกดปิดหน้าต่าง ให้ซ่อนไว้เบื้องหลังแทนการปิดโปรแกรม",
                          "en": "When closing the window, hide it instead of quitting"},
    "tray_unavailable": {"th": "* ยังไม่พร้อมใช้งานฟีเจอร์ซ่อนเบื้องหลัง กรุณาติดตั้งตามคู่มือที่แนบมา",
                          "en": "* Background hiding isn't available yet — see the included setup guide."},
    "font_not_found": {"th": "💡 ตอนนี้ยังไม่พบฟอนต์ Prompt ในเครื่อง โปรแกรมจึงใช้ฟอนต์สำรองแทนไปก่อน "
                             "ดาวน์โหลดและติดตั้งฟอนต์ Prompt แล้วเปิดโปรแกรมใหม่ เพื่อหน้าตาที่สวยขึ้น",
                        "en": "💡 The Prompt font wasn't found, so a fallback font is used. Install the "
                              "Prompt font and reopen the app for the intended look."},

    "sec_history": {"th": "📋  ประวัติการทำงาน", "en": "📋  Activity History"},
    "clear_history": {"th": "ล้างประวัติ", "en": "Clear History"},
    "about_button": {"th": "ℹ️  เกี่ยวกับโปรแกรม", "en": "ℹ️  About"},

    # ---------- กล่องโต้ตอบขั้นตอน ----------
    "step_title_click": {"th": "เพิ่มขั้นตอน: คลิกที่ตำแหน่งนี้", "en": "Add Step: Click at Position"},
    "step_title_drag": {"th": "เพิ่มขั้นตอน: ลากเมาส์", "en": "Add Step: Drag Mouse"},
    "step_title_key": {"th": "เพิ่มขั้นตอน: กดปุ่มนี้", "en": "Add Step: Press a Key"},
    "step_title_wait": {"th": "เพิ่มขั้นตอน: รอสักครู่", "en": "Add Step: Wait"},
    "delay_before_label": {"th": "รอกี่วินาทีก่อนทำขั้นตอนนี้:", "en": "Seconds to wait before this step:"},
    "pos_x_label": {"th": "ตำแหน่งแนวนอน (X):", "en": "Horizontal position (X):"},
    "pos_y_label": {"th": "ตำแหน่งแนวตั้ง (Y):", "en": "Vertical position (Y):"},
    "mouse_button_label": {"th": "ปุ่มเมาส์:", "en": "Mouse button:"},
    "capture_from_mouse": {"th": "📍 จิ้มตำแหน่งจากเมาส์ (3 วิ)", "en": "📍 Grab from mouse (3s)"},
    "pick_saved_position": {"th": "🗂 เลือกจากที่บันทึกไว้", "en": "🗂 Choose from saved"},
    "drag_start_label": {"th": "จุดเริ่มลาก:", "en": "Drag start point:"},
    "drag_end_label": {"th": "จุดปล่อยลาก:", "en": "Drag end point:"},
    "capture_start": {"th": "📍 จิ้มจุดเริ่ม (3 วิ)", "en": "📍 Grab start (3s)"},
    "capture_end": {"th": "📍 จิ้มจุดปล่อย (3 วิ)", "en": "📍 Grab end (3s)"},
    "drag_duration_label": {"th": "ลากนานกี่วินาที:", "en": "Drag duration (seconds):"},
    "key_char_label": {"th": "พิมพ์ตัวอักษรที่ต้องการกด (เช่น a, 1):", "en": "Type the character to press (e.g. a, 1):"},
    "key_special_label": {"th": "หรือเลือกปุ่มพิเศษ:", "en": "Or choose a special key:"},
    "key_none_selected": {"th": "— ไม่เลือก —", "en": "— none —"},
    "key_space": {"th": "เว้นวรรค (Space)", "en": "Space"},
    "key_enter": {"th": "ตอบตกลง (Enter)", "en": "Enter"},
    "key_tab": {"th": "แท็บ (Tab)", "en": "Tab"},
    "key_backspace": {"th": "ลบถอยหลัง (Backspace)", "en": "Backspace"},
    "key_up": {"th": "ลูกศรขึ้น", "en": "Arrow Up"},
    "key_down": {"th": "ลูกศรลง", "en": "Arrow Down"},
    "key_left": {"th": "ลูกศรซ้าย", "en": "Arrow Left"},
    "key_right": {"th": "ลูกศรขวา", "en": "Arrow Right"},
    "key_shift": {"th": "Shift", "en": "Shift"},
    "key_ctrl": {"th": "Ctrl", "en": "Ctrl"},
    "key_alt": {"th": "Alt", "en": "Alt"},
    "save": {"th": "บันทึก", "en": "Save"},
    "cancel": {"th": "ยกเลิก", "en": "Cancel"},
    "invalid_input_title": {"th": "กรอกไม่ถูกต้อง", "en": "Invalid Input"},
    "invalid_delay_msg": {"th": "ช่องเวลารอ ต้องเป็นตัวเลขเท่านั้น", "en": "The wait time must be a number."},
    "invalid_xy_msg": {"th": "ตำแหน่ง X และ Y ต้องเป็นตัวเลขเท่านั้น", "en": "X and Y must both be numbers."},
    "invalid_drag_msg": {"th": "ตำแหน่งและระยะเวลาต้องเป็นตัวเลขเท่านั้น", "en": "Position and duration must be numbers."},
    "invalid_key_msg": {"th": "กรุณาระบุปุ่มที่ต้องการกด", "en": "Please specify a key to press."},
    "capture_countdown": {"th": "เตรียมตัว... อีก {n} วินาที (ย้ายเมาส์ไปตำแหน่งที่ต้องการไว้ก่อน)",
                           "en": "Get ready... {n}s left (move the mouse where you want first)"},
    "capture_done": {"th": "จิ้มตำแหน่งแล้ว ✓ ({x}, {y})", "en": "Captured ✓ ({x}, {y})"},
    "picked_done": {"th": "เลือกตำแหน่งแล้ว ✓ ({x}, {y})", "en": "Selected ✓ ({x}, {y})"},

    # ---------- ตัวช่วยจับพิกัด ----------
    "position_picker_title": {"th": "🗂 ตัวช่วยจับพิกัด", "en": "🗂 Position Picker"},
    "position_picker_desc": {"th": "บันทึกตำแหน่งบนหน้าจอไว้เป็นชื่อที่จำง่าย แล้วเลือกใช้ซ้ำได้ทุกที่ในโปรแกรม",
                              "en": "Save screen positions with a memorable name and reuse them anywhere."},
    "col_name": {"th": "ชื่อตำแหน่ง", "en": "Name"},
    "add_new_position": {"th": "➕ จับตำแหน่งใหม่", "en": "➕ Capture New Position"},
    "use_this_position": {"th": "✓ ใช้ตำแหน่งนี้", "en": "✓ Use This Position"},
    "close": {"th": "ปิด", "en": "Close"},
    "capturing_title": {"th": "กำลังจับตำแหน่ง", "en": "Capturing Position"},
    "preparing": {"th": "เตรียมตัว...", "en": "Get ready..."},
    "move_mouse_countdown": {"th": "ย้ายเมาส์ไปตำแหน่งที่ต้องการ... อีก {n} วินาที",
                              "en": "Move the mouse where you want... {n}s left"},
    "name_position_title": {"th": "ตั้งชื่อตำแหน่ง", "en": "Name This Position"},
    "name_position_prompt": {"th": "จับตำแหน่งได้แล้ว: ({x}, {y})\nตั้งชื่อตำแหน่งนี้ (เช่น ปุ่มยืนยัน):",
                              "en": "Captured: ({x}, {y})\nName this position (e.g. Confirm Button):"},
    "no_selection_title": {"th": "ยังไม่ได้เลือก", "en": "Nothing Selected"},
    "no_selection_msg": {"th": "กรุณาเลือกตำแหน่งจากรายการก่อน", "en": "Please select a position from the list first."},
    "confirm": {"th": "ยืนยัน", "en": "Confirm"},
    "confirm_delete_position": {"th": "ลบตำแหน่ง '{name}' ทิ้งหรือไม่?", "en": "Delete position '{name}'?"},
    "not_ready_generic": {"th": "ยังใช้งานไม่ได้", "en": "Not Available"},
    "needs_extra_setup": {"th": "ฟีเจอร์นี้ต้องติดตั้งตัวช่วยเพิ่มเติมก่อน", "en": "This feature needs an extra component installed first."},

    # ---------- ตั้งปุ่มลัดเอง ----------
    "hotkey_capture_title": {"th": "ตั้งปุ่มลัดเอง", "en": "Set Custom Shortcut"},
    "hotkey_capture_prompt": {"th": "กดปุ่มที่ต้องการตั้งเป็นปุ่มลัด...", "en": "Press the key you want to use..."},
    "hotkey_esc_reserved": {"th": "ปุ่ม ESC สงวนไว้แล้ว กรุณากดปุ่มอื่น", "en": "ESC is reserved. Please press another key."},
    "hotkey_conflict_title": {"th": "ปุ่มนี้ถูกใช้แล้ว", "en": "Key Already In Use"},
    "hotkey_conflict_msg": {"th": "ปุ่มนี้ถูกตั้งไว้กับฟังก์ชันอื่นแล้ว กรุณาเลือกปุ่มอื่น",
                             "en": "This key is already assigned elsewhere. Please pick another key."},

    # ---------- เกี่ยวกับ ----------
    "about_title": {"th": "เกี่ยวกับโปรแกรม", "en": "About"},
    "about_desc": {"th": "โปรแกรมช่วยคลิกอัตโนมัติ และสร้างชุดคำสั่งอัตโนมัติของคุณเอง",
                    "en": "An auto-clicker and custom command-set automation tool."},
    "about_hotkey_note": {"th": "ปุ่มลัด: ตั้งค่าได้ในหน้า 'ตั้งค่า'\nปุ่ม ESC = หยุดทุกอย่างทันที",
                           "en": "Shortcuts: configurable in 'Settings'\nESC = stop everything instantly"},
    "version_label": {"th": "เวอร์ชัน {version}", "en": "Version {version}"},

    # ---------- ข้อความสถานะจากเอนจิน ----------
    "status_autoclick_running": {"th": "คลิกอัตโนมัติ: กำลังทำงาน...", "en": "Auto Click: running..."},
    "status_autoclick_stopped": {"th": "คลิกอัตโนมัติ: หยุดแล้ว", "en": "Auto Click: stopped"},
    "status_autoclick_stopped_count": {"th": "คลิกอัตโนมัติ: หยุดแล้ว (คลิกไปทั้งหมด {count} ครั้ง)",
                                        "en": "Auto Click: stopped ({count} clicks total)"},
    "status_recording_started": {"th": "กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว 0 ขั้นตอน)",
                                  "en": "Recording command set... (0 steps so far)"},
    "status_recording_stopped": {"th": "หยุดบันทึกชุดคำสั่งแล้ว (ได้ {count} ขั้นตอน)",
                                  "en": "Stopped recording ({count} steps captured)"},
    "status_recording_progress": {"th": "กำลังบันทึกชุดคำสั่ง... (บันทึกแล้ว {count} ขั้นตอน)",
                                   "en": "Recording command set... ({count} steps so far)"},
    "status_no_macro": {"th": "ยังไม่มีชุดคำสั่งให้เล่น กรุณาบันทึกหรือสร้างชุดคำสั่งก่อน",
                         "en": "No command set to play — record or build one first."},
    "status_play_started": {"th": "กำลังเล่นชุดคำสั่ง...", "en": "Playing command set..."},
    "status_play_stopped": {"th": "เล่นชุดคำสั่ง: หยุดแล้ว", "en": "Playback: stopped"},
    "status_play_stopped_rounds": {"th": "เล่นชุดคำสั่ง: หยุดแล้ว (เล่นไปทั้งหมด {rounds} รอบ)",
                                    "en": "Playback: stopped ({rounds} round(s) played)"},

    # ---------- ข้อความสถานะจากหน้าจอ ----------
    "status_emergency_stop": {"th": "⛔ หยุดการทำงานทั้งหมดแล้ว", "en": "⛔ Everything stopped"},
    "status_hidden_to_tray": {"th": "ซ่อนหน้าต่างไว้เบื้องหลังแล้ว (คลิกไอคอนโปรแกรมมุมจอเพื่อเปิดกลับมา)",
                               "en": "Window hidden in background (click the tray icon to bring it back)"},
    "status_startup_fail_title": {"th": "ทำไม่สำเร็จ", "en": "Failed"},
    "status_startup_fail_msg": {"th": "ไม่สามารถตั้งค่าให้เปิดอัตโนมัติได้", "en": "Couldn't enable auto-start."},
    "status_startup_on": {"th": "เปิดอัตโนมัติเมื่อเปิดเครื่อง: เปิดใช้งาน", "en": "Launch at startup: enabled"},
    "status_startup_off": {"th": "เปิดอัตโนมัติเมื่อเปิดเครื่อง: ปิดใช้งาน", "en": "Launch at startup: disabled"},
    "status_hotkey_set": {"th": "ตั้งปุ่มลัดใหม่แล้ว: {key}", "en": "New shortcut set: {key}"},
    "status_capture_prepare": {"th": "เตรียมตัว... อีก {n} วินาที (ย้ายเมาส์ไปตำแหน่งที่ต้องการไว้ก่อน)",
                                "en": "Get ready... {n}s left (move the mouse where you want first)"},
    "status_capture_done": {"th": "จิ้มตำแหน่งแล้ว ✓ ({x}, {y})", "en": "Captured ✓ ({x}, {y})"},
    "status_picked_done": {"th": "เลือกตำแหน่งแล้ว ✓ ({x}, {y})", "en": "Selected ✓ ({x}, {y})"},
    "status_position_saved": {"th": "บันทึกตำแหน่ง '{name}' ไว้แล้ว", "en": "Saved position '{name}'"},
    "status_step_added": {"th": "เพิ่มขั้นตอนแล้ว", "en": "Step added"},
    "status_step_edited": {"th": "แก้ไขขั้นตอนแล้ว", "en": "Step updated"},
    "status_step_removed": {"th": "ลบขั้นตอนแล้ว", "en": "Step removed"},
    "status_steps_cleared": {"th": "ล้างชุดคำสั่งทั้งหมดแล้ว", "en": "All steps cleared"},
    "status_macro_saved": {"th": "บันทึกชุดคำสั่ง '{name}' ไว้แล้ว", "en": "Saved command set '{name}'"},
    "status_macro_loaded": {"th": "เปิดใช้ชุดคำสั่ง '{name}' แล้ว ({count} ขั้นตอน)",
                             "en": "Loaded command set '{name}' ({count} steps)"},
    "status_macro_deleted": {"th": "ลบชุดคำสั่ง '{name}' แล้ว", "en": "Deleted command set '{name}'"},
    "status_file_exported": {"th": "บันทึกไฟล์แล้ว: {path}", "en": "File saved: {path}"},
    "status_file_imported": {"th": "นำเข้าไฟล์แล้ว ({count} ขั้นตอน)", "en": "File imported ({count} steps)"},
    "confirm_clear_steps": {"th": "ล้างขั้นตอนทั้งหมดในชุดคำสั่งนี้หรือไม่?", "en": "Clear all steps in this command set?"},
    "confirm_delete_macro": {"th": "ลบชุดคำสั่ง '{name}' ทิ้งหรือไม่?", "en": "Delete command set '{name}'?"},
    "no_step_selected_edit": {"th": "กรุณาเลือกขั้นตอนที่ต้องการแก้ไขจากรายการก่อน", "en": "Please select a step to edit first."},
    "no_step_selected_delete": {"th": "กรุณาเลือกขั้นตอนที่ต้องการลบจากรายการก่อน", "en": "Please select a step to delete first."},
    "no_name_title": {"th": "ยังไม่ได้ตั้งชื่อ", "en": "No Name Given"},
    "no_name_msg": {"th": "กรุณาตั้งชื่อชุดคำสั่งนี้ก่อนบันทึก", "en": "Please name this command set before saving."},
    "no_steps_title": {"th": "ยังไม่มีขั้นตอน", "en": "No Steps Yet"},
    "no_steps_msg": {"th": "ยังไม่มีขั้นตอนให้บันทึกในชุดคำสั่งนี้", "en": "There are no steps to save in this command set."},
    "no_steps_export_msg": {"th": "ยังไม่มีชุดคำสั่งให้บันทึกเป็นไฟล์", "en": "There's no command set to export."},
    "load_fail_title": {"th": "เปิดไม่สำเร็จ", "en": "Couldn't Open"},
    "delete_fail_title": {"th": "ลบไม่สำเร็จ", "en": "Couldn't Delete"},
    "import_fail_title": {"th": "นำเข้าไม่สำเร็จ", "en": "Import Failed"},
    "file_type_macro": {"th": "ไฟล์ชุดคำสั่ง", "en": "Command set file"},

    # ---------- ถาดระบบ ----------
    "tray_show": {"th": "เปิดหน้าต่างโปรแกรม", "en": "Show Window"},
    "tray_toggle_click": {"th": "เริ่ม/หยุด คลิกอัตโนมัติ", "en": "Start/Stop Auto Click"},
    "tray_toggle_play": {"th": "เริ่ม/หยุด เล่นชุดคำสั่ง", "en": "Start/Stop Playing"},
    "tray_stop_all": {"th": "⛔ หยุดทุกอย่างทันที", "en": "⛔ Stop Everything"},
    "tray_exit": {"th": "ออกจากโปรแกรม", "en": "Exit"},
    "tray_tooltip": {"th": "คลิกอัตโนมัติ", "en": "Auto Clicker"},
}


def set_language(lang):
    global _current_lang
    if lang in (LANG_TH, LANG_EN):
        _current_lang = lang


def get_language():
    return _current_lang


def t(key, **kwargs):
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_lang) or entry.get(LANG_TH) or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
