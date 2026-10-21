"""Inimigos comuns. Todos herdam de Enemy, que herda de Creature."""
import math
import random

import pygame

from .creature import Creature
from .items import SeedCoin
from .projectiles import Thorn
from ..config import TILE


class Enemy(Creature):
    name = "Inimigo"
    xp_reward = 3
    coin_reward = 1
    contact_damage = 3
    stompable = True
    collides = True
    death_color = (200, 80, 60)

    def __init__(self, x, y, w, h, hp):
        super().__init__(x, y, w, h, hp)
        self.active = False
        self.facing = -1
        self.knockback = 3
        self.invuln_time = 12

    # --- interface usada pelo Level para colisões -------------------------
    def stomp_rect(self):
        return self.rect if self.stompable else None

    def body_rects(self):
        return [self.rect]

    def hit_rect(self):
        return self.rect

    def on_stomp(self, player, level):
        level.sfx("pisao")
        self.take_damage(player.stomp_damage, level)

    def receive_attack(self, damage, level, source_x):
        return self.take_damage(damage, level, source_x)

    @property
    def stunned_by_hit(self):
        return self.invuln > self.invuln_time - 8

    def player_dir(self, level):
        return 1 if level.player.centerx > self.centerx else -1

    def dist_to_player(self, level):
        p = level.player
        return math.hypot(p.centerx - self.centerx, p.centery - self.centery)

    # --- ciclo ------------------------------------------------------------
    def update(self, level):
        super().update(level)
        self.ai(level)
        if self.collides:
            self.apply_gravity()
            self.move_and_collide(level)
        else:
            self.x += self.vx
            self.y += self.vy
        if self.y > level.height_px + 64:
            self.kill()

    def ai(self, level):
        pass

    def die(self, level):
        self.kill()
        level.sfx("inimigo")
        level.particles.burst(self.centerx, self.centery, self.death_color, 14, 3.5, 30, 5)
        level.gain_xp(self.xp_reward, self.centerx, self.y)
        for _ in range(self.coin_reward):
            coin = SeedCoin(self.centerx - 7, self.y)
            coin.drop(random.uniform(-2, 2))
            level.spawn(coin)


