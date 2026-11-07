# MATRIX GREEN PRO | estilo PLANTA TÉCNICA (família 13) | versão 3.1.0-alfa | 01/11/2026 09:35 (-03) | motor com variantes
# histórico: 3.0.0-alfa2 01/11/2026 01:30 criação do estilo 13 original (heliográfico azul)
#
# Motor da família 13 (desenho técnico). Cada variante define paleta, malha,
# moldura das seções, barras e decoração; as métricas usam o esqueleto vertical.
#   13   heliográfico azul, balões de detalhe e hachuras (original)
#   13-A papel vegetal: grafite sobre creme, margem de prancha, caneta vermelha
#   13-B CAD escuro: fundo preto, camadas coloridas, malha de pontos, linha de comando
#   13-C placa de circuito: máscara verde, trilhas de cobre, ilhas douradas, serigrafia
from .base import Canvas, VM, font, JB, W, H, OK, WARN, CRIT, NA, LOST, NEUTRAL, grid, strip_status
from .kit import Style, std_layout

GEN = "generale-mono/GeneraleMonoA.ttf"

HELIO = {
    "bg": (15, 59, 115), "fine": (31, 80, 138), "bold": (52, 102, 160), "line": (190, 214, 245),
    "ink": (240, 246, 255), "sub": (150, 186, 230), "ok": (155, 255, 176), "warn": (255, 224, 102),
    "crit": (255, 107, 107), "bar": (240, 246, 255), "title": "PLANTA TÉCNICA", "subtitle": "MONITOR MGP",
    "dwg": "MGP-001", "scale": "1:1", "grid": "lines", "section": "bubble", "barmode": "hatch", "deco": None,
}


class Drawing(Style):
    def __init__(self, fonts, colors, col, P):
        super().__init__(fonts, colors, col)
        self.P, self.n = P, 0

    def section(self, c, name, y0, y1, label, level):
        P = self.P
        k = self.col(level) if level in (WARN, CRIT, LOST) else P["line"]
        letter = "ABCDEFGHI"[self.n]
        self.n += 1
        if P["section"] == "bubble":
            c.rect((4, y0, 316, y1), outline=P["line"])
            c.d.ellipse((150, y0 - 6, 162, y0 + 6), fill=P["bg"], outline=k)
            c.text(f"{name}.det", 156, y0 + 4, letter, font(GEN, 11), k, anchor="ms")
        elif P["section"] == "cad":                          # cantos de seleção e "grips" azuis
            c.rect((4, y0, 316, y1), outline=P["fine"])
            for x, y in ((4, y0), (316, y0), (4, y1), (316, y1), (160, y0)):
                c.rect((x - 2, y - 2, x + 2, y + 2), fill=(40, 110, 255) if level not in (WARN, CRIT) else k)
        elif P["section"] == "pcb":                          # contorno serigrafado + ilhas
            c.rrect((4, y0, 316, y1), 4, outline=P["line"])
            for x in (4, 316):
                c.d.ellipse((x - 4, y0 + 6, x + 4, y0 + 14), fill=(196, 158, 70), outline=(120, 90, 40))
                c.d.ellipse((x - 1, y0 + 9, x + 1, y0 + 11), fill=P["bg"])
            c.d.ellipse((152, y0 - 4, 160, y0 + 4), fill=k if level in (WARN, CRIT) else (40, 220, 90))

    def bar(self, c, x, y, w, h, pct, color):
        P = self.P
        mode = P["barmode"]
        if mode == "hatch":
            c.rect((x, y, x + w - 1, y + h - 1), outline=P["fine"])
            if pct is None:
                return
            fw = round((w - 1) * max(0, min(100, pct)) / 100)
            for xx in range(x, x + fw, 3):
                c.line((xx, y + h - 1, min(xx + h - 1, x + fw), y), color)
            c.line((x + fw, y - 2, x + fw, y + h + 1), color)
        elif mode == "cad":                                  # linha de cota com setas
            my = y + h // 2
            c.line((x, my, x + w - 1, my), P["fine"])
            c.line((x, y - 1, x, y + h), P["sub"])
            c.line((x + w - 1, y - 1, x + w - 1, y + h), P["sub"])
            if pct is not None:
                fw = round((w - 1) * max(0, min(100, pct)) / 100)
                c.line((x, my, x + fw, my), color, 2)
                c.poly([(x + fw, my), (x + fw - 5, my - 3), (x + fw - 5, my + 3)], fill=color)
        else:                                               # trilha de cobre
            c.rrect((x, y, x + w - 1, y + h - 1), 2, fill=(14, 72, 36))
            if pct is not None:
                fw = round((w - 1) * max(0, min(100, pct)) / 100)
                if fw > 1:
                    c.rrect((x, y, x + fw, y + h - 1), 2, fill=color)


def render(vm_dict, P):
    v = VM(vm_dict)
    c = Canvas(P["bg"])
    if P["grid"] == "lines":
        grid(c, 8, P["fine"]); grid(c, 40, P["bold"])
    elif P["grid"] == "dots":
        for yy in range(0, H, 10):
            for xx in range(0, W, 10):
                c.d.point((xx, yy), fill=P["bold"])
    if P.get("deco"):
        P["deco"](c, P)
    LV = {OK: P["ok"], WARN: P["warn"], CRIT: P["crit"], NA: P["sub"], LOST: P["warn"], NEUTRAL: P["ink"]}
    col = lambda lv: LV.get(lv, P["ink"])
    f_gen = font(GEN, 12)
    S = Drawing({"xl": font(JB, 22, "Bold"), "m": font(JB, 15, "Bold"), "sb": font(JB, 12, "Bold"),
                 "s": font(JB, 12, "Regular"), "xs": font(JB, 11, "Regular"), "tag": f_gen},
                {"tag": P.get("tag", P["ink"]), "sub": P["sub"], "val": P["ink"], "dim": P["sub"],
                 "track": P["fine"], "bar": P["bar"]}, col, P)
    S.Y = dict(S.Y)
    S.Y["pwr"] = (444, 478)

    # ---------- cabeçalho com carimbo do desenho
    c.rect((0, 0, W - 1, 28), fill=P.get("hdr_bg", P["bg"]))
    tb = c.text("hdr.title", 6, 13, P["title"], f_gen, P.get("tag", P["ink"]))
    c.text("hdr.sub", 6, 26, P["subtitle"], font(JB, 11, "Regular"), P["sub"])
    if v.raw("demo"):
        c.text("hdr.demo", tb[2] + 6, 13, "DEMO", font(JB, 11, "Regular"), P["warn"])
    c.rect((236, 2, 316, 15), outline=P["line"])
    c.line((290, 2, 290, 15), P["line"])
    c.text("hdr.dwg", 240, 12, P["dwg"], font(JB, 11, "Regular"), P["sub"])
    c.text("hdr.scale", 313, 12, P["scale"], font(JB, 11, "Regular"), P["sub"], anchor="rs")
    st, slv = v("hdr_status")
    c.text("hdr.status", 314, 27, strip_status(st), font(JB, 12, "Bold"), col(slv), anchor="rs")
    c.line((0, 30, W, 30), P["line"])

    std_layout(c, v, S)
    if P.get("post"):
        P["post"](c, P, v)
    return c, v


def draw_frame(vm_dict):
    return render(vm_dict, HELIO)
