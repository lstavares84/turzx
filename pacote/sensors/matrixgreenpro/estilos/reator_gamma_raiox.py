# MATRIX GREEN PRO | estilo GAMMA RAIO-X (variante) | versão 3.2.0 | 02/11/2026 17:40 (-03) | criação original
# Variante do GAMMA: chapa de raio-X em aço e branco sobre grafite, linhas de varredura de
# monitor, cantoneiras de moldura e células grandes (13). O verde fica só como sinal de saúde.
from .base import OK, WARN, CRIT, NA, NEUTRAL, W, H
from .reator import render


def deco(c, P):
    for y in range(0, H, 3):
        c.line((0, y, W, y), (11, 14, 18))
    k, n = (70, 82, 96), 12
    for x, y, dx, dy in ((2, 2, 1, 1), (W - 3, 2, -1, 1), (2, H - 3, 1, -1), (W - 3, H - 3, -1, -1)):
        c.line((x, y, x + dx * n, y), k)
        c.line((x, y, x, y + dy * n), k)


RAIOX = {
    "bg": (6, 8, 10), "accent": (232, 240, 248), "ice": (150, 255, 180), "white": (244, 248, 252),
    "sub": (122, 134, 148), "dim": (52, 62, 74), "amber": (255, 190, 0), "red": (255, 60, 50),
    "cells": {OK: ((16, 36, 26), (150, 255, 180)), WARN: ((60, 44, 0), (255, 190, 0)),
              CRIT: ((72, 4, 4), (255, 60, 50)), NA: ((12, 15, 19), (40, 48, 58)),
              NEUTRAL: ((20, 25, 32), (120, 132, 146))},
    "title": "GAMMA", "subtitle": None, "bloom": (2, 0.4, 150), "deco": deco,
}


def draw_frame(vm_dict):
    return render(vm_dict, RAIOX, "favo13")
