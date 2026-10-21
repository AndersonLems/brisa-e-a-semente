"""Criaturas: entidades com vida, dano, invencibilidade e sprite procedural."""
import pygame

from .entity import PhysicsEntity


class Creature(PhysicsEntity):
    invuln_time = 30
    damage_color = (255, 255, 255)

    def __init__(self, x, y, w, h, max_hp):
        super().__init__(x, y, w, h)
        self.max_hp = max_hp
        self.hp = max_hp
        self.invuln = 0
        self.flash = 0
        self.facing = 1
        self.knockback = 4.0

    def update(self, level):
        super().update(level)
        if self.invuln > 0:
            self.invuln -= 1
        if self.flash > 0:
            self.flash -= 1

    def take_damage(self, amount, level, source_x=None):
        """Aplica dano; devolve True se o golpe realmente acertou."""
        if self.invuln > 0 or not self.alive or self.hp <= 0:
            return False
        amount = max(1, int(amount))
        self.hp -= amount
        self.invuln = self.invuln_time
        self.flash = 10
        level.particles.text(self.centerx, self.y - 4, str(amount), self.damage_color)
        if source_x is not None and self.knockback:
            direction = 1 if self.centerx >= source_x else -1
            self.vx = direction * self.knockback
            self.vy = min(self.vy, -3)
        if self.hp <= 0:
            self.hp = 0
            self.die(level)
        return True

    def heal(self, amount):
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before

    def die(self, level):
        self.kill()

    # --- desenho ---------------------------------------------------------
    def render(self):
        """Devolve a Surface do sprite virado para a direita. Subclasses implementam."""
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        surf.fill((255, 0, 255))
        return surf

    def draw(self, surf, cam):
        img = self.render()
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        if self.flash > 0 and (self.flash // 2) % 2 == 0:
            img = img.copy()
            img.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
        r = img.get_rect(midbottom=(round(self.centerx - cam.x), round(self.bottom - cam.y)))
        surf.blit(img, r)
