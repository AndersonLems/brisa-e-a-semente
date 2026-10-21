"""Menu vertical navegável com teclado/controle."""
import math

import pygame

from ..config import GOLD, WHITE
from ..util import draw_text


class MenuOption:
    def __init__(self, label, action, enabled=True):
        self._label = label
        self.action = action
        self.enabled = enabled

    @property
    def label(self):
        return self._label() if callable(self._label) else self._label


class Menu:
    def __init__(self, options, audio=None, size=34, spacing=44):
        self.options = options
        self.audio = audio
        self.size = size
        self.spacing = spacing
        self.index = 0
        self.tick = 0
        self._skip_disabled(1)

    def _skip_disabled(self, step):
        for _ in range(len(self.options)):
            if self.options[self.index].enabled:
                return
            self.index = (self.index + step) % len(self.options)

    def update(self, inp):
        self.tick += 1
        for action, step in (("up", -1), ("down", 1)):
            if inp.pressed(action):
                self.index = (self.index + step) % len(self.options)
                self._skip_disabled(step)
                self._sfx("menu")
        if inp.pressed("confirm"):
            opt = self.options[self.index]
            if opt.enabled:
                self._sfx("confirmar")
                opt.action()

    def _sfx(self, name):
        if self.audio:
            self.audio.play(name)

    def draw(self, surf, center_x, top_y):
        for i, opt in enumerate(self.options):
            y = top_y + i * self.spacing
            selected = i == self.index
            color = GOLD if selected else (WHITE if opt.enabled else (110, 110, 130))
            r = draw_text(surf, opt.label, (center_x, y), self.size, color, "midtop", bold=selected)
            if selected:
                off = int(math.sin(self.tick * 0.15) * 4)
                cy = r.centery
                pygame.draw.polygon(surf, GOLD, [(r.left - 24 + off, cy - 8), (r.left - 24 + off, cy + 8), (r.left - 12 + off, cy)])
