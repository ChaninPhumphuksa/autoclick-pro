# -*- coding: utf-8 -*-
"""
core/logger.py
==============
ตั้งค่าระบบ logging แบบมืออาชีพ: บันทึกลงไฟล์ (หมุนไฟล์อัตโนมัติเมื่อไฟล์ใหญ่เกินไป)
เพื่อให้สามารถตรวจสอบย้อนหลัง/ดีบักปัญหาได้หลังแจกจ่ายเป็น .exe
"""

import logging
import logging.handlers
import os

from .config import LOG_DIR, ensure_dirs

LOG_FILE = os.path.join(LOG_DIR, "autoclicker.log")

_logger = None


def get_logger():
    global _logger
    if _logger is not None:
        return _logger

    ensure_dirs()
    logger = logging.getLogger("autoclicker_pro")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _logger = logger
    return logger
