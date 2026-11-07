# GAMMA v2 UTI "MONITOR VITAL" | versão 0.1.0 | 07/11/2026 20:25 (-03) | criação original (Claude, para Lucas Tavares)
# Monitor de leito: cinco canais empilhados (CPU°, GPU°, VRAM, RAM e rede), cada um com o traçado das últimas 24 h
# à esquerda e o número grande à direita, como frequência cardíaca e saturação. Faixa de alarme no topo (médio em
# âmbar, alto em vermelho piscando) e os demais parâmetros em letras pequenas embaixo, como no rodapé do monitor.
from .v2_base import Ctx, P, mix, JB, ROBOTO, OK, WARN, CRIT, NA

XW0, XW1 = 4, 206            # traçado
XN = 314                     # números à direita


def _traco(cx, serie, y0, y1, vmin, vmax, cor):
    vals = [x for x in (serie or [])]
    if not vals:
        return
    n = len(vals)
    pts, d = [], cx.c.d
    for i, x in enumerate(vals):
        xx = XW0 + (XW1 - XW0) * i / max(1, n - 1)
        if x is None:
            if len(pts) > 1:
                d.line(pts, fill=cor, width=1)
            pts = []
            continue
        t = max(0.0, min(1.0, (x - vmin) / max(1e-9, vmax - vmin)))
        pts.append((xx, y1 - (y1 - y0) * t))
    if len(pts) > 1:
        d.line(pts, fill=cor, width=1)
    if pts:
        d.ellipse((pts[-1][0] - 2, pts[-1][1] - 2, pts[-1][0] + 2, pts[-1][1] + 2), fill=cor)


