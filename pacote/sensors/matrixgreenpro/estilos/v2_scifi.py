# GAMMA v2 SCI-FI "HUD ORBITAL" | versão 0.1.0 | 07/11/2026 20:10 (-03) | criação original (Claude, para Lucas Tavares)
# Visor de nave: quatro mostradores em arco (CPU°, GPU°, RAM, VRAM) nos cantos de um anel central que mostra o
# nível N0/N1/N2, painéis de cantos cortados com abas de título em GeForce e marcas de escala finas.
import math

from .v2_base import Ctx, P, mix, JB, GEFORCE, OK, WARN, CRIT, NA


def _moldura(cx, x0, y0, x1, y1, titulo=None, k=7, cor=None):
    """Painel de cantos cortados (dois cantos opostos) com aba de título sobre a borda."""
    cor = cor or mix(P["accent"], P["bg"], 0.45)
    pts = [(x0 + k, y0), (x1, y0), (x1, y1 - k), (x1 - k, y1), (x0, y1), (x0, y0 + k)]
    cx.c.poly(pts, outline=cor)
    if titulo:
        f = cx.f(GEFORCE, 9, "Bold")
        w = cx.c.width(titulo, f)
        cx.c.rect((x0 + k + 2, y0 - 5, x0 + k + 8 + w, y0 + 4), fill=P["bg"])
        cx.t(f"tab.{titulo}", x0 + k + 5, y0 + 4, titulo, f, P["accent"])


def _arco(cx, nome, x, y, r, pct, lv, valor, rot):
    """Mostrador de 270 graus: trilho, marcas a cada 10%, arco do valor e leitura no centro."""
    d = cx.c.d
    cor = cx.cor_nivel(lv) if lv in (OK, WARN, CRIT) else P["sub"]
    caixa = (x - r, y - r, x + r, y + r)
    d.arc(caixa, 135, 405, fill=mix(P["accent"], P["bg"], 0.85), width=5)
    if pct is not None and (cx.on or lv != CRIT):
        d.arc(caixa, 135, 135 + 270 * pct / 100, fill=cor, width=5)
    for i in range(11):
        a = math.radians(135 + 27 * i)
        r0, r1 = r + 3, r + (7 if i % 5 == 0 else 5)
        d.line((x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a)), fill=P["dim"])
    cx.t(f"{nome}.v", x, y + 6, valor, cx.f(JB, 17, "Bold"), cx.col(lv, P["white"]), anchor="ms")
    cx.t(f"{nome}.r", x, y + r - 2, rot, cx.f(GEFORCE, 9, "Bold"), P["sub"], anchor="ms")


def _num(t):
    try:
        return float("".join(ch for ch in t if ch.isdigit() or ch == "."))
    except ValueError:
        return None


