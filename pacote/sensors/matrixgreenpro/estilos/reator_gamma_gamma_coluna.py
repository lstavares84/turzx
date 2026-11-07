# GAMMA GAMMA COLUNA | versão 1.0.0 | 07/11/2026 18:40 (-03) | criação original (Claude, para Lucas Tavares)
# Quarta variante de estudo do GAMMA GAMMA (depois de COLMEIA, MINI e PAINEL). Não entra nos ZIPs.
# Ideia: os 7 hexágonos de resumo viram uma coluna vertebral à esquerda. CORE é a vértebra do topo, ao lado da
# escala N0/N1/N2; cada grupo tem a sua vértebra (nome e OK, ATEN ou CRIT) encostada nos próprios números.
# Quando um grupo sai do verde, a faixa inteira do grupo ganha um fundo âmbar ou vermelho (o crítico pisca).
# O TERRAMASTER é informativo: vértebra pequena e vazia, sem estado. Relógio no alto à direita; clima no rodapé.
import math

from .base import W, OK, WARN, CRIT, NA, LOST, NEUTRAL, bloom, iface_row
from .alerta import mix, _escala, counts, label
from .reator import hexagon
from .reator_gamma import GAMMA
from .reator_grupos import _base, _cell, _pair, _paren, _resumos

P = dict(GAMMA, selo="COLUNA", alert="nenhum", pct="paren", flow=True, cool=True, temps=True)

R = 21                      # raio das vértebras (largura 36,4 px: cabe "DISCOS" com folga)
XC = 22                     # eixo da coluna
X0 = 46                     # início do texto
STEP = 14                   # altura de linha
MIN_H = 2 * R + 4           # altura mínima de uma faixa (a vértebra não encosta na vizinha)


def _faixa(c, P, lv, on, y0, y1):
    """Fundo da faixa do grupo quando ele não está OK. O crítico alterna entre forte e fraco."""
    if lv not in (WARN, CRIT, LOST):
        return
    cor = P["red"] if lv == CRIT else P["amber"]
    forte = lv == CRIT and on
    c.rect((X0 - 6, y0 + 1, 317, y1 - 1), fill=mix(cor, P["bg"], 0.78 if forte else 0.88))
    c.rect((X0 - 6, y0 + 1, X0 - 5, y1 - 1), fill=cor if (on or lv != CRIT) else mix(cor, P["bg"], 0.5))


