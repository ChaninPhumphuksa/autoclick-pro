# -*- coding: utf-8 -*-
"""
gui/fonts.py
============
จัดการฟอนต์ของโปรแกรมให้ใช้ "Prompt" เป็นหลัก (อ่านง่าย ทันสมัย รองรับภาษาไทยดี)
หากเครื่องผู้ใช้ยังไม่ได้ติดตั้งฟอนต์ Prompt โปรแกรมจะเลือกฟอนต์ที่ใกล้เคียงและอ่านง่าย
ให้อัตโนมัติแทน เพื่อไม่ให้หน้าตาโปรแกรมพังหรือใช้งานไม่ได้
"""

import tkinter.font as tkfont

# เรียงจากที่ต้องการมากที่สุดไปน้อยที่สุด
PREFERRED_FONTS = ["Prompt", "Noto Sans Thai", "Segoe UI", "TH Sarabun New", "Leelawadee UI", "Tahoma"]

_family_cache = None


def detect_font_family():
    """ตรวจสอบว่าเครื่องผู้ใช้มีฟอนต์ตัวไหนในลิสต์ที่ต้องการติดตั้งอยู่บ้าง คืนตัวแรกที่เจอ"""
    global _family_cache
    if _family_cache:
        return _family_cache
    try:
        available = set(tkfont.families())
    except Exception:
        available = set()
    for f in PREFERRED_FONTS:
        if f in available:
            _family_cache = f
            return f
    _family_cache = "TkDefaultFont"
    return _family_cache


def is_prompt_installed():
    return detect_font_family() == "Prompt"


def ui_font(size=10, weight="normal"):
    """คืน tuple (family, size, weight) พร้อมใช้กับ widget option font=..."""
    return (detect_font_family(), size, weight)


def apply_default_font(root, size=10):
    """ตั้งฟอนต์เริ่มต้นของทั้งโปรแกรม (มีผลกับ widget ที่ไม่ได้ระบุ font เอง)"""
    family = detect_font_family()
    for name in ("TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont",
                 "TkHeadingFont", "TkCaptionFont", "TkSmallCaptionFont",
                 "TkIconFont", "TkTooltipFont"):
        try:
            f = tkfont.nametofont(name)
            f.configure(family=family, size=size)
        except Exception:
            pass
    return family
