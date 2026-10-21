"""Partículas e textos flutuantes (números de dano, XP etc.)."""
import math
import random

import pygame

from .entity import Entity
from ..util import font


class Particle(Entity):
    def __init__(self, x, y, vx, vy, color, life, size=4, gravity=0.2):
        super().__init__(x, y, size, size)
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = self.max_life = life
        self.size = size
        self.gravity = gravity

    def update(self, level=None):
        self.tick += 1
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.kill()

    def draw(self, surf, cam):
        k = self.life / self.max_life
        s = max(1, int(self.size * (0.4 + 0.6 * k)))
        pygame.draw.rect(surf, self.color, (int(self.x - cam.x), int(self.y - cam.y), s, s))


class Spark(Particle):
    """Partícula circular com brilho."""

    def draw(self, surf, cam):
        k = self.life / self.max_life
        r = max(1, int(self.size * k))
        pos = (int(self.x - cam.x), int(self.y - cam.y))
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, int(90 * k)), (r * 2, r * 2), r * 2)
        surf.blit(glow, (pos[0] - r * 2, pos[1] - r * 2))
        pygame.draw.circle(surf, self.color, pos, r)


class FloatingText(Particle):
    def __init__(self, x, y, text, color, size=24):
        super().__init__(x, y, random.uniform(-0.3, 0.3), -1.6, color, 50, 1, gravity=0.03)
        self.image = font(size, True).render(text, True, color)
        self.shadow = font(size, True).render(text, True, (0, 0, 0))

    def draw(self, surf, cam):
        alpha = int(255 * min(1.0, self.life / 20))
        self.image.set_alpha(alpha)
        self.shadow.set_alpha(alpha)
        r = self.image.get_rect(center=(int(self.x - cam.x), int(self.y - cam.y)))
        surf.blit(self.shadow, r.move(1, 1))
        surf.blit(self.image, r)


class ParticleSystem:
    def __init__(self):
        self.items = []

    def add(self, p):
        self.items.append(p)

    def burst(self, x, y, color, n=10, speed=3.0, life=30, size=4, gravity=0.2, spark=False):
        cls = Spark if spark else Particle
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(0.3, 1.0) * speed
            self.items.append(cls(x, y, math.cos(a) * v, math.sin(a) * v - speed * 0.3,
                                  color, random.randint(life // 2, life), size, gravity))

    def text(self, x, y, msg, color=(255, 255, 255), size=24):
        self.items.append(FloatingText(x, y, msg, color, size))

    def update(self):
        for p in self.items:
            p.update()
        self.items = [p for p in self.items if p.alive]

    def draw(self, surf, cam):
        for p in self.items:
            p.draw(surf, cam)
