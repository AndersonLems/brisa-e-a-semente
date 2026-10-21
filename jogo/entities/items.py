"""Itens coletáveis espalhados pelo mundo."""
import math
import random

import pygame

from .entity import PhysicsEntity


class Item(PhysicsEntity):
    """Item base: flutua parado, ou salta para fora de um baú e cai."""

    sound = "moeda"
    glow_color = (255, 255, 200)

    def __init__(self, x, y, w=16, h=16):
        super().__init__(x, y, w, h)
        self.floating = True
        self.pickup_delay = 0
        self.lifetime = None

    def pop_out(self):
        """Salta de um baú."""
        self.floating = False
        self.vy = -7
        self.pickup_delay = 12

    def drop(self, vx):
        """Cai de um inimigo derrotado; some depois de um tempo."""
        self.floating = False
        self.vx, self.vy = vx, random.uniform(-6, -3)
        self.pickup_delay = 15
        self.lifetime = 600

    @property
    def collectible(self):
        return self.pickup_delay <= 0

    def update(self, level):
        super().update(level)
        if self.pickup_delay > 0:
            self.pickup_delay -= 1
        if not self.floating:
            self.apply_gravity()
            self.move_and_collide(level)
            if self.on_ground:
                self.vx *= 0.85
        if self.lifetime is not None:
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.kill()
        if self.y > level.height_px:
            self.kill()

    def on_wall(self, level, direction):
        self.vx = -self.vx * 0.5

    def collect(self, player, level):
        self.apply(player, level)
        level.sfx(self.sound)
        level.particles.burst(self.centerx, self.centery, self.glow_color, 8, 2.0, 20, 3, 0.05, spark=True)
        self.kill()

    def apply(self, player, level):
        raise NotImplementedError

    def icon(self, surf, cx, cy):
        raise NotImplementedError

    def draw(self, surf, cam):
        bob = math.sin(self.tick * 0.08 + self.x * 0.1) * 3 if self.floating else 0
        if self.lifetime is not None and self.lifetime < 120 and (self.tick // 4) % 2:
            return
        self.icon(surf, int(self.centerx - cam.x), int(self.centery - cam.y + bob))


class SeedCoin(Item):
    """Semente Dourada: a moeda do jogo."""
    glow_color = (255, 220, 90)

    def __init__(self, x, y):
        super().__init__(x, y, 14, 16)
        self.auto = False

    def pop_out(self):
        super().pop_out()
        self.vy = -9
        self.auto = True

    def update(self, level):
        super().update(level)
        if self.auto and self.tick > 22:
            self.collect(level.player, level)

    def apply(self, player, level):
        level.add_coins(1)

    def icon(self, surf, cx, cy):
        squash = abs(math.cos(self.tick * 0.06 + self.x * 0.01))
        w = max(4, int(12 * (0.3 + 0.7 * squash)))
        pygame.draw.ellipse(surf, (170, 110, 20), (cx - w // 2 - 1, cy - 8, w + 2, 17))
        pygame.draw.ellipse(surf, (255, 205, 60), (cx - w // 2, cy - 7, w, 15))
        if w > 5:
            pygame.draw.ellipse(surf, (255, 245, 180), (cx - w // 4, cy - 5, max(2, w // 3), 6))


class HeartFruit(Item):
    """Fruta-coração: recupera vida."""
    sound = "cura"
    glow_color = (255, 120, 140)
    HEAL = 8

    def apply(self, player, level):
        healed = player.heal(self.HEAL)
        level.particles.text(player.centerx, player.y - 10, f"+{healed} HP", (255, 120, 140))

    def icon(self, surf, cx, cy):
        pygame.draw.circle(surf, (210, 30, 60), (cx - 4, cy - 1), 5)
        pygame.draw.circle(surf, (210, 30, 60), (cx + 4, cy - 1), 5)
        pygame.draw.polygon(surf, (210, 30, 60), [(cx - 9, cy), (cx + 9, cy), (cx, cy + 9)])
        pygame.draw.circle(surf, (255, 150, 170), (cx - 5, cy - 3), 2)
        pygame.draw.ellipse(surf, (70, 170, 60), (cx, cy - 11, 8, 5))


class ManaFlower(Item):
    """Flor-de-mana: recupera magia."""
    sound = "cura"
    glow_color = (120, 180, 255)
    RESTORE = 6

    def apply(self, player, level):
        before = player.mp
        player.mp = min(player.stats.max_mp, player.mp + self.RESTORE)
        level.particles.text(player.centerx, player.y - 10, f"+{player.mp - before} MP", (120, 180, 255))

    def icon(self, surf, cx, cy):
        for i in range(5):
            a = i * math.tau / 5 + self.tick * 0.03
            pygame.draw.circle(surf, (90, 150, 255), (int(cx + math.cos(a) * 5), int(cy + math.sin(a) * 5)), 4)
        pygame.draw.circle(surf, (255, 240, 150), (cx, cy), 3)


class XPCrystal(Item):
    """Cristal de experiência."""
    sound = "bau"
    glow_color = (200, 140, 255)
    XP = 5

    def __init__(self, x, y):
        super().__init__(x, y, 14, 18)

    def apply(self, player, level):
        level.gain_xp(self.XP, self.centerx, self.y)

    def icon(self, surf, cx, cy):
        glow = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(glow, (190, 120, 255, 60 + int(30 * math.sin(self.tick * 0.1))), (18, 18), 16)
        surf.blit(glow, (cx - 18, cy - 18))
        pts = [(cx, cy - 10), (cx + 7, cy), (cx, cy + 10), (cx - 7, cy)]
        pygame.draw.polygon(surf, (170, 100, 250), pts)
        pygame.draw.polygon(surf, (230, 200, 255), [(cx, cy - 10), (cx + 3, cy - 1), (cx, cy + 4), (cx - 3, cy - 1)])
        pygame.draw.polygon(surf, (80, 40, 140), pts, 1)


class AncestralSeed(Item):
    """A Semente Ancestral: recuperá-la vence o jogo."""
    sound = "vitoria"
    glow_color = (200, 255, 150)

    def __init__(self, x, y):
        super().__init__(x, y, 24, 28)

    def apply(self, player, level):
        level.scene.level_complete()

    def icon(self, surf, cx, cy):
        t = self.tick
        glow = pygame.Surface((120, 120), pygame.SRCALPHA)
        for i in range(8):
            a = i * math.tau / 8 + t * 0.02
            end = (60 + math.cos(a) * 55, 60 + math.sin(a) * 55)
            pygame.draw.line(glow, (255, 255, 160, 90), (60, 60), end, 3)
        pygame.draw.circle(glow, (220, 255, 150, 90), (60, 60), 26 + int(4 * math.sin(t * 0.1)))
        surf.blit(glow, (cx - 60, cy - 60))
        pygame.draw.ellipse(surf, (120, 80, 20), (cx - 11, cy - 13, 22, 28))
        pygame.draw.ellipse(surf, (240, 190, 70), (cx - 9, cy - 11, 18, 24))
        pygame.draw.ellipse(surf, (255, 250, 200), (cx - 5, cy - 8, 6, 9))
        pygame.draw.line(surf, (60, 160, 60), (cx, cy - 12), (cx + 2, cy - 20), 3)
        pygame.draw.ellipse(surf, (90, 200, 80), (cx + 1, cy - 24, 10, 6))
