"""Brisa, a Guardiã do Vento — a personagem jogável."""
import math

import pygame

from .creature import Creature
from .projectiles import WindBolt
from ..util import approach


class Player(Creature):
    ACCEL = 0.5
    AIR_ACCEL = 0.35
    FRICTION = 0.45
    WALK_SPEED = 3.6
    RUN_SPEED = 5.6
    JUMP_SPEED = -11.2
    RUN_JUMP_SPEED = -11.9
    DOUBLE_JUMP_SPEED = -9.8
    COYOTE_FRAMES = 6
    JUMP_BUFFER = 7
    ATTACK_FRAMES = 20
    MAGIC_COST = 3
    MAGIC_COOLDOWN = 22
    MP_REGEN_FRAMES = 150
    invuln_time = 75
    damage_color = (255, 90, 90)

    def __init__(self, x, y, progress):
        self.progress = progress
        self.stats = progress.stats
        self.inventory = progress.inventory
        super().__init__(x, y, 20, 30, self.stats.max_hp)
        self.knockback = 5
        self.mp = self.stats.max_mp
        self.coyote = 0
        self.jump_buffer = 0
        self.air_jumps = 0
        self.attack_timer = 0
        self.attack_hits = set()
        self.magic_cooldown = 0
        self.mp_regen = 0
        self.dying = 0
        self.anim = 0.0
        self.scarf = []

    # ------------------------------------------------------------ propriedades
    @property
    def attack_damage(self):
        return self.stats.attack

    @property
    def stomp_damage(self):
        return self.stats.attack * 2 + 2

    def attack_hitbox(self):
        if not 5 <= self.attack_timer <= 16:
            return None
        w, h = 32, 30
        x = self.x + self.w - 2 if self.facing > 0 else self.x - w + 2
        return pygame.Rect(round(x), round(self.y - 2), w, h)

    # ------------------------------------------------------------ atualização
    def update(self, level):
        if self.dying:
            self._update_dying(level)
            return
        super().update(level)
        inp = level.input
        self._horizontal(inp)
        self._jump(inp, level)
        self._actions(inp, level)
        self.apply_gravity()
        if self.drop_through > 0:
            self.drop_through -= 1
        self.move_and_collide(level)
        level.check_hazards(self)
        self._regen()
        self._animate()
        if self.y > level.height_px + 40:
            self.fall_out(level)

    def _horizontal(self, inp):
        direction = inp.axis_x()
        top = self.RUN_SPEED if inp.held("run") else self.WALK_SPEED
        if direction:
            if self.attack_timer == 0:
                self.facing = direction
            accel = self.ACCEL if self.on_ground else self.AIR_ACCEL
            if self.vx * direction < top:
                self.vx = min(self.vx * direction + accel, top) * direction
            else:
                self.vx = approach(self.vx, direction * top, 0.2)
        else:
            self.vx = approach(self.vx, 0, self.FRICTION if self.on_ground else 0.12)

    def _jump(self, inp, level):
        if self.on_ground:
            self.coyote = self.COYOTE_FRAMES
            self.air_jumps = 1 if self.stats.has_double_jump else 0
        elif self.coyote > 0:
            self.coyote -= 1

        if inp.pressed("jump"):
            self.jump_buffer = self.JUMP_BUFFER
        elif self.jump_buffer > 0:
            self.jump_buffer -= 1

        if self.jump_buffer > 0:
            if inp.held("down") and self.on_ground and self.standing_on_one_way(level):
                self.drop_through = 12
                self.y += 2
                self.jump_buffer = 0
            elif self.coyote > 0:
                fast = abs(self.vx) > self.WALK_SPEED + 0.5
                self.vy = self.RUN_JUMP_SPEED if fast else self.JUMP_SPEED
                self.coyote = self.jump_buffer = 0
                level.sfx("pulo")
            elif self.air_jumps > 0 and inp.pressed("jump"):
                self.vy = self.DOUBLE_JUMP_SPEED
                self.air_jumps -= 1
                self.jump_buffer = 0
                level.sfx("pulo_duplo")
                level.particles.burst(self.centerx, self.bottom, (220, 250, 255), 10, 2.5, 22, 4, 0.05)

        if inp.released("jump") and self.vy < -4:
            self.vy = -4

    def _actions(self, inp, level):
        if self.attack_timer > 0:
            self.attack_timer -= 1
        elif inp.pressed("attack"):
            self.attack_timer = self.ATTACK_FRAMES
            self.attack_hits.clear()
            level.sfx("golpe")

        if self.magic_cooldown > 0:
            self.magic_cooldown -= 1
        if inp.pressed("magic"):
            self._cast(level)
        if inp.pressed("potion_hp"):
            self._use_item("pocao_vida", level)
        if inp.pressed("potion_mp"):
            self._use_item("elixir_mana", level)

    def _cast(self, level):
        if not self.stats.has_magic:
            level.scene.notify("A Rajada de Vento desperta no nível 2", (180, 220, 255), 90)
            level.sfx("erro")
            return
        if self.magic_cooldown > 0:
            return
        if self.mp < self.MAGIC_COST:
            level.particles.text(self.centerx, self.y - 8, "Sem mana!", (120, 170, 255), 20)
            level.sfx("erro")
            return
        self.mp -= self.MAGIC_COST
        self.magic_cooldown = self.MAGIC_COOLDOWN
        dmg = self.stats.attack + 2
        x = self.centerx + self.facing * 14
        spreads = (0.0, -1.6, 1.6) if self.stats.has_triple_bolt else (0.0,)
        for vy in spreads:
            level.spawn(WindBolt(x, self.y + 12, self.facing, dmg, vy))
        level.sfx("magia")

    def _use_item(self, item_id, level):
        if self.inventory.use(item_id, self, level):
            level.sfx("cura")
        else:
            level.sfx("erro")

    def _regen(self):
        if self.mp < self.stats.max_mp:
            self.mp_regen += 1
            if self.mp_regen >= self.MP_REGEN_FRAMES:
                self.mp_regen = 0
                self.mp += 1

    def _animate(self):
        if self.on_ground:
            self.anim += abs(self.vx) * 0.07
        anchor = (self.centerx - self.facing * 3, self.y + 11)
        if not self.scarf:
            self.scarf = [anchor] * 7
        pts = [anchor]
        for i in range(1, 7):
            px, py = self.scarf[i]
            tx = pts[i - 1][0] - self.facing * 4 - self.vx * 0.4
            ty = pts[i - 1][1] + math.sin(self.tick * 0.25 + i) * 1.3 + 0.5 - self.vy * 0.15
            nx, ny = px + (tx - px) * 0.55, py + (ty - py) * 0.55
            # mantém o cachecol com comprimento fixo
            ax, ay = pts[i - 1]
            d = math.hypot(nx - ax, ny - ay)
            if d > 5:
                nx, ny = ax + (nx - ax) * 5 / d, ay + (ny - ay) * 5 / d
            pts.append((nx, ny))
        self.scarf = pts

    # ------------------------------------------------------------ eventos
    def on_ceiling(self, level, tile):
        tile.on_bump(level, self)

    def bounce(self, level):
        """Quique após pisar num inimigo (segurar pulo = quique mais alto)."""
        self.vy = -11 if level.input.held("jump") else -7.5
        self.air_jumps = 1 if self.stats.has_double_jump else 0

    def take_damage(self, amount, level, source_x=None):
        if self.dying:
            return False
        hit = super().take_damage(max(1, amount - self.stats.defense), level, source_x)
        if hit and not self.dying:
            level.sfx("dano")
            level.camera.shake(4, 10)
        return hit

    def die(self, level):
        self.dying = 1
        self.vx, self.vy = 0, -9
        level.sfx("morte")
        level.game.audio.stop_music()

    def fall_out(self, level):
        self.hp = 0
        self.dying = 50
        self.vy = 0
        level.sfx("morte")
        level.game.audio.stop_music()

    def _update_dying(self, level):
        self.dying += 1
        self.tick += 1
        if self.dying < 100:
            self.vy += 0.45
            self.y += self.vy
        if self.dying == 110:
            level.on_player_dead()

    def on_level_up(self):
        self.max_hp = self.stats.max_hp
        self.hp = self.max_hp
        self.mp = self.stats.max_mp

    # ------------------------------------------------------------ desenho
    def render(self):
        s = pygame.Surface((48, 50), pygame.SRCALPHA)
        cx, by = 24, 50
        skin, hair = (245, 205, 165), (110, 60, 30)
        tunic, tunic_dark = (40, 170, 160), (25, 115, 110)
        pants, boot = (60, 60, 110), (95, 55, 30)
        moving = self.on_ground and abs(self.vx) > 0.4
        bob = 0 if moving or not self.on_ground else int(math.sin(self.tick * 0.08) * 1.2)
        if self.dying:
            by -= 2
        by += bob

        # pernas
        if not self.on_ground:
            pygame.draw.line(s, pants, (cx - 3, by - 12), (cx - 7, by - 5), 4)
            pygame.draw.line(s, pants, (cx + 3, by - 12), (cx + 6, by - 7), 4)
            pygame.draw.circle(s, boot, (cx - 7, by - 4), 3)
            pygame.draw.circle(s, boot, (cx + 6, by - 6), 3)
        else:
            sw = math.sin(self.anim) * 5 if moving else 0
            for side, k in ((-3, 1), (3, -1)):
                fx = cx + side + sw * k
                pygame.draw.line(s, pants, (cx + side, by - 12), (fx, by - 3), 4)
                pygame.draw.ellipse(s, boot, (fx - 3, by - 4, 8, 4))

        # túnica
        pygame.draw.polygon(s, tunic, [(cx - 7, by - 25), (cx + 7, by - 25), (cx + 9, by - 10), (cx - 9, by - 10)])
        pygame.draw.polygon(s, tunic_dark, [(cx - 9, by - 13), (cx + 9, by - 13), (cx + 9, by - 10), (cx - 9, by - 10)])
        pygame.draw.line(s, (230, 190, 80), (cx - 8, by - 17), (cx + 8, by - 17), 2)

        # cajado
        attacking = self.attack_timer > 0
        if attacking:
            prog = 1 - self.attack_timer / self.ATTACK_FRAMES
            ang = -1.2 + prog * 2.4
            hx, hy = cx + 6, by - 19
            ex, ey = hx + math.cos(ang) * 20, hy + math.sin(ang) * 20
            pygame.draw.line(s, (140, 90, 40), (hx - math.cos(ang) * 6, hy - math.sin(ang) * 6), (ex, ey), 3)
            pygame.draw.circle(s, (150, 240, 255), (int(ex), int(ey)), 4)
            pygame.draw.circle(s, skin, (hx, hy), 3)
        else:
            pygame.draw.line(s, (140, 90, 40), (cx + 9, by - 6), (cx + 9, by - 38), 3)
            pygame.draw.circle(s, (150, 240, 255), (cx + 9, by - 40), 4)
            pygame.draw.circle(s, (255, 255, 255), (cx + 8, by - 41), 1)
            pygame.draw.circle(s, skin, (cx + 8, by - 19), 3)

        # cabeça
        hy = by - 32
        pygame.draw.circle(s, hair, (cx - 2, hy - 1), 9)
        pygame.draw.circle(s, skin, (cx + 1, hy + 1), 7)
        pygame.draw.polygon(s, hair, [(cx - 9, hy - 2), (cx + 7, hy - 6), (cx + 2, hy - 9), (cx - 8, hy - 8)])
        pygame.draw.ellipse(s, hair, (cx - 13, hy - 1, 7, 12))  # rabo de cavalo
        eye_y = hy if not self.dying else hy + 1
        pygame.draw.line(s, (30, 30, 50), (cx + 4, eye_y - 2), (cx + 4, eye_y + 1), 2)
        pygame.draw.circle(s, (250, 150, 140), (cx + 2, hy + 4), 2)
        # chapéu de folha
        leaf = [(cx - 11, hy - 6), (cx + 10, hy - 9), (cx + 2, hy - 18), (cx - 6, hy - 15)]
        pygame.draw.polygon(s, (90, 190, 80), leaf)
        pygame.draw.line(s, (50, 120, 50), (cx - 9, hy - 7), (cx + 3, hy - 16), 2)
        return s

    def draw(self, surf, cam):
        if self.invuln > 0 and not self.dying and (self.invuln // 4) % 2 == 0:
            return
        if len(self.scarf) > 1 and not self.dying:
            pts = [(x - cam.x, y - cam.y) for x, y in self.scarf]
            pygame.draw.lines(surf, (200, 40, 50), False, pts, 5)
            pygame.draw.lines(surf, (240, 90, 90), False, pts[:4], 2)
        super().draw(surf, cam)
        if self.attack_timer > 4:
            prog = 1 - self.attack_timer / self.ATTACK_FRAMES
            cx, cy = self.centerx - cam.x + self.facing * 10, self.centery - cam.y - 2
            r = pygame.Rect(0, 0, 56, 52)
            r.center = (int(cx), int(cy))
            span = 0.4 + prog * 2.4
            if self.facing > 0:
                start, stop = 1.3 - span, 1.3
            else:
                start, stop = math.pi - 1.3, math.pi - 1.3 + span
            pygame.draw.arc(surf, (190, 250, 255), r, start, stop, 4)
            pygame.draw.arc(surf, (255, 255, 255), r.inflate(-10, -10), start, stop, 2)