def draw_frame(vm):
    cx = Ctx(vm, "HUD")
    v, c = cx.v, cx.c
    sb, s, xs = cx.f(JB, 11, "Bold"), cx.f(JB, 11, "Regular"), cx.f(JB, 10, "Regular")
    g9 = cx.f(GEFORCE, 9, "Bold")

    # ---- barra superior
    c.poly([(0, 0), (319, 0), (319, 14), (300, 22), (20, 22), (0, 14)], fill=mix(P["accent"], P["bg"], 0.86))
    cx.t("hdr.t", 26, 16, "GAMMA // HUD ORBITAL", cx.f(GEFORCE, 11, "Bold"), P["accent"])
    if cx.demo:
        cx.t("hdr.demo", 170, 16, "SIMULAÇÃO", g9, P["amber"])
    cx.selo_versao(296, 16, cx.f(JB, 9, "Regular"), P["sub"])

    # ---- anel central do estado e os quatro mostradores
    cor = cx.cor_nivel()
    d = c.d
    for r, w in ((40, 1), (34, 3)):
        d.ellipse((160 - r, 118 - r, 160 + r, 118 + r), outline=cor if (cx.on or r == 40) else mix(cor, P["bg"], 0.6), width=w)
    for i in range(24):
        a = math.radians(i * 15)
        d.line((160 + 43 * math.cos(a), 118 + 43 * math.sin(a), 160 + 47 * math.cos(a), 118 + 47 * math.sin(a)),
               fill=cor if i % 6 == 0 else P["dim"])
    cx.t("st.nivel", 160, 126, {OK: "N0", WARN: "N1", CRIT: "N2"}[cx.lvl], cx.f(GEFORCE, 22, "Bold"), cor, anchor="ms")
    cx.t("st.rot", 160, 178, cx.rotulo, g9, cor, anchor="ms")
    t, lv = v("cpu_temp"); _arco(cx, "a.cpu", 52, 74, 30, min(100, _num(t) or 0) if t != "N/D" else None, lv, t.replace("°C", "°"), "CPU")
    t, lv = v("gpu_temp"); _arco(cx, "a.gpu", 268, 74, 30, min(100, _num(t) or 0) if t != "N/D" else None, lv, t.replace("°C", "°"), "GPU")
    rp, rl = cx.ram_pct_txt(); _arco(cx, "a.ram", 52, 160, 30, cx.pct("ram_pct"), rl, rp, "RAM")
    t, lv = v("vram_pct_txt"); _arco(cx, "a.vram", 268, 160, 30, cx.pct("vram_pct"), lv, t, "VRAM")

    # ---- leituras de apoio sob os mostradores
    y = 202
    _, xe = cx.par("cpu.u", 8, y, "USO", "cpu_util", g9, sb)
    cx.par("cpu.f", xe + 8, y, "", "cpu_ghz", g9, s)
    _, xe = cx.par("gpu.u", 312, y, "", "gpu_mhz", g9, s, right=True)
    cx.par("gpu.uu", xe - 8 - (xe - _) - 4, y, "USO", "gpu_util", g9, sb) if False else cx.par("gpu.uu", _ - 8, y, "USO", "gpu_util", g9, sb, right=True)

    # ---- painel da GPU e da memória
    _moldura(cx, 4, 214, 316, 262, "PROPULSÃO GRÁFICA / MEMÓRIA")
    y = 230
    _, xe = cx.par("vram", 12, y, "VRAM", "vram_txt", g9, sb)
    _, xe = cx.par("gpu.w", xe + 10, y, "W", "gpu_w", g9, sb)
    t, _ = v("gpu_wlim"); cx.t("gpu.lim", xe + 3, y, t.replace("LIM ", "/"), xs, P["sub"])
    cx.par("fps", 308, y, "FPS", "fps", g9, sb, right=True)
    y += 14
    t, lv = v("ram_used"); t2, _ = v("ram_total")
    b = cx.t("ram.l", 12, y, "RAM", g9, P["sub"])
    b = cx.t("ram.v", b[2] + 4, y, t + t2, sb, cx.col(lv, P["white"]))
    _, xe = cx.par("ram.d", b[2] + 10, y, "DISP", "ram_avail", g9, sb)
    cx.par("fan", 308, y, "FAN", "gpu_fan_pct", g9, sb, right=True)
    y += 13
    cx.par("load", 12, y, "CARGA", "cpu_load", g9, s)
    cx.par("tram", 308, y, "RAM°", "t_ram", g9, s, right=True)

    # ---- armazenamento
    _moldura(cx, 4, 272, 316, 334 if cx.baias() else 322, "ARMAZENAMENTO")
    y = 288
    for i, dd in enumerate(cx.discos()):
        cx.t(f"d{i}.n", 12, y, dd["name"], sb, P["accent"])
        ub = cx.t(f"d{i}.u", 46, y, dd["use"], s, cx.col(dd.get("use_lvl", NA), P["white"]))
        pb = cx.t(f"d{i}.p", ub[2] + 5, y, f"[{dd['pct_txt']}]", sb, cx.col(dd["lvl"]))
        cx.t(f"d{i}.f", pb[2] + 6, y, dd["free"], xs, cx.col(dd["lvl"]))
        cx.t(f"d{i}.t", 308, y, dd.get("temp_txt", "N/D"), sb, cx.col(dd.get("temp_lvl", NA)), anchor="rs")
        y += 12
    bs = cx.baias()
    if bs:
        x = 12
        for i, bb in enumerate(bs[:4]):
            sv = bb.get("pct_txt") if bb.get("use") else (bb["cap"] or "--")
            nb = cx.t(f"bay{i}.n", x, y, f"B{bb['n']}", g9, P["accent"])
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, sv, xs, cx.col(bb["lvl"]))
            x = vb[2] + 4
            wb = cx.t(f"bay{i}.s", x, y, bb["curta"], cx.f(JB, 8, "Regular"), P["sub"])
            x = wb[2] + 8
    yb = 346 if bs else 334

    # ---- refrigeração e rede
    _moldura(cx, 4, yb, 316, yb + 72, "TÉRMICA / COMUNICAÇÃO")
    y = yb + 16
    x = 12
    for nome, lab, k in (("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("inf", "INF", "fan_sqi"),
                         ("lat", "LAT", "fan_sql"), ("tra", "TRA", "fan_sqt")):
        _, x = cx.par("f." + nome, x, y, lab, k, g9, sb, troca=cx.sem_rpm, gap=3)
        x += 6
    y += 13
    _, xe = cx.par("placa", 12, y, "PLACA", "t_placa", g9, s)
    _, xe = cx.par("ssd", xe + 8, y, "SSD", "t_ssd", g9, s)
    t, _ = v("net_down"); b = cx.t("n.d", xe + 12, y, "↓" + t, sb, P["white"])
    t, _ = v("net_up"); cx.t("n.u", 308, y, "↑" + t, sb, P["white"], anchor="rs")
    y += 13
    from .base import iface_row
    for k, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        iface_row(c, v, k, y, 12, tag, 44, 308, g9, cx.f(JB, 10, "Bold"), xs, xs, cx.col, P["sub"], c_info=P["white"], c_rates=P["white"])
        y += 12
    _, xe = cx.par("rx", 12, y, "RX", "net_rx", g9, xs)
    _, xe = cx.par("tx", xe + 8, y, "TX", "net_tx", g9, xs)
    _, xe = cx.par("png", xe + 10, y, "PING", "ping", g9, sb)
    t, lv = v("inet"); cx.t("inet", 308, y, t, cx.f(JB, 9, "Regular"), cx.col(lv), anchor="rs")

    # ---- rodapé: tempo de missão e ambiente externo
    c.poly([(0, 479), (0, 440), (14, 432), (306, 432), (319, 440), (319, 479)], outline=mix(P["accent"], P["bg"], 0.45))
    t, _ = v("clock"); cx.t("sys.clock", 10, 466, t, cx.f(JB, 24, "Bold"), P["accent"])
    t, _ = v("date"); cx.t("sys.date", 10, 476, t, cx.f(JB, 8, "Regular"), P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 136, 448, "T+ " + t, cx.f(JB, 9, "Regular"), P["sub"])
    t, _ = v("os"); cx.t("sys.os", 136, 476, cx.fit(t, cx.f(JB, 8, "Regular"), 70), cx.f(JB, 8, "Regular"), P["sub"])
    t, lv = v("wtemp"); cx.t("wx.t", 310, 462, t, cx.f(JB, 18, "Bold"), cx.col(lv, P["white"]), anchor="rs")
    cx.t("wx.c", 310, 446, cx.fit(v.raw("city", ""), g9, 90), g9, P["sub"], anchor="rs")
    t, lv = v("wdesc"); cx.t("wx.d", 136, 462, cx.fit(t, xs, 100), xs, P["white"])
    t, lv = v("wage"); cx.t("wx.a", 310, 476, cx.fit(t.replace("OPEN-METEO ", "OM "), cx.f(JB, 8, "Regular"), 90), cx.f(JB, 8, "Regular"), P["sub"], anchor="rs")
    for k in ("coleta", "cpu_pct", "gpu_pct"):
        v.raw(k)
    return cx.fim()
