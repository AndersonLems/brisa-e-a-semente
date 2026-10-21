"""Funções auxiliares de desenho e matemática."""
import pygame

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        _fonts[key] = f
    return _fonts[key]


def draw_text(surf, msg, pos, size=26, color=(255, 255, 255), anchor="topleft",
              shadow=True, bold=False, alpha=255):
    """Desenha texto com sombra opcional e devolve o retângulo ocupado."""
    f = font(size, bold)
    img = f.render(msg, True, color)
    rect = img.get_rect(**{anchor: pos})
    if shadow:
        sh = f.render(msg, True, (0, 0, 0))
        if alpha < 255:
            sh.set_alpha(alpha)
        surf.blit(sh, rect.move(2, 2))
    if alpha < 255:
        img.set_alpha(alpha)
    surf.blit(img, rect)
    return rect


def wrap_text(msg, size, max_width):
    """Quebra um texto em linhas que caibam em max_width pixels."""
    f = font(size)
    lines, current = [], ""
    for word in msg.split():
        test = f"{current} {word}".strip()
        if f.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def approach(value, target, step):
    """Move value em direção a target sem ultrapassá-lo."""
    if value < target:
        return min(value + step, target)
    return max(value - step, target)


def mix(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def vertical_gradient(w, h, top, bottom):
    surf = pygame.Surface((w, h))
    for y in range(h):
        pygame.draw.line(surf, mix(top, bottom, y / max(1, h - 1)), (0, y), (w, y))
    return surf


def panel(surf, rect, color=(22, 20, 44), border=(240, 210, 120), alpha=215, radius=10):
    """Painel semitransparente com borda arredondada."""
    rect = pygame.Rect(rect)
    box = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(box, (*color, alpha), box.get_rect(), border_radius=radius)
    pygame.draw.rect(box, border, box.get_rect(), 2, border_radius=radius)
    surf.blit(box, rect)


def bar(surf, rect, frac, color, back=(40, 30, 50)):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surf, back, rect, border_radius=4)
    inner = rect.inflate(-4, -4)
    inner.width = int(inner.width * clamp(frac, 0, 1))
    if inner.width > 0:
        pygame.draw.rect(surf, color, inner, border_radius=3)
        hi = pygame.Rect(inner.x, inner.y, inner.width, max(1, inner.height // 3))
        pygame.draw.rect(surf, mix(color, (255, 255, 255), 0.4), hi, border_radius=3)
    pygame.draw.rect(surf, (0, 0, 0), rect, 2, border_radius=4)
