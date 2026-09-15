#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Clicker Pro — จุดเริ่มต้นโปรแกรม
=========================================
รัน:
    python main.py

ติดตั้งไลบรารีที่จำเป็นก่อน:
    pip install -r requirements.txt
"""

import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import App
from core.logger import get_logger

log = get_logger()


def main():
    try:
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception:
        log.exception("Fatal error, application crashed")
        raise


if __name__ == "__main__":
    main()
