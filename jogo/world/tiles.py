"""Tipos de bloco do cenário. Todos herdam de Tile."""
import math

import pygame

from ..config import TILE


class Tile:
    solid = True
    one_way = False
    hazard = False

    def __init__(self, cx, cy):
        self.cx, self.cy = cx, cy
        self.rect = pygame.Rect(cx * TILE, cy * TILE, TILE, TILE)
        self.bump = 0

    def link(self, level):
        """Chamado depois que o mapa inteiro foi carregado (para olhar vizinhos)."""

    def update(self):
        if self.bump > 0:
            self.bump -= 1

    def sprite_key(self, tick):
        return "ground"

    def on_bump(self, level, entity):
        """Cabeçada vinda de baixo."""

    def on_attack(self, level):
        """Golpe do cajado."""

    def draw(self, surf, cam, tileset, tick):
        off = -int(math.sin(self.bump / 10 * math.pi) * 8) if self.bump else 0
        surf.blit(tileset.get(self.sprite_key(tick)), (self.rect.x - cam.x, self.rect.y - cam.y + off))


class GroundTile(Tile):
    def link(self, level):
        above = level.tile_at(self.cx, self.cy - 1)
        self.top = above is None or not above.solid

    def sprite_key(self, tick):
        return "ground_top" if self.top else "ground"


class BumpableTile(Tile):
    """Bloco que reage a cabeçadas e golpes, atingindo inimigos em cima dele."""

    def on_bump(self, level, entity):
        self.bump = 10
        level.hit_enemies_above(self)
        self.activate(level)

    def on_attack(self, level):
        self.bump = 10
        self.activate(level)

    def activate(self, level):
        raise NotImplementedError


class BrickTile(BumpableTile):
    """Pedra rachada: quebra com cabeçada ou golpe."""

    def sprite_key(self, tick):
        return "brick"

    def activate(self, level):
        level.remove_tile(self)
        level.sfx("quebrar")
        level.particles.burst(self.rect.centerx, self.rect.centery,
                              level.theme["brick"], 14, 4.5, 40, 6, 0.35)


class ChestTile(BumpableTile):
    """Baú-bloco que libera um item uma única vez."""

    def __init__(self, cx, cy, content_cls):
        super().__init__(cx, cy)
        self.content_cls = content_cls
        self.used = False

    def sprite_key(self, tick):
        return "chest_used" if self.used else "chest"

    def activate(self, level):
        if self.used:
            level.sfx("bump")
            return
        self.used = True
        item = self.content_cls.spawn_at_tile(self.cx, self.cy - 1)
        item.pop_out()
        level.spawn(item)
        level.sfx("bau")


class OneWayTile(Tile):
    """Plataforma que dá para atravessar por baixo (e descer com ↓ + pulo)."""
    solid = False
    one_way = True

    def sprite_key(self, tick):
        return "platform"


class HazardTile(Tile):
    """Bloco que machuca ao toque."""
    solid = False
    hazard = True
    damage = 4

    def hazard_rect(self):
        return self.rect

    def on_touch(self, level, entity):
        entity.take_damage(self.damage, level, self.rect.centerx)


class SpikeTile(HazardTile):
    damage = 4

    def hazard_rect(self):
        return pygame.Rect(self.rect.x + 3, self.rect.bottom - 14, TILE - 6, 14)

    def sprite_key(self, tick):
        return "spike"

    def on_touch(self, level, entity):
        if entity.take_damage(self.damage, level):
            entity.vy = -7


class LavaTile(HazardTile):
    """Lava: queima e arremessa para cima (dá para escapar!)."""
    damage = 6

    def link(self, level):
        above = level.tile_at(self.cx, self.cy - 1)
        self.surface = not isinstance(above, LavaTile)

    def hazard_rect(self):
        return self.rect.inflate(0, -12).move(0, 6)

    def sprite_key(self, tick):
        frame = (tick // 6 + self.cx) % 8
        return f"liquid_top{frame}" if self.surface else f"liquid{frame}"

    def on_touch(self, level, entity):
        entity.take_damage(self.damage, level)
        if not getattr(entity, "dying", False):
            entity.vy = -13.5
            level.sfx("lava")
            level.particles.burst(entity.centerx, entity.bottom, (255, 160, 40), 12, 4, 30, 5, spark=True)
