# GAMMA v2 ARCADE "8 BITS" | versão 0.1.0 | 07/11/2026 20:45 (-03) | criação original (Claude, para Lucas Tavares)
# Fliperama de 8 bits: fonte de pixel (Fusion Pixel 12 e 24), vidas em corações de pixel (3 com tudo verde, uma a
# menos por nível de alerta), a frase da rodada (PRONTO!, CUIDADO!, FIM DE JOGO), barras de calor em blocos para
# cada "personagem" (CPU, GPU, RAM, VRAM), recorde do dia (pico de temperatura) e os discos como itens do inventário.
from .v2_base import Ctx, P, mix, PIXEL, JB, OK, WARN, CRIT, NA

CORACAO = ["01100110", "11111111", "11111111", "11111111", "01111110", "00111100", "00011000"]


def _coracao(c, x, y, cheio, cor, px=2):
    for j, linha in enumerate(CORACAO):
        for i, b in enumerate(linha):
            if b == "1":
                c.rect((x + i * px, y + j * px, x + i * px + px - 1, y + j * px + px - 1),
                       fill=cor if cheio else mix(cor, P["bg"], 0.8))


def _blocos(cx, x, y, n, pct, lv, w=7, h=8):
    k = 0 if pct is None else round(n * pct / 100)
    for i in range(n):
        cor = cx.cor_nivel(lv) if lv in (OK, WARN, CRIT) else P["sub"]
        cx.c.rect((x + i * (w + 1), y, x + i * (w + 1) + w - 1, y + h - 1), fill=cor if i < k else mix(P["accent"], P["bg"], 0.88))


def _num(t):
    try:
        return float("".join(ch for ch in t if ch.isdigit() or ch == ".") or "x")
    except ValueError:
        return None


