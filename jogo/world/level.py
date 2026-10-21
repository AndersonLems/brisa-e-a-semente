"""Level: carrega o mapa, guarda tiles e entidades e resolve as interações entre eles."""
import pygame

from ..camera import Camera
from ..config import TILE, WIDTH, HEIGHT, GOLD
from ..entities import (
    Player, Enemy, Item, Projectile, NPC, MovingPlatform, WorldObject, ParticleSystem,
    Sauva, Besouro, Lodo, Brasinha, Carcara, Morcego, Espinhoso, Boitata,
    SeedCoin, HeartFruit, ManaFlower, XPCrystal, Checkpoint, Goal, Merchant, NPC_TYPES,
)
from .background import Background
from .themes import THEMES
from .tiles import GroundTile, BrickTile, ChestTile, OneWayTile, SpikeTile, LavaTile
from .tileset import Tileset

TILE_CHARS = {
    "#": GroundTile,
    "=": BrickTile,
    "-": OneWayTile,
    "^": SpikeTile,
    "~": LavaTile,
    "?": lambda cx, cy: ChestTile(cx, cy, SeedCoin),
    "!": lambda cx, cy: ChestTile(cx, cy, HeartFruit),
    "*": lambda cx, cy: ChestTile(cx, cy, ManaFlower),
}

ENTITY_CHARS = {
    "o": SeedCoin, "h": HeartFruit, "m": ManaFlower, "x": XPCrystal,
    "s": Sauva, "e": Besouro, "l": Lodo, "r": Brasinha,
    "b": Carcara, "v": Morcego, "k": Espinhoso, "B": Boitata,
    "C": Checkpoint, "F": Goal, "M": MovingPlatform, "$": Merchant,
}


