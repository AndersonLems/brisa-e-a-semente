"""HUD: vida, mana, XP, sementes, vidas, poções e barra do chefe."""
import pygame

from ..config import WIDTH, HEIGHT, HP_COLOR, MP_COLOR, XP_COLOR, GOLD, WHITE, SOFT_TEXT
from ..util import draw_text, panel, bar


class HUD:
    def draw(self, surf, level):
        p = level.player
        st = level.progress.stats
        inv = level.progress.inventory

        panel(surf, (10, 8, 270, 86))
        draw_text(surf, "Brisa", (22, 15), 26, WHITE, bold=True)
        draw_text(surf, f"Nv {st.level}", (90, 16), 24, GOLD)
        draw_text(surf, f"ATQ {st.attack}  DEF {st.defense}", (150, 17), 20, SOFT_TEXT)
        bar(surf, (22, 38, 180, 14), p.hp / max(1, p.max_hp), HP_COLOR)
        draw_text(surf, f"{p.hp}/{p.max_hp}", (210, 37), 20, WHITE)
        bar(surf, (22, 56, 180, 12), p.mp / max(1, st.max_mp), MP_COLOR)
        draw_text(surf, f"{p.mp}/{st.max_mp}", (210, 54), 20, WHITE)
        bar(surf, (22, 74, 180, 8), st.xp / st.xp_to_next(), XP_COLOR)
        draw_text(surf, "XP", (210, 71), 18, XP_COLOR)

        panel(surf, (WIDTH - 230, 8, 220, 62))
        x = WIDTH - 216
        pygame.draw.ellipse(surf, (255, 205, 60), (x, 16, 12, 16))
        draw_text(surf, f"x {st.coins}", (x + 18, 16), 24, GOLD)
        pygame.draw.ellipse(surf, (90, 200, 80), (x + 100, 18, 16, 10))
        draw_text(surf, f"x {st.lives}", (x + 122, 16), 24, (150, 255, 150))
        draw_text(surf, f"[1] Poção x{inv.count('pocao_vida')}   [2] Elixir x{inv.count('elixir_mana')}",
                  (x, 44), 19, SOFT_TEXT)

        draw_text(surf, level.data.name, (WIDTH // 2, 14), 22, WHITE, "midtop")

        boss = level.boss
        if boss and boss.awake and boss.alive:
            w = 420
            r = pygame.Rect((WIDTH - w) // 2, HEIGHT - 40, w, 18)
            draw_text(surf, boss.name.upper(), (r.centerx, r.top - 4), 24, (255, 170, 80), "midbottom", bold=True)
            bar(surf, r, boss.hp / boss.max_hp, (240, 90, 30))
