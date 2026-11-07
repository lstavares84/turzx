# MATRIX GREEN PRO | estilo GAMMA ULTRAVIOLETA (variante) | versão 3.2.0 | 02/11/2026 17:40 (-03) | criação original
# Variante do GAMMA: violeta de luz negra, 12 células em anel ao redor do núcleo e raios
# irradiando do centro, como uma explosão de raios gama. Fundo em degradê roxo-escuro.
import math
from .base import OK, WARN, CRIT, NA, NEUTRAL, vgradient, W, H
from .reator import render


def deco(c, P):
    vgradient(c, (0, 0, W - 1, H - 1), (10, 4, 22), (4, 2, 9))
    cx, cy = 160, 120
    for a in range(0, 360, 10):
        t = math.radians(a)
        c.line((cx + 50 * math.cos(t), cy + 50 * math.sin(t), cx + 97 * math.cos(t), cy + 97 * math.sin(t)),
               (34, 20, 62) if a % 30 else (52, 30, 92))


UV = {
    "bg": (7, 3, 14), "accent": (160, 110, 255), "ice": (214, 190, 255), "white": (244, 238, 255),
    "sub": (140, 120, 180), "dim": (52, 34, 88), "amber": (255, 190, 0), "red": (255, 60, 50),
    "cells": {OK: ((30, 14, 66), (160, 110, 255)), WARN: ((62, 44, 0), (255, 190, 0)),
              CRIT: ((76, 4, 10), (255, 60, 50)), NA: ((14, 8, 28), (46, 30, 78)),
              NEUTRAL: ((22, 12, 46), (100, 76, 160))},
    "title": "GAMMA", "subtitle": None, "bloom": (4, 0.8, 115), "deco": deco,
}


def draw_frame(vm_dict):
    return render(vm_dict, UV, "anel")
