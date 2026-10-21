"""Gera os gráficos dos tiles proceduralmente a partir da paleta do tema."""
import math
import random

import pygame

from ..config import TILE

T = TILE


class Tileset:
    LIQUID_FRAMES = 8

    def __init__(self, theme):
        self.th = theme
        self.cache = {}
        rng = random.Random(1234)
        self.cache["ground"] = self._ground(rng, top=False)
        self.cache["ground_top"] = self._ground(rng, top=True)
        self.cache["brick"] = self._brick()
        self.cache["chest"] = self._chest(used=False)
        self.cache["chest_used"] = self._chest(used=True)
        self.cache["platform"] = self._plank()
        self.cache["spike"] = self._spike()
        for i in range(self.LIQUID_FRAMES):
            self.cache[f"liquid_top{i}"] = self._liquid(i, surface=True)
            self.cache[f"liquid{i}"] = self._liquid(i, surface=False)

    def get(self, key):
        return self.cache[key]

    def _ground(self, rng, top):
        th = self.th
        s = pygame.Surface((T, T))
        s.fill(th["dirt"])
        for _ in range(14):
            c = th["dirt_dark"] if rng.random() < 0.6 else th["dirt_light"]
            x, y = rng.randrange(T), rng.randrange(T)
            pygame.draw.rect(s, c, (x, y, rng.choice((2, 3, 4)), 2))
        if top:
            pygame.draw.rect(s, th["top_dark"], (0, 0, T, 10))
            pygame.draw.rect(s, th["top"], (0, 0, T, 8))
            pygame.draw.rect(s, th["top_light"], (0, 0, T, 3))
            for x in range(1, T, 4):
                h = rng.randint(2, 5)
                pygame.draw.line(s, th["top_dark"], (x, 8), (x, 8 + h), 2)
        return s

    def _brick(self):
        th = self.th
        s = pygame.Surface((T, T))
        s.fill(th["brick_line"])
        for row in range(4):
            off = 0 if row % 2 == 0 else -8
            for col in range(-1, 3):
                r = pygame.Rect(col * 16 + off + 1, row * 8 + 1, 14, 6)
                pygame.draw.rect(s, th["brick"], r)
                pygame.draw.line(s, tuple(min(255, c + 30) for c in th["brick"]), r.topleft, r.topright)
        return s

    def _chest(self, used):
        th = self.th
        s = pygame.Surface((T, T), pygame.SRCALPHA)
        base = th["chest"] if not used else (120, 100, 85)
        dark = th["chest_dark"] if not used else (70, 55, 45)
        pygame.draw.rect(s, dark, (0, 0, T, T), border_radius=5)
        pygame.draw.rect(s, base, (2, 2, T - 4, T - 4), border_radius=4)
        for x, y in ((5, 5), (T - 6, 5), (5, T - 6), (T - 6, T - 6)):
            pygame.draw.circle(s, dark, (x, y), 2)
        if not used:
            # símbolo: uma semente com broto
            pygame.draw.ellipse(s, (110, 70, 25), (11, 13, 11, 14))
            pygame.draw.ellipse(s, (250, 220, 120), (12, 14, 9, 12))
            pygame.draw.line(s, (40, 130, 50), (16, 14), (16, 8), 2)
            pygame.draw.ellipse(s, (70, 180, 70), (16, 5, 8, 5))
            pygame.draw.ellipse(s, (70, 180, 70), (9, 6, 8, 5))
        return s

    def _plank(self):
        th = self.th
        s = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.rect(s, th["plank"], (0, 0, T, 12), border_radius=2)
        pygame.draw.rect(s, th["plank_top"], (0, 0, T, 4), border_radius=2)
        pygame.draw.line(s, tuple(max(0, c - 50) for c in th["plank"]), (0, 11), (T, 11), 2)
        pygame.draw.circle(s, tuple(max(0, c - 60) for c in th["plank"]), (6, 7), 2)
        pygame.draw.circle(s, tuple(max(0, c - 60) for c in th["plank"]), (T - 6, 7), 2)
        return s

    def _spike(self):
        th = self.th
        s = pygame.Surface((T, T), pygame.SRCALPHA)
        for i in range(3):
            x = i * 11 - 1
            pts = [(x, T), (x + 6, T - 16), (x + 12, T)]
            pygame.draw.polygon(s, th["spike"], pts)
            pygame.draw.line(s, (255, 255, 255), (x + 6, T - 16), (x + 2, T - 2))
            pygame.draw.polygon(s, (70, 70, 80), pts, 1)
        return s

    def _liquid(self, frame, surface):
        th = self.th
        s = pygame.Surface((T, T), pygame.SRCALPHA)
        s.fill(th["liquid"])
        phase = frame / self.LIQUID_FRAMES * math.tau
        for i in range(3):
            x = (i * 13 + frame * 2) % T
            y = 12 + i * 7 + int(math.sin(phase + i) * 2)
            pygame.draw.circle(s, th["liquid_top"], (x, y), 2)
        if surface:
            pts = [(0, T)]
            for x in range(0, T + 1, 4):
                pts.append((x, 5 + math.sin(phase + x / T * math.tau) * 3))
            pts.append((T, T))
            s.fill((0, 0, 0, 0))
            pygame.draw.polygon(s, th["liquid"], pts)
            pygame.draw.lines(s, th["liquid_top"], False, pts[1:-1], 3)
        return s