def draw_frame(vm_dict):
    v, c, col, F, vals = _base(vm_dict, P)
    vals.update(_resumos(v, vals))
    v.raw("cpu_pct"); v.raw("gpu_pct"); v.raw("vram_pct"); v.raw("gpu_fan_rpm"); v.raw("t_ssd")
    for k in ("power", "power_tag", "coleta"):                  # fora da tela, como no GAMMA GAMMA
        v.raw(k)
    blink = vm_dict.get("blink")
    if blink is None:
        import time
        blink = int(time.time()) % 2 == 0

    # ---- topo: CORE (cabeça da coluna), escala N0/N1/N2 ao lado, data e relógio à direita
    st, slv = v("hdr_status")
    lvl = slv if slv in (OK, WARN, CRIT) else OK
    ncrit, nwarn = counts(v)
    on = blink or lvl != CRIT
    core_y = 47
    _escala(c, P, X0 - 4, 28, 92, lvl, on, ncrit, nwarn, label(st, ncrit, nwarn, lvl), F["hv"], limpo=True)
    t, _ = v("date"); c.text("sys.date", 314, 39, t, F["sb"], P["white"], anchor="rs")
    t, _ = v("clock"); c.text("sys.clock", 314, 63, t, F["xl"], P["accent"], anchor="rs")

    def linha(y, itens, x=X0, folga=10, fv=None):
        for nome, lab, chave in itens:
            t, lv = v(chave)
            _, x = _pair(c, P, col, nome, x, y, lab, t.replace("RPM", ""), fv or F["sb"], lv, F)
            x += folga
        return x

    def direita(nome, lab, chave, y, x=314, fv=None):
        t, lv = v(chave)
        return _pair(c, P, col, nome, x, y, lab, t.replace("RPM", ""), fv or F["sb"], lv, F, right=True)[0]

    # ---- cada grupo: (chave do resumo ou None, nº de linhas, função que desenha as linhas a partir da 1ª base)
    def g_cpu(y):
        linha(y, (("cpu.util", "USO", "cpu_util"), ("cpu.temp", "TEMP", "cpu_temp"), ("cpu.ghz", "FREQ", "cpu_ghz")))
        linha(y + STEP, (("cpu.load", "LOAD", "cpu_load"),))

    def g_gpu(y):
        linha(y, (("gpu.util", "USO", "gpu_util"), ("gpu.temp", "TEMP", "gpu_temp"), ("gpu.mhz", "FREQ", "gpu_mhz")))
        y += STEP
        t, lv = v("vram_txt"); _, xe = _pair(c, P, col, "gpu.vram", X0, y, "VRAM", t, F["sb"], lv, F)
        pt, pl = vals["vram"][1]; c.text("gpu.vrampct", xe + 5, y, _paren(pt), F["sb"], col(pl))
        direita("gpu.fps", "FPS", "fps", y)
        y += STEP
        t, lv = v("gpu_w"); _, xe = _pair(c, P, col, "gpu.w", X0, y, "W", t, F["sb"], lv, F)
        t, _ = v("gpu_wlim"); c.text("gpu.wlim", xe + 6, y, t, F["xs"], P["sub"])
        direita("gpu.fan", "FAN", "gpu_fan_pct", y)

    def g_ram(y):
        t, lv = v("ram_used"); _, xe = _pair(c, P, col, "ram.used", X0, y, "USO", t, F["sb"], lv, F)
        t2, _ = v("ram_total"); rb = c.text("ram.total", xe + 1, y, t2, F["sb"], P["white"])
        pt, pl = vals["ram"][1]; c.text("ram.pct", rb[2] + 6, y, _paren(pt), F["sb"], col(pl))
        direita("ram.temp", "TEMP", "t_ram", y)
        linha(y + STEP, (("ram.avail", "DISP", "ram_avail"),))

    def g_dsk(y):
        for i, d in enumerate(v.raw("disks", [])[:3]):
            yy = y + i * STEP
            nb = c.text(f"dsk{i}.name", X0, yy, d["name"], F["sb"], P["white"])
            ub = c.text(f"dsk{i}.use", max(nb[2] + 5, X0 + 26), yy, d["use"], F["s"], col(d.get("use_lvl", NEUTRAL)))
            pbx = c.text(f"dsk{i}.pct", ub[2] + 5, yy, _paren(d["pct_txt"]), F["sb"], col(d["lvl"]))
            fb = c.text(f"dsk{i}.free", pbx[2] + 8, yy, d["free"], F["sb"], col(d["lvl"]))
            tb = c.text(f"dsk{i}.temp", 314, yy, d.get("temp_txt", "N/D"), F["sb"], col(d.get("temp_lvl", NA)), anchor="rs")
            c.text(f"dsk{i}.freelab", fb[2] + 3, yy, c.fit("LIVRE", F["xs"], tb[0] - fb[2] - 8), F["xs"], P["sub"])

    def g_bay(y):
        for i, b in enumerate(v.raw("baias", [])[:4]):
            x = X0 if i % 2 == 0 else 184
            yy = y + (i // 2) * STEP
            bx = c.text(f"bay{i}.n", x, yy, f"{b['n']}", F["sb"], P["accent"])
            if b["cap"]:
                bx = c.text(f"bay{i}.cap", bx[2] + 5, yy, b["cap"], F["sb"], col(b["lvl"]))
            c.text(f"bay{i}.st", bx[2] + 5, yy, b["palavra"], F["xs"], col(b["lvl"]))

    def g_ref(y):
        linha(y, (("fan.pump", "BOMBA", "pump"), ("fan.rad", "RAD", "cpu_fan"), ("fan.placa", "PLACA", "t_placa")))
        linha(y + STEP, (("fan.sqi", "SQUAMA INF", "fan_sqi"), ("fan.sql", "LAT", "fan_sql"), ("fan.sqt", "TRA", "fan_sqt")))

    def g_rede(y):
        t, _ = v("net_down"); b = c.text("net.down", X0, y, "↓" + t, F["sb"], P["white"])
        t, _ = v("net_up"); c.text("net.up", b[2] + 8, y, "↑" + t, F["sb"], P["white"])
        direita("png", "PING", "ping", y)
        y += STEP
        t, lv = v("net_rx"); _, xe = _pair(c, P, col, "net.rx", X0, y, "RX", t, F["s"], lv, F)
        t, lv = v("net_tx"); _pair(c, P, col, "net.tx", xe + 10, y, "TX", t, F["s"], lv, F)
        t, lv = v("inet"); c.text("inet", 314, y, t, F["xs"], col(lv), anchor="rs")
        for key, tag in (("eth", "ETH"), ("wifi", "WIFI")):
            y += STEP
            iface_row(c, v, key, y, X0, tag, X0 + 34, 314, F["xs"], F["sb"], F["xs"], F["xs"], col, P["sub"],
                      c_info=P["white"], c_rates=P["white"])

    grupos = [("g_cpu", 2, g_cpu), ("g_gpu", 3, g_gpu), ("g_ram", 2, g_ram), ("g_dsk", 3, g_dsk)]
    if v.raw("baias", []):
        grupos.append((None, 2, g_bay))
    grupos += [("g_ref", 2, g_ref), ("g_rede", 4, g_rede)]

    # ---- faixas: calcula as alturas, pinta os fundos, depois a espinha, as vértebras e o texto
    y, faixas = 70, []
    for chave, n, fn in grupos:
        h = max(MIN_H, n * STEP + 10)
        faixas.append((chave, y, y + h, n, fn))
        y += h
    for chave, y0, y1, _, _ in faixas:
        if chave:
            _faixa(c, P, vals[chave][1][1], on, y0, y1)
    meio = lambda y0, y1: (y0 + y1) / 2
    c.line((XC, core_y, XC, meio(*faixas[-1][1:3])), P["dim"], 2)
    for i, (chave, y0, y1, n, fn) in enumerate(faixas):
        if i:
            c.line((X0, y0, 314, y0), mix(P["dim"], P["bg"], 0.35))
        cy = meio(y0, y1)
        if chave:
            _cell(c, P, col, vals, chave, XC, cy, R, F["hs"], F["hv"])
        else:                                                   # informativo: vértebra vazia, sem estado
            c.poly(hexagon(XC, cy, 8), fill=P["bg"], outline=P["sub"])
        fn(cy - (n - 1) * STEP / 2 + 4)
    _cell(c, P, col, vals, "core", XC, core_y, R, F["hs"], F["hv"])

    # ---- rodapé: sistema à esquerda, clima à direita
    yr = 431
    c.line((X0, faixas[-1][2], 314, faixas[-1][2]), mix(P["dim"], P["bg"], 0.35))
    t, lv = v("uptime"); _pair(c, P, col, "sys.up", 6, yr + 14, "UP", t, F["sb"], lv, F)
    t, _ = v("os"); c.text("sys.os", 6, yr + 30, c.fit(t, F["xs"], 180), F["xs"], P["sub"])
    t, lv = v("wage"); c.text("wx.age", 6, yr + 45, c.fit(t, F["xs"], 180), F["xs"], col(lv) if lv != NA else P["sub"])
    t, lv = v("wtemp"); tb = c.text("wx.temp", 314, yr + 26, t, F["xl"], col(lv), anchor="rs")
    c.text("wx.city", 314, yr + 9, c.fit(v.raw("city", ""), F["xs"], 120), F["xs"], P["sub"], anchor="rs")
    t, lv = v("wdesc"); c.text("wx.desc", 314, yr + 42, c.fit(t, F["xs"], 120), F["xs"],
                               col(lv) if lv != NA else P["sub"], anchor="rs")
    if P.get("bloom"):
        c.img = bloom(c.img, *P["bloom"])
    return c, v
