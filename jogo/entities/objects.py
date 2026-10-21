"""Objetos de cenário interativos: checkpoint, portal de saída e plataforma móvel."""
import math

import pygame

from .entity import Entity
from ..config import TILE


class WorldObject(Entity):
    """Objeto fixo que reage ao toque do jogador."""

    def on_player_touch(self, player, level):
        pass


class Checkpoint(WorldObject):
    """Totem do Vento: salva a posição e restaura vida/mana."""

    def __init__(self, x, y):
        super().__init__(x, y, 20, 52)
        self.activated = False

    def on_player_touch(self, player, level):
        if self.activated:
            return
        for o in level.objects:
            if isinstance(o, Checkpoint):
                o.activated = False
        self.activated = True
        level.checkpoint = (self.centerx, self.bottom)
        player.hp = player.max_hp
        player.mp = player.stats.max_mp
        level.sfx("checkpoint")
        level.particles.burst(self.centerx, self.y + 8, (150, 255, 200), 24, 4, 40, 4, 0.02, spark=True)
        level.particles.text(self.centerx, self.y - 10, "Totem ativado!", (150, 255, 200), 22)

    def draw(self, surf, cam):
        x, y = round(self.x - cam.x), round(self.y - cam.y)
        pygame.draw.rect(surf, (110, 75, 45), (x + 6, y + 14, 8, 38))
        pygame.draw.rect(surf, (80, 55, 35), (x + 2, y + 46, 16, 6))
        for i, yy in enumerate((y + 20, y + 30)):
            pygame.draw.line(surf, (160, 110, 60), (x + 6, yy), (x + 14, yy + 3), 2)
        if self.activated:
            pulse = 4 + 2 * math.sin(self.tick * 0.12)
            glow = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(glow, (120, 255, 190, 70), (30, 30), int(18 + pulse))
            surf.blit(glow, (x + 10 - 30, y + 8 - 30))
            color = (150, 255, 200)
        else:
            color = (140, 140, 160)
        pts = [(x + 10, y), (x + 18, y + 8), (x + 10, y + 16), (x + 2, y + 8)]
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, (40, 60, 60), pts, 2)


class Goal(WorldObject):
    """Portal de folhas que leva à próxima fase."""

    def __init__(self, x, y):
        super().__init__(x, y, 40, 64)
        self.used = False

    def on_player_touch(self, player, level):
        if not self.used:
            self.used = True
            level.sfx("portal")
            level.particles.burst(self.centerx, self.centery, (180, 255, 180), 40, 6, 50, 5, 0, spark=True)
            level.scene.level_complete()

    def update(self, level):
        super().update(level)
        if self.tick % 5 == 0:
            a = self.tick * 0.3
            level.particles.burst(self.centerx + math.cos(a) * 16, self.centery + math.sin(a) * 26,
                                  (170, 255, 170), 1, 0.6, 30, 3, -0.02)

    def draw(self, surf, cam):
        cx, cy = round(self.centerx - cam.x), round(self.centery - cam.y)
        for i in range(5):
            k = (self.tick * 0.03 + i / 5) % 1.0
            w, h = int(40 * (1 - k)) + 4, int(64 * (1 - k)) + 4
            col = (int(100 + 155 * k), 255, int(120 + 100 * k))
            pygame.draw.ellipse(surf, col, (cx - w // 2, cy - h // 2, w, h), 2)
        pygame.draw.ellipse(surf, (60, 140, 70), (cx - 22, cy - 34, 44, 68), 4)
        for i in range(8):
            a = i * math.tau / 8 + self.tick * 0.02
            lx, ly = cx + math.cos(a) * 22, cy + math.sin(a) * 34
            pygame.draw.ellipse(surf, (90, 190, 80), (lx - 5, ly - 3, 10, 6))


class MovingPlatform(Entity):
    """Plataforma que vai e volta na horizontal levando quem estiver em cima."""

    RANGE = 2.5 * TILE

    def __init__(self, x, y):
        super().__init__(x, y, 3 * TILE, 14)
        self.base_x = x
        self.dx = 0.0
        self.phase = 0.0
        self.color = (170, 120, 70)

    def on_spawn(self):
        self.y -= TILE - self.h  # topo alinhado ao topo do tile
        self.base_x = self.x
        self.phase = (self.base_x / TILE) * 0.7

    def update(self, level):
        super().update(level)
        old = self.x
        self.x = self.base_x + math.sin(self.tick * 0.02 + self.phase) * self.RANGE
        self.dx = self.x - old
        p = level.player
        if p.riding is self:
            p.x += self.dx

    def draw(self, surf, cam):
        r = pygame.Rect(round(self.x - cam.x), round(self.y - cam.y), self.w, self.h)
        dark = tuple(max(0, c - 60) for c in self.color)
        pygame.draw.rect(surf, dark, r, border_radius=4)
        pygame.draw.rect(surf, self.color, r.inflate(-4, -6).move(0, -1), border_radius=3)
        for x in range(r.x + 12, r.right - 6, 24):
            pygame.draw.circle(surf, dark, (x, r.centery), 2)
