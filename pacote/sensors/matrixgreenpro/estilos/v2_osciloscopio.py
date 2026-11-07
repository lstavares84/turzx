# GAMMA v2 LABORATÓRIO "OSCILOSCÓPIO" | versão 0.1.0 | 07/11/2026 20:50 (-03) | criação original (Claude, para Lucas Tavares)
# Bancada de laboratório: a metade de cima é a retícula de um osciloscópio (10 x 8 divisões, base de tempo de
# 2,4 h por divisão) com quatro canais das últimas 24 h, cada um com seu marcador de nível à esquerda; embaixo,
# as caixas de medição (atual e máximo de cada canal) e o restante como as teclas e leituras do painel do aparelho.
from .v2_base import Ctx, P, mix, JB, ROBOTO_MONO, OK, WARN, CRIT, NA

GX0, GX1, GY0, GY1 = 6, 314, 26, 206


def _canal(cx, serie, vmin, vmax, cor, tracejado=False, faixa=(GY0, GY1), n_ch=None):
    vals = list(serie or [])
    if not vals:
        return
    n, pts, d = len(vals), [], cx.c.d
    def flush():
        if len(pts) > 1:
            if tracejado:
                for k in range(0, len(pts) - 1, 2):
                    d.line((pts[k], pts[k + 1]), fill=cor, width=1)
            else:
                d.line(pts, fill=cor, width=1)
    for i, x in enumerate(vals):
        if x is None:
            flush(); pts = []
            continue
        t = max(0.0, min(1.0, (x - vmin) / max(1e-9, vmax - vmin)))
        pts.append((GX0 + (GX1 - GX0) * i / max(1, n - 1), faixa[1] - 2 - (faixa[1] - faixa[0] - 4) * t))
    flush()
    if n_ch:                                                    # marcador do canal na borda esquerda
        yb = faixa[1] - 2
        d.polygon([(GX0, yb - 4), (GX0 + 6, yb), (GX0, yb + 4)], fill=cor)


