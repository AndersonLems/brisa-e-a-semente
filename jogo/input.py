"""Mapeamento de teclado/controle para ações do jogo."""
import pygame

KEYMAP = {
    "left": (pygame.K_LEFT, pygame.K_a),
    "right": (pygame.K_RIGHT, pygame.K_d),
    "up": (pygame.K_UP, pygame.K_w),
    "down": (pygame.K_DOWN, pygame.K_s),
    "jump": (pygame.K_z, pygame.K_SPACE, pygame.K_k),
    "attack": (pygame.K_x, pygame.K_j),
    "magic": (pygame.K_c, pygame.K_l),
    "run": (pygame.K_LSHIFT, pygame.K_RSHIFT),
    "potion_hp": (pygame.K_1,),
    "potion_mp": (pygame.K_2,),
    "confirm": (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_z, pygame.K_SPACE),
    "cancel": (pygame.K_ESCAPE, pygame.K_x, pygame.K_BACKSPACE),
    "pause": (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN),
}

# Botões de controle (layout estilo Xbox/SDL)
JOYMAP = {
    0: ("jump", "confirm"),
    1: ("cancel", "magic"),
    2: ("attack",),
    3: ("magic",),
    4: ("potion_hp",),
    5: ("potion_mp",),
    7: ("pause",),
}


class Input:
    """Guarda o estado das ações: segurando, apertou neste quadro, soltou neste quadro."""

    def __init__(self):
        self._keys = set()
        self._joy_actions = set()
        self._axis_actions = set()
        self._pressed = set()
        self._released = set()
        self._joysticks = []
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            self._joysticks.append(pygame.joystick.Joystick(i))

    def process(self, events):
        self._pressed.clear()
        self._released.clear()
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                self._keys.add(ev.key)
                self._pressed.update(a for a, keys in KEYMAP.items() if ev.key in keys)
            elif ev.type == pygame.KEYUP:
                self._keys.discard(ev.key)
                self._released.update(a for a, keys in KEYMAP.items() if ev.key in keys)
            elif ev.type == pygame.JOYBUTTONDOWN:
                acts = JOYMAP.get(ev.button, ())
                self._joy_actions.update(acts)
                self._pressed.update(acts)
            elif ev.type == pygame.JOYBUTTONUP:
                acts = JOYMAP.get(ev.button, ())
                self._joy_actions.difference_update(acts)
                self._released.update(acts)
            elif ev.type in (pygame.JOYHATMOTION, pygame.JOYAXISMOTION):
                self._update_axes(ev)
            elif ev.type == pygame.JOYDEVICEADDED:
                self._joysticks.append(pygame.joystick.Joystick(ev.device_index))
            elif ev.type == pygame.WINDOWFOCUSLOST:
                self._keys.clear()
                self._joy_actions.clear()

    def _update_axes(self, ev):
        before = set(self._axis_actions)
        if ev.type == pygame.JOYHATMOTION:
            hx, hy = ev.value
            vals = {"left": hx < 0, "right": hx > 0, "up": hy > 0, "down": hy < 0}
        elif ev.axis in (0, 1):
            names = ("left", "right") if ev.axis == 0 else ("up", "down")
            vals = {names[0]: ev.value < -0.5, names[1]: ev.value > 0.5}
        else:
            return
        for act, on in vals.items():
            if on:
                self._axis_actions.add(act)
            else:
                self._axis_actions.discard(act)
        self._pressed.update(self._axis_actions - before)
        self._released.update(before - self._axis_actions)

    def held(self, action):
        if action in self._joy_actions or action in self._axis_actions:
            return True
        return any(k in self._keys for k in KEYMAP[action])

    def pressed(self, action):
        return action in self._pressed

    def released(self, action):
        return action in self._released

    def axis_x(self):
        return int(self.held("right")) - int(self.held("left"))
