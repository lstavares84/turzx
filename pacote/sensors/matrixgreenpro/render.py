# MATRIX GREEN PRO | versão 2.1.0 | 31/10/2026 23:50 (-03) | ajustes finais: 'FAN 72% | 1800RPM', estado da
#   internet na linha do ping, estado da coleta no rodapé
# histórico: 2.0.0 31/10/2026 23:25 hierarquia branco/verde, trilhos de saúde, fontes mínimas de 11 px
# histórico: 1.0.0 31/10/2026 22:40 criação inicial
#
# Desenho do quadro 320x480 em modo RETRATO. Única fonte de verdade do layout:
# a prévia PNG, os testes de sobreposição e a tela física usam esta função.
# Origem no canto superior esquerdo; x 0..319, y 0..479. Textos pela linha de
# base (anchor "ls"/"rs"), o que alinha números de tamanhos diferentes.
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .alerts import PALETTE, color, worst, OK, WARN, CRIT, NA, NEUTRAL

W, H = 320, 480
X0, X1 = 7, 314          # margem esquerda 7 px (trilho de saúde em x 0..2), direita 6 px
XV = 44                  # coluna de valores, após o rótulo da seção
XC2 = 170                # segunda coluna (upload, TX)

FONT_DIR = Path(__file__).resolve().parents[3] / "res" / "fonts" / "jetbrains-mono"
_FONTS = {}


def font(size, weight="Regular"):
    key = (size, weight)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(str(FONT_DIR / f"JetBrainsMonoNL-{weight}.ttf"), size)
    return _FONTS[key]


# Escala tipográfica (JetBrains Mono NL, largura fixa 0,6 em, sem ligaduras).
# Menor corpo usado: 11 px (~1,7 mm de corpo a 165 ppi no TUS-35).
F_XL = ("Bold", 22)      # valores primários: temperaturas, utilização, relógio
F_M = ("Bold", 15)       # valores secundários de destaque
F_SB = ("Bold", 12)      # rótulos de seção e percentuais
F_S = ("Regular", 12)    # linhas de detalhe
F_XS = ("Regular", 11)   # contexto (LIVRE, DESDE BOOT, origem do dado)

WHITE, AUX, GREEN, YELLOW = PALETTE["white"], PALETTE["aux"], PALETTE["green"], PALETTE["yellow"]


class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), PALETTE["bg"])
        self.d = ImageDraw.Draw(self.img)
        self.elements = []   # (nome, (x0, y0, x1, y1)) para testes e tabela de coordenadas

    def _rec(self, name, box):
        self.elements.append((name, tuple(int(round(v)) for v in box)))

    def text(self, name, x, y, s, f, fill, anchor="ls"):
        if not s:
            return (x, y, x, y)
        fnt = font(f[1], f[0])
        box = self.d.textbbox((x, y), s, font=fnt, anchor=anchor)
        self.d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)
        self._rec(name, box)
        return box

    def width(self, s, f):
        return font(f[1], f[0]).getlength(s) if s else 0

    def tag(self, name, y, s):
        """Rótulo de seção: branco, negrito (identificador permanece branco)."""
        return self.text(name, X0, y, s, F_SB, WHITE)

    def bar(self, name, x, y, w, h, pct, fill):
        self.d.rectangle((x, y, x + w - 1, y + h - 1), fill=PALETTE["bg2"])
        if pct is not None:
            p = max(0.0, min(100.0, float(pct)))
            fw = int(round(w * p / 100.0))
            if fw > 0:
                self.d.rectangle((x, y, x + fw - 1, y + h - 1), fill=fill)
        self._rec(name, (x, y, x + w, y + h))

    def sep(self, name, y):
        self.d.line((X0, y, X1, y), fill=PALETTE["div"], width=1)
        self._rec(name, (X0, y, X1 + 1, y + 1))

    def rail(self, name, y0, y1, level):
        """Trilho de saúde da seção (x 0..2): verde, amarelo, vermelho ou cinza (sem dados)."""
        self.d.rectangle((0, y0, 2, y1), fill=color(level) if level != NA else PALETTE["div"])
        self._rec(name, (0, y0, 3, y1 + 1))

    def pair(self, name, x, y, lab, val, f_val, lvl, f_lab=F_S, gap=4, anchor_right=False, lab_fill=None):
        """Rótulo auxiliar (cinza) + valor (cor do nível); com anchor_right o par termina em x."""
        wl = self.width(lab, f_lab) + (gap if lab else 0)
        wv = self.width(val, f_val)
        if anchor_right:
            x = x - wl - wv
        if lab:
            self.text(name + ".lab", x, y, lab, f_lab, lab_fill or AUX)
        self.text(name + ".val", x + wl, y, val, f_val, color(lvl))
        return x, x + wl + wv