class Walker(Enemy):
    """Anda de um lado a outro, virando em paredes e beiradas."""
    speed = 1.0

    def ai(self, level):
        if self.stunned_by_hit or not self.on_ground:
            return
        self.vx = self.facing * self.speed
        front = self.x + self.w + 1 if self.facing > 0 else self.x - 1
        if not level.is_ground(int(front // TILE), int((self.bottom + 1) // TILE)):
            self.facing *= -1
            self.vx = 0

    def on_wall(self, level, direction):
        self.vx = 0
        self.facing = -direction


class Sauva(Walker):
    """Formiga saúva gigante: o inimigo mais comum da serra."""
    name = "Saúva"
    xp_reward = 3

    def __init__(self, x, y):
        super().__init__(x, y, 26, 18, 3)

    def render(self):
        s = pygame.Surface((34, 22), pygame.SRCALPHA)
        body, dark = (190, 60, 35), (110, 30, 20)
        step = math.sin(self.tick * 0.3) * 3
        for i, lx in enumerate((10, 16, 22)):
            off = step if i % 2 else -step
            pygame.draw.line(s, dark, (lx, 14), (lx + off - 2, 21), 2)
            pygame.draw.line(s, dark, (lx, 14), (lx - off + 2, 21), 2)
        pygame.draw.ellipse(s, body, (1, 6, 14, 12))
        pygame.draw.ellipse(s, body, (13, 9, 9, 8))
        pygame.draw.circle(s, body, (26, 10), 6)
        pygame.draw.ellipse(s, (240, 120, 90), (3, 8, 6, 3))
        pygame.draw.circle(s, (255, 255, 255), (28, 9), 2)
        pygame.draw.circle(s, (0, 0, 0), (29, 9), 1)
        pygame.draw.line(s, dark, (27, 5), (32, 0), 2)
        pygame.draw.line(s, dark, (31, 13), (34, 15), 2)
        return s


class Besouro(Walker):
    """Besouro de casca dura: pisões o viram de costas; golpeie enquanto está atordoado."""
    name = "Besouro"
    xp_reward = 10
    coin_reward = 3
    contact_damage = 4
    speed = 0.7
    death_color = (60, 160, 140)

    def __init__(self, x, y):
        super().__init__(x, y, 28, 20, 10)
        self.knockback = 1.5
        self.stunned = 0

    def on_stomp(self, player, level):
        level.sfx("pisao")
        self.stunned = 240
        self.vx = 0
        level.particles.text(self.centerx, self.y - 6, "Virou!", (200, 255, 220), 20)

    def body_rects(self):
        return [] if self.stunned else [self.rect]

    def receive_attack(self, damage, level, source_x):
        if self.stunned:
            return self.take_damage(damage * 2, level, source_x)
        level.particles.burst(self.centerx, self.centery, (230, 230, 230), 5, 2, 12, 2)
        return self.take_damage(max(1, damage // 3), level, source_x)

    def ai(self, level):
        if self.stunned:
            self.stunned -= 1
            if self.on_ground:
                self.vx *= 0.8
            return
        super().ai(level)

    def render(self):
        s = pygame.Surface((34, 26), pygame.SRCALPHA)
        shell, shine = (40, 120, 120), (120, 220, 200)
        if self.stunned:
            wig = math.sin(self.tick * 0.8) * 3
            for lx in (10, 17, 24):
                pygame.draw.line(s, (30, 30, 30), (lx, 8), (lx + wig, 1), 2)
            pygame.draw.ellipse(s, (60, 50, 40), (3, 6, 28, 16))
            pygame.draw.ellipse(s, shell, (3, 12, 28, 13))
            shake = 1 if self.stunned < 60 and (self.tick // 3) % 2 else 0
            if shake:
                s.scroll(1, 0)
            return s
        step = math.sin(self.tick * 0.25) * 3
        for i, lx in enumerate((9, 16, 23)):
            off = step if i % 2 else -step
            pygame.draw.line(s, (30, 30, 30), (lx, 18), (lx + off, 25), 2)
        pygame.draw.ellipse(s, shell, (2, 4, 26, 18))
        pygame.draw.line(s, (20, 70, 70), (15, 5), (15, 21), 2)
        pygame.draw.ellipse(s, shine, (6, 7, 8, 5))
        pygame.draw.circle(s, (40, 40, 50), (28, 14), 6)
        pygame.draw.line(s, (40, 40, 50), (30, 10), (34, 3), 3)
        pygame.draw.circle(s, (255, 230, 120), (30, 13), 2)
        return s


class Lodo(Enemy):
    """Gosma do brejo que salta em direção ao jogador."""
    name = "Lodo"
    xp_reward = 5
    contact_damage = 3
    death_color = (90, 200, 90)
    colors = ((90, 200, 90), (50, 130, 60), (190, 255, 180))

    def __init__(self, x, y):
        super().__init__(x, y, 26, 20, 6)
        self.wait = random.randint(30, 90)

    def ai(self, level):
        if not self.on_ground:
            return
        if not self.stunned_by_hit:
            self.vx *= 0.7
        self.wait -= 1
        if self.wait <= 0 and self.dist_to_player(level) < 420:
            self.facing = self.player_dir(level)
            self.vy = -8.5
            self.vx = 2.2 * self.facing
            self.wait = 70 + random.randint(0, 40)

    def render(self):
        s = pygame.Surface((36, 30), pygame.SRCALPHA)
        main, dark, light = self.colors
        if not self.on_ground:
            w, h = 22, 26
        else:
            squish = 1 + 0.12 * math.sin(self.tick * 0.15) + (0.25 if self.wait < 10 else 0)
            w, h = int(26 * squish), int(20 / squish)
        r = pygame.Rect(0, 0, w, h)
        r.midbottom = (18, 30)
        pygame.draw.ellipse(s, dark, r)
        pygame.draw.ellipse(s, main, r.inflate(-4, -4))
        pygame.draw.ellipse(s, light, (r.x + 5, r.y + 4, 7, 4))
        ey = r.y + h // 2 - 1
        for ex in (r.centerx + 2, r.centerx + 8):
            pygame.draw.circle(s, (255, 255, 255), (ex, ey), 3)
            pygame.draw.circle(s, (20, 20, 20), (ex + 1, ey), 1)
        return s


class Brasinha(Lodo):
    """Brasa viva do vulcão: salta como o Lodo, mas queima quem pisa."""
    name = "Brasinha"
    xp_reward = 6
    contact_damage = 4
    stompable = False
    death_color = (255, 140, 40)
    colors = ((255, 130, 40), (180, 50, 20), (255, 230, 120))

    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = self.max_hp = 5

    def update(self, level):
        super().update(level)
        if self.tick % 4 == 0:
            level.particles.burst(self.centerx, self.y + 4, (255, 180, 60), 1, 0.8, 18, 3, -0.06)


class Carcara(Enemy):
    """Carcará: patrulha o céu e dá rasantes quando vê o jogador por baixo."""
    name = "Carcará"
    xp_reward = 5
    collides = False
    gravity_scale = 0
    death_color = (150, 100, 60)
    patrol_speed = 1.2
    dive_speed = 4.6
    flap_rate = 0.3

    def __init__(self, x, y):
        super().__init__(x, y, 32, 22, 4)
        self.state = "patrol"
        self.state_t = 0
        self.home = (x, y)

    def on_spawn(self):
        self.home = (self.x, self.y)

    def ai(self, level):
        p = level.player
        self.state_t += 1
        hx, hy = self.home
        if self.state == "patrol":
            if abs(self.x - hx) > 4 * TILE:
                self.facing = 1 if self.x < hx else -1
            self.vx = self.facing * self.patrol_speed
            self.vy = (hy + math.sin(self.tick * 0.05) * 12 - self.y) * 0.1
            if (abs(p.centerx - self.centerx) < 200 and p.y > self.y + 20 and not p.dying
                    and self.state_t > 60):
                self.state, self.state_t = "dive", 0
                dx, dy = p.centerx - self.centerx, p.centery - self.centery
                d = max(1, math.hypot(dx, dy))
                self.vx, self.vy = dx / d * self.dive_speed, dy / d * self.dive_speed
                self.facing = 1 if dx > 0 else -1
        elif self.state == "dive":
            if self.state_t > 55 or level.rect_hits_solid(self.rect):
                self.state, self.state_t = "return", 0
        elif self.state == "return":
            self.vx = (hx - self.x) * 0.02
            self.vy = -2.2
            if self.y <= hy:
                self.y = hy
                self.state, self.state_t = "patrol", 0

    def render(self):
        s = pygame.Surface((40, 30), pygame.SRCALPHA)
        flap = math.sin(self.tick * self.flap_rate)
        wing_y = 13 - flap * 11 if self.state != "dive" else 4
        pygame.draw.polygon(s, (110, 70, 40), [(12, 14), (26, 14), (16, wing_y)])
        pygame.draw.ellipse(s, (140, 95, 55), (6, 10, 24, 12))
        pygame.draw.polygon(s, (90, 60, 35), [(6, 14), (0, 10), (0, 19)])
        pygame.draw.circle(s, (240, 235, 220), (30, 12), 6)
        pygame.draw.polygon(s, (20, 20, 20), [(26, 6), (35, 7), (30, 9)])
        pygame.draw.polygon(s, (240, 150, 40), [(35, 11), (40, 13), (35, 15)])
        pygame.draw.circle(s, (0, 0, 0), (32, 11), 1)
        pygame.draw.polygon(s, (160, 115, 70), [(12, 15), (26, 15), (18, 26 - flap * 4)])
        return s


class Morcego(Carcara):
    """Morcego das cavernas: menor, mais rápido e mais nervoso."""
    name = "Morcego"
    xp_reward = 5
    death_color = (140, 90, 170)
    patrol_speed = 1.8
    dive_speed = 5.2
    flap_rate = 0.6

    def __init__(self, x, y):
        super().__init__(x, y)
        self.w, self.h = 26, 18
        self.hp = self.max_hp = 3

    def render(self):
        s = pygame.Surface((40, 26), pygame.SRCALPHA)
        flap = math.sin(self.tick * self.flap_rate)
        wy = int(10 - flap * 9)
        for side in (-1, 1):
            tip = (20 + side * 19, wy)
            pygame.draw.polygon(s, (80, 50, 110), [(20, 12), tip, (20 + side * 13, 16), (20 + side * 7, 13)])
        pygame.draw.ellipse(s, (110, 70, 140), (13, 7, 14, 13))
        pygame.draw.polygon(s, (110, 70, 140), [(15, 8), (16, 2), (19, 8)])
        pygame.draw.polygon(s, (110, 70, 140), [(21, 8), (24, 2), (25, 8)])
        pygame.draw.circle(s, (255, 230, 90), (23, 12), 2)
        pygame.draw.circle(s, (255, 230, 90), (17, 12), 2)
        return s


class Espinhoso(Enemy):
    """Cacto guardião: fica parado e dispara espinhos. Não pise nele!"""
    name = "Espinhoso"
    xp_reward = 8
    coin_reward = 2
    stompable = False
    death_color = (90, 170, 80)

    def __init__(self, x, y):
        super().__init__(x, y, 24, 36, 8)
        self.knockback = 0
        self.fire_timer = 90

    def ai(self, level):
        self.vx = 0
        self.facing = self.player_dir(level)
        if abs(level.player.centerx - self.centerx) < 380 and abs(level.player.centery - self.centery) < 120:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                self.fire_timer = 110
                level.spawn(Thorn(self.centerx + self.facing * 12, self.y + 14, self.facing))
                level.sfx("tiro")

    def render(self):
        s = pygame.Surface((36, 40), pygame.SRCALPHA)
        swell = 2 if self.fire_timer < 20 and (self.tick // 3) % 2 else 0
        green, dark = (70, 160, 70), (40, 110, 50)
        pygame.draw.rect(s, dark, (10 - swell, 4 - swell, 16 + swell * 2, 36 + swell), border_radius=8)
        pygame.draw.rect(s, green, (12 - swell, 6 - swell, 12 + swell * 2, 34 + swell), border_radius=6)
        pygame.draw.rect(s, green, (2, 14, 8, 6), border_radius=3)
        pygame.draw.rect(s, green, (2, 8, 6, 10), border_radius=3)
        pygame.draw.rect(s, green, (26, 18, 8, 6), border_radius=3)
        pygame.draw.rect(s, green, (28, 12, 6, 10), border_radius=3)
        for y in range(10, 38, 7):
            pygame.draw.line(s, (240, 240, 200), (10, y), (7, y - 2), 1)
            pygame.draw.line(s, (240, 240, 200), (26, y + 3), (29, y + 1), 1)
        pygame.draw.circle(s, (255, 120, 170), (18, 4), 4)
        pygame.draw.line(s, (20, 40, 20), (17, 14), (21, 16), 2)
        pygame.draw.line(s, (20, 40, 20), (23, 16), (26, 14), 2)
        pygame.draw.circle(s, (20, 20, 20), (20, 18), 1)
        pygame.draw.circle(s, (20, 20, 20), (24, 18), 1)
        return s
