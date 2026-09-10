# -*- coding: utf-8 -*-
"""
gui/capture_hub.py
===================
ตัวกลางเล็ก ๆ ที่ทำให้ปุ่ม "จิ้มตำแหน่งเมาส์" ทุกปุ่มในโปรแกรม (ไม่ว่าจะอยู่ในหน้าต่างหลัก
หรือกล่องโต้ตอบย่อยที่เปิดซ้อนอยู่) ถูกสั่งจับตำแหน่งได้ทันทีผ่านปุ่มลัดคีย์บอร์ดที่ตั้งไว้
ในหน้า "ตั้งค่า" โดยไม่ต้องรู้จักกันโดยตรงระหว่างหน้าต่าง

วิธีใช้:
- ปุ่ม "จิ้มตำแหน่ง" เวลาถูกกด จะเรียก capture_hub.set_pending(callback) เพื่อ "ลงทะเบียน"
  ว่าตัวเองเป็นเป้าหมายล่าสุดที่รอรับการจับตำแหน่ง (พร้อมกับเริ่มนับถอยหลัง 3 วิ ตามปกติ)
- เมื่อผู้ใช้กดปุ่มลัดที่ตั้งไว้ (เช่น F9) เมื่อไหร่ก็ตาม ระบบจะเรียก capture_hub.trigger()
  ซึ่งจะยิง callback ที่ค้างอยู่ล่าสุดทันที (ไม่ต้องรอครบ 3 วิ)
- ถ้านับถอยหลังครบ 3 วิเองโดยไม่มีใครกดปุ่มลัด ก็จะจับตำแหน่งตามปกติแล้วเคลียร์ตัวเองออก
"""


class CaptureHub:
    def __init__(self):
        self._pending = None

    def set_pending(self, callback):
        self._pending = callback

    def is_pending(self, callback):
        return self._pending is callback

    def clear(self, callback=None):
        """ล้างตัวเองออก ถ้า callback ตรงกับที่ค้างอยู่ (หรือล้างทิ้งเสมอถ้าไม่ระบุ)"""
        if callback is None or self._pending is callback:
            self._pending = None

    def trigger(self):
        """เรียกใช้จาก handler ของปุ่มลัด — ยิง callback ที่ค้างอยู่ล่าสุด (ถ้ามี) แล้วเคลียร์ทิ้ง"""
        cb = self._pending
        if cb is not None:
            self._pending = None
            cb()


# ใช้ตัวเดียวร่วมกันทั้งโปรแกรม (หน้าต่างหลักและกล่องโต้ตอบย่อยทุกอันอ้างถึงตัวเดียวกัน)
capture_hub = CaptureHub()
