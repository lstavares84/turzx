# GAMMA v2 METRÔ "LINHA GAMMA" | versão 0.1.0 | 07/11/2026 20:35 (-03) | criação original (Claude, para Lucas Tavares)
# O computador como uma linha de metrô que serpenteia pela tela: cada métrica é uma estação, com o nome acima e a
# leitura abaixo, e a cor do círculo diz a saúde. Leituras longas ficam longe das curvas. O estado geral usa a linguagem dos avisos de operação
# ("operação normal", "velocidade reduzida", "operação interrompida"). Embaixo, um quadro de partidas com os discos.
from .v2_base import Ctx, P, mix, JB, ROBOTO, OK, WARN, CRIT, NA, LOST, NEUTRAL

XS = (36, 116, 196, 276)     # estações por linha
Y0, DY = 66, 50              # primeira linha e distância entre linhas
LARG = 4


def _estacao(cx, nome, x, y, rot, txt, lv, txt2=None):
    d = cx.c.d
    cor = {OK: P["accent"], WARN: P["amber"], CRIT: P["red"], LOST: P["amber"]}.get(lv, P["sub"])
    if lv == CRIT and not cx.on:
        cor = mix(cor, P["bg"], 0.55)
    cheia = lv in (WARN, CRIT, LOST)
    d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=cor if cheia else P["bg"], outline=cor if lv != NEUTRAL else P["white"], width=3)
    cx.t(f"{nome}.r", x, y - 10, rot, cx.f(ROBOTO, 9, "Bold"), P["sub"], anchor="ms")
    cx.t(f"{nome}.v", x, y + 19, txt, cx.f(JB, 10 if len(txt) < 12 else 9, "Bold"), cx.col(lv, P["white"]), anchor="ms")
    if txt2:
        cx.t(f"{nome}.v2", x, y + 29, txt2, cx.f(JB, 8, "Regular"), P["sub"], anchor="ms")


