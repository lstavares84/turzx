# MATRIX GREEN PRO | estilo GAMMA (ex 06-A NÚCLEO URÂNIO) | versão 3.2.0 | 02/11/2026 17:40 (-03) | renomeado
# histórico: 3.1.0-alfa 01/11/2026 09:25 criação como 06-A NÚCLEO URÂNIO
# Verde fluorescente de vidro de urânio, favo de 19 hexágonos, brilho suave e malha hexagonal.
# Na tela aparece só o título "GAMMA" (sem subtítulo).
import math
from .base import OK, WARN, CRIT, NA, NEUTRAL
from .reator import render, hexagon


def deco(c, P):
    r = 12
    sx, sy = math.sqrt(3) * r, 1.5 * r
    for j in range(0, 40):
        for i in range(-1, 12):
            cx = i * sx + (sx / 2 if j % 2 else 0)
            cy = j * sy
            c.poly(hexagon(cx, cy, r), outline=(10, 26, 11))


GAMMA = {
    "bg": (3, 10, 4), "accent": (120, 255, 90), "ice": (190, 255, 170), "white": (230, 255, 225),
    "sub": (110, 170, 110), "dim": (35, 75, 35), "amber": (255, 190, 0), "red": (255, 60, 50),
    "cells": {OK: ((10, 48, 12), (120, 255, 90)), WARN: ((60, 44, 0), (255, 190, 0)),
              CRIT: ((72, 4, 4), (255, 60, 50)), NA: ((8, 18, 9), (30, 52, 30)),
              NEUTRAL: ((8, 28, 10), (64, 120, 60))},
    "title": "GAMMA", "subtitle": None, "bloom": (3, 0.75, 120), "deco": deco,
}


def draw_frame(vm_dict):
    return render(vm_dict, GAMMA, "favo19")
