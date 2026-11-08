# GAMMA | estilos/graficos.py | versão 2.3.0 | 07/11/2026 20:40 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 2.3.0 07/11/2026 20:40 rótulos girados recortados, centrados e com fonte que cabe na altura
# histórico: 2.2.0 07/11/2026 20:30 rótulos girados 90° (P['rotulos_rot']) e gráficos mais largos
# histórico: 2.1.0 07/11/2026 19:40 pico da VRAM e da RAM em GB
# histórico: 2.0.0 07/11/2026 19:30 base na proposta B, gráfico de temperatura no alto e 3 formas de mostrar o pico
# histórico: 1.0.0 07/11/2026 19:15 propostas A (3 gráficos) e B (2 gráficos)
# Gráficos de linha das últimas 24 h no espaço livre do GAMMA DELTA:
#   no alto, à direita da escala N0/N1/N2: temperatura da CPU (área verde) e da GPU (linha branca);
#   abaixo da escala: VRAM (área verde) com RAM (linha branca), cada linha em % da própria capacidade e o pico
#   em GB usados, e rede com download (área) e upload (linha).
# A linha é a média de cada intervalo; o pico é o maior valor lido nas 24 h (historico.py guarda os máximos).
# Três formas de mostrar o pico (P["pico"]):
#   "legenda"  = o valor do pico fica na legenda, ao lado do nome, na cor da série;
#   "marcador" = um ponto no lugar e na altura do pico, com o valor ao lado;
#   "linha"    = uma linha tracejada na altura do pico, com o valor na ponta.
# Marcas verticais a cada 6 h; a borda direita é agora. Falha na linha = sem dado.
from .alerta import mix
from .base import font, JB, ROBOTO

X0, LARG = 46, 148          # gráficos de baixo: um pixel por intervalo (= historico.N)
XT, LT = 136, 74            # gráfico de temperatura: um pixel a cada dois intervalos
XT_LEG = 96                 # legenda da temperatura (logo depois da escala N0/N1/N2)


def _pares(vals, fn):
    """Junta os intervalos de dois em dois (148 -> 74) para o gráfico estreito."""
    out = []
    for i in range(0, len(vals) - 1, 2):
        p = [x for x in vals[i:i + 2] if x is not None]
        out.append(fn(p) if p else None)
    return out


def _fmt(tipo, x):
    if isinstance(tipo, tuple):                                 # ("gb", capacidade): percentual -> GB usados
        return f"{x * tipo[1] / 100:.1f}GB" if tipo[1] else f"{round(x)}%"
    if tipo == "pct":
        return f"{round(x)}%"
    if tipo == "temp":
        return f"{round(x)}°"
    from ..viewmodel import rate
    return rate(x, short=True)