def draw_frame(vm):
    cx = Ctx(vm, "8 BITS")
    v, c = cx.v, cx.c
    px12, px24 = cx.f(PIXEL.format(12), 12), cx.f(PIXEL.format(12), 24)
    px10 = cx.f(PIXEL.format(10), 10)
    h = v.raw("hist") or {}
    w_, s_, a_ = P["white"], P["sub"], P["accent"]

    # ---- placar
    cx.t("hdr.1up", 6, 13, "1UP", px12, P["red"])
    cx.t("hdr.gamma", 6, 26, "GAMMA", px12, w_)
    picos = [x for x in (h.get("cpu_t_max") or []) if x is not None]
    cx.t("hdr.hi", 160, 13, "RECORDE CPU", px12, P["red"], anchor="ms")
    cx.t("hdr.hiv", 160, 26, f"{round(max(picos))}°" if picos else "--", px12, w_, anchor="ms")
    t, _ = v("clock"); cx.t("sys.clock", 314, 13, t, px12, w_, anchor="rs")
    cx.selo_versao(314, 26, px10, s_)
    if cx.demo:
        cx.t("demo", 96, 26, "DEMO", px10, P["amber"], anchor="ms")

    # ---- vidas e frase da rodada
    vidas = {OK: 3, WARN: 2, CRIT: 1}[cx.lvl]
    for i in range(3):
        _coracao(c, 6 + i * 20, 40, i < vidas, P["red"])
    frase = {OK: "PRONTO!", WARN: "CUIDADO!", CRIT: "FIM DE JOGO"}[cx.lvl]
    cor = cx.cor_nivel()
    if cx.on:
        cx.t("st.frase", 314, 58, frase, px24, cor, anchor="rs")
    cx.t("st.rot", 6, 70, f"{({OK: 'N0', WARN: 'N1', CRIT: 'N2'}[cx.lvl])} {cx.rotulo}", px12, cor)

    # ---- personagens: nível (uso), barra de calor e temperatura
    y = 92
    cx.t("tit.p", 6, y, "PERSONAGENS", px12, a_)
    y += 16
    rp, rl = cx.ram_pct_txt()
    pers = [("CPU", "cpu_util", "cpu_temp", None), ("GPU", "gpu_util", "gpu_temp", None)]
    for i, (nome, ku, kt, _) in enumerate(pers):
        t, lv = v(ku); cx.t(f"p{i}.n", 6, y, nome, px12, w_)
        cx.t(f"p{i}.lv", 40, y, f"NV {t}", px12, cx.col(lv, w_))
        tt, lt = v(kt)
        _blocos(cx, 120, y - 8, 18, min(100, _num(tt) or 0) if tt != "N/D" else None, lt)
        cx.t(f"p{i}.t", 314, y, tt.replace("°C", "°"), px12, cx.col(lt, w_), anchor="rs")
        y += 16
    t, lv = v("vram_pct_txt"); cx.t("p2.n", 6, y, "VRAM", px12, w_)
    cx.t("p2.v", 40, y, v("vram_txt")[0], px12, cx.col(lv, w_))
    _blocos(cx, 120, y - 8, 18, cx.pct("vram_pct"), lv)
    cx.t("p2.p", 314, y, t, px12, cx.col(lv, w_), anchor="rs")
    y += 16
    t, lv = v("ram_used"); t2, _ = v("ram_total")
    cx.t("p3.n", 6, y, "RAM", px12, w_)
    cx.t("p3.v", 40, y, (t + t2).replace("GB", "G"), px12, cx.col(lv, w_))
    _blocos(cx, 120, y - 8, 18, cx.pct("ram_pct"), rl)
    cx.t("p3.p", 314, y, rp, px12, cx.col(rl, w_), anchor="rs")
    y += 16
    x = 6
    for nome, lab, k in (("ghz", "", "cpu_ghz"), ("mhz", "", "gpu_mhz"), ("fps", "FPS", "fps"), ("fan", "FAN", "gpu_fan_pct")):
        _, x = cx.par("x." + nome, x, y, lab, k, px12, px12, gap=6)
        x += 12
    y += 14
    x = 6
    _, x = cx.par("w", x, y, "W", "gpu_w", px12, px12, gap=6)
    t, _ = v("gpu_wlim"); b = cx.t("wlim", x + 2, y, t.replace("LIM ", "/"), px12, s_)
    _, x = cx.par("disp", b[2] + 12, y, "LIVRE", "ram_avail", px12, px12, gap=6)
    y += 14
    cx.par("load", 6, y, "CARGA", "cpu_load", px12, px12, gap=6)
    cx.par("tram", 314, y, "RAM°", "t_ram", px12, px12, gap=6, right=True)

    # ---- inventário: discos e baias como itens
    y += 30
    cx.t("tit.i", 6, y, "INVENTÁRIO", px12, a_)
    y += 6
    itens = [(dd["name"], dd["pct_txt"], dd["lvl"], dd.get("temp_txt", "N/D"), dd.get("temp_lvl", NA), dd["free"]) for dd in cx.discos()]
    for i, (nome, pct, lv, tt, lt, livre) in enumerate(itens):
        x0 = 6 + i * 104
        c.rect((x0, y, x0 + 98, y + 40), outline=cx.cor_nivel(lv) if lv in (WARN, CRIT) else mix(P["accent"], P["bg"], 0.5), width=2)
        cx.t(f"inv{i}.n", x0 + 6, y + 14, nome, px12, a_)
        cx.t(f"inv{i}.t", x0 + 92, y + 14, tt.replace("°C", "°"), px12, cx.col(lt, w_), anchor="rs")
        cx.t(f"inv{i}.p", x0 + 6, y + 34, pct, px24 if len(pct) <= 3 else px12, cx.col(lv, w_))
        cx.t(f"inv{i}.l", x0 + 92, y + 34, livre, px10, cx.col(lv, s_), anchor="rs")
    y += 50
    for i, dd in enumerate(cx.discos()):
        cx.t(f"dsk{i}.u", 6 + i * 104, y, dd["use"].replace("TB", "T"), px10, cx.col(dd.get("use_lvl", NA), s_))
    y += 14
    bs = cx.baias()
    if bs:
        x = 6
        for i, bb in enumerate(bs[:4]):
            sv = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"B{bb['n']}", px12, a_)
            vb = cx.t(f"bay{i}.v", nb[2] + 4, y, f"{sv} {bb['curta']}".strip(), px12, cx.col(bb["lvl"], w_))
            x = vb[2] + 10
        y += 16

    # ---- turbinas (refrigeração) e conexão
    y += 10
    x = 6
    for nome, lab, k in (("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("inf", "INF", "fan_sqi"), ("lat", "LAT", "fan_sql"), ("tra", "TRA", "fan_sqt")):
        _, x = cx.par("f." + nome, x, y, lab, k, px10, px12, troca=cx.sem_rpm, gap=3)
        x += 6
    y += 14
    x = 6
    for nome, lab, k in (("placa", "PLACA", "t_placa"), ("ssd", "SSD", "t_ssd"), ("png", "LAG", "ping")):
        _, x = cx.par("t." + nome, x, y, lab, k, px12, px12, gap=6)
        x += 12
    t, lv = v("inet"); cx.t("inet", 314, y, t.replace("INTERNET ", "NET "), px12, cx.col(lv), anchor="rs")
    y += 14
    y += 4
    t, _ = v("net_down"); b = cx.t("n.d", 6, y, "↓" + t, px12, w_)
    t, _ = v("net_up"); b = cx.t("n.u", b[2] + 10, y, "↑" + t, px12, w_)
    _, xe = cx.par("tx", 314, y, "TX", "net_tx", px10, px12, right=True)
    cx.par("rx", _ - 10, y, "RX", "net_rx", px10, px12, right=True)
    y += 14
    from .base import iface_row
    for k, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        iface_row(c, v, k, y, 6, tag, 44, 314, px12, px12, px10, px10, cx.col, s_, c_info=w_, c_rates=w_)
        y += 15

    # ---- rodapé
    c.rect((0, 446, 319, 447), fill=mix(P["accent"], P["bg"], 0.5))
    t, _ = v("date"); cx.t("sys.date", 6, 462, t, px12, w_)
    t, lv = v("uptime"); cx.t("sys.up", 6, 476, "TEMPO " + t, px12, s_)
    t, _ = v("os"); cx.t("sys.os", 160, 476, cx.fit(t, px10, 70), px10, s_, anchor="ms")
    t, lv = v("wtemp"); tw = cx.t("wx.t", 314, 462, t, px12, cx.col(lv, w_), anchor="rs")
    cx.t("wx.c", tw[0] - 8, 462, cx.fit(v.raw("city", ""), px12, 90), px12, s_, anchor="rs")
    t, lv = v("wdesc"); wd = cx.t("wx.d", 314, 476, cx.fit(t, px12, 60), px12, w_, anchor="rs")
    t, lv = v("wage"); cx.t("wx.a", wd[0] - 6, 476, cx.fit(t.replace("OPEN-METEO ", ""), px10, 32), px10, s_, anchor="rs")
    for k in ("coleta", "cpu_pct", "gpu_pct"):
        v.raw(k)
    return cx.fim((2, 0.5, 140))
