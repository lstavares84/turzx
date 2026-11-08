# MATRIX GREEN PRO | estilos alternativos | versão 4.0.0 | 08/11/2026 13:18 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 4.0.0 08/11/2026 13:18 escala por tela (tela.py): 3,5" em 1x, 5,2" em 2,25x com fontes e traços na resolução real
# histórico: 3.0.0-alfa 31/10/2026 23:40 criação
# Base comum dos cinco estilos alternativos. Todos recebem o MESMO modelo de visão
# (viewmodel.py da versão 2.1.0 congelada): mesmas métricas, mesma saúde, mesmo
# estado da coleta. Só muda o desenho. Os estilos desenham em coordenadas lógicas de 320x480 (retrato);
# o Canvas multiplica tudo pela ESCALA da tela (tela.py). Na 5,2" (720x1280, escala 2,25) o quadro é exatamente
# o mesmo da 3,5": ocupa os primeiros 1080 px de altura e embaixo fica só o fundo (malha de hexágonos).
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..tela import TELA, LARGURA, ALTURA, ESCALA

W, H = 320, 480                       # área lógica que todos os estilos desenham
K = ESCALA
HL = ALTURA / K                       # altura lógica total (480 na 3,5"; 568,9 na 5,2", sobra só com o fundo)
OK, WARN, CRIT, NA, LOST, NEUTRAL = 0, 1, 2, 3, 4, 9

# estilos/ -> matrixgreenpro/ -> sensors/ -> library/ -> raiz do programa
FONT_ROOT = Path(__file__).resolve().parents[4] / "res" / "fonts"
_FONTS = {}

# Fontes já distribuídas pelo turing-smart-screen (nada é redistribuído aqui)
JB = "jetbrains-mono/JetBrainsMonoNL-{}.ttf"     # cobertura completa (setas, °, acentos)
ROBOTO = "roboto/Roboto-{}.ttf"                   # sem setas: usar só em rótulos
ROBOTO_MONO = "roboto-mono/RobotoMono-{}.ttf"
DIGITAL7 = "digital/DIGITAL-7.TTF"                # 7 segmentos: só dígitos, sem °
GEFORCE = "geforce/GeForce-{}.ttf"                # sem setas: só títulos
PIXEL12 = "fusion-pixel/fusion-pixel-12px-monospaced-zh_hans.otf"


