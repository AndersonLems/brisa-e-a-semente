"""Classe Game: janela, loop principal, pilha de cenas e transições."""
import pygame

from .audio import Audio
from .config import WIDTH, HEIGHT, FPS, TITLE
from .input import Input
from .rpg import Progress


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        flags = pygame.SCALED | pygame.RESIZABLE
        try:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags, vsync=1)
        except pygame.error:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        self.clock = pygame.time.Clock()
        self.input = Input()
        self.audio = Audio()
        self.progress = Progress()
        self.scenes = []
        self.running = True
        self._fade = 0          # opacidade atual do fade (0..255)
        self._fade_dir = 0      # +1 escurecendo, -1 clareando
        self._fade_speed = 17
        self._pending = None

        from .scenes import TitleScene
        self.push(TitleScene(self))

    # ------------------------------------------------------------ pilha de cenas
    @property
    def top(self):
        return self.scenes[-1]

    def push(self, scene):
        self.scenes.append(scene)
        scene.on_enter()

    def pop(self):
        if len(self.scenes) > 1:
            self.scenes.pop()

    def replace(self, scene):
        self.scenes = [scene]
        scene.on_enter()

    def transition(self, scene, frames=15):
        """Escurece a tela, troca de cena e clareia."""
        if self._pending is None:
            self._pending = scene
            self._fade_dir = 1
            self._fade_speed = max(1, 255 // frames)

    def quit(self):
        self.running = False

    # ------------------------------------------------------------ loop
    def step(self, events):
        """Avança um quadro (separado de run() para facilitar testes automáticos)."""
        for ev in events:
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
        self.input.process(events)

        if self._fade_dir == 1:
            self._fade = min(255, self._fade + self._fade_speed)
            if self._fade >= 255:
                self.replace(self._pending)
                self._pending = None
                self._fade_dir = -1
        else:
            if self._fade_dir == -1:
                self._fade = max(0, self._fade - self._fade_speed)
                if self._fade == 0:
                    self._fade_dir = 0
            self.top.update(self.input)

        self._draw()

    def _draw(self):
        first = len(self.scenes) - 1
        while first > 0 and self.scenes[first].overlay:
            first -= 1
        for scene in self.scenes[first:]:
            scene.draw(self.screen)
        if self._fade:
            veil = pygame.Surface((WIDTH, HEIGHT))
            veil.set_alpha(self._fade)
            self.screen.blit(veil, (0, 0))

    def run(self):
        while self.running:
            self.step(pygame.event.get())
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