class Grafico:
    """Um gráfico: fundo, marcas de 6 h, séries e (conforme o modo) o pico de cada série."""

    def __init__(self, c, P, x0, larg, y0, y1, vmin, vmax):
        self.c, self.P = c, P
        self.x0, self.x1, self.y0, self.y1 = x0, x0 + larg - 1, y0, y1
        self.larg, self.vmin, self.vmax = larg, vmin, vmax
        self.fundo = mix(P["accent"], P["bg"], 0.95)
        self.ocupados = []
        c.rect((x0, y0, self.x1, y1), fill=self.fundo)
        for k in range(1, 4):                                   # 6 h, 12 h e 18 h atrás
            x = x0 + round(larg * k / 4)
            for y in range(y0 + 1, y1, 3):
                c.d.point((x, y), fill=P["dim"])
        c.line((x0, y1, self.x1, y1), P["dim"])

    def y(self, val):
        t = (val - self.vmin) / max(1e-9, self.vmax - self.vmin)
        return round(self.y1 - 1 - (self.y1 - self.y0 - 2) * max(0.0, min(1.0, t)))

    def x(self, i, n):
        if n < self.larg and n > 1:                             # gráfico mais largo que a série: estica
            return self.x0 + round(i * (self.larg - 1) / (n - 1))
        return self.x0 + self.larg - n + i

    def serie(self, vals, cor, preencher):
        vals = list(vals)[-self.larg:]
        n, trecho = len(vals), []
        for i, val in enumerate(vals + [None]):
            if val is None:
                if len(trecho) >= 2:
                    if preencher:
                        self.c.poly(trecho + [(trecho[-1][0], self.y1 - 1), (trecho[0][0], self.y1 - 1)],
                                    fill=mix(cor, self.P["bg"], 0.72))
                    self.c.line(trecho, cor, 1)
                elif len(trecho) == 1:
                    self.c.d.point(trecho[0], fill=cor)
                trecho = []
            else:
                trecho.append((self.x(i, n), self.y(val)))

    def rotulo(self, nome, s, f, cor, candidatos):
        """Escreve o valor na primeira posição que cabe no gráfico sem encostar em outro valor (fundo por trás).
        Se nenhuma posição perto do pico servir, usa os cantos do gráfico."""
        cantos = [(self.x1 - 2, self.y0 + 9, "rs"), (self.x1 - 2, self.y1 - 2, "rs"),
                  (self.x0 + 2, self.y0 + 9, "ls"), (self.x0 + 2, self.y1 - 2, "ls")]
        for x, y, anc in list(candidatos) + cantos:
            y = max(self.y0 + 8, min(self.y1 - 1, y))
            b = self.c.d.textbbox((x, y), s, font=f, anchor=anc)
            caixa = (b[0] - 1, b[1] - 1, b[2] + 1, b[3] + 1)
            dentro = caixa[0] >= self.x0 and caixa[2] <= self.x1 and caixa[1] >= self.y0 and caixa[3] <= self.y1
            livre = all(caixa[2] < o[0] or o[2] < caixa[0] or caixa[3] < o[1] or o[3] < caixa[1] for o in self.ocupados)
            if dentro and livre:
                self.c.rect(caixa, fill=self.fundo)
                self.c.text(nome, x, y, s, f, cor, anchor=anc)
                self.ocupados.append(caixa)
                return True
        return False

    def pico(self, modo, nome, maximos, cor, tipo, f):
        vals = list(maximos)[-self.larg:]
        validos = [(x, i) for i, x in enumerate(vals) if x is not None]
        if not validos:
            return None
        pk, i = max(validos)
        if modo == "marcador":
            mx, my = self.x(i, len(vals)), self.y(pk)
            self.c.d.ellipse((mx - 2, my - 2, mx + 2, my + 2), fill=cor, outline=self.P["bg"])
            self.rotulo(nome, _fmt(tipo, pk), f, cor,
                        [(mx + 5, my + 4, "ls"), (mx - 5, my + 4, "rs"), (mx + 5, my + 13, "ls"), (mx - 5, my + 13, "rs"),
                         (mx + 5, my - 5, "ls"), (mx - 5, my - 5, "rs")])
        elif modo == "linha":
            ly = self.y(pk)
            for x in range(self.x0, self.x1 + 1, 5):
                self.c.line((x, ly, min(x + 2, self.x1), ly), mix(cor, self.P["bg"], 0.25))
            self.rotulo(nome, _fmt(tipo, pk), f, cor,
                        [(self.x1 - 2, ly - 2, "rs"), (self.x1 - 2, ly + 10, "rs"), (self.x0 + 2, ly - 2, "ls"),
                         (self.x0 + 2, ly + 10, "ls"), (self.x1 - 40, ly - 2, "rs"), (self.x1 - 40, ly + 10, "rs")])
        return pk


