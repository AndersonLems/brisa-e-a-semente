"""Tela de título, história de abertura e tela de controles."""
import math

import pygame

from .scene import Scene, OverlayScene
from ..config import WIDTH, HEIGHT, GOLD, WHITE, SOFT_TEXT
from ..rpg import Progress
from ..ui import Menu, MenuOption
from ..util import draw_text, panel, wrap_text
from ..world import Background


class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg = Background("campo")
        options = [MenuOption("Novo Jogo", self.new_game)]
        if Progress.has_save():
            options.insert(0, MenuOption("Continuar", self.continue_game))
        options += [MenuOption("Controles", lambda: game.push(ControlsScene(game))),
                    MenuOption("Sair", game.quit)]
        self.menu = Menu(options, game.audio)

    def on_enter(self):
        self.game.audio.play_music("titulo")

    def new_game(self):
        self.game.progress = Progress()
        self.game.transition(StoryScene(self.game))

    def continue_game(self):
        from .play import PlayScene
        from ..world import LEVELS
        self.game.progress = Progress.load()
        if self.game.progress.level_index >= len(LEVELS):  # jogo zerado: recomeça mantendo o nível
            self.game.progress.level_index = 0
        self.game.transition(PlayScene(self.game, self.game.progress.level_index))

    def update(self, inp):
        super().update(inp)
        self.menu.update(inp)

    def draw(self, surf):
        self.bg.draw(surf, self.tick * 1.2, 0, self.tick)
        y = 110 + int(math.sin(self.tick * 0.03) * 6)
        draw_text(surf, "BRISA", (WIDTH // 2, y), 110, (255, 250, 230), "center", bold=True)
        draw_text(surf, "e a Semente Ancestral", (WIDTH // 2, y + 62), 44, GOLD, "center")
        panel(surf, (WIDTH // 2 - 170, 250, 340, 30 + 44 * len(self.menu.options)))
        self.menu.draw(surf, WIDTH // 2, 268)
        draw_text(surf, "Setas: navegar   Enter/Z: confirmar   F11: tela cheia",
                  (WIDTH // 2, HEIGHT - 26), 22, WHITE, "center")


class StoryScene(Scene):
    PAGES = [
        "Na Serra dos Ipês, as árvores florescem o ano inteiro graças à Semente Ancestral, "
        "guardada no coração da floresta.",
        "Mas numa noite sem lua, o Boitatá, a grande serpente de fogo, despertou no vulcão "
        "e roubou a semente para aquecer seu covil.",
        "Desde então, as flores murcham, os rios secam e as criaturas da serra ficaram agitadas.",
        "Brisa, a jovem Guardiã do Vento, pega seu cajado de cristal e parte em jornada. "
        "É hora de trazer a semente de volta!",
    ]

    def __init__(self, game):
        super().__init__(game)
        self.page = 0
        self.page_tick = 0

    def update(self, inp):
        super().update(inp)
        self.page_tick += 1
        if inp.pressed("confirm") or inp.pressed("attack"):
            self.game.audio.play("menu")
            self.page += 1
            self.page_tick = 0
            if self.page >= len(self.PAGES):
                from .play import PlayScene
                self.game.transition(PlayScene(self.game, 0))
        elif inp.pressed("cancel"):
            from .play import PlayScene
            self.game.transition(PlayScene(self.game, 0))

    def draw(self, surf):
        surf.fill((14, 12, 30))
        for i in range(60):
            x = (i * 131) % WIDTH
            y = (i * 71) % HEIGHT
            a = 120 + int(100 * math.sin(self.tick * 0.05 + i))
            pygame.draw.circle(surf, (a, a, min(255, a + 40)), (x, y), 1)
        page = self.PAGES[min(self.page, len(self.PAGES) - 1)]
        alpha = min(255, self.page_tick * 8)
        for i, line in enumerate(wrap_text(page, 34, 720)):
            draw_text(surf, line, (WIDTH // 2, 200 + i * 40), 34, WHITE, "center", alpha=alpha)
        draw_text(surf, "Enter: continuar    Esc: pular", (WIDTH // 2, HEIGHT - 40), 22, SOFT_TEXT, "center")


class ControlsScene(OverlayScene):
    LINES = [
        ("Setas / A D", "Andar"),
        ("Shift", "Correr"),
        ("Z / Espaço", "Pular (segure para ir mais alto)"),
        ("X", "Golpe de cajado (quebra pedras rachadas)"),
        ("C", "Rajada de Vento (magia, nível 2)"),
        ("Baixo + Pulo", "Descer de plataformas finas"),
        ("Cima", "Conversar / Comprar"),
        ("1 / 2", "Poção de Vida / Elixir de Mana"),
        ("Esc / P", "Pausa e status"),
        ("F11", "Tela cheia"),
    ]

    def update(self, inp):
        super().update(inp)
        if inp.pressed("confirm") or inp.pressed("cancel"):
            self.game.audio.play("menu")
            self.game.pop()

    def draw(self, surf):
        super().draw(surf)
        panel(surf, (WIDTH // 2 - 300, 50, 600, 440))
        draw_text(surf, "CONTROLES", (WIDTH // 2, 70), 40, GOLD, "midtop", bold=True)
        for i, (key, desc) in enumerate(self.LINES):
            y = 125 + i * 34
            draw_text(surf, key, (WIDTH // 2 - 40, y), 28, GOLD, "topright")
            draw_text(surf, desc, (WIDTH // 2 - 20, y), 28, WHITE)
        draw_text(surf, "Controle (gamepad) também funciona.", (WIDTH // 2, 470), 20, SOFT_TEXT, "midtop")
