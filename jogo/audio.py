"""Áudio 100% sintetizado em tempo de execução (nenhum arquivo externo)."""
import math
import random
from array import array

import pygame

NOTE_OFFSETS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_freq(name):
    """'A4' -> 440.0 ; aceita sustenido (#) e bemol (b)."""
    letter, rest = name[0], name[1:]
    semitone = NOTE_OFFSETS[letter]
    if rest.startswith("#"):
        semitone, rest = semitone + 1, rest[1:]
    elif rest.startswith("b"):
        semitone, rest = semitone - 1, rest[1:]
    midi = 12 * (int(rest) + 1) + semitone
    return 440.0 * 2 ** ((midi - 69) / 12)


def wave(kind, phase):
    p = phase % 1.0
    if kind == "square":
        return 1.0 if p < 0.5 else -1.0
    if kind == "pulse":
        return 1.0 if p < 0.25 else -1.0
    if kind == "triangle":
        return 4 * abs(p - 0.5) - 1
    if kind == "noise":
        return random.uniform(-1, 1)
    return math.sin(2 * math.pi * p)


# Músicas: cada token é uma colcheia; "-" é pausa; "nota:n" dura n colcheias.
SONGS = {
    "titulo": dict(bpm=100, lead=(
        "E5:2 G5:2 A5:3 G5 E5:2 D5:2 C5:4 - - "
        "D5:2 E5:2 G5:3 E5 D5:2 C5:2 A4:4 - - "
        "E5:2 G5:2 A5:3 C6 B5:2 A5:2 G5:4 E5:2 "
        "F5:2 E5:2 D5:2 B4:2 C5:6 - -"),
        bass="C3:4 G3:4 A2:4 E3:4 F2:4 C3:4 G2:4 G2:4 C3:4 G3:4 A2:4 E3:4 F2:4 G2:4 C3:8"),
    "campo": dict(bpm=150, lead=(
        "C5 E5 G5 E5 A5 G5 E5 - F5 A5 C6 A5 G5:2 - - "
        "E5 G5 C6 B5 A5 G5 A5 B5 C6:2 G5:2 E5:2 - - "
        "F5 F5 A5 F5 E5 E5 G5 E5 D5 E5 F5 G5 A5:2 G5:2 "
        "C5 E5 G5 E5 A5 G5 E5 D5 C5:4 - - - -"),
        bass=("C3 - G3 - C3 - G3 - F3 - C4 - F3 - C4 - "
              "A2 - E3 - A2 - E3 - G2 - D3 - G2 - B2 - "
              "F2 - C3 - F2 - C3 - G2 - D3 - G2 - D3 - "
              "C3 - G3 - A2 - E3 - C3 - G2 - C3:4")),
    "caverna": dict(bpm=104, lead=(
        "A4:2 - C5:2 - E5:2 D5:2 C5:4 - - B4:4 "
        "A4:2 - C5:2 - E5:2 G5:2 F5:4 - - E5:4 "
        "D5:2 - F5:2 - A5:2 G5:2 F5:2 E5:2 D5:4 "
        "C5:2 B4:2 G#4:4 A4:8"),
        bass=("A2:4 A2:4 F2:4 G2:4 A2:4 A2:4 D2:4 E2:4 "
              "D2:4 D2:4 F2:4 G2:4 A2:4 E2:4 A2:8")),
    "vulcao": dict(bpm=168, lead=(
        "D5 D5 F5 D5 G5 F5 E5 C5 D5 D5 F5 D5 A5 G5 F5 E5 "
        "D5 D5 F5 D5 G5 F5 E5 C5 Bb4 C5 D5 E5 F5:2 E5:2 "
        "A5 A5 G5 F5 G5 G5 F5 E5 F5 F5 E5 D5 E5:2 C5:2 "
        "D5 F5 A5 D6 C6 A5 G5 E5 D5:4 - - - -"),
        bass=("D3 D3 D3 D3 D3 D3 D3 D3 Bb2 Bb2 Bb2 Bb2 C3 C3 C3 C3 "
              "D3 D3 D3 D3 D3 D3 D3 D3 Bb2 Bb2 Bb2 Bb2 A2 A2 A2 A2 "
              "F2 F2 F2 F2 C3 C3 C3 C3 Bb2 Bb2 Bb2 Bb2 A2 A2 A2 A2 "
              "D3 D3 D3 D3 A2 A2 A2 A2 D3 D3 D3 D3 D3 D3 D3 D3")),
}


