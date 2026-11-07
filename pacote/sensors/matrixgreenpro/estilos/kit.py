# MATRIX GREEN PRO | estilos alternativos | versão 3.0.0-alfa2 | 01/11/2026 00:45 (-03) | criação
# Esqueleto vertical reutilizável: posiciona TODAS as métricas em faixas fixas e
# delega ao estilo a moldura das seções, as barras, as fontes e as cores. Estilos
# com layout próprio (reator, F1, zen, papel, HMI, vidro) não usam este esqueleto.
from .base import NA, NEUTRAL, OK, worst, iface_row

DEFAULT_Y = {
    "cpu": (36, 92), "gpu": (95, 178), "ram": (181, 212), "dsk": (215, 289),
    "net": (292, 360), "sys": (363, 402), "wx": (405, 441), "pwr": (444, 479),
}


class Style:
    """Parâmetros do esqueleto. Os estilos sobrescrevem só o que precisam."""
    x0, x1 = 10, 310          # área útil dentro das molduras
    xv = 48                   # coluna de valores
    Y = DEFAULT_Y
    tag_in_row = True         # rótulo da seção na 1ª linha (False = a moldura desenha)
    upper = True              # rótulos auxiliares em maiúsculas

    def __init__(self, fonts, colors, col):
        self.f = fonts        # xl, m, sb, s, xs, tag
        self.k = colors       # tag, sub, val, dim, track, bar
        self.col = col

    def section(self, c, name, y0, y1, label, level):
        pass

    def bar(self, c, x, y, w, h, pct, color):
        c.hbar(x, y, w, h, pct, color, self.k["track"])

    def lab(self, s):
        return s.upper() if self.upper else s