def draw_frame(vm):
    cx = Ctx(vm, "VITAL")
    v, c = cx.v, cx.c
    h = v.raw("hist") or {}
    r9, r10b = cx.f(ROBOTO, 9, "Bold"), cx.f(ROBOTO, 10, "Bold")
    j9, j10, j10b = cx.f(JB, 9, "Regular"), cx.f(JB, 10, "Regular"), cx.f(JB, 10, "Bold")
    big = cx.f(JB, 30, "Bold")

    # ---- faixa de alarme e hora
    cor = cx.cor_nivel()
    texto = {OK: "MONITORANDO", WARN: "ALARME MÉDIO", CRIT: "ALARME ALTO"}[cx.lvl]
    if cx.lvl != OK and cx.on:
        c.rect((0, 0, 200, 18), fill=cor)
        cx.t("al.t", 6, 14, f"{texto}  {cx.rotulo}", r10b, P["bg"])
    else:
        cx.t("al.t", 6, 14, f"{texto}  {cx.rotulo}" if cx.lvl != OK else texto, r10b, cor)
    t, _ = v("clock"); cx.t("sys.clock", 314, 15, t, cx.f(JB, 14, "Bold"), P["white"], anchor="rs")
    if cx.demo:
        cx.t("demo", 206, 14, "DEMO", r9, P["amber"])
    c.line((0, 22, 319, 22), P["dim"])

    # ---- canais
    t, lv = v("gpu_temp")
    canais = [
        ("CPU", "°C", "cpu_temp", h.get("cpu_t"), 20, 100, P["accent"], (("USO", "cpu_util"), ("", "cpu_ghz"))),
        ("GPU", "°C", "gpu_temp", h.get("gpu_t"), 20, 100, P["white"], (("USO", "gpu_util"), ("", "gpu_mhz"))),
        ("VRAM", "%", "vram_pct_txt", h.get("vram"), 0, 100, P["ice"], (("", "vram_txt"),)),
        ("RAM", "%", None, h.get("ram"), 0, 100, mix(P["accent"], P["white"], 0.5), (("", "ram_used"), ("", "ram_total"))),
    ]
    y0 = 26
    ch = 53
    for i, (nome, un, chave, serie, vmin, vmax, ccor, apoio) in enumerate(canais):
        ya, yb = y0 + i * ch, y0 + (i + 1) * ch - 4
        if chave:
            t, lv = v(chave)
        else:
            t, lv = cx.ram_pct_txt()
        num = t.replace("°C", "").replace("%", "")
        alerta = lv in (WARN, CRIT)
        cn = cx.col(lv) if alerta else ccor
        cx.t(f"ch{i}.n", XW0, ya + 10, nome, r9, ccor)
        for g in range(1, 4):
            for xx in range(XW0, XW1, 4):
                c.d.point((xx, ya + 12 + (yb - ya - 12) * g / 4), fill=mix(P["dim"], P["bg"], 0.4))
        _traco(cx, serie, ya + 13, yb - 2, vmin, vmax, mix(ccor, P["bg"], 0.15))
        if alerta and not cx.on:
            cn = mix(cn, P["bg"], 0.6)
        nb = cx.t(f"ch{i}.v", XN - 16, yb - 6, num, big, cn, anchor="rs")
        cx.t(f"ch{i}.u", XN, yb - 6, un, r9, ccor, anchor="rs")
        cx.t(f"ch{i}.l", nb[0] - 4, ya + 10, nome, r9, P["sub"], anchor="rs") if False else None
        x = XW1 + 8
        ys = ya + 10
        for lab, k in apoio:
            tt, ll = v(k)
            b = cx.t(f"ch{i}.{k}", x, ys, (lab + " " if lab else "") + tt, j9, cx.col(ll, P["sub"]))
            x = b[2] + 5
    # canal de rede
    ya, yb = y0 + 4 * ch, y0 + 5 * ch - 4
    cx.t("ch4.n", XW0, ya + 10, "REDE ↓↑", cx.f(JB, 9, "Bold"), P["accent"])
    topo = max([x for k in ("down", "up") for x in (h.get(k) or []) if x is not None] or [1e5])
    _traco(cx, h.get("up"), ya + 13, yb - 2, 0, topo, mix(P["white"], P["bg"], 0.3))
    _traco(cx, h.get("down"), ya + 13, yb - 2, 0, topo, P["accent"])
    t, _ = v("net_down"); cx.t("ch4.d", XN, ya + 24, "↓" + t, cx.f(JB, 14, "Bold"), P["accent"], anchor="rs")
    t, _ = v("net_up"); cx.t("ch4.u", XN, yb - 2, "↑" + t, cx.f(JB, 12, "Bold"), P["white"], anchor="rs")
    c.line((0, yb + 3, 319, yb + 3), P["dim"])

    # ---- parâmetros secundários
    y = yb + 16
    def linha(itens, y, x=4):
        for nome, lab, k in itens:
            _, x = cx.par(nome, x, y, lab, k, r9, j10b, troca=cx.sem_rpm, gap=3)
            x += 8
        return x
    linha((("w", "W", "gpu_w"), ("fan", "FAN", "gpu_fan_pct"), ("fps", "FPS", "fps"), ("load", "LOAD", "cpu_load")), y)
    t, _ = v("gpu_wlim"); cx.t("wlim", 314, y, t, j9, P["sub"], anchor="rs")
    y += 13
    x = linha((("vp", "VRAM", "vram_pct_txt"), ("disp", "RAM DISP", "ram_avail"), ("tram", "RAM°", "t_ram"), ("tssd", "SSD°", "t_ssd")), y)
    y += 13
    linha((("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("inf", "INF", "fan_sqi"), ("lat", "LAT", "fan_sql"), ("tra", "TRA", "fan_sqt")), y)
    y += 13
    linha((("placa", "PLACA", "t_placa"), ("png", "PING", "ping"), ("rx", "RX", "net_rx"), ("tx", "TX", "net_tx")), y)
    t, lv = v("inet"); cx.t("inet", 314, y, t.replace("INTERNET ", "NET "), j9, cx.col(lv), anchor="rs")
    y += 15
    for i, d in enumerate(cx.discos()):
        cx.t(f"d{i}.n", 4, y, d["name"], r10b, P["white"])
        ub = cx.t(f"d{i}.u", 36, y, d["use"], j10, cx.col(d.get("use_lvl", NA), P["white"]))
        pb = cx.t(f"d{i}.p", ub[2] + 5, y, d["pct_txt"], j10b, cx.col(d["lvl"], P["white"]))
        cx.t(f"d{i}.f", pb[2] + 6, y, d["free"], j9, cx.col(d["lvl"], P["sub"]))
        cx.t(f"d{i}.t", 314, y, d.get("temp_txt", "N/D"), j10b, cx.col(d.get("temp_lvl", NA), P["white"]), anchor="rs")
        y += 12
    bs = cx.baias()
    if bs:
        x = 4
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"B{bb['n']}", r9, P["accent"])
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, f"{s} {bb['curta']}".strip(), j9, cx.col(bb["lvl"], P["white"]))
            x = vb[2] + 10
        y += 13
    from .base import iface_row
    for k, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        iface_row(c, v, k, y, 4, tag, 34, 314, r9, j10b, j9, j9, cx.col, P["sub"], c_info=P["white"], c_rates=P["white"])
        y += 12

    # ---- rodapé do leito
    c.line((0, 452, 319, 452), P["dim"])
    t, _ = v("date"); cx.t("sys.date", 4, 465, t, j9, P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 4, 477, "INTERNADO HÁ " + t, j9, P["sub"])
    t, _ = v("os"); cx.t("sys.os", 160, 465, cx.fit(t, j9, 70), j9, P["sub"], anchor="ms")
    cx.selo_versao(314, 446, cx.f(JB, 8, "Regular"), mix(P["sub"], P["bg"], 0.3))
    t, lv = v("wtemp"); tb = cx.t("wx.t", 314, 466, t, cx.f(JB, 13, "Bold"), cx.col(lv, P["white"]), anchor="rs")
    cx.t("wx.c", tb[0] - 6, 465, cx.fit(v.raw("city", ""), j9, 60), j9, P["sub"], anchor="rs")
    t, lv = v("wdesc"); wd = cx.t("wx.d", 314, 477, cx.fit(t, j9, 60), j9, P["white"], anchor="rs")
    t, lv = v("wage"); cx.t("wx.a", wd[0] - 6, 477, cx.fit(t.replace("OPEN-METEO ", ""), j9, 40), j9, P["sub"], anchor="rs")
    for k in ("coleta", "cpu_pct", "gpu_pct", "vram_pct"):
        v.raw(k)
    return cx.fim((2, 0.7, 120))
