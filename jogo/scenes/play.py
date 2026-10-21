"""Cena principal de jogo: roda a fase, HUD, diálogos e avisos."""
from .scene import Scene
from ..config import WIDTH, HEIGHT, GOLD, WHITE
from ..ui import HUD, DialogueBox
from ..util import draw_text
from ..world import Level, LEVELS


class PlayScene(Scene):
    def __init__(self, game, level_index):
        super().__init__(game)
        self.level_index = level_index
        self.data = LEVELS[level_index]
        self.level = Level(self.data, self)
        self.hud = HUD()
        self.dialogue = None
        self.notices = []
        self.banner = 200
        self.finished = False

    @property
    def progress(self):
        return self.game.progress

    def on_enter(self):
        self.game.audio.play_music(self.data.music)

    # ------------------------------------------------------------ chamadas vindas do Level
    def open_dialogue(self, speaker, lines, on_close=None):
        self.dialogue = DialogueBox(speaker, lines, on_close, self.game.audio)

    def open_shop(self):
        from .menus import ShopScene
        self.game.push(ShopScene(self.game, self.level.player))

    def notify(self, text, color=GOLD, frames=150):
        if not any(n[0] == text for n in self.notices):
            self.notices.append([text, frames, color])

    def level_complete(self):
        if self.finished:
            return
        self.finished = True
        self.game.audio.stop_music()
        self.game.audio.play("vitoria")
        self.progress.level_index = self.level_index + 1
        self.progress.save()
        from .results import LevelCompleteScene
        self.game.transition(LevelCompleteScene(self.game, self.level_index), frames=40)

    def player_died(self):
        st = self.progress.stats
        st.lives -= 1
        if st.lives <= 0:
            from .results import GameOverScene
            self.game.transition(GameOverScene(self.game, self.level_index))
        else:
            self.level = Level(self.data, self, checkpoint=self.level.checkpoint)
            self.notices.clear()
            self.banner = 120
            self.game.audio.play_music(self.data.music)

    # ------------------------------------------------------------ ciclo
    def update(self, inp):
        super().update(inp)
        if self.dialogue:
            self.dialogue.update(inp)
            if self.dialogue.done:
                callback = self.dialogue.on_close
                self.dialogue = None
                if callback:
                    callback()
            return
        if inp.pressed("pause") and not self.finished:
            from .menus import PauseScene
            self.game.push(PauseScene(self.game, self))
            return
        self.level.update()
        if self.banner > 0:
            self.banner -= 1
        for n in self.notices:
            n[1] -= 1
        self.notices = [n for n in self.notices if n[1] > 0]

    def draw(self, surf):
        self.level.draw(surf)
        self.hud.draw(surf, self.level)
        for i, (text, frames, color) in enumerate(self.notices[-3:]):
            alpha = min(255, frames * 6)
            draw_text(surf, text, (WIDTH // 2, 130 + i * 36), 34, color, "center", bold=True, alpha=alpha)
        if self.banner > 0:
            alpha = min(255, self.banner * 4)
            draw_text(surf, self.data.subtitle, (WIDTH // 2, HEIGHT // 2 - 60), 30, WHITE, "center", alpha=alpha)
            draw_text(surf, self.data.name, (WIDTH // 2, HEIGHT // 2 - 20), 64, GOLD, "center", bold=True, alpha=alpha)
            lives = self.progress.stats.lives
            draw_text(surf, f"Vidas: {lives}", (WIDTH // 2, HEIGHT // 2 + 25), 28, WHITE, "center", alpha=alpha)
        if self.dialogue:
            self.dialogue.draw(surf)
