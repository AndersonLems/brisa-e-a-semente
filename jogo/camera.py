"""Câmera que segue o jogador com suavização, limites e tremor."""
import random

import pygame

from .config import WIDTH, HEIGHT
from .util import clamp


class Camera:
    def __init__(self, world_w, world_h):
        self.world = pygame.Rect(0, 0, world_w, world_h)
        self.bounds = self.world.copy()
        self.fx = self.fy = 0.0
        self.x = self.y = 0
        self.look = 0.0
        self._shake_amount = 0
        self._shake_frames = 0

    def lock(self, rect):
        self.bounds = pygame.Rect(rect)

    def unlock(self):
        self.bounds = self.world.copy()

    def shake(self, amount, frames):
        self._shake_amount = max(self._shake_amount, amount)
        self._shake_frames = max(self._shake_frames, frames)

    def follow(self, target, instant=False):
        self.look += (getattr(target, "facing", 1) * 60 - self.look) * 0.04
        tx = target.centerx + self.look - WIDTH / 2
        ty = target.centery - HEIGHT * 0.55
        if instant:
            self.fx, self.fy = tx, ty
        else:
            self.fx += (tx - self.fx) * 0.15
            self.fy += (ty - self.fy) * 0.1
        b = self.bounds
        if b.width <= WIDTH:
            self.fx = b.centerx - WIDTH / 2
        else:
            self.fx = clamp(self.fx, b.left, b.right - WIDTH)
        self.fy = clamp(self.fy, b.top, max(b.top, b.bottom - HEIGHT))

        sx = sy = 0
        if self._shake_frames > 0:
            self._shake_frames -= 1
            sx = random.randint(-self._shake_amount, self._shake_amount)
            sy = random.randint(-self._shake_amount, self._shake_amount)
            if self._shake_frames == 0:
                self._shake_amount = 0
        self.x = int(self.fx) + sx
        self.y = int(self.fy) + sy
