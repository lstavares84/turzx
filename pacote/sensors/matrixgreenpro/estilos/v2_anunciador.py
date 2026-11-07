# GAMMA v2 SALA DE CONTROLE "ANUNCIADOR" | versão 0.1.0 | 07/11/2026 20:40 (-03) | criação original (Claude, para Lucas Tavares)
# Mesa de operação de usina: no alto, o painel anunciador de 16 janelas, escuras quando está tudo normal e acesas
# em âmbar ou vermelho (piscando) quando um alarme dispara; no meio, três medidores analógicos de ponteiro e
# mostradores de sete segmentos; embaixo, o registro dos equipamentos em letras pequenas.
import math

from .v2_base import Ctx, P, mix, JB, ROBOTO, DIGITAL, OK, WARN, CRIT, NA, LOST


def _janela(cx, nome, x0, y0, x1, y1, legenda, lv):
    c = cx.c
    lit = lv in (WARN, CRIT, LOST) and (cx.on or lv != CRIT)
    cor = P["red"] if lv == CRIT else P["amber"]
    if lit:
        c.rect((x0, y0, x1, y1), fill=cor)
        tinta = P["bg"]
    else:
        c.rect((x0, y0, x1, y1), fill=mix(P["accent"], P["bg"], 0.93), outline=mix(P["accent"], P["bg"], 0.8))
        tinta = mix(P["sub"], P["bg"], 0.25 if lv != NA else 0.6)
    f = cx.f(ROBOTO, 9, "Bold")
    partes = legenda.split("\n")
    for k, s in enumerate(partes):
        cx.t(f"{nome}.{k}", (x0 + x1) / 2, (y0 + y1) / 2 + 4 + (k - (len(partes) - 1) / 2) * 10, s, f, tinta, anchor="ms")


def _medidor(cx, nome, x, y, r, val, vmax, lv, rot, txt):
    """Medidor analógico: escala de 240°, marcas, faixa de alarme no fim, ponteiro e placa com o nome."""
    d = cx.c.d
    d.ellipse((x - r - 4, y - r - 4, x + r + 4, y + r + 4), outline=P["dim"], width=2)
    a0, a1 = 150, 390
    d.arc((x - r, y - r, x + r, y + r), a1 - 48, a1 - 20, fill=mix(P["amber"], P["bg"], 0.3), width=3)
    d.arc((x - r, y - r, x + r, y + r), a1 - 20, a1, fill=mix(P["red"], P["bg"], 0.3), width=3)
    for i in range(11):
        a = math.radians(a0 + (a1 - a0) * i / 10)
        r0 = r - (6 if i % 5 == 0 else 3)
        d.line((x + r0 * math.cos(a), y + r0 * math.sin(a), x + r * math.cos(a), y + r * math.sin(a)), fill=P["sub"])
    if val is not None:
        a = math.radians(a0 + (a1 - a0) * max(0, min(1, val / vmax)))
        cor = cx.cor_nivel(lv) if lv in (WARN, CRIT) else P["white"]
        d.line((x, y, x + (r - 4) * math.cos(a), y + (r - 4) * math.sin(a)), fill=cor, width=2)
    d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=P["sub"])
    cx.t(f"{nome}.r", x, y + 13, rot, cx.f(ROBOTO, 8, "Bold"), P["sub"], anchor="ms")
    cx.t(f"{nome}.v", x, y + r + 16, txt, cx.f(JB, 11, "Bold"), cx.col(lv, P["white"]), anchor="ms")


def _num(t):
    try:
        return float("".join(ch for ch in t if ch.isdigit() or ch == ".") or "x")
    except ValueError:
        return None


def _segmentos(cx, nome, x, y, txt, rot, lv, w=70):
    """Mostrador de sete segmentos (DIGITAL-7): só algarismos; a unidade fica na plaqueta."""
    c = cx.c
    c.rect((x, y, x + w, y + 24), fill=mix(P["bg"], (0, 0, 0), 0.5), outline=P["dim"])
    dig = "".join(ch for ch in txt if ch.isdigit() or ch in ".:") or "--"
    cx.t(f"{nome}.v", x + w - 4, y + 20, dig, cx.f(DIGITAL, 22), cx.col(lv, P["accent"]), anchor="rs")
    cx.t(f"{nome}.r", x + 2, y + 34, rot, cx.f(ROBOTO, 8, "Bold"), P["sub"])


