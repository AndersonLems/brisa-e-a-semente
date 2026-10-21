"""Personagens com quem a Brisa conversa."""
import math

import pygame

from .entity import Entity


class NPC(Entity):
    """NPC base: mostra um balão quando o jogador chega perto e abre um diálogo."""

    def __init__(self, x, y, name="???", lines=(), w=30, h=40):
        super().__init__(x, y, w, h)
        self.name = name
        self.lines = list(lines)
        self.near = False

    def update(self, level):
        super().update(level)
        p = level.player
        self.near = abs(p.centerx - self.centerx) < 44 and abs(p.bottom - self.bottom) < 40

    def interact(self, level):
        level.scene.open_dialogue(self.name, self.lines, lambda: self.after_talk(level))

    def after_talk(self, level):
        """Gancho chamado quando o diálogo termina."""

    def render(self):
        raise NotImplementedError

    def draw(self, surf, cam):
        img = self.render()
        r = img.get_rect(midbottom=(round(self.centerx - cam.x), round(self.bottom - cam.y)))
        surf.blit(img, r)
        if self.near:
            bx, by = r.centerx, r.top - 14 + int(math.sin(self.tick * 0.15) * 3)
            pygame.draw.circle(surf, (255, 255, 255), (bx, by), 11)
            pygame.draw.circle(surf, (40, 40, 60), (bx, by), 11, 2)
            pygame.draw.polygon(surf, (40, 40, 60), [(bx - 5, by + 3), (bx + 5, by + 3), (bx, by - 5)])


class TreeSpirit(NPC):
    """Espírito ancião de uma árvore (Vovó Jacarandá)."""

    def __init__(self, x, y, name, lines):
        super().__init__(x, y, name, lines, 34, 56)

    def render(self):
        s = pygame.Surface((60, 62), pygame.SRCALPHA)
        sway = math.sin(self.tick * 0.04) * 2
        pygame.draw.polygon(s, (110, 75, 45), [(22, 62), (38, 62), (35, 30), (25, 30)])
        pygame.draw.line(s, (80, 55, 35), (28, 60), (29, 34), 2)
        for (x, y, r) in ((30, 18, 15), (17, 24, 11), (43, 24, 11), (22, 10, 10), (39, 11, 10)):
            pygame.draw.circle(s, (150, 100, 200), (int(x + sway), y), r)
        for (x, y) in ((24, 16), (36, 20), (30, 8), (18, 26), (44, 26)):
            pygame.draw.circle(s, (200, 160, 240), (int(x + sway), y), 3)
        pygame.draw.circle(s, (30, 20, 10), (26, 42), 2)
        pygame.draw.circle(s, (30, 20, 10), (34, 42), 2)
        pygame.draw.arc(s, (30, 20, 10), (25, 44, 10, 6), 3.4, 6.0, 2)
        return s


class Capybara(NPC):
    """Dona Capivara, exploradora das cavernas."""

    def __init__(self, x, y, name, lines):
        super().__init__(x, y, name, lines, 40, 30)

    def render(self):
        s = pygame.Surface((48, 40), pygame.SRCALPHA)
        breathe = int(math.sin(self.tick * 0.06) * 1)
        pygame.draw.ellipse(s, (140, 95, 60), (2, 14 - breathe, 38, 24 + breathe))
        pygame.draw.ellipse(s, (150, 105, 65), (26, 10, 20, 20))
        pygame.draw.rect(s, (110, 75, 45), (8, 34, 6, 6))
        pygame.draw.rect(s, (110, 75, 45), (28, 34, 6, 6))
        pygame.draw.circle(s, (30, 20, 10), (38, 17), 2)
        pygame.draw.ellipse(s, (90, 60, 40), (40, 20, 7, 6))
        pygame.draw.ellipse(s, (120, 80, 50), (28, 7, 6, 6))
        pygame.draw.ellipse(s, (200, 170, 100), (24, 2, 22, 7))   # chapéu
        pygame.draw.rect(s, (200, 170, 100), (29, 0, 12, 5))
        pygame.draw.line(s, (120, 60, 40), (29, 4), (41, 4), 2)
        lamp = 150 + int(80 * abs(math.sin(self.tick * 0.05)))
        pygame.draw.circle(s, (255, 230, 120), (35, 1), 2)
        glow = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 230, 120, lamp // 3), (10, 10), 9)
        s.blit(glow, (25, -9))
        return s


class Merchant(NPC):
    """Seu Tatu, o mercador ambulante. Depois da conversa abre a loja."""

    def __init__(self, x, y, name="Seu Tatu", lines=None):
        lines = lines or ["Opa! Sementes douradas são bem-vindas por aqui.",
                          "Dá uma olhada no meu estoque, preço justo pra quem salva a floresta!"]
        super().__init__(x, y, name, lines, 36, 34)
        self.talked = False

    def interact(self, level):
        if self.talked:
            level.scene.open_shop()
        else:
            super().interact(level)

    def after_talk(self, level):
        self.talked = True
        level.scene.open_shop()

    def render(self):
        s = pygame.Surface((50, 42), pygame.SRCALPHA)
        bob = int(math.sin(self.tick * 0.07) * 1)
        pygame.draw.rect(s, (150, 90, 40), (2, 8 + bob, 16, 22), border_radius=4)  # mochila
        pygame.draw.line(s, (100, 60, 20), (4, 14 + bob), (16, 14 + bob), 2)
        pygame.draw.ellipse(s, (170, 150, 130), (8, 12 + bob, 32, 26))
        for x in (14, 20, 26, 32):
            pygame.draw.line(s, (130, 110, 95), (x, 13 + bob), (x, 36 + bob), 2)
        pygame.draw.ellipse(s, (185, 160, 140), (32, 18 + bob, 16, 12))
        pygame.draw.polygon(s, (185, 160, 140), [(34, 20 + bob), (37, 10 + bob), (40, 19 + bob)])
        pygame.draw.circle(s, (20, 20, 20), (42, 22 + bob), 2)
        pygame.draw.circle(s, (120, 70, 70), (48, 25 + bob), 2)
        pygame.draw.rect(s, (110, 90, 75), (14, 36, 6, 6))
        pygame.draw.rect(s, (110, 90, 75), (30, 36, 6, 6))
        return s


NPC_TYPES = {
    "espirito": TreeSpirit,
    "capivara": Capybara,
}