def draw_frame(vm):
    cx = Ctx(vm, "LINHA GAMMA")
    v, c = cx.v, cx.c
    d = c.d
    r9b, j9, j10b = cx.f(ROBOTO, 9, "Bold"), cx.f(JB, 9, "Regular"), cx.f(JB, 10, "Bold")

    # ---- aviso de operação
    cor = cx.cor_nivel()
    aviso = {OK: "Operação normal", WARN: "Velocidade reduzida", CRIT: "Operação interrompida"}[cx.lvl]
    d.rounded_rectangle((4, 4, 26, 26), 5, fill=P["accent"])
    cx.t("hdr.g", 15, 21, "Γ", cx.f(JB, 16, "Bold"), P["bg"], anchor="ms")
    cx.t("hdr.n", 32, 14, "Linha Gamma", cx.f(ROBOTO, 12, "Bold"), P["white"])
    cx.t("hdr.a", 32, 27, f"{aviso}  {cx.rotulo.lower()}" if cx.lvl != OK else aviso, cx.f(ROBOTO, 10, "Medium"),
         cor if cx.on else mix(cor, P["bg"], 0.5))
    t, _ = v("clock"); cx.t("sys.clock", 314, 18, t[:5], cx.f(JB, 16, "Bold"), P["white"], anchor="rs")
    cx.selo_versao(314, 29, cx.f(JB, 8, "Regular"), mix(P["sub"], P["bg"], 0.2))
    if cx.demo:
        cx.t("demo", 240, 18, "teste", cx.f(ROBOTO, 9, "Regular"), P["amber"], anchor="rs")

    # ---- o traçado em serpentina
    rp, rl = cx.ram_pct_txt()
    t_ram, _ = v("ram_used"); t_tot, _ = v("ram_total")
    vram_t, _ = v("vram_txt"); wl, _ = v("gpu_wlim")
    linhas = [
        [("CPU", "cpu_temp"), ("freq.", "cpu_ghz"), ("carga", "cpu_load"), ("uso", "cpu_util")],
        [("GPU", "gpu_temp"), ("uso", "gpu_util"), ("freq.", "gpu_mhz"), ("fps", "fps")],
        [("VRAM", "vram_pct_txt", vram_t), ("RAM", None, f"{t_ram}{t_tot}"), ("watts", "gpu_w", wl.replace("LIM ", "lim ")), ("fan", "gpu_fan_pct")],
        [("livre", "ram_avail"), ("ram °", "t_ram"), ("placa °", "t_placa"), ("bomba", "pump")],
        [("radiador", "cpu_fan"), ("inf.", "fan_sqi"), ("lat.", "fan_sql"), ("tras.", "fan_sqt")],
    ]
    n = len(linhas)
    trilho = mix(P["accent"], P["bg"], 0.25)
    for i in range(n):
        y = Y0 + i * DY
        d.line((XS[0], y, XS[-1], y), fill=trilho, width=LARG)
        if i < n - 1:                                            # curva para a linha de baixo, alternando os lados
            if i % 2 == 0:
                d.arc((XS[-1] - DY / 2, y, XS[-1] + DY / 2, y + DY), 270, 90, fill=trilho, width=LARG)
            else:
                d.arc((XS[0] - DY / 2, y, XS[0] + DY / 2, y + DY), 90, 270, fill=trilho, width=LARG)
    for i, est in enumerate(linhas):
        y = Y0 + i * DY
        ordem = est if i % 2 == 0 else list(reversed(est))
        for j, e in enumerate(ordem):
            rot, k = e[0], e[1]
            extra = e[2] if len(e) > 2 else None
            if k is None:
                txt, lv = rp, rl
            else:
                txt, lv = v(k)
            _estacao(cx, f"e{i}{j}", XS[j], y, rot, cx.sem_rpm(txt).replace("°C", "°"), lv, extra)

    # ---- quadro de partidas: discos, baias, rede
    y = Y0 + n * DY - 8
    c.rect((0, y - 12, 319, 479), fill=mix(P["accent"], P["bg"], 0.94))
    cx.t("q.t", 6, y, "Próximas paradas", cx.f(ROBOTO, 10, "Bold"), P["accent"])
    _, xe = cx.par("tssd", 314, y, "ssd", "t_ssd", r9b, j9, right=True)
    y += 13
    for i, dd in enumerate(cx.discos()):
        cx.t(f"d{i}.n", 6, y, dd["name"], j10b, P["accent"])
        ub = cx.t(f"d{i}.u", 38, y, dd["use"], j9, cx.col(dd.get("use_lvl", NA), P["white"]))
        pb = cx.t(f"d{i}.p", ub[2] + 5, y, dd["pct_txt"], j10b, cx.col(dd["lvl"], P["white"]))
        cx.t(f"d{i}.f", pb[2] + 6, y, dd["free"] + " livre", j9, cx.col(dd["lvl"], P["sub"]))
        cx.t(f"d{i}.t", 314, y, dd.get("temp_txt", "N/D"), j10b, cx.col(dd.get("temp_lvl", NA), P["white"]), anchor="rs")
        y += 12
    bs = cx.baias()
    if bs:
        x = 6
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"plat. {bb['n']}", cx.f(ROBOTO, 9, "Regular"), P["sub"])
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, f"{s} {bb['curta'].lower()}".strip(), j9, cx.col(bb["lvl"], P["white"]))
            x = vb[2] + 8
        y += 12
    y += 4
    t, _ = v("net_down"); b = cx.t("n.d", 6, y, "↓" + t, j10b, P["white"])
    t, _ = v("net_up"); b = cx.t("n.u", b[2] + 8, y, "↑" + t, j10b, P["white"])
    _, xe = cx.par("png", b[2] + 10, y, "ping", "ping", r9b, j10b)
    t, lv = v("inet"); cx.t("inet", 314, y, t.lower(), j9, cx.col(lv), anchor="rs")
    y += 12
    from .base import iface_row
    for k, tag in (("eth", "cabo"), ("wifi", "wi-fi")):
        iface_row(c, v, k, y, 6, tag, 38, 314, cx.f(ROBOTO, 9, "Regular"), j10b, j9, j9, cx.col, P["sub"], c_info=P["white"], c_rates=P["white"])
        y += 12
    _, xe = cx.par("rx", 6, y, "recebido", "net_rx", cx.f(ROBOTO, 9, "Regular"), j9)
    cx.par("tx", xe + 10, y, "enviado", "net_tx", cx.f(ROBOTO, 9, "Regular"), j9)

    # ---- rodapé
    t, _ = v("date"); cx.t("sys.date", 6, 476, t.lower(), j9, P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 6, 465, "em circulação há " + t, j9, P["sub"])
    t, _ = v("os"); cx.t("sys.os", 160, 476, cx.fit(t.lower(), j9, 70), j9, P["sub"], anchor="ms")
    t, lv = v("wtemp"); tw = cx.t("wx.t", 314, 466, t, j10b, cx.col(lv, P["white"]), anchor="rs")
    cx.t("wx.c", tw[0] - 6, 466, cx.fit(v.raw("city", "").title(), j9, 70), j9, P["sub"], anchor="rs")
    t, lv = v("wdesc"); wd = cx.t("wx.d", 314, 477, cx.fit(t.lower(), j9, 60), j9, P["white"], anchor="rs")
    t, lv = v("wage"); cx.t("wx.a", wd[0] - 6, 477, cx.fit(t.replace("OPEN-METEO ", ""), j9, 34), j9, P["sub"], anchor="rs")
    for k in ("coleta", "cpu_pct", "gpu_pct", "vram_pct"):
        v.raw(k)
    return cx.fim((2, 0.6, 130))
