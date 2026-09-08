"""
humanizer.py
Anti-Ban Humanizer - ทำให้การคลิก/การเคลื่อนไหวดูเป็นธรรมชาติมากขึ้น
โดยการสุ่มหน่วงเวลา (delay jitter), สุ่มตำแหน่งคลิก (position jitter),
และสุ่มความเร็วการเคลื่อนที่ของเมาส์ (movement curve)
"""

import random
import time
import math


class Humanizer:
    """
    ค่าที่ปรับได้:
      enabled          : เปิด/ปิดระบบ humanizer
      delay_variance   : % ความแปรผันของเวลาหน่วง (0.0 - 1.0), เช่น 0.2 = ±20%
      position_jitter  : พิกเซลสูงสุดที่จะสุ่มขยับตำแหน่งคลิก (x,y)
      misclick_chance  : โอกาส (0.0 - 1.0) ที่จะเกิดการคลิกพลาดเล็กน้อยก่อนคลิกจริง
      move_curve       : เปิดการเคลื่อนเมาส์แบบโค้งธรรมชาติ (ease-in-out + สั่นเล็กน้อย)
    """

    def __init__(self, enabled=True, delay_variance=0.2, position_jitter=3,
                 misclick_chance=0.0, move_curve=True):
        self.enabled = enabled
        self.delay_variance = max(0.0, min(delay_variance, 1.0))
        self.position_jitter = max(0, int(position_jitter))
        self.misclick_chance = max(0.0, min(misclick_chance, 1.0))
        self.move_curve = move_curve

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "delay_variance": self.delay_variance,
            "position_jitter": self.position_jitter,
            "misclick_chance": self.misclick_chance,
            "move_curve": self.move_curve,
        }

    @staticmethod
    def from_dict(d):
        if not d:
            return Humanizer()
        return Humanizer(
            enabled=d.get("enabled", True),
            delay_variance=d.get("delay_variance", 0.2),
            position_jitter=d.get("position_jitter", 3),
            misclick_chance=d.get("misclick_chance", 0.0),
            move_curve=d.get("move_curve", True),
        )

    def delay(self, base_seconds: float) -> float:
        """คืนค่าเวลาหน่วงที่ถูกสุ่มแปรผันจากค่าเริ่มต้น"""
        base_seconds = max(0.0, base_seconds)
        if not self.enabled or self.delay_variance <= 0:
            return base_seconds
        low = base_seconds * (1 - self.delay_variance)
        high = base_seconds * (1 + self.delay_variance)
        low = max(0.0, low)
        # ใช้ triangular distribution ให้ค่าที่ได้เกาะกลุ่มใกล้ base มากกว่า uniform ล้วน ๆ
        return max(0.0, random.triangular(low, high, base_seconds))

    def sleep(self, base_seconds: float):
        time.sleep(self.delay(base_seconds))

    def jitter_point(self, x: int, y: int):
        """สุ่มขยับพิกัดคลิกเล็กน้อยในรัศมี position_jitter พิกเซล"""
        if not self.enabled or self.position_jitter <= 0:
            return x, y
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.position_jitter)
        dx = int(round(radius * math.cos(angle)))
        dy = int(round(radius * math.sin(angle)))
        return x + dx, y + dy

    def should_misclick(self) -> bool:
        return self.enabled and random.random() < self.misclick_chance

    def movement_path(self, start, end, steps=None):
        """
        สร้างลำดับจุด (path) สำหรับเคลื่อนเมาส์จาก start ไป end แบบโค้งธรรมชาติ
        โดยใช้ ease-in-out + เพิ่ม noise เล็กน้อยระหว่างทาง คืนค่าเป็น list ของ (x, y)
        """
        sx, sy = start
        ex, ey = end
        dist = math.hypot(ex - sx, ey - sy)
        if steps is None:
            steps = max(3, min(30, int(dist / 15)))
        if not self.enabled or not self.move_curve or steps <= 1:
            return [end]

        points = []
        for i in range(1, steps + 1):
            t = i / steps
            # ease-in-out cubic
            t_eased = 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2
            x = sx + (ex - sx) * t_eased
            y = sy + (ey - sy) * t_eased
            if i != steps:  # จุดสุดท้ายต้องตรงเป้าเป๊ะ ๆ ไม่สุ่มเบี่ยง
                noise = self.position_jitter * 0.5
                x += random.uniform(-noise, noise)
                y += random.uniform(-noise, noise)
            points.append((int(round(x)), int(round(y))))
        return points