class Level:
    def __init__(self, data, scene, checkpoint=None):
        self.data = data
        self.scene = scene
        self.game = scene.game
        self.input = self.game.input
        self.progress = self.game.progress
        self.theme = THEMES[data.theme]
        self.tileset = Tileset(self.theme)
        self.background = Background(data.theme)

        self.rows = len(data.rows)
        self.cols = max(len(r) for r in data.rows)
        self.width_px = self.cols * TILE
        self.height_px = self.rows * TILE
        self.floor_y = 14 * TILE

        self.tiles = {}
        self.enemies, self.items, self.projectiles = [], [], []
        self.npcs, self.objects, self.platforms = [], [], []
        self.particles = ParticleSystem()
        self.boss = None
        self.arena_rect = None
        self.arena_locked = False
        self.tick = 0

        self._parse(data)
        for t in self.tiles.values():
            t.link(self)

        self.checkpoint = checkpoint or self.start
        self.player = Player(0, 0, self.progress)
        self.player.x = self.checkpoint[0] - self.player.w / 2
        self.player.y = self.checkpoint[1] - self.player.h
        if checkpoint:
            for o in self.objects:
                if isinstance(o, Checkpoint) and abs(o.centerx - checkpoint[0]) < 2:
                    o.activated = True
        if data.arena:
            c0, c1 = data.arena
            self.arena_rect = pygame.Rect(c0 * TILE, 0, (c1 - c0) * TILE, self.floor_y)

        self.camera = Camera(self.width_px, self.height_px)
        self.camera.follow(self.player, instant=True)

    # ------------------------------------------------------------ carga
    def _parse(self, data):
        npc_specs = iter(data.npcs)
        self.start = (2 * TILE, 14 * TILE)
        for cy, row in enumerate(data.rows):
            for cx, ch in enumerate(row):
                if ch in TILE_CHARS:
                    self.tiles[(cx, cy)] = TILE_CHARS[ch](cx, cy)
                elif ch in ENTITY_CHARS:
                    ent = ENTITY_CHARS[ch].spawn_at_tile(cx, cy)
                    if isinstance(ent, MovingPlatform):
                        ent.color = self.theme["platform"]
                    self.spawn(ent)
                elif ch == "N":
                    spec = next(npc_specs)
                    self.spawn(NPC_TYPES[spec["type"]].spawn_at_tile(cx, cy, spec["name"], spec["lines"]))
                elif ch == "P":
                    self.start = (cx * TILE + TILE / 2, (cy + 1) * TILE)

    def spawn(self, ent):
        if isinstance(ent, Enemy):
            self.enemies.append(ent)
            if isinstance(ent, Boitata):
                self.boss = ent
        elif isinstance(ent, Item):
            self.items.append(ent)
        elif isinstance(ent, Projectile):
            self.projectiles.append(ent)
        elif isinstance(ent, NPC):
            self.npcs.append(ent)
        elif isinstance(ent, MovingPlatform):
            self.platforms.append(ent)
        elif isinstance(ent, WorldObject):
            self.objects.append(ent)
        else:
            raise TypeError(f"Entidade desconhecida: {ent!r}")

    # ------------------------------------------------------------ consultas de tiles
    def tile_at(self, cx, cy):
        return self.tiles.get((cx, cy))

    def is_solid(self, cx, cy):
        if cx < 0 or cx >= self.cols:
            return True
        t = self.tiles.get((cx, cy))
        return t is not None and t.solid

    def is_ground(self, cx, cy):
        t = self.tiles.get((cx, cy))
        return t is not None and (t.solid or t.one_way)

    def tiles_in_rect(self, rect):
        for cy in range(rect.top // TILE, (rect.bottom - 1) // TILE + 1):
            for cx in range(rect.left // TILE, (rect.right - 1) // TILE + 1):
                t = self.tiles.get((cx, cy))
                if t:
                    yield t

    def rect_hits_solid(self, rect):
        return any(t.solid for t in self.tiles_in_rect(rect))

    def remove_tile(self, tile):
        self.tiles.pop((tile.cx, tile.cy), None)
        below = self.tiles.get((tile.cx, tile.cy + 1))
        if below:
            below.link(self)

    def check_hazards(self, ent):
        r = ent.rect
        for t in list(self.tiles_in_rect(r)):
            if t.hazard and t.hazard_rect().colliderect(r):
                t.on_touch(self, ent)
                return

    def hit_enemies_above(self, tile):
        zone = pygame.Rect(tile.rect.x, tile.rect.y - 6, TILE, 8)
        for e in self.enemies:
            if e.alive and e.hit_rect().colliderect(zone):
                e.vy = -6
                e.receive_attack(self.player.attack_damage + 2, self, tile.rect.centerx)

    # ------------------------------------------------------------ RPG / eventos
    def sfx(self, name):
        self.game.audio.play(name)

    def add_coins(self, n):
        self.progress.stats.coins += n

    def gain_xp(self, amount, x, y):
        self.particles.text(x, y - 14, f"+{amount} XP", (200, 160, 255), 22)
        for new_level in self.progress.stats.gain_xp(amount):
            self.player.on_level_up()
            self.sfx("nivel")
            self.particles.burst(self.player.centerx, self.player.centery, GOLD, 30, 5, 50, 5, 0, spark=True)
            unlocked = self.progress.stats.ABILITIES.get(new_level)
            msg = f"NÍVEL {new_level}!" + (f"  Novo poder: {unlocked}" if unlocked else "")
            self.scene.notify(msg, GOLD, 220)

    def on_player_dead(self):
        self.scene.player_died()

    def on_boss_defeated(self):
        self.arena_locked = False
        self.camera.unlock()
        self.scene.notify("O Boitatá foi derrotado!", GOLD, 200)

    # ------------------------------------------------------------ atualização
    def update(self):
        self.tick += 1
        for t in self.tiles.values():
            if t.bump:
                t.update()
        for p in self.platforms:
            p.update(self)

        self.player.update(self)
        self._update_arena()
        self._update_enemies()
        for group in (self.items, self.projectiles, self.npcs, self.objects):
            for e in list(group):
                e.update(self)
        self.particles.update()

        if not self.player.dying:
            self._interactions()
            self._collisions()

        self.enemies = [e for e in self.enemies if e.alive]
        self.items = [e for e in self.items if e.alive]
        self.projectiles = [e for e in self.projectiles if e.alive]
        self.camera.follow(self.player)

    def _update_enemies(self):
        view = pygame.Rect(self.camera.x - 96, self.camera.y - 200, WIDTH + 192, HEIGHT + 400)
        for e in list(self.enemies):
            if not e.active and view.colliderect(e.rect):
                e.active = True
            if e.active or isinstance(e, Boitata):
                e.update(self)

    def _update_arena(self):
        if not self.boss or not self.arena_rect:
            return
        p = self.player
        if not self.boss.awake and self.boss.alive and p.x > self.arena_rect.left + 3 * TILE:
            self.arena_locked = True
            self.camera.lock(pygame.Rect(self.arena_rect.x, 0, self.arena_rect.width, self.height_px))
            self.boss.wake(self, self.arena_rect)
        if self.arena_locked:
            p.x = max(self.arena_rect.left, min(p.x, self.arena_rect.right - p.w))

    def _interactions(self):
        if self.input.pressed("up") and self.player.on_ground:
            for npc in self.npcs:
                if npc.near:
                    npc.interact(self)
                    break

    def _collisions(self):
        p = self.player
        pr = p.rect

        for it in self.items:
            if it.alive and it.collectible and pr.colliderect(it.rect):
                it.collect(p, self)

        for o in self.objects:
            if pr.colliderect(o.rect):
                o.on_player_touch(p, self)

        hitbox = p.attack_hitbox()
        if hitbox:
            for t in list(self.tiles_in_rect(hitbox)):
                if isinstance(t, BrickTile) or (isinstance(t, ChestTile) and not t.used):
                    t.on_attack(self)

        for e in self.enemies:
            if not e.alive or not e.active:
                continue
            if hitbox and id(e) not in p.attack_hits and hitbox.colliderect(e.hit_rect()):
                p.attack_hits.add(id(e))
                e.receive_attack(p.attack_damage, self, p.centerx)
            sr = e.stomp_rect()
            if sr and p.vy > 0 and p.prev_bottom <= sr.top + 10 and pr.colliderect(sr):
                e.on_stomp(p, self)
                p.bounce(self)
                continue
            for r in e.body_rects():
                if pr.colliderect(r):
                    p.take_damage(e.contact_damage, self, r.centerx)
                    break

        for pj in self.projectiles:
            if not pj.alive:
                continue
            if pj.team == "player":
                for e in self.enemies:
                    if e.alive and e.active and pj.rect.colliderect(e.hit_rect()):
                        e.receive_attack(pj.damage, self, pj.centerx)
                        pj.impact(self)
                        break
            elif pr.colliderect(pj.rect):
                p.take_damage(pj.damage, self, pj.centerx)
                pj.impact(self)

    # ------------------------------------------------------------ desenho
    def draw(self, surf):
        cam = self.camera
        self.background.draw(surf, cam.x, cam.y, self.tick)
        c0, c1 = cam.x // TILE, (cam.x + WIDTH) // TILE + 1
        r0, r1 = max(0, cam.y // TILE), (cam.y + HEIGHT) // TILE + 1
        for cy in range(r0, r1 + 1):
            for cx in range(c0, c1 + 1):
                t = self.tiles.get((cx, cy))
                if t:
                    t.draw(surf, cam, self.tileset, self.tick)
        for group in (self.objects, self.platforms, self.npcs, self.items, self.enemies):
            for e in group:
                e.draw(surf, cam)
        self.player.draw(surf, cam)
        for pj in self.projectiles:
            pj.draw(surf, cam)
        self.particles.draw(surf, cam)
