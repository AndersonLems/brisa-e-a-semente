"""Cenários de fundo com parallax, gerados proceduralmente por bioma."""
import math
import random

import pygame

from ..config import WIDTH, HEIGHT
from ..util import vertical_gradient
from .themes import THEMES

LAYER_W = 1024


def ridge(height, base, waves, color, rng):
    """Silhueta contínua e repetível (as frequências são inteiras)."""
    surf = pygame.Surface((LAYER_W, height), pygame.SRCALPHA)
    phases = [rng.uniform(0, math.tau) for _ in waves]
    pts = [(0, height)]
    for x in range(0, LAYER_W + 1, 8):
        y = base - sum(a * math.sin(math.tau * k * x / LAYER_W + p) for (k, a), p in zip(waves, phases))
        pts.append((x, y))
    pts.append((LAYER_W, height))
    pygame.draw.polygon(surf, color, pts)
    return surf


class Background:
    def __init__(self, theme_name):
        self.name = theme_name
        self.theme = THEMES[theme_name]
        self.sky = vertical_gradient(WIDTH, HEIGHT, *self.theme["sky"])
        self.layers = []  # (surface, fator_parallax, y)
        rng = random.Random(42)
        getattr(self, "_build_" + theme_name)(rng)

    # ------------------------------------------------------------ campo
    def _build_campo(self, rng):
        clouds = pygame.Surface((LAYER_W, 200), pygame.SRCALPHA)
        for _ in range(7):
            x, y = rng.randrange(LAYER_W), rng.randrange(20, 150)
            for i in range(5):
                for dx in (0, LAYER_W, -LAYER_W):
                    pygame.draw.ellipse(clouds, (255, 255, 255, 200),
                                        (x + dx + i * 18 - 40, y - (i % 2) * 10, 60, 30))
        self.layers.append((clouds, 0.05, 10))
        self.layers.append((ridge(300, 160, [(2, 40), (5, 18), (9, 6)], (150, 170, 220), rng), 0.12, 230))
        self.layers.append((ridge(260, 120, [(3, 22), (7, 10)], (110, 175, 120), rng), 0.3, 300))
        trees = pygame.Surface((LAYER_W, 280), pygame.SRCALPHA)
        palette = [(235, 110, 175), (250, 210, 60), (160, 110, 210), (240, 140, 190)]
        for i in range(9):
            x = i * (LAYER_W // 9) + rng.randint(0, 50)
            self._ipe(trees, x, 280, rng.randint(90, 150), rng.choice(palette), rng)
        self.layers.append((trees, 0.55, 300))

    def _ipe(self, surf, x, ground, h, color, rng):
        for dx in (0, LAYER_W, -LAYER_W):
            px = x + dx
            pygame.draw.polygon(surf, (90, 60, 45), [(px - 5, ground), (px + 5, ground), (px + 2, ground - h), (px - 2, ground - h)])
            pygame.draw.line(surf, (90, 60, 45), (px, ground - h * 0.6), (px + 22, ground - h * 0.85), 4)
            pygame.draw.line(surf, (90, 60, 45), (px, ground - h * 0.7), (px - 20, ground - h * 0.9), 4)
        blobs = [(rng.randint(-38, 38), rng.randint(-25, 15), rng.randint(14, 24)) for _ in range(9)]
        dark = tuple(max(0, c - 40) for c in color)
        for dx in (0, LAYER_W, -LAYER_W):
            for bx, by, r in blobs:
                pygame.draw.circle(surf, dark, (x + dx + bx, ground - h + by + 3), r)
            for bx, by, r in blobs:
                pygame.draw.circle(surf, color, (x + dx + bx, ground - h + by), r - 2)

    # ------------------------------------------------------------ caverna
    def _build_caverna(self, rng):
        back = ridge(HEIGHT, 330, [(3, 50), (8, 20), (17, 8)], (45, 35, 70), rng)
        top = pygame.Surface((LAYER_W, 220), pygame.SRCALPHA)
        for _ in range(26):
            x, w, h = rng.randrange(LAYER_W), rng.randint(16, 40), rng.randint(40, 180)
            for dx in (0, LAYER_W, -LAYER_W):
                pygame.draw.polygon(top, (35, 28, 55), [(x + dx - w, 0), (x + dx + w, 0), (x + dx, h)])
        self.layers.append((back, 0.1, 0))
        self.layers.append((top, 0.25, 0))
        crystals = pygame.Surface((LAYER_W, 260), pygame.SRCALPHA)
        for _ in range(16):
            x, y = rng.randrange(LAYER_W), rng.randint(120, 250)
            col = rng.choice([(110, 230, 220), (200, 130, 255), (120, 170, 255)])
            for dx in (0, LAYER_W, -LAYER_W):
                for k in range(3):
                    h = rng.randint(20, 55)
                    bx = x + dx + k * 9 - 9
                    pygame.draw.circle(crystals, (*col, 40), (bx + 4, y - h // 2), h // 2)
                    pygame.draw.polygon(crystals, (*col, 210), [(bx, y), (bx + 4, y - h), (bx + 9, y)])
        self.layers.append((ridge(240, 120, [(4, 30), (11, 10)], (55, 45, 85), rng), 0.4, 320))
        self.layers.append((crystals, 0.45, 280))

    # ------------------------------------------------------------ vulcão
    def _build_vulcao(self, rng):
        far = pygame.Surface((LAYER_W, 360), pygame.SRCALPHA)
        for vx, w, h in ((260, 260, 260), (760, 200, 200)):
            pygame.draw.polygon(far, (70, 25, 30), [(vx - w, 360), (vx - 40, 360 - h), (vx + 40, 360 - h), (vx + w, 360)])
            pygame.draw.ellipse(far, (255, 120, 40), (vx - 40, 360 - h - 8, 80, 18))
            for k in range(4):
                pygame.draw.line(far, (230, 90, 30), (vx - 20 + k * 12, 360 - h + 4),
                                 (vx - 40 + k * 25 + rng.randint(-20, 20), 360 - h + 90), 3)
        self.layers.append((far, 0.08, 120))
        self.layers.append((ridge(280, 140, [(3, 35), (9, 14)], (50, 22, 25), rng), 0.25, 280))
        spires = pygame.Surface((LAYER_W, 260), pygame.SRCALPHA)
        for _ in range(14):
            x, w, h = rng.randrange(LAYER_W), rng.randint(10, 26), rng.randint(60, 200)
            for dx in (0, LAYER_W, -LAYER_W):
                pygame.draw.polygon(spires, (35, 18, 20), [(x + dx - w, 260), (x + dx, 260 - h), (x + dx + w, 260)])
        self.layers.append((spires, 0.5, 300))

    # ------------------------------------------------------------ desenho
    def draw(self, surf, cam_x, cam_y, tick):
        surf.blit(self.sky, (0, 0))
        if self.name == "campo":
            pygame.draw.circle(surf, (255, 245, 200), (780, 90), 46)
            pygame.draw.circle(surf, (255, 255, 235), (780, 90), 38)
        for img, factor, y in self.layers:
            ox = -int(cam_x * factor) % LAYER_W
            yy = y - int(cam_y * factor * 0.5)
            surf.blit(img, (ox - LAYER_W, yy))
            surf.blit(img, (ox, yy))
        self._ambient(surf, tick)

    def _ambient(self, surf, tick):
        if self.name == "campo":   # pétalas de ipê caindo
            for i in range(16):
                x = (i * 137 + tick * (0.5 + (i % 3) * 0.3)) % (WIDTH + 40) - 20
                y = (i * 71 + tick * (0.7 + (i % 4) * 0.2)) % (HEIGHT + 20) - 10
                x += math.sin(tick * 0.03 + i) * 12
                col = (240, 130, 190) if i % 2 else (250, 215, 80)
                pygame.draw.ellipse(surf, col, (int(x), int(y), 6, 4))
        elif self.name == "caverna":   # brilhos flutuando
            for i in range(22):
                x = (i * 97 + math.sin(tick * 0.01 + i) * 40) % WIDTH
                y = (i * 53 - tick * (0.2 + (i % 3) * 0.1)) % HEIGHT
                a = 0.5 + 0.5 * math.sin(tick * 0.08 + i)
                pygame.draw.circle(surf, (int(120 + 100 * a), int(200 + 50 * a), 255), (int(x), int(y)), 1 + (i % 2))
        elif self.name == "vulcao":   # brasas subindo
            for i in range(26):
                x = (i * 83 + math.sin(tick * 0.02 + i) * 30) % WIDTH
                y = HEIGHT - (i * 41 + tick * (0.8 + (i % 4) * 0.3)) % (HEIGHT + 20)
                pygame.draw.circle(surf, (255, 150 + (i % 3) * 30, 50), (int(x), int(y)), 2)