def draw_frame(vm):
    cx = Ctx(vm, "ANUNCIADOR")
    v, c = cx.v, cx.c
    r8b, r9b = cx.f(ROBOTO, 8, "Bold"), cx.f(ROBOTO, 9, "Bold")
    j9, j10b = cx.f(JB, 9, "Regular"), cx.f(JB, 10, "Bold")

    # ---- cabeçalho
    cor = cx.cor_nivel()
    cx.t("hdr.t", 6, 14, "PAINEL DE ALARMES  UNIDADE GAMMA", r9b, P["accent"])
    cx.t("hdr.n", 314, 14, f"{({OK: 'N0', WARN: 'N1', CRIT: 'N2'}[cx.lvl])} {cx.rotulo}", r9b, cor if cx.on else mix(cor, P["bg"], 0.5), anchor="rs")
    xo = 6
    if cx.demo:
        xo = cx.t("demo", 6, 25, "MODO TREINAMENTO", r8b, P["amber"])[2] + 8
    t, _ = v("os"); cx.t("sys.os", xo, 25, cx.fit(t, cx.f(JB, 8, "Regular"), 120), cx.f(JB, 8, "Regular"), P["sub"])
    cx.selo_versao(314, 25, cx.f(JB, 8, "Regular"), mix(P["sub"], P["bg"], 0.2))

    # ---- anunciador 4 x 4
    h = v.raw("health", {}) or {}
    ds = cx.discos()
    lvd = lambda i: ds[i]["lvl"] if i < len(ds) else NA
    tdisc = [dd.get("temp_lvl", NA) for dd in ds]
    pior_t = CRIT if CRIT in tdisc else WARN if WARN in tdisc else OK if OK in tdisc else NA
    janelas = [("CPU\nTEMP", v("cpu_temp")[1]), ("GPU\nTEMP", v("gpu_temp")[1]), ("VRAM\nCHEIA", v("vram_pct_txt")[1]),
               ("RAM\nCHEIA", cx.ram_pct_txt()[1]), ("DISCO 1\nESPAÇO", lvd(0)), ("DISCO 2\nESPAÇO", lvd(1)),
               ("DISCO 3\nESPAÇO", lvd(2)), ("DISCOS\nTEMP", pior_t), ("BOMBA\nPARADA", v("pump")[1]),
               ("RADIADOR\nFAN", v("cpu_fan")[1]), ("GPU\nFAN", v("gpu_fan_pct")[1]), ("RAM\nTEMP", v("t_ram")[1]),
               ("SSD\nTEMP", v("t_ssd")[1]), ("REDE\nLOCAL", h.get("conexao", OK)), ("PING\nALTO", v("ping")[1]),
               ("SEM\nINTERNET", v("inet")[1])]
    for i, (leg, lv) in enumerate(janelas):
        x0, y0 = 4 + (i % 4) * 78, 32 + (i // 4) * 28
        _janela(cx, f"an{i}", x0, y0, x0 + 75, y0 + 25, leg, lv)

    # ---- medidores analógicos
    y = 186
    t, lv = v("cpu_temp"); _medidor(cx, "m.cpu", 56, y, 34, _num(t), 100, lv, "CPU °C", t)
    t, lv = v("gpu_temp"); _medidor(cx, "m.gpu", 160, y, 34, _num(t), 100, lv, "GPU °C", t)
    rp, rl = cx.ram_pct_txt(); _medidor(cx, "m.ram", 264, y, 34, cx.pct("ram_pct"), 100, rl, "RAM %", rp)

    # ---- mostradores digitais
    y = 248
    t, lv = v("cpu_util"); _segmentos(cx, "s.cpu", 4, y, t, "CPU USO %", lv, 58)
    t, lv = v("gpu_util"); _segmentos(cx, "s.gpu", 66, y, t, "GPU USO %", lv, 58)
    t, lv = v("vram_pct_txt"); _segmentos(cx, "s.vram", 128, y, t, "VRAM %", lv, 58)
    t, lv = v("gpu_w"); _segmentos(cx, "s.w", 190, y, t, "GPU W", lv, 58)
    t, lv = v("fps"); _segmentos(cx, "s.fps", 252, y, t, "FPS", lv, 64)

    # ---- registro dos equipamentos
    y = 300
    def linha(itens, y, x=4):
        for nome, lab, k in itens:
            _, x = cx.par(nome, x, y, lab, k, r8b, j10b, troca=cx.sem_rpm, gap=3)
            x += 7
        return x
    linha((("ghz", "CPU", "cpu_ghz"), ("mhz", "GPU", "gpu_mhz"), ("load", "CARGA", "cpu_load")), y)
    t, _ = v("gpu_wlim"); cx.t("wlim", 314, y, t, j9, P["sub"], anchor="rs")
    y += 12
    x = linha((("vram", "VRAM", "vram_txt"), ("fan", "FAN", "gpu_fan_pct")), y)
    t, lv = v("ram_used"); t2, _ = v("ram_total")
    b = cx.t("ram.l", x, y, "RAM", r8b, P["sub"])
    b = cx.t("ram.v", b[2] + 3, y, t + t2, j10b, cx.col(lv, P["white"]))
    cx.par("ram.d", 314, y, "DISP", "ram_avail", r8b, j10b, right=True)
    y += 12
    linha((("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("inf", "INF", "fan_sqi"), ("lat", "LAT", "fan_sql"), ("tra", "TRA", "fan_sqt")), y)
    y += 12
    x = linha((("placa", "PLACA", "t_placa"), ("tram", "RAM", "t_ram"), ("tssd", "SSD", "t_ssd"), ("png", "PING", "ping")), y)
    t, lv = v("inet"); cx.t("inet", 314, y, t.replace("INTERNET ", "NET "), j9, cx.col(lv), anchor="rs")
    y += 14
    for i, dd in enumerate(ds):
        cx.t(f"d{i}.n", 4, y, dd["name"], j10b, P["accent"])
        ub = cx.t(f"d{i}.u", 36, y, dd["use"], j9, cx.col(dd.get("use_lvl", NA), P["white"]))
        pb = cx.t(f"d{i}.p", ub[2] + 5, y, dd["pct_txt"], j10b, cx.col(dd["lvl"], P["white"]))
        cx.t(f"d{i}.f", pb[2] + 6, y, dd["free"], j9, cx.col(dd["lvl"], P["sub"]))
        cx.t(f"d{i}.t", 314, y, dd.get("temp_txt", "N/D"), j10b, cx.col(dd.get("temp_lvl", NA), P["white"]), anchor="rs")
        y += 12
    bs = cx.baias()
    if bs:
        x = 4
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"BAIA {bb['n']}", r8b, P["sub"])
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, f"{s} {bb['curta']}".strip(), j9, cx.col(bb["lvl"], P["white"]))
            x = vb[2] + 8
        y += 12
    y += 2
    t, _ = v("net_down"); b = cx.t("n.d", 4, y, "↓" + t, j10b, P["white"])
    t, _ = v("net_up"); b = cx.t("n.u", b[2] + 8, y, "↑" + t, j10b, P["white"])
    _, xe = cx.par("tx", 314, y, "TX", "net_tx", r8b, j9, right=True)
    cx.par("rx", _ - 8, y, "RX", "net_rx", r8b, j9, right=True)
    y += 12
    from .base import iface_row
    for k, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        iface_row(c, v, k, y, 4, tag, 34, 314, r8b, j10b, j9, j9, cx.col, P["sub"], c_info=P["white"], c_rates=P["white"])
        y += 12

    # ---- rodapé: relógio da sala e condições externas
    c.line((0, 452, 319, 452), P["dim"])
    t, _ = v("clock"); cx.t("sys.clock", 4, 474, t, cx.f(DIGITAL, 24), P["accent"])
    t, _ = v("date"); cx.t("sys.date", 104, 464, t, j9, P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 104, 476, "EM OPERAÇÃO " + t, j9, P["sub"])
    t, lv = v("wtemp"); tw = cx.t("wx.t", 314, 465, t, j10b, cx.col(lv, P["white"]), anchor="rs")
    cx.t("wx.c", tw[0] - 5, 465, cx.fit(v.raw("city", ""), j9, 54), j9, P["sub"], anchor="rs")
    t, lv = v("wdesc"); wd = cx.t("wx.d", 314, 477, cx.fit(t, j9, 54), j9, P["white"], anchor="rs")
    t, lv = v("wage"); cx.t("wx.a", wd[0] - 5, 477, cx.fit(t.replace("OPEN-METEO ", ""), j9, 30), j9, P["sub"], anchor="rs")
    for k in ("coleta", "cpu_pct", "gpu_pct", "vram_pct"):
        v.raw(k)
    return cx.fim((2, 0.6, 130))