def draw_frame(vm):
    cx = Ctx(vm, "OSCILOSCÓPIO")
    v, c = cx.v, cx.c
    d = c.d
    h = v.raw("hist") or {}
    m9, m9b, m10b = cx.f(ROBOTO_MONO, 9, "Regular"), cx.f(ROBOTO_MONO, 9, "Bold"), cx.f(ROBOTO_MONO, 10, "Bold")
    j9, j10b = cx.f(JB, 9, "Regular"), cx.f(JB, 10, "Bold")
    CH = [("1", "CPU °C", P["accent"]), ("2", "GPU °C", P["white"]), ("3", "RAM %", P["ice"]), ("4", "REDE ↓", P["sub"])]

    # ---- barra superior: canais e estado de aquisição
    x = 6
    for n, nome, cor in CH:
        c.rect((x, 4, x + 11, 15), fill=cor)
        cx.t(f"ch{n}.n", x + 6, 13, n, m9b, P["bg"], anchor="ms")
        b = cx.t(f"ch{n}.l", x + 14, 13, nome, j9, cor)
        x = b[2] + 7
    cor = cx.cor_nivel()
    estado = {OK: "ESTÁVEL", WARN: "DISPARO", CRIT: "SATURADO"}[cx.lvl]
    if cx.on:
        c.rect((246, 3, 314, 16), fill=mix(cor, P["bg"], 0.7), outline=cor)
    cx.t("st.e", 280, 13, estado, m9b, cor if not cx.on else P["white"], anchor="ms")

    # ---- retícula
    c.rect((GX0, GY0, GX1, GY1), fill=mix(P["accent"], P["bg"], 0.96), outline=P["dim"])
    for i in range(1, 10):
        xx = GX0 + (GX1 - GX0) * i / 10
        for yy in range(GY0 + 2, GY1, 4):
            d.point((xx, yy), fill=mix(P["dim"], P["bg"], 0.2 if i != 5 else -0.2 if False else 0.0))
    for j in range(1, 8):
        yy = GY0 + (GY1 - GY0) * j / 8
        for xx in range(GX0 + 2, GX1, 4):
            d.point((xx, yy), fill=P["dim"])
    xm, ym = (GX0 + GX1) / 2, (GY0 + GY1) / 2
    for k in range(0, 50):
        xx = GX0 + (GX1 - GX0) * k / 50
        d.line((xx, ym - 2, xx, ym + 2), fill=P["dim"])
    for k in range(0, 40):
        yy = GY0 + (GY1 - GY0) * k / 40
        d.line((xm - 2, yy, xm + 2, yy), fill=P["dim"])
    topo = max([x for x in (h.get("down") or []) if x is not None] or [1e5])
    fx = lambda k: (GY0 + 14 + (GY1 - GY0 - 14) * k / 4, GY0 + 14 + (GY1 - GY0 - 14) * (k + 1) / 4)   # 4 faixas
    _canal(cx, h.get("cpu_t"), 20, 100, P["accent"], faixa=fx(0), n_ch=1)
    _canal(cx, h.get("gpu_t"), 20, 100, P["white"], faixa=fx(1), n_ch=2)
    _canal(cx, h.get("ram"), 0, 100, P["ice"], tracejado=True, faixa=fx(2), n_ch=3)
    _canal(cx, h.get("down"), 0, topo, P["sub"], faixa=fx(3), n_ch=4)
    cx.t("tb", GX1 - 4, GY1 - 4, "2,4 h/div", j9, P["sub"], anchor="rs")
    cx.t("esc", GX0 + 4, GY0 + 11, "4 canais, 24 h", j9, P["sub"])
    if cx.demo:
        cx.t("demo", xm, GY0 + 11, "SINAL DE TESTE", m9b, P["amber"], anchor="ms")
    cx.selo_versao(GX1 - 4, GY0 + 11, cx.f(JB, 8, "Regular"), P["sub"])

    # ---- caixas de medição
    rp, rl = cx.ram_pct_txt()
    maxi = lambda k, fmt: (fmt(max(x for x in h.get(k) if x is not None)) if any(x is not None for x in (h.get(k) or [])) else "--")
    from ..viewmodel import rate
    med = [(CH[0], v("cpu_temp"), "máx " + maxi("cpu_t_max", lambda x: f"{round(x)}°")),
           (CH[1], v("gpu_temp"), "máx " + maxi("gpu_t_max", lambda x: f"{round(x)}°")),
           (CH[2], (rp, rl), "máx " + maxi("ram_max", lambda x: f"{round(x)}%")),
           (CH[3], v("net_down"), "máx " + maxi("down_max", lambda x: rate(x, short=True)))]
    for i, ((n, nome, cc), (t, lv), mx) in enumerate(med):
        x0 = 6 + i * 78
        c.rect((x0, 212, x0 + 74, 250), outline=cc)
        cx.t(f"m{n}.l", x0 + 4, 223, f"CH{n}", m9b, cc)
        cx.t(f"m{n}.v", x0 + 70, 239, t.replace("°C", "°"), j10b if len(t) < 9 else j9, cx.col(lv, P["white"]) if lv != 9 else P["white"], anchor="rs")
        cx.t(f"m{n}.x", x0 + 70, 248, mx, cx.f(JB, 8, "Regular"), P["sub"], anchor="rs")

    # ---- painel do aparelho
    y = 266
    def linha(itens, y, x=6):
        for nome, lab, k in itens:
            _, x = cx.par(nome, x, y, lab, k, m9, j10b, troca=cx.sem_rpm, gap=3)
            x += 7
        return x
    linha((("cu", "CPU", "cpu_util"), ("cf", "", "cpu_ghz"), ("cl", "CARGA", "cpu_load")), y)
    y += 13
    linha((("gu", "GPU", "gpu_util"), ("gf", "", "gpu_mhz"), ("gw", "W", "gpu_w"), ("gfan", "FAN", "gpu_fan_pct"), ("fps", "FPS", "fps")), y)
    y += 13
    x = linha((("vram", "VRAM", "vram_txt"), ("vp", "", "vram_pct_txt")), y)
    t, _ = v("gpu_wlim"); cx.t("wlim", 314, y, t, j9, P["sub"], anchor="rs")
    y += 13
    t, lv = v("ram_used"); t2, _ = v("ram_total")
    b = cx.t("ram.l", 6, y, "RAM", m9, P["sub"])
    b = cx.t("ram.v", b[2] + 3, y, t + t2, j10b, cx.col(lv, P["white"]))
    linha((("rd", "DISP", "ram_avail"), ("rt", "TEMP", "t_ram")), y, b[2] + 8)
    y += 15
    for i, dd in enumerate(cx.discos()):
        cx.t(f"d{i}.n", 6, y, dd["name"], j10b, P["accent"])
        ub = cx.t(f"d{i}.u", 38, y, dd["use"], j9, cx.col(dd.get("use_lvl", NA), P["white"]))
        pb = cx.t(f"d{i}.p", ub[2] + 5, y, dd["pct_txt"], j10b, cx.col(dd["lvl"], P["white"]))
        cx.t(f"d{i}.f", pb[2] + 6, y, dd["free"], j9, cx.col(dd["lvl"], P["sub"]))
        cx.t(f"d{i}.t", 314, y, dd.get("temp_txt", "N/D"), j10b, cx.col(dd.get("temp_lvl", NA), P["white"]), anchor="rs")
        y += 12
    bs = cx.baias()
    if bs:
        x = 6
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"B{bb['n']}", m9b, P["sub"])
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, f"{s} {bb['curta']}".strip(), j9, cx.col(bb["lvl"], P["white"]))
            x = vb[2] + 9
        y += 12
    y += 3
    linha((("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("inf", "INF", "fan_sqi"), ("lat", "LAT", "fan_sql"), ("tra", "TRA", "fan_sqt")), y)
    y += 13
    linha((("placa", "PLACA", "t_placa"), ("ssd", "SSD", "t_ssd"), ("png", "PING", "ping")), y)
    t, lv = v("inet"); cx.t("inet", 314, y, t.replace("INTERNET ", "NET "), j9, cx.col(lv), anchor="rs")
    y += 13
    t, _ = v("net_up"); b = cx.t("n.u", 6, y, "↑" + t, j10b, P["white"])
    _, xe = cx.par("tx", 314, y, "TX", "net_tx", m9, j9, right=True)
    cx.par("rx", _ - 8, y, "RX", "net_rx", m9, j9, right=True)
    y += 13
    from .base import iface_row
    for k, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        iface_row(c, v, k, y, 6, tag, 36, 314, m9b, j10b, j9, j9, cx.col, P["sub"], c_info=P["white"], c_rates=P["white"])
        y += 12

    # ---- rodapé
    c.line((0, 452, 319, 452), P["dim"])
    t, _ = v("clock"); cx.t("sys.clock", 6, 468, t, cx.f(JB, 14, "Bold"), P["accent"])
    t, _ = v("date"); cx.t("sys.date", 6, 478, t, cx.f(JB, 8, "Regular"), P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 100, 464, "LIGADO " + t, j9, P["sub"])
    t, _ = v("os"); cx.t("sys.os", 100, 476, cx.fit(t, j9, 90), j9, P["sub"])
    t, lv = v("wtemp"); tw = cx.t("wx.t", 314, 465, t, j10b, cx.col(lv, P["white"]), anchor="rs")
    cx.t("wx.c", tw[0] - 5, 465, cx.fit(v.raw("city", ""), j9, 60), j9, P["sub"], anchor="rs")
    t, lv = v("wdesc"); wd = cx.t("wx.d", 314, 477, cx.fit(t, j9, 54), j9, P["white"], anchor="rs")
    t, lv = v("wage"); cx.t("wx.a", wd[0] - 5, 477, cx.fit(t.replace("OPEN-METEO ", ""), j9, 30), j9, P["sub"], anchor="rs")
    for k in ("coleta", "cpu_pct", "gpu_pct", "vram_pct"):
        v.raw(k)
    return cx.fim((2, 0.7, 120))
