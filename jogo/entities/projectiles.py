"""Projéteis: rajada de vento da Brisa, espinhos e bolas de fogo inimigas."""
import math

import pygame

from .entity import Entity


class Projectile(Entity):
    team = "enemy"
    gravity = 0.0
    color = (255, 255, 255)

    def __init__(self, x, y, vx, vy, w, h, damage, life=150):
        super().__init__(x - w / 2, y - h / 2, w, h)
        self.vx, self.vy = vx, vy
        self.damage = damage
        self.life = life

    def update(self, level):
        super().update(level)
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0 or level.rect_hits_solid(self.rect):
            self.impact(level)

    def impact(self, level):
        level.particles.burst(self.centerx, self.centery, self.color, 6, 2.5, 20, 3)
        self.kill()


class WindBolt(Projectile):
    """Rajada de Vento: magia da Brisa."""
    team = "player"
    color = (180, 245, 255)

    def __init__(self, x, y, direction, damage, vy=0.0):
        super().__init__(x, y, direction * 8.5, vy, 22, 16, damage, life=55)
        self.direction = direction

    def update(self, level):
        super().update(level)
        if self.tick % 3 == 0:
            level.particles.burst(self.centerx - self.direction * 8, self.centery, (200, 250, 255),
                                  1, 0.6, 14, 3, 0)

    def draw(self, surf, cam):
        cx, cy = int(self.centerx - cam.x), int(self.centery - cam.y)
        spin = self.tick * 0.5
        for i in range(3):
            r = 10 - i * 3
            rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            start = spin + i * 2.1
            pygame.draw.arc(surf, self.color if i else (255, 255, 255), rect, start, start + 3.6, 3)


class Thorn(Projectile):
    """Espinho disparado pelo Espinhoso."""
    color = (120, 200, 90)

    def __init__(self, x, y, direction):
        super().__init__(x, y, direction * 4.2, 0, 14, 6, 3, life=160)
        self.direction = direction

    def draw(self, surf, cam):
        cx, cy = self.centerx - cam.x, self.centery - cam.y
        d = self.direction
        pts = [(cx + 8 * d, cy), (cx - 7 * d, cy - 3), (cx - 7 * d, cy + 3)]
        pygame.draw.polygon(surf, (230, 240, 180), pts)
        pygame.draw.polygon(surf, (60, 110, 40), pts, 1)


class Fireball(Projectile):
    """Bola de fogo do Boitatá."""
    color = (255, 150, 40)

    def __init__(self, x, y, vx, vy, damage=5, gravity=0.0):
        super().__init__(x, y, vx, vy, 16, 16, damage, life=220)
        self.gravity = gravity

    def update(self, level):
        super().update(level)
        if self.tick % 2 == 0:
            level.particles.burst(self.centerx, self.centery, (255, 200, 60), 1, 0.8, 16, 4, -0.05)

    def impact(self, level):
        level.particles.burst(self.centerx, self.centery, (255, 120, 30), 12, 3.5, 25, 5, spark=True)
        self.kill()

    def draw(self, surf, cam):
        cx, cy = int(self.centerx - cam.x), int(self.centery - cam.y)
        pulse = 2 * math.sin(self.tick * 0.4)
        glow = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 120, 20, 70), (24, 24), int(20 + pulse))
        surf.blit(glow, (cx - 24, cy - 24))
        pygame.draw.circle(surf, (255, 90, 20), (cx, cy), 9)
        pygame.draw.circle(surf, (255, 220, 90), (cx, cy), 5)
