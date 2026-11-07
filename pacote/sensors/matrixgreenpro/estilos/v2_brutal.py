# GAMMA v2 BRUTALISTA "CONCRETO" | versão 0.1.0 | 07/11/2026 20:00 (-03) | criação original (Claude, para Lucas Tavares)
# Blocos crus de borda grossa, números enormes em JetBrains Mono ExtraBold, nenhum enfeite. O estado geral é uma
# laje inteira no topo (verde, âmbar ou vermelho) com o nível gigante. Grupo fora do verde vira bloco invertido.
from .v2_base import Ctx, P, mix, JB, ROBOTO, OK, WARN, CRIT, NA

B = 3                       # espessura das bordas


def _bloco(x, cx, x0, y0, x1, y1, lv):
    """Bloco de concreto: borda grossa; invertido (cheio) quando o grupo está em atenção ou crítico."""
    cheio = lv in (WARN, CRIT)
    cor = cx.cor_nivel(lv) if cheio else P["accent"]
    if cheio and (cx.on or lv != CRIT):
        cx.c.rect((x0, y0, x1, y1), fill=cor)
        return P["bg"], P["bg"]
    cx.c.rect((x0, y0, x1, y1), outline=cor, width=B)
    return P["white"], P["sub"]


def _pior(*lvs):
    return CRIT if CRIT in lvs else WARN if WARN in lvs else OK


