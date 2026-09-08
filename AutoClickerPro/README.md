# AutoClicker Pro

โปรแกร Auto Click มืออาชีพสำหรับ Windows เขียนด้วย Python + customtkinter + pynput

## ฟีเจอร์หลัก

| ฟีเจอร์ | รายละเอียด |
|---|---|
| ✅ Hotkey ปุ่มไหนก็ได้ | กด "ตั้งค่า Hotkey" แล้วกดปุ่มจริงบนคีย์บอร์ดปุ่มไหนก็ได้เพื่อผูกกับ Start/Stop |
| ✅ Auto Click แบบละเอียด | ตั้ง interval (ชม./นาที/วินาที/มิลลิวินาที), ปุ่มเมาส์ (ซ้าย/ขวา/กลาง), single/double/triple click, ตำแหน่งคลิก (เมาส์ปัจจุบัน หรือ พิกัดคงที่), จำนวนรอบ (ไม่จำกัด/จำกัด) |
| ✅ Macro Recorder | บันทึกการกระทำเมาส์+คีย์บอร์ดจริงแบบ real-time แล้วเล่นซ้ำได้ (1 รอบ หรือวนไม่จำกัด) พร้อมบันทึกเป็นไฟล์ |
| ✅ Custom Script Engine | เขียนสคริปต์มาโครเองแบบ JSON DSL รองรับ loop ซ้อนกัน, click, move, key, wait (สุ่มช่วงเวลา), type_text, scroll |
| 🛡 Anti-Ban Humanizer | สุ่มหน่วงเวลา (delay variance), สุ่มขยับตำแหน่งคลิก (pixel jitter), จำลองการคลิกพลาดเล็กน้อย, เส้นทางเมาส์โค้งธรรมชาติแบบ ease-in-out |
| ⛔ Failsafe | กด **ESC** เพื่อหยุดทุกการทำงาน (auto click / มาโคร / สคริปต์) ได้ทันทีทุกเมื่อ |
| 💾 Profile & Macro Manager | บันทึก/โหลดค่าตั้งค่า Auto Clicker และไฟล์มาโคร/สคริปต์ เป็นไฟล์ .json แยกโฟลเดอร์ |
| 🎨 UI ทันสมัย | ธีมมืด/สว่างสลับได้ (customtkinter), แบ่งเป็นแท็บใช้งานง่าย |

### ฟีเจอร์เพิ่มเติมที่แนะนำและได้ใส่ไว้ให้แล้ว
- **Failsafe แบบ global hotkey (ESC)** — ป้องกันโปรแกรมค้างหรือคลิกเลยจุดที่ต้องการ
- **ตัวจับตำแหน่งเมาส์ (F8)** — ระบุพิกัด X, Y แบบไม่ต้องพิมพ์เอง
- **Movement curve** — เมาส์เคลื่อนที่แบบโค้งธรรมชาติแทนการกระโดดไปตำแหน่งทันที ช่วยให้พฤติกรรมดูสมจริงมากขึ้น
- **Misclick simulation** — จำลองการคลิกพลาดเล็กน้อยแบบสุ่ม (ปรับความถี่ได้)
- **Profile/Macro folder แยกชัดเจน** — สลับใช้งานหลายโปรไฟล์ได้เร็ว

### แนวคิดที่ยังไม่ได้ใส่ (ต่อยอดได้ในอนาคต)
- System tray icon (ย่อโปรแกรมไปอยู่ที่ tray แทนการปิด)
- Image/Pixel-color trigger (คลิกอัตโนมัติเมื่อพบสีพิกเซลที่กำหนดบนหน้าจอ)
- Scheduling (ตั้งเวลาเริ่ม-หยุดอัตโนมัติตามเวลาจริง)

---

## วิธีใช้งาน (รันจาก source โดยตรง)

```bash
pip install -r requirements.txt
python main.py
```

## วิธีแปลงเป็นไฟล์ .exe (ทำบนเครื่อง Windows เท่านั้น)

PyInstaller ต้องรันบน Windows เพื่อสร้างไฟล์ .exe สำหรับ Windows (ไม่สามารถ cross-compile จาก Linux/Mac ได้)

1. ติดตั้ง Python 3.10+ บนเครื่อง Windows: https://www.python.org/downloads/
2. คัดลอกโฟลเดอร์ `AutoClickerPro` ทั้งหมดไปไว้บนเครื่อง Windows
3. เปิด Command Prompt ในโฟลเดอร์นั้น แล้วรัน:
   ```
   build.bat
   ```
4. รอสักครู่ ไฟล์ `AutoClickerPro.exe` พร้อมใช้งานจะอยู่ในโฟลเดอร์ `dist\`
5. คัดลอก `AutoClickerPro.exe` ไปไว้ที่ไหนก็ได้ แล้วดับเบิลคลิกเพื่อใช้งาน

> หมายเหตุ: โปรแกรมประเภทควบคุมเมาส์/คีย์บอร์ดอาจถูก Windows Defender หรือโปรแกรมแอนตี้ไวรัสบางตัวเตือนเป็น false positive (เพราะพฤติกรรมคล้าย automation tool ทั่วไป) — สามารถเพิ่ม exception ได้หากมั่นใจในซอร์สโค้ด

---

## โครงสร้างไฟล์

```
AutoClickerPro/
├── main.py            # หน้า UI หลัก (4 แท็บ)
├── humanizer.py        # ระบบ Anti-Ban Humanizer
├── macro_engine.py      # ClickerEngine + MacroRecorder
├── script_engine.py    # ตัวรันสคริปต์ Custom DSL
├── hotkey_manager.py    # ระบบ Hotkey แบบปุ่มไหนก็ได้ + global listener
├── profile_manager.py  # บันทึก/โหลดโปรไฟล์และมาโคร (.json)
├── profiles/            # โปรไฟล์ auto-clicker ที่บันทึกไว้
├── macros/               # ไฟล์มาโคร/สคริปต์ที่บันทึกไว้
├── requirements.txt
└── build.bat            # สคริปต์แปลงเป็น .exe
```

## รูปแบบสคริปต์ (Custom Script DSL)

```json
{
  "name": "ชื่อมาโคร",
  "hotkey": "f7",
  "repeat": 0,
  "humanizer": { "enabled": true, "delay_variance": 0.2, "position_jitter": 3 },
  "actions": [
    { "type": "loop_start", "count": 5 },
    { "type": "click", "x": 400, "y": 400, "button": "left", "clicks": 1 },
    { "type": "wait", "min": 0.2, "max": 0.5 },
    { "type": "loop_end" },
    { "type": "key", "key": "enter", "action": "tap" },
    { "type": "type_text", "text": "hello" }
  ]
}
```

- `repeat: 0` = วนไม่จำกัด, `N` = วน N รอบ
- `loop_start` ที่ไม่มี `count` = วนซ้ำไม่จำกัด (จนกด ESC หรือปุ่มหยุด)
- action types: `click`, `move`, `key`, `wait`, `type_text`, `scroll`, `loop_start`, `loop_end`

## ข้อควรทราบ

โปรแกรมนี้เป็นเครื่องมือ automation สำหรับ PC ของผู้ใช้เอง (คล้าย GS Auto Clicker / OP Auto Clicker ที่มีขายทั่วไป) โปรดใช้งานให้สอดคล้องกับข้อตกลงการใช้งาน (Terms of Service) ของซอฟต์แวร์หรือเกมที่นำไปใช้ร่วมด้วย ผู้ใช้เป็นผู้รับผิดชอบการนำไปใช้งานเอง
