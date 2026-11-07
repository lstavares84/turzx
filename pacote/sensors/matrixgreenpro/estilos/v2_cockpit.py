# GAMMA v2 COCKPIT "PAINEL DE VOO" | versão 0.1.0 | 07/11/2026 20:30 (-03) | criação original (Claude, para Lucas Tavares)
# Cabine de avião: luzes MASTER CAUTION e MASTER WARNING, fitas verticais rolantes para a temperatura da CPU e da
# GPU (como velocímetro e altímetro), mostradores de motor com ponteiro para o uso, barras de combustível para
# RAM e VRAM e a lista de mensagens no estilo ECAM, montada a partir dos indicadores fora do verde.
import math

from .v2_base import Ctx, P, mix, JB, ROBOTO, OK, WARN, CRIT, NA, LOST

NOMES = {"cpu_temp": "CPU TEMP", "gpu_temp": "GPU TEMP", "vram": "VRAM", "ram": "RAM", "disk0": "DISCO 1",
         "disk1": "DISCO 2", "disk2": "DISCO 3", "disk0_t": "DISCO 1 TEMP", "disk1_t": "DISCO 2 TEMP",
         "disk2_t": "DISCO 3 TEMP", "conexao": "CONEXÃO", "ping": "PING", "cpu_fan": "RADIADOR", "gpu_fan": "FAN GPU",
         "pump": "BOMBA", "energia": "ENERGIA", "t_ram": "RAM TEMP", "t_ssd": "SSD TEMP"}