# Linhas de base (y) de cada linha do layout. Ajustadas por medição real.
Y = {
    "hdr": 14,
    "cpu1": 46, "cpu2": 70, "sep_cpu": 77,
    "gpu1": 101, "gpu2": 125, "gpu3": 142, "gpu4": 159, "sep_gpu": 166,
    "ram1": 186, "sep_ram": 203,
    "dsk": (221, 246, 271), "sep_dsk": 282,
    "net1": 302, "net2": 319, "net3": 336, "net4": 353, "sep_net": 360,
    "sys1": 385, "sys2": 402, "sep_sys": 409,
    "wx1": 429, "wx2": 446, "sep_wx": 453,
    "pwr": 472,
}


def background(elements=None):
    """Fundo estático (theme.yaml/static_images): cabeçalho e divisórias."""
    c = Canvas()
    _header(c, None)
    for k, v in Y.items():
        if k.startswith("sep"):
            c.sep(k, v)
    return c.img


def _header(c, vm):
    c.d.rectangle((0, 0, W - 1, 19), fill=PALETTE["bg2"])
    c._rec("hdr.band", (0, 0, W, 20))
    b = c.text("hdr.title", X0, Y["hdr"], "MATRIX GREEN", F_SB, GREEN)
    c.text("hdr.pro", b[2] + 5, Y["hdr"], "PRO", F_SB, YELLOW)   # único detalhe amarelo de identidade
    if vm is None:
        return
    if vm.get("demo"):
        c.text("hdr.demo", 150, Y["hdr"], "DEMO", F_XS, YELLOW)
    st, lv = vm.get("hdr_status", ("", NA))
    c.text("hdr.status", X1, Y["hdr"], st, F_SB, color(lv), anchor="rs")