def std_layout(c, v, S):
    f, k, col = S.f, S.k, S.col
    hl = v.raw("health", {})
    X0, X1, XV = S.x0, S.x1, S.xv

    def pair(name, x, y, lab, val, fv, lv, right=False, fl=None):
        fl = fl or f["xs"]
        wl = c.width(lab, fl) + 4
        wv = c.width(val, fv)
        if right:
            x = x - wl - wv
        c.text(name + ".lab", x, y, lab, fl, k["sub"])
        c.text(name + ".val", x + wl, y, val, fv, col(lv))
        return x, x + wl + wv

    def barcol(lv):
        return col(lv) if lv not in (NA, NEUTRAL) else k["bar"]

    # ---------- CPU
    y0, y1 = S.Y["cpu"]
    S.section(c, "cpu", y0, y1, "CPU", worst([hl.get("cpu_temp", NA), hl.get("cpu_fan", NA)]))
    y = y0 + 23
    if S.tag_in_row:
        c.text("cpu.tag", X0, y, S.lab("CPU"), f["tag"], k["tag"])
    t, lv = v("cpu_util"); c.text("cpu.util", XV, y, t, f["xl"], col(lv))
    t, lv = v("cpu_ghz"); c.text("cpu.ghz", XV + 70, y, t, f["m"], col(lv))
    t, lv = v("cpu_temp"); c.text("cpu.temp", X1, y, t, f["xl"], col(lv), anchor="rs")
    S.bar(c, X0, y + 5, X1 - X0, 5, v.raw("cpu_pct"), k["bar"])
    y += 24
    t, lv = v("cpu_fan"); pair("cpu.fan", X0, y, S.lab("FAN"), t, f["sb"], lv)
    t, lv = v("cpu_load"); pair("cpu.load", X1, y, S.lab("LOAD"), t, f["s"], lv, right=True)

    # ---------- GPU
    y0, y1 = S.Y["gpu"]
    S.section(c, "gpu", y0, y1, "GPU", worst([hl.get(x, NA) for x in ("gpu", "gpu_temp", "vram", "gpu_fan")]))
    y = y0 + 23
    if S.tag_in_row:
        c.text("gpu.tag", X0, y, S.lab("GPU"), f["tag"], k["tag"])
    t, lv = v("gpu_util"); c.text("gpu.util", XV, y, t, f["xl"], col(lv))
    t, lv = v("gpu_mhz"); c.text("gpu.mhz", XV + 70, y, t, f["m"], col(lv))
    t, lv = v("gpu_temp"); c.text("gpu.temp", X1, y, t, f["xl"], col(lv), anchor="rs")
    S.bar(c, X0, y + 5, X1 - X0, 5, v.raw("gpu_pct"), k["bar"])
    y += 23
    t, lv = v("vram_txt"); pair("gpu.vram", X0, y, S.lab("VRAM"), t, f["sb"], lv)
    p, lvp = v("vram_pct_txt"); c.text("gpu.vrampct", X1, y, p, f["sb"], col(lvp), anchor="rs")
    S.bar(c, 172, y - 7, X1 - 172 - 36, 5, v.raw("vram_pct"), barcol(lvp))
    y += 16
    t, lv = v("gpu_fan_pct"); _, xe = pair("gpu.fan", X0, y, S.lab("FAN"), t, f["sb"], lv)
    b = c.text("gpu.fansep", xe + 5, y, "|", f["s"], k["dim"])
    t, lv = v("gpu_fan_rpm"); c.text("gpu.fanrpm", b[2] + 5, y, t, f["sb"] if lv != NA else f["s"], col(lv))
    t, lv = v("fps"); pair("gpu.fps", X1, y, "FPS", t, f["m"], lv, right=True)
    y += 16
    t, lv = v("gpu_w"); pair("gpu.w", X0, y, S.lab("GPU W"), t, f["sb"], lv)
    t, lv = v("gpu_wlim"); c.text("gpu.wlim", X1, y, t, f["xs"], k["dim"], anchor="rs")

    # ---------- RAM
    y0, y1 = S.Y["ram"]
    rl = v("ram_used")[1]
    S.section(c, "ram", y0, y1, "RAM", hl.get("ram", NA))
    y = y0 + 19
    if S.tag_in_row:
        c.text("ram.tag", X0, y, S.lab("RAM"), f["tag"], k["tag"])
    t, lv = v("ram_used"); b = c.text("ram.used", XV, y, t, f["m"], col(lv))
    t, _ = v("ram_total"); c.text("ram.total", b[2] + 1, y, t, f["m"], k["val"])
    t, lv = v("ram_avail"); pair("ram.avail", X1, y, S.lab("DISP"), t, f["sb"], lv, right=True)
    S.bar(c, X0, y + 5, X1 - X0, 4, v.raw("ram_pct"), barcol(rl))

    # ---------- discos
    y0, y1 = S.Y["dsk"]
    disks = v.raw("disks", [])
    S.section(c, "dsk", y0, y1, "DISCOS", worst([d["lvl"] for d in disks]))
    for i, dk in enumerate(disks[:3]):
        y = y0 + 19 + i * 23
        c.text(f"dsk{i}.name", X0, y, dk["name"], f["sb"], k["tag"])
        c.text(f"dsk{i}.use", XV, y, dk["use"], f["s"], col(dk.get("use_lvl", NEUTRAL)))
        c.text(f"dsk{i}.pct", 200, y, dk["pct_txt"], f["sb"], col(dk["lvl"]), anchor="rs")
        b = c.text(f"dsk{i}.freelab", X1, y, S.lab("livre"), f["xs"], k["sub"], anchor="rs")
        c.text(f"dsk{i}.free", b[0] - 4, y, dk["free"], f["sb"], col(dk["lvl"]), anchor="rs")
        S.bar(c, XV, y + 4, X1 - XV, 3, dk.get("pct"), barcol(dk["lvl"]))

    # ---------- rede
    y0, y1 = S.Y["net"]
    S.section(c, "net", y0, y1, "REDE", hl.get("conexao", NA))
    y = y0 + 19
    t, lv = v("net_down"); c.text("net.down", X0, y, "↓" + t, f["m"], col(lv))
    t, lv = v("net_up"); c.text("net.up", 165, y, "↑" + t, f["m"], col(lv))
    y += 15
    t, lv = v("net_rx"); pair("net.rx", X0, y, "RX", t, f["s"], lv)
    t, lv = v("net_tx"); pair("net.tx", 165, y, "TX", t, f["s"], lv)
    c.text("net.period", X1, y, S.lab("boot"), f["xs"], k["dim"], anchor="rs")
    for key, tag, dy in (("eth", "ETH", 15), ("wifi", "WIFI", 30)):
        iface_row(c, v, key, y + dy, X0, S.lab(tag), XV, X1, f["xs"], f["sb"], f["xs"], f["xs"],
                  col, k["sub"], c_info=k["val"], c_rates=k["val"])

    # ---------- sistema
    y0, y1 = S.Y["sys"]
    S.section(c, "sys", y0, y1, "SISTEMA", NA)
    y = y0 + 26
    t, lv = v("clock"); c.text("sys.clock", X0, y, t, f["xl"], col(lv))
    t, lv = v("date"); c.text("sys.date", X1, y - 10, t, f["sb"], col(lv), anchor="rs")
    t, lv = v("uptime"); pair("sys.up", X1, y + 4, "UP", t, f["s"], lv, right=True)
    t, _ = v("os"); c.text("sys.os", X0, y + 12, t, f["xs"], k["dim"])

    # ---------- ping, internet, clima
    y0, y1 = S.Y["wx"]
    S.section(c, "wx", y0, y1, "LINK", hl.get("ping", NA))
    y = y0 + 17
    t, lv = v("ping"); _, xe = pair("png", X0, y, S.lab("PING"), t, f["m"], lv)
    t, lv = v("inet"); c.text("inet", xe + 6, y, t, f["xs"], col(lv))
    t, lv = v("wtemp"); b = c.text("wx.temp", X1, y, t, f["m"], col(lv), anchor="rs")
    c.text("wx.city", b[0] - 5, y, v.raw("city", ""), f["xs"], k["sub"], anchor="rs")
    y += 14
    t, lv = v("wdesc"); c.text("wx.desc", X0, y, t, f["xs"], col(lv) if lv != NA else k["dim"])
    t, lv = v("wage"); c.text("wx.age", X1, y, t, f["xs"], col(lv) if lv != NA else k["dim"], anchor="rs")

    # ---------- energia total e coleta
    y0, y1 = S.Y["pwr"]
    S.section(c, "pwr", y0, y1, "ENERGIA", hl.get("energia", NA))
    y = y0 + (y1 - y0) // 2 + 5
    t, lv = v("power"); _, xe = pair("pwr", X0, y, S.lab("TOTAL W"), t, f["m"], lv)
    t, lv = v("power_tag"); tb = c.text("pwr.tag", xe + 6, y, t, f["xs"], k["dim"])
    t, lv = v("coleta"); c.text("coleta", X1, y, c.fit(t, f["xs"], X1 - tb[2] - 8), f["xs"], col(lv), anchor="rs")
