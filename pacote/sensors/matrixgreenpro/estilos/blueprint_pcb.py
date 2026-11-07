# MATRIX GREEN PRO | estilo 13-C PLACA DE CIRCUITO | versão 3.1.0-alfa | 01/11/2026 09:40 (-03) | criação
# Variante da família 13: placa de circuito impresso com máscara verde, trilhas de
# cobre e vias ao fundo, ilhas douradas nas seções, serigrafia branca e barras como
# trilhas de cobre que se preenchem.
from .base import W, H
from .blueprint import render

TRACE = (18, 86, 46)


def deco(c, P):
    for x0 in (60, 120, 200, 260):                    # trilhas ao fundo, com dobras de 45°
        pts = [(x0, 0), (x0, 120), (x0 + 20, 140), (x0 + 20, 300), (x0 - 10, 330), (x0 - 10, H)]
        c.line(pts, TRACE, 3)
    for (x, y) in ((60, 120), (140, 300), (280, 140), (190, 330), (250, 330), (110, 330)):
        c.d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(20, 96, 52), outline=(150, 120, 60))
        c.d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(6, 40, 20))


PCB = {
    "bg": (8, 58, 30), "fine": (20, 90, 46), "bold": (24, 100, 52), "line": (225, 235, 220),
    "ink": (245, 248, 242), "tag": (255, 255, 255), "sub": (170, 212, 170), "ok": (150, 255, 120),
    "warn": (255, 214, 60), "crit": (255, 90, 70), "bar": (205, 150, 70), "title": "PCB MGP",
    "subtitle": "REV A · 4 CAMADAS", "dwg": "U1", "scale": "REV A", "grid": "none",
    "section": "pcb", "barmode": "trace", "deco": deco, "hdr_bg": (6, 46, 24),
}


def draw_frame(vm_dict):
    return render(vm_dict, PCB)
