# -*- coding: utf-8 -*-
"""
core/tray.py
============
ไอคอน System Tray (พื้นที่แจ้งเตือนข้าง ๆ นาฬิกา) ด้วย pystray
ให้ผู้ใช้ย่อโปรแกรมลงถาดได้ และควบคุมการทำงานหลักจากเมนูคลิกขวาได้โดยไม่ต้องเปิดหน้าต่าง
"""

import threading

try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None

from .logger import get_logger

log = get_logger()


class TrayIcon:
    def __init__(self, icon_path, on_show, on_toggle_click, on_toggle_play, on_stop_all, on_exit):
        self.icon_path = icon_path
        self.on_show = on_show
        self.on_toggle_click = on_toggle_click
        self.on_toggle_play = on_toggle_play
        self.on_stop_all = on_stop_all
        self.on_exit = on_exit
        self._icon = None
        self._thread = None

    def available(self):
        return pystray is not None and Image is not None

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem("เปิดหน้าต่างโปรแกรม", lambda: self.on_show(), default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("เริ่ม/หยุด คลิกอัตโนมัติ", lambda: self.on_toggle_click()),
            pystray.MenuItem("เริ่ม/หยุด เล่นชุดคำสั่ง", lambda: self.on_toggle_play()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⛔ หยุดทุกอย่างทันที", lambda: self.on_stop_all()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("ออกจากโปรแกรม", lambda: self._on_exit_clicked()),
        )

    def _on_exit_clicked(self):
        self.stop()
        self.on_exit()

    def start(self):
        if not self.available() or self._icon is not None:
            return
        try:
            image = Image.open(self.icon_path)
        except Exception:
            log.exception("Failed to load tray icon image")
            return
        self._icon = pystray.Icon("AutoClickerPro", image, "คลิกอัตโนมัติ", self._build_menu())
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()
        log.info("Tray icon started")

    def stop(self):
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
            log.info("Tray icon stopped")

    def notify(self, title, message):
        if self._icon is not None:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass
