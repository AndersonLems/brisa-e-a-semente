"""Boitatá, a serpente de fogo — chefe final."""
import math
import random

import pygame

from .enemies import Enemy
from .items import AncestralSeed
from .projectiles import Fireball


class Boitata(Enemy):
    name = "Boitatá"
    xp_reward = 100
    coin_reward = 15
    contact_damage = 6
    collides = False
    gravity_scale = 0
    death_color = (255, 160, 40)
    SEGMENTS = 11
    SPACING = 5

    def __init__(self, x, y):
        super().__init__(x, y, 44, 38, 90)
        self.invuln_time = 35
        self.knockback = 0
        self.active = False       # só acorda quando o jogador entra na arena
        self.awake = False
        self.state = "sleep"
        self.state_t = 0
        self.trail = []
        self.target = (0, 0)
        self.dying_t = 0
        self.arena = None

    def on_spawn(self):
        self.home = (self.x, self.y)
        self.trail = [(self.centerx, self.centery)] * (self.SEGMENTS * self.SPACING + 1)

    # --- interface de colisão --------------------------------------------
    @property
    def enraged(self):
        return self.hp <= self.max_hp // 2

    def stomp_rect(self):
        return self.rect if self.awake and not self.dying_t else None

    def body_rects(self):
        if not self.awake or self.dying_t:
            return []
        rects = [self.rect]
        for i in range(2, self.SEGMENTS):
            x, y = self.trail[i * self.SPACING]
            r = self._seg_radius(i) - 3
            rects.append(pygame.Rect(x - r, y - r, r * 2, r * 2))
        return rects

    def hit_rect(self):
        return self.rect if self.awake and not self.dying_t else pygame.Rect(0, 0, 0, 0)

    def _seg_radius(self, i):
        return int(18 - i * 1.1)

    def wake(self, level, arena):
        self.awake = True
        self.arena = arena
        self._set("rise")
        level.sfx("rugido")
        level.camera.shake(6, 50)
        level.scene.notify("O BOITATÁ DESPERTOU!", (255, 140, 60), 150)

    def _set(self, state):
        self.state, self.state_t = state, 0

    # --- dano -------------------------------------------------------------
    def on_stomp(self, player, level):
        level.sfx("pisao")
        self.receive_attack(player.stomp_damage, level, player.centerx)

    def receive_attack(self, damage, level, source_x):
        was_enraged = self.enraged
        bonus = 1.5 if self.state == "tired" else 1.0
        hit = self.take_damage(int(damage * bonus), level, source_x)
        if hit and self.alive:
            level.sfx("chefe_dano")
            level.camera.shake(3, 8)
            if self.enraged and not was_enraged:
                level.sfx("rugido")
                level.scene.notify("O Boitatá está furioso!", (255, 90, 40), 120)
                self._set("rise")
        return hit

    def die(self, level):
        self.dying_t = 1
        self.hp = 0
        level.sfx("rugido")
        level.camera.shake(8, 120)

    # --- comportamento ----------------------------------------------------
    def update(self, level):
        self.tick += 1
        if self.invuln > 0:
            self.invuln -= 1
        if self.flash > 0:
            self.flash -= 1
        if self.dying_t:
            self._update_dying(level)
        elif self.awake:
            self.state_t += 1
            getattr(self, "_state_" + self.state)(level)
        else:
            self.y = self.home[1] + 70 + math.sin(self.tick * 0.03) * 4
            self.x = self.home[0]
        self.trail.insert(0, (self.centerx, self.centery))
        self.trail.pop()

    def _move_towards(self, tx, ty, k):
        self.x += (tx - self.w / 2 - self.x) * k
        self.y += (ty - self.h / 2 - self.y) * k

    def _state_rise(self, level):
        a = self.arena
        self._move_towards(a.centerx, a.top + 150, 0.05)
        if self.state_t > 70:
            self._set("fly")

    def _state_fly(self, level):
        a, speed = self.arena, (1.5 if self.enraged else 1.0)
        t = self.state_t * 0.018 * speed
        tx = a.centerx + math.sin(t) * a.width * 0.38
        ty = a.top + 150 + math.sin(t * 2) * 70
        old = self.centerx
        self._move_towards(tx, ty, 0.08)
        self.facing = 1 if self.centerx >= old else -1
        interval = 55 if self.enraged else 80
        if self.state_t % interval == interval - 1:
            self._shoot(level)
        if self.state_t > (260 if self.enraged else 320):
            self._set("aim")

    def _shoot(self, level):
        p = level.player
        dx, dy = p.centerx - self.centerx, p.centery - self.centery
        base = math.atan2(dy, dx)
        angles = (base - 0.3, base, base + 0.3) if self.enraged else (base,)
        for a in angles:
            level.spawn(Fireball(self.centerx, self.centery, math.cos(a) * 4.2, math.sin(a) * 4.2, 5))
        level.sfx("fogo")

    def _state_aim(self, level):
        self.x += random.uniform(-2, 2)
        p = level.player
        self.facing = 1 if p.centerx > self.centerx else -1
        if self.state_t % 6 == 0:
            level.particles.burst(self.centerx, self.centery, (255, 220, 120), 3, 2, 18, 4, 0, spark=True)
        if self.state_t > (30 if self.enraged else 45):
            self.target = (p.centerx, p.centery)
            dx, dy = self.target[0] - self.centerx, self.target[1] - self.centery
            d = max(1, math.hypot(dx, dy))
            sp = 11 if self.enraged else 9
            self.vx, self.vy = dx / d * sp, dy / d * sp
            self._set("charge")
            level.sfx("rugido")

    def _state_charge(self, level):
        self.x += self.vx
        self.y += self.vy
        floor = level.floor_y - self.h
        a = self.arena
        hit_floor = self.y >= floor
        out = self.x < a.left or self.x + self.w > a.right
        if hit_floor or out or self.state_t > 80:
            self.y = min(self.y, floor)
            self.x = max(a.left, min(self.x, a.right - self.w))
            level.camera.shake(7, 20)
            level.particles.burst(self.centerx, self.bottom, (255, 140, 40), 20, 5, 35, 6, spark=True)
            level.sfx("quebrar")
            if self.enraged:
                for vx in (-4, -2, 2, 4):
                    level.spawn(Fireball(self.centerx, self.bottom - 10, vx, -7, 4, gravity=0.3))
            self._set("tired")

    def _state_tired(self, level):
        self.y = level.floor_y - self.h + math.sin(self.state_t * 0.1) * 2
        if self.state_t % 10 == 0:
            level.particles.burst(self.centerx, self.y, (120, 110, 110), 2, 1, 40, 6, -0.05)
        if self.state_t > (90 if self.enraged else 130):
            self._set("rise")

    def _update_dying(self, level):
        self.dying_t += 1
        self.x += random.uniform(-3, 3)
        if self.dying_t % 6 == 0:
            i = random.randrange(len(self.trail))
            x, y = self.trail[i]
            level.particles.burst(x, y, random.choice([(255, 200, 60), (255, 110, 30), (255, 255, 200)]),
                                  12, 5, 35, 6, spark=True)
            level.sfx("inimigo")
        if self.dying_t > 140:
            super().die(level)  # recompensas de Enemy.die (XP e sementes)
            seed = AncestralSeed(self.arena.centerx - 12, self.arena.top + 200)
            level.spawn(seed)
            level.on_boss_defeated()

    # --- desenho ----------------------------------------------------------
    def draw(self, surf, cam):
        if not self.awake:
            return
        flick = self.tick * 0.3
        for i in range(self.SEGMENTS - 1, 0, -1):
            x, y = self.trail[i * self.SPACING]
            r = self._seg_radius(i)
            px, py = int(x - cam.x), int(y - cam.y)
            glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 120, 20, 50), (r * 2, r * 2), r * 2)
            surf.blit(glow, (px - r * 2, py - r * 2))
            col = (255, int(90 + 60 * math.sin(flick + i)), 30)
            pygame.draw.circle(surf, col, (px, py), r)
            pygame.draw.circle(surf, (255, 220, 120), (px, py), max(2, r // 2))
        super().draw(surf, cam)

    def render(self):
        s = pygame.Surface((64, 56), pygame.SRCALPHA)
        cx, cy = 30, 30
        glow = 60 + int(30 * math.sin(self.tick * 0.2))
        pygame.draw.circle(s, (255, 140, 30, glow), (cx, cy), 27)
        pygame.draw.ellipse(s, (230, 70, 20), (cx - 22, cy - 18, 46, 36))
        pygame.draw.ellipse(s, (255, 150, 40), (cx - 16, cy - 13, 34, 24))
        pygame.draw.polygon(s, (255, 220, 120), [(cx - 12, cy - 15), (cx - 18, cy - 30), (cx - 4, cy - 17)])
        pygame.draw.polygon(s, (255, 220, 120), [(cx + 2, cy - 17), (cx + 4, cy - 32), (cx + 12, cy - 15)])
        tired = self.state == "tired"
        eye = (255, 255, 255) if not tired else (200, 200, 200)
        if tired:
            pygame.draw.line(s, (40, 10, 0), (cx + 6, cy - 4), (cx + 16, cy - 4), 3)
        else:
            pygame.draw.circle(s, eye, (cx + 11, cy - 5), 7)
            pygame.draw.circle(s, (200, 20, 0), (cx + 13, cy - 5), 4)
            pygame.draw.circle(s, (0, 0, 0), (cx + 14, cy - 5), 2)
        mouth = 8 if self.state in ("aim", "charge") else 3
        pygame.draw.ellipse(s, (90, 10, 0), (cx + 6, cy + 5, 20, mouth + 4))
        pygame.draw.polygon(s, (255, 255, 230), [(cx + 10, cy + 6), (cx + 13, cy + 11), (cx + 15, cy + 6)])
        pygame.draw.polygon(s, (255, 255, 230), [(cx + 18, cy + 6), (cx + 21, cy + 11), (cx + 23, cy + 6)])
        return s
