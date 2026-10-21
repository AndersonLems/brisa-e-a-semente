"""Classes-base de tudo que existe no mundo do jogo."""
import pygame

from ..config import TILE, GRAVITY, MAX_FALL


class Entity:
    """Algo com posição, tamanho e velocidade. Raiz da hierarquia."""

    def __init__(self, x, y, w, h):
        self.x, self.y = float(x), float(y)
        self.w, self.h = w, h
        self.vx = self.vy = 0.0
        self.alive = True
        self.tick = 0

    @classmethod
    def spawn_at_tile(cls, cx, cy, *args, **kwargs):
        """Cria a entidade apoiada no fundo do tile (cx, cy), centralizada."""
        ent = cls(0, 0, *args, **kwargs)
        ent.x = cx * TILE + (TILE - ent.w) / 2
        ent.y = (cy + 1) * TILE - ent.h
        ent.on_spawn()
        return ent

    def on_spawn(self):
        """Gancho chamado depois do posicionamento inicial."""

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.w, self.h)

    @property
    def centerx(self):
        return self.x + self.w / 2

    @property
    def centery(self):
        return self.y + self.h / 2

    @property
    def bottom(self):
        return self.y + self.h

    def update(self, level):
        self.tick += 1

    def draw(self, surf, cam):
        pass

    def kill(self):
        self.alive = False


class PhysicsEntity(Entity):
    """Entidade com gravidade e colisão contra tiles e plataformas móveis."""

    gravity_scale = 1.0

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.on_ground = False
        self.prev_bottom = self.bottom
        self.riding = None
        self.drop_through = 0

    def apply_gravity(self):
        self.vy = min(self.vy + GRAVITY * self.gravity_scale, MAX_FALL)

    def move_and_collide(self, level):
        self.prev_bottom = self.bottom
        self._move_x(level)
        self._move_y(level)

    # --- eixo X -----------------------------------------------------------
    def _rows(self):
        return range(int(self.y // TILE), int((self.y + self.h - 0.01) // TILE) + 1)

    def _cols(self):
        return range(int(self.x // TILE), int((self.x + self.w - 0.01) // TILE) + 1)

    def _move_x(self, level):
        self.x += self.vx
        if self.vx > 0:
            col = int((self.x + self.w - 0.01) // TILE)
            if any(level.is_solid(col, r) for r in self._rows()):
                self.x = col * TILE - self.w
                self.on_wall(level, 1)
        elif self.vx < 0:
            col = int(self.x // TILE)
            if any(level.is_solid(col, r) for r in self._rows()):
                self.x = (col + 1) * TILE
                self.on_wall(level, -1)

    # --- eixo Y -----------------------------------------------------------
    def _move_y(self, level):
        self.on_ground = False
        self.riding = None
        self.y += self.vy
        if self.vy > 0:
            row = int((self.y + self.h - 0.01) // TILE)
            top = row * TILE
            for c in self._cols():
                t = level.tile_at(c, row)
                if t is None:
                    continue
                if t.solid or (t.one_way and self.drop_through <= 0 and self.prev_bottom <= top + 0.5):
                    self.y = top - self.h
                    self.vy = 0
                    self.on_ground = True
                    self.on_land(level)
                    break
        elif self.vy < 0:
            row = int(self.y // TILE)
            hits = [level.tile_at(c, row) for c in self._cols() if level.is_solid(c, row)]
            if hits:
                self.y = (row + 1) * TILE
                self.vy = 0
                # o tile mais próximo do centro recebe a "cabeçada"
                best = min(hits, key=lambda t: abs(t.rect.centerx - self.centerx))
                self.on_ceiling(level, best)

        if self.vy >= 0 and not self.on_ground and self.drop_through <= 0:
            for p in level.platforms:
                if (self.x + self.w > p.x and self.x < p.x + p.w
                        and self.prev_bottom <= p.y + 2 and self.bottom >= p.y):
                    self.y = p.y - self.h
                    self.vy = 0
                    self.on_ground = True
                    self.riding = p
                    self.on_land(level)
                    break

    def standing_on_one_way(self, level):
        row = int((self.bottom + 1) // TILE)
        tiles = [level.tile_at(c, row) for c in self._cols()]
        return any(t and t.one_way for t in tiles) and not any(t and t.solid for t in tiles)

    # --- ganchos para subclasses -----------------------------------------
    def on_wall(self, level, direction):
        self.vx = 0

    def on_land(self, level):
        pass

    def on_ceiling(self, level, tile):
        pass
