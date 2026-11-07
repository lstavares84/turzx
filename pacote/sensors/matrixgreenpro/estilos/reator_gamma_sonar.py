# MATRIX GREEN PRO | estilo GAMMA SONAR (variante) | versão 3.2.0 | 02/11/2026 17:40 (-03) | criação original
# Variante do GAMMA: verde-água de detector, 14 células em losango sobre um radar
# (anéis concêntricos, mira e marcas de graus). Fundo azul-petróleo quase preto.
import math
from .base import OK, WARN, CRIT, NA, NEUTRAL
from .reator import render


def deco(c, P):
    cx, cy = 160, 122
    for R in (24, 48, 72, 94):
        c.d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(8, 40, 40))
    c.line((cx - 98, cy, cx + 98, cy), (8, 40, 40))
    c.line((cx, cy - 94, cx, cy + 94), (8, 40, 40))
    for a in range(0, 360, 10):
        t = math.radians(a)
        r0, r1 = (94, 99) if a % 30 else (94, 103)
        c.line((cx + r0 * math.cos(t), cy + r0 * math.sin(t), cx + r1 * math.cos(t), cy + r1 * math.sin(t)),
               (14, 70, 66))


SONAR = {
    "bg": (1, 9, 11), "accent": (0, 235, 200), "ice": (150, 255, 235), "white": (225, 255, 250),
    "sub": (90, 150, 150), "dim": (20, 72, 70), "amber": (255, 190, 0), "red": (255, 60, 50),
    "cells": {OK: ((0, 44, 42), (0, 235, 200)), WARN: ((60, 44, 0), (255, 190, 0)),
              CRIT: ((72, 4, 4), (255, 60, 50)), NA: ((6, 20, 22), (24, 56, 58)),
              NEUTRAL: ((4, 30, 32), (50, 120, 118))},
    "title": "GAMMA", "subtitle": None, "bloom": (3, 0.8, 115), "deco": deco,
}


def draw_frame(vm_dict):
    return render(vm_dict, SONAR, "losango")