def font(path, size, weight=None):
    rel = path.format(weight) if weight else path
    key = (rel, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(str(FONT_ROOT / rel), max(1, round(size * K)))   # corpo na resolução real
    return _FONTS[key]


_CMAPS = {}


def missing_glyphs(fnt, s):
    path = getattr(fnt, "path", None)
    if not path:
        return ""
    if path not in _CMAPS:
        try:
            from fontTools.ttLib import TTFont
            _CMAPS[path] = set(TTFont(path, fontNumber=0, lazy=True).getBestCmap().keys())
        except Exception:
            _CMAPS[path] = None
    cm = _CMAPS[path]
    if cm is None:
        return ""
    return "".join(sorted({ch for ch in s if ord(ch) not in cm and not ch.isspace()}))


class VM:
    """Acesso ao modelo de visão registrando o que foi usado (teste de cobertura:
    nenhum estilo pode omitir métrica)."""

    def __init__(self, vm):
        self.vm, self.used = vm, set()

    def __call__(self, key, default=("N/D", NA)):
        self.used.add(key)
        return self.vm.get(key, default)

    def raw(self, key, default=None):
        self.used.add(key)
        return self.vm.get(key, default)


def selo_versao(c, P, fonte):
    """Canto superior direito: nome do estilo (ALPHA, BETA ou GAMMA) e a versão do pacote, ex.: 'BETA v1.5.0'."""
    nome = P.get("selo")
    if not nome:
        return
    from .. import versao
    vb = c.text("hdr.ver", 314, 17, (f"v{versao.VERSAO}" if versao.VERSAO[:1].isdigit() else versao.VERSAO), fonte, P["sub"], anchor="rs")
    c.text("hdr.estilo", vb[0] - 5, 17, nome, fonte, P["accent"], anchor="rs")


REQUIRED = {
    "hdr_status", "cpu_util", "cpu_pct", "cpu_ghz", "cpu_temp", "cpu_fan", "cpu_load", "pump", "fan_sqi", "fan_sql", "fan_sqt", "t_placa", "t_ram", "t_ssd",
    "gpu_util", "gpu_pct", "gpu_mhz", "gpu_temp", "vram_txt", "vram_pct_txt", "vram_pct",
    "gpu_fan_pct", "gpu_fan_rpm", "gpu_w", "gpu_wlim", "fps",
    "ram_used", "ram_total", "ram_avail", "ram_pct", "disks",
    "net_down", "net_up", "net_rx", "net_tx", "eth", "wifi",
    "clock", "date", "os", "uptime", "ping", "inet", "city", "wtemp", "wdesc", "wage",
    "power", "power_tag", "coleta",
}


def _esc(xy, k):
    """Multiplica coordenadas (número, par, lista de pares ou caixa) pela escala."""
    if isinstance(xy, (int, float)):
        return xy * k
    return type(xy)(_esc(v, k) for v in xy) if isinstance(xy, (list, tuple)) else xy


def _caixa(box, k):
    """Caixa inclusiva (x0, y0, x1, y1) lógica -> real, cobrindo os pixels inteiros (sem frestas entre blocos)."""
    if k == 1:
        return box
    if len(box) == 2:                                     # [(x0, y0), (x1, y1)]
        (x0, y0), (x1, y1) = box
    else:
        x0, y0, x1, y1 = box
    return (round(x0 * k), round(y0 * k), max(round(x0 * k), round((x1 + 1) * k) - 1),
            max(round(y0 * k), round((y1 + 1) * k) - 1))


class Desenho:
    """ImageDraw em coordenadas lógicas: os estilos chamam c.d.* como antes e tudo sai na resolução real."""

    def __init__(self, img, k):
        self.raw, self.k = ImageDraw.Draw(img), k

    def _w(self, width):
        return max(1, round(width * self.k)) if width else 0

    def text(self, xy, s, font=None, fill=None, anchor=None, stroke_width=0, stroke_fill=None, **kw):
        self.raw.text(_esc(xy, self.k), s, font=font, fill=fill, anchor=anchor,
                      stroke_width=self._w(stroke_width), stroke_fill=stroke_fill, **kw)

    def textbbox(self, xy, s, font=None, anchor=None, stroke_width=0, **kw):
        b = self.raw.textbbox(_esc(xy, self.k), s, font=font, anchor=anchor, stroke_width=self._w(stroke_width), **kw)
        return tuple(v / self.k for v in b)

    def textlength(self, s, font=None, **kw):
        return self.raw.textlength(s, font=font, **kw) / self.k

    def line(self, xy, fill=None, width=1, joint=None):
        self.raw.line(_esc(xy, self.k), fill=fill, width=self._w(width), joint=joint)

    def rectangle(self, xy, fill=None, outline=None, width=1):
        self.raw.rectangle(_caixa(xy, self.k), fill=fill, outline=outline, width=self._w(width))

    def rounded_rectangle(self, xy, radius=0, fill=None, outline=None, width=1, **kw):
        self.raw.rounded_rectangle(_caixa(xy, self.k), radius * self.k, fill=fill, outline=outline,
                                   width=self._w(width), **kw)

    def polygon(self, xy, fill=None, outline=None, width=1):
        self.raw.polygon(_esc(xy, self.k), fill=fill, outline=outline, width=self._w(width))

    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.raw.ellipse(_caixa(xy, self.k), fill=fill, outline=outline, width=self._w(width))

    def arc(self, xy, start, end, fill=None, width=1):
        self.raw.arc(_caixa(xy, self.k), start, end, fill=fill, width=self._w(width))

    def pieslice(self, xy, start, end, fill=None, outline=None, width=1):
        self.raw.pieslice(_caixa(xy, self.k), start, end, fill=fill, outline=outline, width=self._w(width))

    def point(self, xy, fill=None):
        pts = [xy] if isinstance(xy[0], (int, float)) else xy
        for x, y in pts:                                  # um pixel lógico vira um quadradinho de K x K
            self.raw.rectangle(_caixa((x, y, x, y), self.k), fill=fill)


class Canvas:
    def __init__(self, bg):
        self.k = K
        self.img = Image.new("RGB", (LARGURA, ALTURA), bg)
        self.texts = []     # (nome, caixa) dos textos: base do teste de sobreposição
        self.shapes = []
        self.glyph_issues = []   # caracteres sem glifo na fonte (evita "quadradinhos")

    def text(self, name, x, y, s, fnt, fill, anchor="ls", stroke=0, stroke_fill=None):
        if not s:
            return (x, y, x, y)
        if stroke:
            box = self.d.textbbox((x, y), s, font=fnt, anchor=anchor, stroke_width=stroke)
            self.d.text((x, y), s, font=fnt, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)
            self.texts.append((name, tuple(int(round(v)) for v in box)))
            return box
        miss = missing_glyphs(fnt, s)
        if miss:
            self.glyph_issues.append((name, miss, Path(getattr(fnt, "path", "?")).name))
        box = self.d.textbbox((x, y), s, font=fnt, anchor=anchor)
        self.d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)
        self.texts.append((name, tuple(int(round(v)) for v in box)))
        return box

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, im):                                   # trocar a imagem (ex.: depois do brilho) refaz o desenho
        self._img = im
        self.d = Desenho(im, self.k)

    def width(self, s, fnt):
        return fnt.getlength(s) / self.k if s else 0

    def paste(self, im, xy, mask=None):
        """Cola uma imagem já na resolução real numa posição lógica."""
        self.img.paste(im, (int(round(xy[0] * self.k)), int(round(xy[1] * self.k))), mask)

    def fit(self, s, fnt, maxw):
        """Encurta com reticências para caber em maxw (nunca sobrepõe)."""
        if self.width(s, fnt) <= maxw:
            return s
        while s and self.width(s + "…", fnt) > maxw:
            s = s[:-1]
        return (s.rstrip() + "…") if s else ""

    def rect(self, box, fill=None, outline=None, width=1, name=None):
        self.d.rectangle(box, fill=fill, outline=outline, width=width)
        if name:
            self.shapes.append((name, box))

    def rrect(self, box, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon(pts, fill=fill, outline=outline, width=width)

    def line(self, pts, fill, width=1):
        self.d.line(pts, fill=fill, width=width)

    def hbar(self, x, y, w, h, pct, fill, track, seg=0, gap=1):
        """Barra horizontal; seg>0 desenha blocos (barra segmentada)."""
        self.d.rectangle((x, y, x + w - 1, y + h - 1), fill=track)
        if pct is None:
            return
        fw = int(round(w * max(0.0, min(100.0, float(pct))) / 100.0))
        if fw <= 0:
            return
        if seg:
            xx = x
            while xx < x + fw:
                self.d.rectangle((xx, y, min(xx + seg - 1, x + fw - 1), y + h - 1), fill=fill)
                xx += seg + gap
        else:
            self.d.rectangle((x, y, x + fw - 1, y + h - 1), fill=fill)

    def vbar(self, x, y, w, h, pct, fill, track):
        self.d.rectangle((x, y, x + w - 1, y + h - 1), fill=track)
        if pct is None:
            return
        fh = int(round(h * max(0.0, min(100.0, float(pct))) / 100.0))
        if fh > 0:
            self.d.rectangle((x, y + h - fh, x + w - 1, y + h - 1), fill=fill)


def worst(levels):
    lv = [x for x in levels if x in (OK, WARN, CRIT, LOST)]
    if not lv:
        return NA
    if CRIT in lv:
        return CRIT
    if WARN in lv or LOST in lv:
        return WARN
    return OK


def strip_status(s):
    """'● 2 CRÍTICOS ▲1' -> texto sem símbolos, para fontes sem esses glifos."""
    return s.replace("●", "").replace("▲", "+").replace("■", "").strip()


# ---------------------------------------------------------------- efeitos (3.0.0-alfa2)
def bloom(img, radius=3, strength=0.9, threshold=110):
    """Brilho suave nas partes claras (neon/holograma/VFD) sem borrar o texto original."""
    from PIL import ImageChops, ImageFilter
    radius = radius * K
    lum = img.convert("L").point(lambda p: 255 if p > threshold else 0)
    glow = Image.composite(img, Image.new("RGB", img.size, (0, 0, 0)), lum)
    glow = glow.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1:
        glow = glow.point(lambda p: int(p * strength))
    return ImageChops.add(img, glow)


def vgradient(c, box, top, bottom):
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for i in range(h + 1):
        t = i / h
        colr = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        c.d.line((x0, y0 + i, x1, y0 + i), fill=colr)


def grid(c, step, colr, box=(0, 0, W - 1, int(HL) - 1)):
    x0, y0, x1, y1 = box
    for x in range(x0, x1 + 1, step):
        c.d.line((x, y0, x, y1), fill=colr)
    for y in range(y0, y1 + 1, step):
        c.d.line((x0, y, x1, y), fill=colr)


def iface_row(c, v, key, y, x_tag, tag, x_state, x_right, f_tag, f_state, f_info, f_rates,
              col, c_tag, c_info=None, c_rates=None, min_info_x=0):
    """Linha ETH/WIFI padronizada: rótulo, estado, informação ajustada, taxas à direita."""
    d = v.raw(key, {"state": ("N/D", NA), "info": ("", NA), "rates": ("", NA)})
    if tag:
        c.text(f"{key}.tag", x_tag, y, tag, f_tag, c_tag)
    b = c.text(f"{key}.state", x_state, y, d["state"][0], f_state, col(d["state"][1]))
    rb = c.text(f"{key}.rates", x_right, y, d["rates"][0], f_rates,
                c_rates or col(d["rates"][1]), anchor="rs")
    xi = max(b[2] + 6, min_info_x)
    room = (rb[0] if d["rates"][0] else x_right) - 6 - xi
    ic = col(d["info"][1]) if (c_info is None or d["info"][1] != NEUTRAL) else c_info
    c.text(f"{key}.info", xi, y, c.fit(d["info"][0], f_info, room), f_info, ic)
    return d