def _vertical(c, x_dir, y0, y1, partes):
    """Rótulo girado 90° (anti-horário), recortado na tinta, centrado na altura do gráfico (y0 a y1) e encostado
    à esquerda dele (borda direita em x_dir). A fonte diminui até o texto caber na altura do gráfico."""
    from PIL import Image, ImageDraw
    alt = y1 - y0 - 2
    for tam in (9, 8, 7, 6):
        f = font(JB, tam, "Bold")
        if sum(f.getlength(t) for t, _ in partes) <= alt:
            break
    w = int(sum(f.getlength(t) for t, _ in partes)) + 4
    im = Image.new("RGBA", (w, tam + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    xx = 2
    for t, cor in partes:
        d.text((xx, tam + 3), t, font=f, fill=cor + (255,), anchor="ls")
        xx += f.getlength(t)
    im = im.crop(im.getbbox()).rotate(90, expand=True)
    c.img.paste(im, (int(x_dir - 2 - im.width), int(round((y0 + y1) / 2 - im.height / 2))), im)
    return x_dir - 2 - im.width


def _pk(h, k):
    p = [x for x in (h.get(k + "_max") or []) if x is not None]
    return max(p) if p else None


def desenhar(c, v, P, col, F):
    h = v.raw("hist") or {}
    v.raw("vram_pct_txt"); v.raw("ram_pct")
    modo = P.get("pico", "legenda")
    f_lab, f_val, f_pk = font(ROBOTO, 9, "Bold"), font(JB, 10, "Bold"), font(JB, 9, "Bold")
    verde, branco = P["accent"], P["white"]
    s = lambda k: h.get(k) or []

    rot = P.get("rotulos_rot")
    fv = font(JB, 9, "Bold")
    xt, lt = (110, 101) if rot else (XT, LT)
    x0g, larg = (16, 179) if rot else (X0, LARG)

    def legenda_pico(nome, x, y, tipo, k, cor):
        pk = _pk(h, k)
        return c.text(nome, x, y, _fmt(tipo, pk) if pk is not None else "--", f_pk, cor)

    # ---- temperatura (no alto, à direita da escala): faixa de 20 a 100 °C
    g = Grafico(c, P, xt, lt, 28, 60, 20.0, 100.0)
    g.serie(_pares(s("cpu_t"), lambda p: sum(p) / len(p)), verde, True)
    g.serie(_pares(s("gpu_t"), lambda p: sum(p) / len(p)), branco, False)
    if rot:
        _vertical(c, xt, 28, 60, [("CPU ", verde), ("GPU", branco)])
    for i, (lab, k, cor) in enumerate((("CPU", "cpu_t", verde), ("GPU", "gpu_t", branco))):
        y = 28 + 12 + 13 * i
        if rot:
            g.pico(modo, f"gr.t{i}.pk", _pares(s(k + "_max"), max), cor, "temp", f_pk)
            continue
        b = c.text(f"gr.t{i}.lab", XT_LEG, y, lab, f_lab, cor)
        if modo == "legenda":
            legenda_pico(f"gr.t{i}.pk", b[2] + 2, y, "temp", k, cor)
        else:
            g.pico(modo, f"gr.t{i}.pk", _pares(s(k + "_max"), max), cor, "temp", f_pk)

    # ---- VRAM (área) e RAM (linha), de 0 a 100%
    y0, y1 = 68, 106
    g = Grafico(c, P, x0g, larg, y0, y1, 0.0, 100.0)
    g.serie(s("vram"), verde, True)
    g.serie(s("ram"), branco, False)
    gb_vram, gb_ram = ("gb", h.get("vram_total")), ("gb", h.get("ram_total"))
    if rot:
        _vertical(c, x0g, y0, y1, [("VRAM ", verde), ("RAM", branco)])
        g.pico(modo, "gr.vram.pk", s("vram_max"), verde, gb_vram, f_pk)
        g.pico(modo, "gr.ram.pk", s("ram_max"), branco, gb_ram, f_pk)
    elif modo == "legenda":
        c.text("gr.vram.lab", 6, y0 + 8, "VRAM", f_lab, verde)
        legenda_pico("gr.vram.pk", 6, y0 + 17, gb_vram, "vram", verde)
        c.text("gr.ram.lab", 6, y0 + 28, "RAM", f_lab, branco)
        legenda_pico("gr.ram.pk", 6, y1 - 1, gb_ram, "ram", branco)
    else:
        c.text("gr.vram.lab", 6, y0 + 9, "VRAM", f_lab, verde)
        c.text("gr.ram.lab", 6, y0 + 20, "RAM", f_lab, branco)
        g.pico(modo, "gr.vram.pk", s("vram_max"), verde, gb_vram, f_pk)
        g.pico(modo, "gr.ram.pk", s("ram_max"), branco, gb_ram, f_pk)

    # ---- rede: download (área) e upload (linha); escala até o pico de 24 h + 10%
    y0, y1 = 109, 146
    topo = max([x for k in ("down_max", "up_max") for x in s(k) if x is not None] or [0.0])
    g = Grafico(c, P, x0g, larg, y0, y1, 0.0, max(topo * 1.1, 100e3))
    g.serie(s("down"), verde, True)
    g.serie(s("up"), branco, False)
    if rot:
        _vertical(c, x0g, y0, y1, [("REDE ", verde), ("↓", verde), ("↑", branco)])
        g.pico(modo, "gr.rede.dpk", s("down_max"), verde, "rede", f_pk)
        g.pico(modo, "gr.rede.upk", s("up_max"), branco, "rede", f_pk)
        return
    c.text("gr.rede.lab", 6, y0 + 8, "REDE", f_lab, verde)
    if modo == "legenda":
        b = c.text("gr.rede.down", 6, y0 + 19, "↓", f_pk, verde)
        legenda_pico("gr.rede.dpk", b[2] + 1, y0 + 19, "rede", "down", verde)
        b = c.text("gr.rede.up", 6, y0 + 30, "↑", f_pk, branco)
        legenda_pico("gr.rede.upk", b[2] + 1, y0 + 30, "rede", "up", branco)
    else:
        b = c.text("gr.rede.down", 6, y0 + 20, "↓", f_val, verde)
        c.text("gr.rede.up", b[2] + 3, y0 + 20, "↑", f_val, branco)
        g.pico(modo, "gr.rede.dpk", s("down_max"), verde, "rede", f_pk)
        g.pico(modo, "gr.rede.upk", s("up_max"), branco, "rede", f_pk)