class Audio:
    """Gera efeitos sonoros e músicas chiptune por síntese."""

    def __init__(self):
        self.ok = False
        self.sounds = {}
        self.music_cache = {}
        self.current_music = None
        self.music_channel = None
        try:
            pygame.mixer.init(22050, -16, 1, 512)
            self.rate, _, self.channels = pygame.mixer.get_init()
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)
            self.music_channel = pygame.mixer.Channel(0)
            self._build_effects()
            self.ok = True
        except (pygame.error, TypeError):
            print("[audio] Sem dispositivo de som; jogando em silêncio.")

    # ----------------------------------------------------------- síntese
    def _to_sound(self, samples, volume=1.0):
        buf = array("h")
        if self.channels == 2:
            for s in samples:
                v = int(max(-1, min(1, s * volume)) * 32000)
                buf.append(v)
                buf.append(v)
        else:
            buf.extend(int(max(-1, min(1, s * volume)) * 32000) for s in samples)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _tone(self, f0, f1, dur, kind="square", vol=0.3, decay=True):
        n = int(self.rate * dur)
        out, phase = [], 0.0
        for i in range(n):
            t = i / n
            phase += (f0 + (f1 - f0) * t) / self.rate
            env = (1 - t) if decay else min(1.0, (1 - t) * 8)
            out.append(wave(kind, phase) * env * vol)
        return out

    def _seq(self, notes, dur, kind="square", vol=0.25):
        out = []
        for f in notes:
            out += self._tone(f, f, dur, kind, vol)
        return out

    def _build_effects(self):
        t, s = self._tone, self._seq
        fx = {
            "pulo": t(320, 640, 0.12, "square", 0.18),
            "pulo_duplo": t(520, 980, 0.14, "triangle", 0.3),
            "moeda": t(988, 988, 0.05, "square", 0.15) + t(1318, 1318, 0.14, "square", 0.15),
            "golpe": [a + b for a, b in zip(t(700, 200, 0.1, "noise", 0.18), t(500, 250, 0.1, "triangle", 0.2))],
            "pisao": t(260, 70, 0.12, "square", 0.25),
            "dano": t(240, 90, 0.28, "pulse", 0.25),
            "quebrar": t(400, 80, 0.22, "noise", 0.3),
            "bau": s([523, 659, 784, 1046], 0.06, "square", 0.16),
            "bump": t(150, 90, 0.08, "triangle", 0.4),
            "magia": [a + b for a, b in zip(t(700, 1700, 0.22, "triangle", 0.25), t(1, 1, 0.22, "noise", 0.08))],
            "nivel": s([523, 659, 784, 1046, 784, 1046, 1318], 0.07, "square", 0.17),
            "checkpoint": s([659, 880, 1174], 0.08, "triangle", 0.35),
            "morte": s([494, 466, 440, 415, 392, 370, 349, 330], 0.07, "pulse", 0.2),
            "menu": t(880, 880, 0.04, "square", 0.12),
            "confirmar": s([660, 990], 0.05, "square", 0.14),
            "erro": t(160, 120, 0.15, "square", 0.18),
            "inimigo": t(500, 90, 0.18, "noise", 0.25),
            "tiro": t(900, 400, 0.1, "pulse", 0.12),
            "fogo": t(200, 60, 0.3, "noise", 0.25),
            "lava": t(120, 60, 0.25, "noise", 0.3),
            "rugido": [a + b for a, b in zip(t(110, 55, 1.0, "noise", 0.35), t(90, 50, 1.0, "square", 0.15))],
            "chefe_dano": t(300, 100, 0.2, "square", 0.25),
            "cura": s([784, 988, 1174], 0.06, "triangle", 0.35),
            "falar": t(600, 600, 0.02, "triangle", 0.15),
            "vitoria": s([523, 523, 523, 659, 784, 659, 784, 1046], 0.11, "square", 0.17),
            "portal": t(300, 1200, 0.5, "triangle", 0.25),
        }
        self.sounds = {name: self._to_sound(data) for name, data in fx.items()}

    def _render_song(self, name):
        spec = SONGS[name]
        eighth = 60 / spec["bpm"] / 2

        def voice(text, kind, vol):
            out = []
            for tok in text.split():
                note, _, length = tok.partition(":")
                n = int(self.rate * eighth * int(length or 1))
                if note == "-":
                    out += [0.0] * n
                    continue
                f, phase = note_freq(note), 0.0
                step = f / self.rate
                for i in range(n):
                    phase += step
                    rel = i / n
                    env = 1.0 if rel < 0.7 else (1 - rel) / 0.3
                    out.append(wave(kind, phase) * vol * env)
            return out

        lead = voice(spec["lead"], "pulse", 0.11)
        bass = voice(spec["bass"], "triangle", 0.22)
        n = max(len(lead), len(bass))
        lead += [0.0] * (n - len(lead))
        bass += [0.0] * (n - len(bass))
        return self._to_sound([a + b for a, b in zip(lead, bass)])

    # ----------------------------------------------------------- API
    def play(self, name):
        if self.ok and name in self.sounds:
            self.sounds[name].play()

    def play_music(self, name):
        if not self.ok or name == self.current_music:
            return
        if name not in self.music_cache:
            self.music_cache[name] = self._render_song(name)
        self.current_music = name
        self.music_channel.stop()
        self.music_channel.set_volume(0.55)
        self.music_channel.play(self.music_cache[name], loops=-1, fade_ms=400)

    def stop_music(self):
        if self.ok:
            self.music_channel.fadeout(300)
        self.current_music = None
