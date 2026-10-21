"""Configurações globais do jogo."""
import os

TITLE = "Brisa e a Semente Ancestral"
WIDTH, HEIGHT = 960, 540
FPS = 60
TILE = 32

# Física (unidades em pixels por quadro, a 60 FPS)
GRAVITY = 0.55
MAX_FALL = 12.0

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_FILE = os.path.join(os.path.expanduser("~"), ".local", "share", "brisa-jogo", "save.json")

# Cores da interface
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UI_BG = (22, 20, 44)
UI_BORDER = (240, 210, 120)
HP_COLOR = (225, 60, 70)
MP_COLOR = (70, 140, 240)
XP_COLOR = (250, 200, 60)
GOLD = (255, 205, 60)
SOFT_TEXT = (200, 200, 220)
