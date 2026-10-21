"""Classe-base das cenas (telas) do jogo."""
import pygame

from ..config import WIDTH, HEIGHT


class Scene:
    overlay = False  # se True, a cena de baixo continua sendo desenhada

    def __init__(self, game):
        self.game = game
        self.tick = 0

    def on_enter(self):
        pass

    def update(self, inp):
        self.tick += 1

    def draw(self, surf):
        pass


class OverlayScene(Scene):
    """Cena desenhada por cima da anterior, com fundo escurecido."""
    overlay = True
    dim_alpha = 150

    def draw(self, surf):
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 10, self.dim_alpha))
        surf.blit(shade, (0, 0))