def draw_frame(vm):
    """vm: modelo de visão (textos formatados + níveis). Retorna (Image, elementos)."""
    c = Canvas()
    g = lambda k: vm.get(k, ("N/D", NA))
    hl = vm.get("health", {})
    _header(c, vm)

    # ---------------- CPU
    y = Y["cpu1"]
    c.rail("rail.cpu", 22, Y["sep_cpu"] - 2, worst([hl.get("cpu_temp", NA), hl.get("cpu_fan", NA)]))
    c.tag("cpu.tag", y, "CPU")
    t, lv = g("cpu_util"); c.text("cpu.util", XV, y, t, F_XL, color(lv))
    t, lv = g("cpu_ghz"); c.text("cpu.ghz", 114, y, t, F_M, color(lv))
    t, lv = g("cpu_temp"); c.text("cpu.temp", X1, y, t, F_XL, color(lv), anchor="rs")
    c.bar("cpu.bar", X0, y + 5, X1 - X0, 5, vm.get("cpu_pct"), GREEN)
    y = Y["cpu2"]
    t, lv = g("cpu_fan"); c.pair("cpu.fan", X0, y, "FAN", t, F_SB, lv)
    t, lv = g("cpu_load"); c.pair("cpu.load", X1, y, "LOAD", t, F_S, lv, anchor_right=True)
    c.sep("sep_cpu", Y["sep_cpu"])

    # ---------------- GPU
    y = Y["gpu1"]
    c.rail("rail.gpu", Y["sep_cpu"] + 2, Y["sep_gpu"] - 2,
           worst([hl.get(k, NA) for k in ("gpu", "gpu_temp", "vram", "gpu_fan")]))
    c.tag("gpu.tag", y, "GPU")
    t, lv = g("gpu_util"); c.text("gpu.util", XV, y, t, F_XL, color(lv))
    t, lv = g("gpu_mhz"); c.text("gpu.mhz", 114, y, t, F_M, color(lv))
    t, lv = g("gpu_temp"); c.text("gpu.temp", X1, y, t, F_XL, color(lv), anchor="rs")
    c.bar("gpu.bar", X0, y + 5, X1 - X0, 5, vm.get("gpu_pct"), GREEN)
    y = Y["gpu2"]
    t, lv = g("vram_txt"); c.pair("gpu.vram", X0, y, "VRAM", t, F_SB, lv)
    t, lv = g("vram_pct_txt"); c.text("gpu.vrampct", X1, y, t, F_SB, color(lv), anchor="rs")
    vp = vm.get("vram_pct")
    c.bar("gpu.vrambar", 176, y - 8, 100, 5, vp, color(lv) if vp is not None else GREEN)
    y = Y["gpu3"]
    t, lv = g("gpu_fan_pct"); _, xe = c.pair("gpu.fan", X0, y, "FAN", t, F_SB, lv)
    xe = c.text("gpu.fansep", xe + 5, y, "|", F_S, AUX)[2]
    t, lv = g("gpu_fan_rpm"); c.text("gpu.fanrpm", xe + 5, y, t, F_SB if lv != NA else F_S, color(lv))
    t, lv = g("fps"); c.pair("gpu.fps", X1, y, "FPS", t, F_M, lv, anchor_right=True)
    y = Y["gpu4"]
    t, lv = g("gpu_w"); c.pair("gpu.w", X0, y, "GPU W", t, F_SB, lv)
    t, lv = g("gpu_wlim"); c.text("gpu.wlim", X1, y, t, F_XS, AUX, anchor="rs")
    c.sep("sep_gpu", Y["sep_gpu"])

    # ---------------- RAM
    y = Y["ram1"]
    rl = vm.get("ram_lvl", NA)
    c.rail("rail.ram", Y["sep_gpu"] + 2, Y["sep_ram"] - 2, hl.get("ram", NA))
    c.tag("ram.tag", y, "RAM")
    t, lv = g("ram_used"); b = c.text("ram.used", XV, y, t, F_M, color(lv))
    t, lv = g("ram_total"); c.text("ram.total", b[2] + 1, y, t, F_M, color(lv))
    t, lv = g("ram_avail"); c.pair("ram.avail", X1, y, "DISP", t, F_SB, lv, anchor_right=True)
    c.bar("ram.bar", X0, y + 5, X1 - X0, 5, vm.get("ram_pct"), color(rl) if rl != NA else GREEN)
    c.sep("sep_ram", Y["sep_ram"])

    # ---------------- Discos
    c.rail("rail.dsk", Y["sep_ram"] + 2, Y["sep_dsk"] - 2, worst([hl.get(f"disk{i}", NA) for i in range(3)]))
    wl = c.width("LIVRE", F_XS)
    for i, dk in enumerate(vm.get("disks", [])[:3]):
        yy = Y["dsk"][i]
        c.tag(f"dsk{i}.tag", yy, dk["name"])
        c.text(f"dsk{i}.use", XV, yy, dk["use"], F_S, color(dk.get("use_lvl", NEUTRAL)))
        c.text(f"dsk{i}.pct", 200, yy, dk["pct_txt"], F_SB, color(dk["lvl"]), anchor="rs")
        c.text(f"dsk{i}.freelab", X1, yy, "LIVRE", F_XS, AUX, anchor="rs")
        c.text(f"dsk{i}.free", X1 - wl - 4, yy, dk["free"], F_SB, color(dk["lvl"]), anchor="rs")
        c.bar(f"dsk{i}.bar", XV, yy + 4, X1 - XV, 3, dk.get("pct"),
              color(dk["lvl"]) if dk["lvl"] != NA else GREEN)
    c.sep("sep_dsk", Y["sep_dsk"])

    # ---------------- Rede
    c.rail("rail.net", Y["sep_dsk"] + 2, Y["sep_net"] - 2, hl.get("conexao", NA))
    y = Y["net1"]
    c.tag("net.tag", y, "NET")
    t, lv = g("net_down"); c.text("net.down", XV, y, "↓" + t, F_M, color(lv))
    t, lv = g("net_up"); c.text("net.up", XC2, y, "↑" + t, F_M, color(lv))
    y = Y["net2"]
    c.text("net.tottag", X0, y, "TOT", F_SB, WHITE)
    t, lv = g("net_rx"); c.pair("net.rx", XV, y, "RX", t, F_S, lv)
    t, lv = g("net_tx"); c.pair("net.tx", XC2, y, "TX", t, F_S, lv)
    c.text("net.period", X1, y, "DESDE BOOT", F_XS, AUX, anchor="rs")
    for key, tagtxt, yk in (("eth", "ETH", "net3"), ("wifi", "WIFI", "net4")):
        y = Y[yk]
        d = vm.get(key, {"state": ("N/D", NA), "info": ("", NA), "rates": ("", NA)})
        c.tag(f"{key}.tag", y, tagtxt)
        b = c.text(f"{key}.state", XV, y, d["state"][0], F_SB, color(d["state"][1]))
        rb = c.text(f"{key}.rates", X1, y, d["rates"][0], F_S, color(d["rates"][1]), anchor="rs")
        xi = max(b[2] + 6, XV + 48)
        room = (rb[0] if d["rates"][0] else X1) - 6 - xi
        info = d["info"][0]
        if c.width(info, F_S) > room and " " in info:   # nome longo: mantém só velocidade/sinal
            info = info.split(" ", 1)[1]
        while info and c.width(info, F_S) > room:        # último recurso: corta com reticências
            info = info[:-2] + "…"
        c.text(f"{key}.info", xi, y, info, F_S, color(d["info"][1]))
    c.sep("sep_net", Y["sep_net"])

    # ---------------- Sistema
    y = Y["sys1"]
    t, lv = g("clock"); c.text("sys.clock", X0, y, t, F_XL, color(lv))
    t, lv = g("date"); c.text("sys.date", X1, y, t, F_M, color(lv), anchor="rs")
    y = Y["sys2"]
    t, lv = g("os"); c.text("sys.os", X0, y, t, F_S, AUX)
    t, lv = g("uptime"); c.pair("sys.up", X1, y, "UP", t, F_SB, lv, anchor_right=True)
    c.sep("sep_sys", Y["sep_sys"])

    # ---------------- Ping e clima
    c.rail("rail.wx", Y["sep_sys"] + 2, Y["sep_wx"] - 2, worst([hl.get("ping", NA)]))
    y = Y["wx1"]
    t, lv = g("ping"); _, xe = c.pair("png", X0, y, "PING", t, F_M, lv, f_lab=F_SB, lab_fill=WHITE)
    t, lv = g("inet"); c.text("inet", xe + 6, y, t, F_XS, color(lv))
    t, lv = g("wtemp"); bx = c.text("wx.temp", X1, y, t, F_M, color(lv), anchor="rs")
    c.text("wx.city", bx[0] - 6, y, vm.get("city", ""), F_S, AUX, anchor="rs")
    y = Y["wx2"]
    t, lv = g("wdesc"); c.text("wx.desc", X0, y, t, F_S, color(lv))
    t, lv = g("wage"); c.text("wx.age", X1, y, t, F_XS, color(lv), anchor="rs")
    c.sep("sep_wx", Y["sep_wx"])

    # ---------------- Energia total e status final
    c.rail("rail.pwr", Y["sep_wx"] + 2, 477, hl.get("energia", NA))
    y = Y["pwr"]
    t, lv = g("power"); _, xe = c.pair("pwr", X0, y, "TOTAL W", t, F_M, lv, f_lab=F_SB, lab_fill=WHITE)
    t, lv = g("power_tag"); tb = c.text("pwr.tag", xe + 6, y, t, F_XS, color(lv))
    t, lv = g("coleta")
    room = X1 - (tb[2] if t else xe) - 8
    while t and c.width(t, F_XS) > room:      # lista de falhas longa: encurta, nunca sobrepõe
        t = t[:-2].rstrip() + "…"
    c.text("coleta", X1, y, t, F_XS, color(lv), anchor="rs")
    return c.img, c.elements
