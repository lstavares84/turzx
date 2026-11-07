# GAMMA v2 | estilos/v2_base.py | versão 0.1.0 | 07/11/2026 19:55 (-03) | criação original (Claude, para Lucas Tavares)
# Base comum das 12 propostas da v2.0.0. Mesma paleta do GAMMA (fundo quase preto, verde fluorescente, âmbar,
# vermelho e cinza-esverdeado), mesmos dados e mesma saúde; cada proposta muda só o desenho.
# Ctx junta o Canvas, o acesso às métricas (VM, que registra a cobertura), as cores por nível, as fontes e o
# estado geral (N0/N1/N2, contagens, fase do piscar). Decisões herdadas: sem RPM da GPU, sem TOTAL W.
import time

from .alerta import counts, label, mix
from .base import Canvas, VM, font, JB, ROBOTO, ROBOTO_MONO, OK, WARN, CRIT, NA, LOST, NEUTRAL, W, H, bloom
from .reator_gamma import GAMMA

GEFORCE = "geforce/GeForce-{}.ttf"
PIXEL = "fusion-pixel/fusion-pixel-{}px-monospaced-zh_hans.otf"
DIGITAL = "digital/DIGITAL-7.TTF"
GENERALE = "generale-mono/GeneraleMono{}.ttf"

P = {k: GAMMA[k] for k in ("bg", "accent", "ice", "white", "sub", "dim", "amber", "red")}
NIVEL_TXT = {OK: "N0", WARN: "N1", CRIT: "N2"}


class Ctx:
    def __init__(self, vm_dict, selo):
        self.v = VM(vm_dict)
        self.c = Canvas(P["bg"])
        self.P = P
        self.selo = selo
        b = vm_dict.get("blink")
        self.blink = (int(time.time()) % 2 == 0) if b is None else b
        st, slv = self.v("hdr_status")
        self.st = st
        self.lvl = slv if slv in (OK, WARN, CRIT) else OK
        self.ncrit, self.nwarn = counts(self.v)
        self.rotulo = label(st, self.ncrit, self.nwarn, self.lvl)
        self.on = self.blink or self.lvl != CRIT              # fase acesa (só o crítico alterna)
        self.demo = bool(self.v.raw("demo"))
        for k in ("gpu_fan_rpm", "power", "power_tag"):          # fora da tela por decisão do projeto
            self.v.raw(k)

    # ---- cores e fontes
    def col(self, lv, ok=None):
        return {OK: ok or P["ice"], WARN: P["amber"], CRIT: P["red"], NA: P["sub"], LOST: P["amber"],
                NEUTRAL: P["white"]}.get(lv, P["white"])

    def cor_nivel(self, lv=None):
        lv = self.lvl if lv is None else lv
        return {OK: P["accent"], WARN: P["amber"], CRIT: P["red"]}.get(lv, P["sub"])

    @staticmethod
    def f(path, size, weight=None):
        return font(path, size, weight)

    # ---- texto
    def t(self, nome, x, y, s, fnt, cor, anchor="ls"):
        return self.c.text(nome, x, y, s, fnt, cor, anchor=anchor)

    def par(self, nome, x, y, lab, chave, f_lab, f_val, cor_lab=None, right=False, ok=None, troca=None, gap=4):
        """'LAB valor' com o valor na cor do nível. Devolve (x esquerdo, x direito)."""
        t, lv = self.v(chave)
        if troca:
            t = troca(t)
        wl = self.c.width(lab, f_lab) + gap if lab else 0
        wv = self.c.width(t, f_val)
        if right:
            x -= wl + wv
        if lab:
            self.c.text(nome + ".lab", x, y, lab, f_lab, cor_lab or P["sub"])
        self.c.text(nome + ".val", x + wl, y, t, f_val, self.col(lv, ok))
        return x, x + wl + wv

    def fit(self, s, fnt, w):
        return self.c.fit(s, fnt, w)

    # ---- dados compostos
    def g(self, chave):
        return self.v(chave)

    def pct(self, chave):
        x = self.v.raw(chave)
        return None if x is None else max(0.0, min(100.0, float(x)))

    def ram_pct_txt(self):
        p = self.v.raw("ram_pct")
        return (f"{round(p)}%", self.v.raw("ram_lvl", OK)) if p is not None else ("N/D", NA)

    def discos(self):
        return self.v.raw("disks", [])[:3]

    def baias(self):
        return self.v.raw("baias", []) or []

    def iface(self, chave):
        return self.v.raw(chave, {"state": ("N/D", NA), "info": ("", NA), "rates": ("", NA)})

    def sem_rpm(self, t):
        return t.replace("RPM", "")

    # ---- desenho
    def barra(self, x, y, w, h, pct, lv, seg=0, gap=1, trilho=None):
        cor = self.cor_nivel(lv) if lv in (OK, WARN, CRIT) else P["sub"]
        self.c.hbar(x, y, w, h, pct, cor, trilho or mix(P["accent"], P["bg"], 0.88), seg=seg, gap=gap)

    def selo_versao(self, x=314, y=None, fnt=None, cor=None):
        """Nome da proposta e versão, discretos (no repositório aparece 'dev')."""
        from .. import versao
        fnt = fnt or font(JB, 9, "Regular")
        ver = f"v{versao.VERSAO}" if versao.VERSAO[:1].isdigit() else versao.VERSAO
        return self.c.text("hdr.selo", x, y if y is not None else 11, f"{self.selo} {ver}", fnt, cor or P["sub"], anchor="rs")

    def fim(self, brilho=(3, 0.75, 120)):
        if brilho:
            self.c.img = bloom(self.c.img, *brilho)
        return self.c, self.v