def _fita(cx, nome, x0, x1, y0, y1, chave, lado):
    """Fita rolante: escala de 5 em 5 °C centrada no valor atual, com o valor numa caixa-ponteiro."""
    t, lv = cx.v(chave)
    try:
        val = float(t.replace("°C", ""))
    except ValueError:
        val = None
    c = cx.c
    c.rect((x0, y0, x1, y1), fill=mix(P["accent"], P["bg"], 0.94), outline=P["dim"])
    ym = (y0 + y1) / 2
    px = 3.0                                                    # pixels por grau
    base = val if val is not None else 50.0
    f = cx.f(JB, 9, "Regular")
    for g in range(int(base - 40) // 5 * 5, int(base + 40) + 5, 5):
        y = ym - (g - base) * px
        if y0 + 6 < y < y1 - 6:
            if lado == "e":
                c.line((x1 - (8 if g % 10 == 0 else 4), y, x1, y), P["sub"])
            else:
                c.line((x0, y, x0 + (8 if g % 10 == 0 else 4), y), P["sub"])
            if g % 10 == 0 and abs(y - ym) > 12 and g >= 0:
                if lado == "e":
                    cx.t(f"{nome}.g{g}", x1 - 11, y + 3, str(g), f, P["sub"], anchor="rs")
                else:
                    cx.t(f"{nome}.g{g}", x0 + 11, y + 3, str(g), f, P["sub"])
    cor = cx.cor_nivel(lv) if lv in (OK, WARN, CRIT) else P["sub"]
    if lv == CRIT and not cx.on:
        cor = mix(cor, P["bg"], 0.5)
    caixa = (x0 - 2, ym - 10, x1 + 2, ym + 10)
    c.rect(caixa, fill=P["bg"], outline=cor, width=2)
    cx.t(f"{nome}.v", (x0 + x1) / 2, ym + 5, t.replace("°C", "°") if val is not None else "N/D",
         cx.f(JB, 14, "Bold"), cor if lv != OK else P["white"], anchor="ms")


def _motor(cx, nome, x, y, r, pct, lv, rot, valor):
    """Mostrador de motor (N1): arco de 210°, faixa âmbar e vermelha no fim, ponteiro e leitura digital."""
    d = cx.c.d
    a0, a1 = 150, 360
    d.arc((x - r, y - r, x + r, y + r), a0, a1 - 30, fill=P["dim"], width=2)
    d.arc((x - r, y - r, x + r, y + r), a1 - 30, a1 - 12, fill=mix(P["amber"], P["bg"], 0.3), width=2)
    d.arc((x - r, y - r, x + r, y + r), a1 - 12, a1, fill=mix(P["red"], P["bg"], 0.3), width=2)
    if pct is not None:
        a = math.radians(a0 + (a1 - a0) * pct / 100)
        cor = cx.cor_nivel(lv) if lv in (OK, WARN, CRIT) else P["white"]
        d.line((x, y, x + (r - 3) * math.cos(a), y + (r - 3) * math.sin(a)), fill=P["white"], width=2)
        d.pieslice((x - r + 4, y - r + 4, x + r - 4, y + r - 4), a0, a0 + (a1 - a0) * pct / 100, fill=mix(cor, P["bg"], 0.8))
        d.line((x, y, x + (r - 3) * math.cos(a), y + (r - 3) * math.sin(a)), fill=P["white"], width=2)
    cx.c.rect((x + 2, y + 2, x + r + 2, y + 18), outline=P["dim"])
    cx.t(f"{nome}.v", x + r, y + 15, valor, cx.f(JB, 12, "Bold"), cx.col(lv, P["white"]), anchor="rs")
    cx.t(f"{nome}.r", x - r, y + 15, rot, cx.f(ROBOTO, 9, "Bold"), P["sub"])


def draw_frame(vm):
    cx = Ctx(vm, "COCKPIT")
    v, c = cx.v, cx.c
    r9, r9b = cx.f(ROBOTO, 9, "Regular"), cx.f(ROBOTO, 9, "Bold")
    j9, j10b, j11b = cx.f(JB, 9, "Regular"), cx.f(JB, 10, "Bold"), cx.f(JB, 11, "Bold")

    # ---- topo: hora local e as duas luzes master
    t, _ = v("clock"); cx.t("sys.clock", 4, 16, t, cx.f(JB, 15, "Bold"), P["white"])
    cx.t("sys.lcl", 4, 26, "LCL", r9, P["sub"])
    if cx.demo:
        cx.t("demo", 82, 16, "SIM", r9b, P["amber"])
    for i, (txt, lvl_luz, cor) in enumerate((("MASTER\nCAUTION", WARN, P["amber"]), ("MASTER\nWARNING", CRIT, P["red"]))):
        x0 = 192 + i * 64
        acesa = (cx.lvl == lvl_luz or (lvl_luz == WARN and cx.lvl == CRIT and cx.nwarn)) and (cx.on or lvl_luz != CRIT)
        c.rect((x0, 3, x0 + 60, 29), fill=cor if acesa else mix(cor, P["bg"], 0.88), outline=mix(cor, P["bg"], 0.5))
        for k, s in enumerate(txt.split("\n")):
            cx.t(f"luz{i}.{k}", x0 + 30, 14 + k * 11, s, r9b, P["bg"] if acesa else mix(cor, P["bg"], 0.55), anchor="ms")
    cx.selo_versao(186, 27, cx.f(JB, 8, "Regular"), mix(P["sub"], P["bg"], 0.2))

    # ---- fitas e mostradores de motor
    cx.t("f.cpu.r", 26, 46, "CPU °C", r9b, P["accent"], anchor="ms")
    cx.t("f.gpu.r", 294, 46, "GPU °C", r9b, P["accent"], anchor="ms")
    _fita(cx, "f.cpu", 4, 48, 52, 216, "cpu_temp", "e")
    _fita(cx, "f.gpu", 272, 316, 52, 216, "gpu_temp", "d")
    t, lv = v("cpu_util"); _motor(cx, "m.cpu", 106, 86, 30, cx.pct("cpu_pct"), lv, "CPU", t)
    t, lv = v("gpu_util"); _motor(cx, "m.gpu", 214, 86, 30, cx.pct("gpu_pct"), lv, "GPU", t)
    y = 126
    _, xe = cx.par("cpu.f", 60, y, "", "cpu_ghz", r9, j9)
    cx.par("gpu.f", 266, y, "", "gpu_mhz", r9, j9, right=True)
    # combustível: RAM e VRAM
    y = 140
    for i, (rot, pk, tk, (pt, pl)) in enumerate((("RAM", "ram_pct", "ram_used", cx.ram_pct_txt()),
                                                  ("VRAM", "vram_pct", "vram_txt", v("vram_pct_txt")))):
        yy = y + i * 30
        cx.t(f"fuel{i}.r", 60, yy, rot, r9b, P["sub"])
        cx.t(f"fuel{i}.p", 266, yy, pt, j10b, cx.col(pl, P["white"]), anchor="rs")
        cx.barra(60, yy + 4, 206, 7, cx.pct(pk), pl, seg=5, gap=1)
        t, lv = v(tk)
        if tk == "ram_used":
            t += v("ram_total")[0]
        ub = cx.t(f"fuel{i}.u", 60, yy + 20, t, j9, P["white"])
        if i == 0:
            cx.par("ram.d", 266, yy + 20, "DISP", "ram_avail", r9, j9, right=True)
        else:
            t, _ = v("gpu_wlim"); lb = cx.t("gpu.lim", 266, yy + 20, t.replace("LIM ", "/"), j9, P["sub"], anchor="rs")
            cx.par("gpu.w", lb[0] - 2, yy + 20, "W", "gpu_w", r9, j9, right=True)
    y = 210
    _, xe = cx.par("fps", 60, y, "FPS", "fps", r9b, j10b)
    _, xe = cx.par("fan", xe + 10, y, "FAN", "gpu_fan_pct", r9b, j10b)
    cx.par("load", 266, y, "", "cpu_load", r9, j9, right=True)

    # ---- ECAM: mensagens
    c.line((0, 224, 319, 224), P["dim"])
    h = v.raw("health", {}) or {}
    msgs = [(NOMES.get(k, k.upper().replace("_", " ")), x) for k, x in h.items() if x in (WARN, CRIT, LOST)]
    msgs.sort(key=lambda m: 0 if m[1] == CRIT else 1)
    y = 240
    if not msgs:
        cx.t("ecam.0", 6, y, "SEM ALERTAS", j10b, P["accent"])
        cx.t("ecam.n", 314, y, cx.rotulo, j9, P["sub"], anchor="rs")
        y += 12
    else:
        for i, (m, x) in enumerate(msgs[:4]):
            cor = P["red"] if x == CRIT else P["amber"]
            cx.t(f"ecam.{i}", 6, y, f"{m} {'CRÍTICO' if x == CRIT else 'AVISO'}", j10b, cor if (cx.on or x != CRIT) else mix(cor, P["bg"], 0.5))
            y += 12
        if len(msgs) > 4:
            cx.t("ecam.mais", 314, y - 12, f"+{len(msgs) - 4}", j9, P["amber"], anchor="rs")
    y = 300
    c.line((0, y - 12, 319, y - 12), P["dim"])

    # ---- página SYS: discos, baias, refrigeração e comunicação
    for i, d in enumerate(cx.discos()):
        cx.t(f"d{i}.n", 6, y, d["name"], j10b, P["accent"])
        ub = cx.t(f"d{i}.u", 38, y, d["use"], j9, cx.col(d.get("use_lvl", NA), P["white"]))
        pb = cx.t(f"d{i}.p", ub[2] + 5, y, d["pct_txt"], j10b, cx.col(d["lvl"], P["white"]))
        cx.t(f"d{i}.f", pb[2] + 6, y, d["free"], j9, cx.col(d["lvl"], P["sub"]))
        cx.t(f"d{i}.t", 314, y, d.get("temp_txt", "N/D"), j10b, cx.col(d.get("temp_lvl", NA), P["white"]), anchor="rs")
        y += 13
    bs = cx.baias()
    if bs:
        x = 6
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"BAY{bb['n']}", r9b, P["sub"])
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, f"{s} {bb['curta']}".strip(), j9, cx.col(bb["lvl"], P["white"]))
            x = vb[2] + 9
        y += 12
    y += 14
    x = 6
    for nome, lab, k in (("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("inf", "INF", "fan_sqi"),
                         ("lat", "LAT", "fan_sql"), ("tra", "TRA", "fan_sqt")):
        _, x = cx.par("f." + nome, x, y, lab, k, r9, j10b, troca=cx.sem_rpm, gap=3)
        x += 7
    y += 12
    x = 6
    for nome, lab, k in (("placa", "PLACA", "t_placa"), ("tram", "RAM", "t_ram"), ("tssd", "SSD", "t_ssd"), ("png", "PING", "ping")):
        _, x = cx.par("t." + nome, x, y, lab, k, r9, j10b, gap=3)
        x += 8
    t, lv = v("inet"); cx.t("inet", 314, y, t, j9, cx.col(lv), anchor="rs")
    y += 24
    t, _ = v("net_down"); b = cx.t("n.d", 6, y, "↓" + t, j11b, P["white"])
    t, _ = v("net_up"); b = cx.t("n.u", b[2] + 8, y, "↑" + t, j11b, P["white"])
    _, xe = cx.par("rx", 314, y, "TX", "net_tx", r9, j9, right=True)
    cx.par("tx", _ - 8, y, "RX", "net_rx", r9, j9, right=True)
    y += 12
    from .base import iface_row
    for k, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        iface_row(c, v, k, y, 6, tag, 36, 314, r9b, j10b, j9, j9, cx.col, P["sub"], c_info=P["white"], c_rates=P["white"])
        y += 12

    # ---- rodapé: data, tempo de voo e meteorologia (METAR)
    c.line((0, 450, 319, 450), P["dim"])
    t, _ = v("date"); cx.t("sys.date", 6, 463, t, j9, P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 6, 475, "TEMPO DE VOO " + t, j9, P["sub"])
    t, _ = v("os"); cx.t("sys.os", 120, 463, cx.fit(t, j9, 80), j9, P["sub"])
    city = v.raw("city", "")
    t, lv = v("wtemp"); tw = cx.t("wx.t", 314, 464, t, j11b, cx.col(lv, P["white"]), anchor="rs")
    cx.t("wx.c", tw[0] - 6, 463, cx.fit(city, j9, 70), j9, P["sub"], anchor="rs")
    t, lv = v("wdesc"); wd = cx.t("wx.d", 314, 475, cx.fit(t, j9, 70), j9, P["white"], anchor="rs")
    t, lv = v("wage"); cx.t("wx.a", wd[0] - 6, 475, cx.fit(t.replace("OPEN-METEO ", "METAR "), j9, 76), j9, P["sub"], anchor="rs")
    for k in ("coleta",):
        v.raw(k)
    return cx.fim((2, 0.6, 130))
