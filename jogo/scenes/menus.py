"""Telas sobrepostas durante o jogo: pausa/status e loja."""
import pygame

from .scene import OverlayScene
from ..config import WIDTH, HEIGHT, GOLD, WHITE, SOFT_TEXT, HP_COLOR, MP_COLOR, XP_COLOR
from ..rpg import CATALOG, BY_ID
from ..rpg.stats import Stats
from ..ui import Menu, MenuOption
from ..util import draw_text, panel, bar


class PauseScene(OverlayScene):
    """Pausa com ficha de status de RPG."""

    def __init__(self, game, play_scene):
        super().__init__(game)
        self.play = play_scene
        inv = game.progress.inventory
        self.menu = Menu([
            MenuOption("Continuar", game.pop),
            MenuOption(lambda: f"Usar Poção de Vida (x{inv.count('pocao_vida')})",
                       lambda: self._use("pocao_vida")),
            MenuOption(lambda: f"Usar Elixir de Mana (x{inv.count('elixir_mana')})",
                       lambda: self._use("elixir_mana")),
            MenuOption("Voltar ao título", self._to_title),
        ], game.audio, size=30, spacing=38)

    def _use(self, item_id):
        level = self.play.level
        if self.game.progress.inventory.use(item_id, level.player, level):
            self.game.audio.play("cura")
        else:
            self.game.audio.play("erro")

    def _to_title(self):
        from .title import TitleScene
        self.game.audio.stop_music()
        self.game.transition(TitleScene(self.game))

    def update(self, inp):
        super().update(inp)
        if inp.pressed("cancel"):
            self.game.audio.play("menu")
            self.game.pop()
            return
        self.menu.update(inp)

    def draw(self, surf):
        super().draw(surf)
        st = self.game.progress.stats
        p = self.play.level.player
        draw_text(surf, "PAUSA", (WIDTH // 2, 30), 54, GOLD, "midtop", bold=True)

        box = pygame.Rect(60, 100, 400, 380)
        panel(surf, box)
        x, y = box.x + 24, box.y + 18
        draw_text(surf, "Brisa, Guardiã do Vento", (x, y), 30, WHITE, bold=True)
        draw_text(surf, f"Nível {st.level}", (x, y + 36), 28, GOLD)
        bar(surf, (x, y + 70, 240, 14), p.hp / p.max_hp, HP_COLOR)
        draw_text(surf, f"HP {p.hp}/{p.max_hp}", (x + 252, y + 68), 22, WHITE)
        bar(surf, (x, y + 92, 240, 14), p.mp / st.max_mp, MP_COLOR)
        draw_text(surf, f"MP {p.mp}/{st.max_mp}", (x + 252, y + 90), 22, WHITE)
        bar(surf, (x, y + 114, 240, 14), st.xp / st.xp_to_next(), XP_COLOR)
        draw_text(surf, f"XP {st.xp}/{st.xp_to_next()}", (x + 252, y + 112), 22, WHITE)
        draw_text(surf, f"Ataque: {st.attack}    Defesa: {st.defense}", (x, y + 142), 26, WHITE)
        draw_text(surf, f"Sementes: {st.coins}    Vidas: {st.lives}", (x, y + 170), 26, WHITE)
        draw_text(surf, "Poderes:", (x, y + 206), 26, GOLD)
        for i, (lvl, name) in enumerate(sorted(Stats.ABILITIES.items())):
            ok = st.level >= lvl
            color = (150, 255, 170) if ok else (120, 120, 140)
            draw_text(surf, f"[x] {name}" if ok else f"[  ] {name} (Nv {lvl})",
                      (x + 10, y + 234 + i * 26), 24, color)
        equips = [BY_ID[u].name for u in sorted(st.upgrades) if u in BY_ID]
        draw_text(surf, "Equipamentos: " + (", ".join(equips) if equips else "nenhum"),
                  (x, y + 320), 20, SOFT_TEXT)

        panel(surf, (500, 140, 400, 210))
        self.menu.draw(surf, 700, 165)
        draw_text(surf, "Esc: voltar ao jogo", (700, 370), 22, SOFT_TEXT, "midtop")


class ShopScene(OverlayScene):
    """Loja do Seu Tatu."""

    def __init__(self, game, player):
        super().__init__(game)
        self.player = player
        self.index = 0
        self.message = ""
        self.message_t = 0

    def update(self, inp):
        super().update(inp)
        if self.message_t > 0:
            self.message_t -= 1
        n = len(CATALOG) + 1  # última opção = sair
        if inp.pressed("up"):
            self.index = (self.index - 1) % n
            self.game.audio.play("menu")
        elif inp.pressed("down"):
            self.index = (self.index + 1) % n
            self.game.audio.play("menu")
        elif inp.pressed("cancel"):
            self.game.pop()
        elif inp.pressed("confirm"):
            if self.index == len(CATALOG):
                self.game.pop()
                return
            self._buy(CATALOG[self.index])

    def _buy(self, item):
        progress = self.game.progress
        ok, reason = item.can_buy(progress)
        if not ok:
            self._say(reason)
            self.game.audio.play("erro")
            return
        item.buy(progress)
        self.player.max_hp = progress.stats.max_hp
        self.player.hp = min(self.player.max_hp, self.player.hp + getattr(item, "hp", 0))
        self._say(f"{item.name} comprado!")
        self.game.audio.play("moeda")

    def _say(self, text):
        self.message, self.message_t = text, 120

    def draw(self, surf):
        super().draw(surf)
        progress = self.game.progress
        box = pygame.Rect(100, 50, WIDTH - 200, HEIGHT - 100)
        panel(surf, box)
        draw_text(surf, "Barraca do Seu Tatu", (box.centerx, box.y + 14), 40, GOLD, "midtop", bold=True)
        draw_text(surf, f"Sementes: {progress.stats.coins}", (box.right - 24, box.y + 22), 26, GOLD, "topright")
        for i, item in enumerate(CATALOG + [None]):
            y = box.y + 70 + i * 46
            sel = i == self.index
            if sel:
                pygame.draw.rect(surf, (70, 55, 110), (box.x + 16, y - 6, box.width - 32, 44), border_radius=8)
            if item is None:
                draw_text(surf, "Sair da loja", (box.x + 40, y + 4), 28, GOLD if sel else WHITE)
                continue
            can, _ = item.can_buy(progress)
            color = WHITE if can else (140, 140, 160)
            draw_text(surf, item.name, (box.x + 40, y), 28, GOLD if sel else color, bold=sel)
            draw_text(surf, item.description, (box.x + 40, y + 22), 19, SOFT_TEXT)
            draw_text(surf, item.status_label(progress), (box.right - 150, y + 4), 22, (150, 255, 170), "topright")
            draw_text(surf, f"{item.price}", (box.right - 40, y + 4), 28, GOLD, "topright")
        if self.message_t > 0:
            draw_text(surf, self.message, (box.centerx, box.bottom - 34), 26, GOLD, "midtop")
        else:
            draw_text(surf, "Enter: comprar    Esc: sair", (box.centerx, box.bottom - 34), 22, SOFT_TEXT, "midtop")
