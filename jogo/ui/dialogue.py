"""Caixa de diálogo com efeito de máquina de escrever."""
import pygame

from ..config import WIDTH, HEIGHT, GOLD, WHITE
from ..util import draw_text, panel, wrap_text


class DialogueBox:
    TEXT_SIZE = 28
    SPEED = 1.2  # caracteres por quadro

    def __init__(self, speaker, lines, on_close=None, audio=None):
        self.speaker = speaker
        self.lines = list(lines)
        self.on_close = on_close
        self.audio = audio
        self.index = 0
        self.shown = 0.0
        self.done = False
        self.tick = 0

    @property
    def current(self):
        return self.lines[self.index]

    def update(self, inp):
        self.tick += 1
        before = int(self.shown)
        self.shown = min(len(self.current), self.shown + self.SPEED)
        if self.audio and int(self.shown) // 3 != before // 3:
            self.audio.play("falar")
        if inp.pressed("confirm") or inp.pressed("attack") or inp.pressed("up"):
            if self.shown < len(self.current):
                self.shown = len(self.current)
            elif self.index + 1 < len(self.lines):
                self.index += 1
                self.shown = 0
            else:
                self.done = True

    def draw(self, surf):
        rect = pygame.Rect(40, HEIGHT - 150, WIDTH - 80, 130)
        panel(surf, rect, alpha=235)
        name_rect = pygame.Rect(rect.x + 20, rect.y - 18, 230, 34)
        panel(surf, name_rect, color=(60, 40, 90), alpha=255, radius=8)
        draw_text(surf, self.speaker, name_rect.center, 26, GOLD, "center", bold=True)
        visible = self.current[:int(self.shown)]
        for i, line in enumerate(wrap_text(visible, self.TEXT_SIZE, rect.width - 50)):
            draw_text(surf, line, (rect.x + 25, rect.y + 28 + i * 28), self.TEXT_SIZE, WHITE)
        if self.shown >= len(self.current) and (self.tick // 20) % 2 == 0:
            bx, by = rect.right - 30, rect.bottom - 22
            pygame.draw.polygon(surf, GOLD, [(bx - 8, by - 5), (bx + 8, by - 5), (bx, by + 5)])
        draw_text(surf, f"{self.index + 1}/{len(self.lines)}", (rect.right - 60, rect.y + 10), 18, (170, 170, 200))
