"""Telas de resultado: fase concluída, fim de jogo e vitória."""
import math
import random

import pygame

from .scene import Scene
from ..config import WIDTH, HEIGHT, GOLD, WHITE, SOFT_TEXT
from ..ui import Menu, MenuOption
from ..util import draw_text, panel, wrap_text
from ..world import LEVELS, Background


class LevelCompleteScene(Scene):
    def __init__(self, game, level_index):
        super().__init__(game)
        self.level_index = level_index
        self.bg = Background(LEVELS[level_index].theme)

    def update(self, inp):
        super().update(inp)
        if self.tick > 40 and (inp.pressed("confirm") or inp.pressed("attack")):
            from .play import PlayScene
            nxt = self.level_index + 1
            self.game.audio.play("confirmar")
            if nxt < len(LEVELS):
                self.game.transition(PlayScene(self.game, nxt))
            else:
                self.game.transition(VictoryScene(self.game))

    def draw(self, surf):
        self.bg.draw(surf, self.tick, 0, self.tick)
        st = self.game.progress.stats
        panel(surf, (WIDTH // 2 - 260, 110, 520, 320))
        draw_text(surf, "FASE CONCLUÍDA!", (WIDTH // 2, 135), 54, GOLD, "midtop", bold=True)
        draw_text(surf, LEVELS[self.level_index].name, (WIDTH // 2, 190), 32, WHITE, "midtop")
        rows = [f"Nível: {st.level}", f"XP: {st.xp}/{st.xp_to_next()}",
                f"Sementes: {st.coins}", f"Vidas: {st.lives}"]
        for i, r in enumerate(rows):
            draw_text(surf, r, (WIDTH // 2, 240 + i * 34), 30, WHITE, "midtop")
        draw_text(surf, "Progresso salvo.", (WIDTH // 2, 385), 22, SOFT_TEXT, "midtop")
        if self.tick > 40 and (self.tick // 25) % 2 == 0:
            draw_text(surf, "Pressione Enter", (WIDTH // 2, HEIGHT - 70), 28, GOLD, "midtop")


class GameOverScene(Scene):
    def __init__(self, game, level_index):
        super().__init__(game)
        self.level_index = level_index
        self.menu = Menu([MenuOption("Tentar de novo", self._retry),
                          MenuOption("Voltar ao título", self._title)], game.audio)

    def on_enter(self):
        self.game.audio.stop_music()

    def _retry(self):
        from .play import PlayScene
        self.game.progress.stats.lives = 3
        self.game.transition(PlayScene(self.game, self.level_index))

    def _title(self):
        from .title import TitleScene
        self.game.transition(TitleScene(self.game))

    def update(self, inp):
        super().update(inp)
        if self.tick > 30:
            self.menu.update(inp)

    def draw(self, surf):
        surf.fill((20, 8, 14))
        draw_text(surf, "FIM DE JOGO", (WIDTH // 2, 150), 80, (230, 80, 90), "center", bold=True)
        draw_text(surf, "A floresta ainda precisa de você, Brisa...", (WIDTH // 2, 220), 30, SOFT_TEXT, "center")
        draw_text(surf, "(Você mantém nível, XP e itens.)", (WIDTH // 2, 255), 22, SOFT_TEXT, "center")
        self.menu.draw(surf, WIDTH // 2, 320)


class VictoryScene(Scene):
    TEXT = ("Com a Semente Ancestral de volta ao coração da floresta, os ipês explodem em flores "
            "rosas, roxas e amarelas. Os rios voltam a correr e a serra canta outra vez. "
            "Obrigado por jogar!")

    def __init__(self, game):
        super().__init__(game)
        self.bg = Background("campo")
        self.petals = [[random.uniform(0, WIDTH), random.uniform(-HEIGHT, 0), random.uniform(1, 2.5),
                        random.choice([(240, 130, 190), (250, 215, 80), (170, 120, 230)])] for _ in range(120)]

    def on_enter(self):
        self.game.audio.play_music("titulo")

    def update(self, inp):
        super().update(inp)
        for p in self.petals:
            p[1] += p[2]
            p[0] += math.sin(self.tick * 0.02 + p[2] * 3)
            if p[1] > HEIGHT:
                p[1] = -10
        if self.tick > 120 and inp.pressed("confirm"):
            from .title import TitleScene
            self.game.transition(TitleScene(self.game))

    def draw(self, surf):
        self.bg.draw(surf, self.tick * 0.8, 0, self.tick)
        for x, y, _, c in self.petals:
            pygame.draw.ellipse(surf, c, (int(x), int(y), 8, 5))
        st = self.game.progress.stats
        panel(surf, (WIDTH // 2 - 330, 90, 660, 360))
        draw_text(surf, "VITÓRIA!", (WIDTH // 2, 110), 72, GOLD, "midtop", bold=True)
        for i, line in enumerate(wrap_text(self.TEXT, 30, 580)):
            draw_text(surf, line, (WIDTH // 2, 190 + i * 32), 30, WHITE, "midtop")
        draw_text(surf, f"Brisa terminou no nível {st.level} com {st.coins} sementes.",
                  (WIDTH // 2, 390), 26, (150, 255, 170), "midtop")
        if self.tick > 120:
            draw_text(surf, "Enter: voltar ao título", (WIDTH // 2, HEIGHT - 50), 24, SOFT_TEXT, "midtop")