def draw_frame(vm):
    cx = Ctx(vm, "CONCRETO")
    v, c = cx.v, cx.c
    XB, XL, MB, L9, L10 = (cx.f(JB, 30, "ExtraBold"), cx.f(JB, 40, "ExtraBold"), cx.f(JB, 13, "ExtraBold"),
                           cx.f(ROBOTO, 9, "Black"), cx.f(ROBOTO, 10, "Black"))
    sb, s, xs = cx.f(JB, 12, "Bold"), cx.f(JB, 12, "Regular"), cx.f(JB, 10, "Regular")

    # ---- laje do estado geral
    cor = cx.cor_nivel()
    acesa = cx.on
    if acesa:
        c.rect((0, 0, 319, 54), fill=cor)
    else:
        c.rect((0, 0, 319, 54), outline=cor, width=B)
    tinta = P["bg"] if acesa else cor
    nb = cx.t("st.nivel", 6, 46, {OK: "N0", WARN: "N1", CRIT: "N2"}[cx.lvl], XL, tinta)
    cx.t("st.rotulo", nb[2] + 10, 30, cx.rotulo, MB, tinta)
    cx.t("st.demo" if cx.demo else "st.marca", nb[2] + 10, 46, "DEMO" if cx.demo else "GAMMA", L10, tinta)
    cx.selo_versao(314, 12, cx.f(JB, 9, "Bold"), tinta)

    # ---- três blocos: CPU, GPU, RAM
    y0, y1 = 60, 146
    blocos = [("CPU", "cpu_temp", "cpu_util", "cpu_ghz"), ("GPU", "gpu_temp", "gpu_util", "gpu_mhz")]
    for i, (nome, kt, ku, kf) in enumerate(blocos):
        x0 = 4 + i * 106
        lt, lu = v(kt)[1], v(ku)[1]
        tc, sc = _bloco(None, cx, x0, y0, x0 + 102, y1, _pior(lt, lu))
        cx.t(f"{nome}.lab", x0 + 8, y0 + 16, nome, L10, sc)
        t, lv = v(kt); cx.t(f"{nome}.temp", x0 + 8, y0 + 52, t.replace("C", ""), XB, tc if tc == P["bg"] else cx.col(lv, P["white"]))
        t, lv = v(ku); cx.t(f"{nome}.util", x0 + 8, y0 + 72, t, MB, tc if tc == P["bg"] else cx.col(lv, P["white"]))
        t, lv = v(kf); cx.t(f"{nome}.freq", x0 + 94, y0 + 72, t, xs, sc, anchor="rs")
    x0 = 216
    rp, rl = cx.ram_pct_txt()
    tc, sc = _bloco(None, cx, x0, y0, 316, y1, rl)
    cx.t("RAM.lab", x0 + 8, y0 + 16, "RAM", L10, sc)
    cx.t("RAM.pct", x0 + 8, y0 + 52, rp, XB, tc if tc == P["bg"] else cx.col(rl, P["white"]))
    t, lv = v("ram_used"); t2, _ = v("ram_total")
    cx.t("RAM.uso", x0 + 8, y0 + 72, t + t2.replace("GB", ""), cx.f(JB, 11, "Bold"), tc if tc == P["bg"] else P["white"])
    t, lv = v("t_ram"); cx.t("RAM.temp", x0 + 92, y0 + 16, t, xs, sc, anchor="rs")

    # ---- faixa da GPU e da CPU (dados de apoio, sem caixa)
    y = 164
    _, xe = cx.par("gpu.vram", 6, y, "VRAM", "vram_txt", L9, sb)
    t, lv = v("vram_pct_txt"); b = cx.t("gpu.vrampct", xe + 4, y, f"({t})", sb, cx.col(lv))
    _, xe = cx.par("gpu.w", b[2] + 10, y, "W", "gpu_w", L9, sb)
    t, _ = v("gpu_wlim"); cx.t("gpu.wlim", xe + 3, y, t.replace("LIM ", "/"), xs, P["sub"])
    y += 15
    _, xe = cx.par("gpu.fan", 6, y, "FAN", "gpu_fan_pct", L9, sb)
    _, xe = cx.par("gpu.fps", xe + 12, y, "FPS", "fps", L9, sb)
    cx.par("cpu.load", 314, y, "LOAD", "cpu_load", L9, sb, right=True)
    c.rect((0, y + 6, 319, y + 6 + B - 1), fill=P["accent"])

    # ---- discos: tabela com réguas grossas
    y = y + 24
    for i, d in enumerate(cx.discos()):
        cx.t(f"dsk{i}.n", 6, y, d["name"], MB, P["white"])
        ub = cx.t(f"dsk{i}.use", 44, y, d["use"], s, cx.col(d.get("use_lvl", NA)))
        pb = cx.t(f"dsk{i}.pct", ub[2] + 5, y, d["pct_txt"], sb, cx.col(d["lvl"]))
        cx.t(f"dsk{i}.free", pb[2] + 8, y, d["free"] + " livre" if d["free"] != "--" else "--", xs, cx.col(d["lvl"]))
        cx.t(f"dsk{i}.temp", 314, y, d.get("temp_txt", "N/D"), sb, cx.col(d.get("temp_lvl", NA)), anchor="rs")
        y += 16
    c.rect((0, y - 9, 319, y - 9 + B - 1), fill=P["accent"])

    # ---- baias: 4 células cruas
    bs = cx.baias()
    if bs:
        for i, bb in enumerate(bs[:4]):
            x0 = 4 + i * 79
            c.rect((x0, y - 3, x0 + 75, y + 24), outline=mix(P["accent"], P["bg"], 0.4), width=1)
            cx.t(f"bay{i}.n", x0 + 5, y + 18, str(bb["n"]), cx.f(JB, 20, "ExtraBold"), P["accent"])
            top = bb.get("pct_txt") if bb.get("use") else bb["cap"] or "--"
            cx.t(f"bay{i}.a", x0 + 71, y + 8, top, cx.f(JB, 10, "Bold"), cx.col(bb.get("pct_lvl", bb["lvl"])), anchor="rs")
            cx.t(f"bay{i}.b", x0 + 71, y + 20, bb["curta"], xs, cx.col(bb["lvl"]), anchor="rs")
        y += 42
    else:
        y += 8

    # ---- refrigeração
    x = 6
    for nome, lab, k in (("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("inf", "INF", "fan_sqi"),
                         ("lat", "LAT", "fan_sql"), ("tra", "TRA", "fan_sqt")):
        _, x = cx.par("fan." + nome, x, y, lab, k, L9, sb, troca=cx.sem_rpm)
        x += 7
    y += 15
    _, xe = cx.par("t.placa", 6, y, "PLACA", "t_placa", L9, sb)
    _, xe = cx.par("t.ssd", xe + 10, y, "SSD", "t_ssd", L9, sb)
    cx.par("png", 314, y, "PING", "ping", L9, sb, right=True)
    c.rect((0, y + 6, 319, y + 6 + B - 1), fill=P["accent"])

    # ---- rede
    y += 24
    t, _ = v("net_down"); b = cx.t("net.down", 6, y, "↓" + t, MB, P["white"])
    t, _ = v("net_up"); cx.t("net.up", b[2] + 8, y, "↑" + t, MB, P["white"])
    t, lv = v("inet"); cx.t("inet", 314, y, t, xs, cx.col(lv), anchor="rs")
    y += 14
    from .base import iface_row
    for k, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        iface_row(c, v, k, y, 6, tag, 40, 314, L9, cx.f(JB, 10, "Bold"), xs, xs, cx.col, P["sub"],
                  c_info=P["white"], c_rates=P["white"])
        y += 13
    _, xe = cx.par("net.rx", 6, y, "RX", "net_rx", L9, cx.f(JB, 10, "Bold"))
    cx.par("net.tx", xe + 10, y, "TX", "net_tx", L9, cx.f(JB, 10, "Bold"))
    y = 408
    cx.par("ram.avail", 6, y, "RAM DISP", "ram_avail", L9, sb)
    t, _ = v("os"); cx.t("sys.os", 314, y, cx.fit(t, xs, 150), xs, P["sub"], anchor="rs")

    # ---- rodapé: relógio cru e clima num bloco
    c.rect((0, 418, 319, 418 + B - 1), fill=P["accent"])
    t, _ = v("clock"); cx.t("sys.clock", 4, 458, t[:5], cx.f(JB, 38, "ExtraBold"), P["accent"])
    t, _ = v("date"); cx.t("sys.date", 4, 474, t, xs, P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 166, 474, "UP " + t, xs, P["sub"], anchor="rs")
    c.rect((172, 424, 316, 477), outline=P["accent"], width=B)
    t, lv = v("wtemp"); wt = cx.t("wx.temp", 178, 458, t, cx.f(JB, 26, "ExtraBold"), cx.col(lv, P["white"]))
    cx.t("wx.city", 309, 437, cx.fit(v.raw("city", ""), xs, 60), xs, P["sub"], anchor="rs")
    t, lv = v("wdesc"); cx.t("wx.desc", 309, 452, cx.fit(t, xs, min(64, 309 - wt[2] - 6)), xs, P["white"], anchor="rs")
    t, lv = v("wage"); cx.t("wx.age", 309, 470, cx.fit(t.replace("OPEN-METEO ", ""), xs, 64), xs, P["sub"], anchor="rs")
    v.raw("coleta"); v.raw("cpu_pct"); v.raw("gpu_pct"); v.raw("vram_pct")
    return cx.fim((2, 0.5, 140))
