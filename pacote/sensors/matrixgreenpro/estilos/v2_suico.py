# GAMMA v2 SUÍÇO "GRADE" | versão 0.1.0 | 07/11/2026 20:55 (-03) | criação original (Claude, para Lucas Tavares)
# Estilo tipográfico internacional: duas colunas rígidas (x = 8 e x = 166), tudo alinhado à esquerda, contraste de
# escala como única hierarquia. O nível do sistema é um algarismo enorme em Roboto Black (0, 1 ou 2); os números
# principais em Roboto Bold grande com legenda curta em caixa baixa; o verde só marca legendas e o algarismo.
from .v2_base import Ctx, P, mix, JB, ROBOTO, OK, WARN, CRIT, NA

C1, C2 = 8, 166


def draw_frame(vm):
    cx = Ctx(vm, "GRADE")
    v, c = cx.v, cx.c
    rb = lambda n: cx.f(ROBOTO, n, "Bold")
    rk = lambda n: cx.f(ROBOTO, n, "Black")
    rm9, rr9, rr10 = cx.f(ROBOTO, 9, "Medium"), cx.f(ROBOTO, 9, "Regular"), cx.f(ROBOTO, 10, "Regular")
    j9, j10 = cx.f(JB, 9, "Regular"), cx.f(JB, 10, "Bold")
    verde, branco, cinza = P["accent"], P["white"], P["sub"]
    cor = lambda lv, base=branco: cx.col(lv, base)

    # ---- o algarismo do nível e o relógio
    nc = cx.cor_nivel()
    cx.t("st.n", C1 - 4, 92, {OK: "0", WARN: "1", CRIT: "2"}[cx.lvl], rk(104), nc if cx.on else mix(nc, P["bg"], 0.6))
    cx.t("st.l", C1 + 66, 26, "nível", rm9, verde)
    cx.t("st.r", C1 + 66, 40, cx.rotulo.capitalize(), rb(12), branco)
    if cx.demo:
        cx.t("st.demo", C1 + 66, 54, "demonstração", rr9, P["amber"])
    t, _ = v("clock"); cx.t("sys.clock", C2, 60, t[:5], rb(40), branco)
    t, _ = v("date"); cx.t("sys.date", C2, 76, t.capitalize(), rr10, branco)
    t, lv = v("uptime"); cx.t("sys.up", C2, 89, "ligado há " + t, rr9, cinza)
    cx.selo_versao(312, 14, cx.f(ROBOTO, 8, "Regular"), mix(cinza, P["bg"], 0.2))

    # ---- quatro números
    rp, rl = cx.ram_pct_txt()
    bloco = [("Processador", v("cpu_temp"), (("cpu_util", ""), ("cpu_ghz", ""))),
             ("Placa de vídeo", v("gpu_temp"), (("gpu_util", ""), ("gpu_mhz", ""))),
             ("Memória", (rp, rl), (("ram_used", ""), ("ram_total", ""))),
             ("Memória de vídeo", v("vram_pct_txt"), (("vram_txt", ""),))]
    for i, (lab, (t, lv), sub) in enumerate(bloco):
        x, y = (C1, C2)[i % 2], 116 + (i // 2) * 58
        cx.t(f"b{i}.l", x, y, lab, rm9, verde)
        nb = cx.t(f"b{i}.v", x - 1, y + 30, t.replace("°C", "°"), rb(30), cor(lv))
        xs = x
        partes = []
        for k, _ in sub:
            tt, ll = v(k)
            partes.append(tt)
        s = ("  ".join(partes)) if i != 2 else "".join(partes)
        cx.t(f"b{i}.s", xs, y + 43, s, j9, cinza)

    # ---- detalhes em duas colunas
    y = 240
    def par(nome, x, y, lab, k):
        b = cx.t(nome + ".l", x, y, lab, rr9, cinza)
        t, lv = v(k)
        return cx.t(nome + ".v", x + 52, y, cx.sem_rpm(t), j10, cor(lv))
    esq = [("load", "Carga", "cpu_load"), ("w", "Potência", "gpu_w"), ("fan", "Fan vídeo", "gpu_fan_pct"),
           ("fps", "Quadros/s", "fps"), ("disp", "RAM livre", "ram_avail"), ("tram", "RAM temp.", "t_ram")]
    dir_ = [("pump", "Bomba", "pump"), ("rad", "Radiador", "cpu_fan"), ("inf", "Inferior", "fan_sqi"),
            ("lat", "Lateral", "fan_sql"), ("tra", "Traseira", "fan_sqt"), ("placa", "Placa-mãe", "t_placa")]
    for i, (n, l, k) in enumerate(esq):
        b = par("e." + n, C1, y + i * 13, l, k)
        if k == "gpu_w":
            t, _ = v("gpu_wlim"); cx.t("e.wlim", b[2] + 4, y + i * 13, t.replace("LIM ", "/"), j9, cinza)
    for i, (n, l, k) in enumerate(dir_):
        par("d." + n, C2, y + i * 13, l, k)

    # ---- discos: percentual grande à esquerda da linha
    y = 318
    cx.t("tit.d", C1, y, "Armazenamento", rm9, verde)
    _, xe = cx.par("ssd", 312, y, "SSD", "t_ssd", rr9, j9, right=True)
    y += 20
    for i, dd in enumerate(cx.discos()):
        x = C1 + i * 104
        cx.t(f"d{i}.p", x - 1, y, dd["pct_txt"], rb(20), cor(dd["lvl"]))
        cx.t(f"d{i}.n", x, y + 12, dd["name"], rm9, branco)
        tb = cx.t(f"d{i}.t", x + 96, y + 12, dd.get("temp_txt", "N/D"), j9, cor(dd.get("temp_lvl", NA), cinza), anchor="rs")
        cx.t(f"d{i}.u", x, y + 23, dd["use"], j9, cinza)
        cx.t(f"d{i}.f", x, y + 33, f"{dd['free']} livre", j9, cor(dd["lvl"], cinza))
    y += 46
    bs = cx.baias()
    if bs:
        x = C1
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"B{bb['n']}", rm9, cinza)
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, f"{s} {bb['curta'].lower()}".strip(), j9, branco if bb["estado"] == "MONT" else cinza)
            x = vb[2] + 10
        y += 14

    # ---- rede
    y += 4
    t, _ = v("net_down"); b = cx.t("n.d", C1, y, "↓ " + t, j10, branco)
    t, _ = v("net_up"); cx.t("n.u", 90, y, "↑ " + t, j10, branco)
    _, xe = cx.par("png", C2, y, "Ping", "ping", rr9, j10)
    t, lv = v("inet"); cx.t("inet", 312, y, t.capitalize(), rr9, cor(lv, cinza), anchor="rs")
    y += 13
    from .base import iface_row
    for k, tag in (("eth", "Cabo"), ("wifi", "Wi-Fi")):
        iface_row(c, v, k, y, C1, tag, 44, 312, rr9, j10, j9, j9, cx.col, cinza, c_info=branco, c_rates=branco)
        y += 12
    _, xe = cx.par("rx", C1, y, "Recebido", "net_rx", rr9, j9)
    cx.par("tx", C2, y, "Enviado", "net_tx", rr9, j9)

    # ---- rodapé: sistema e tempo
    t, _ = v("os"); cx.t("sys.os", C1, 474, cx.fit(t.capitalize(), rr9, 150), rr9, cinza)
    t, lv = v("wtemp"); tw = cx.t("wx.t", C2 - 1, 476, t, rb(22), cor(lv))
    cx.t("wx.c", tw[2] + 6, 456, cx.fit(v.raw("city", "").title(), rm9, 312 - tw[2] - 6), rm9, verde)
    t, lv = v("wdesc"); cx.t("wx.d", tw[2] + 6, 466, cx.fit(t.capitalize(), rr9, 312 - tw[2] - 6), rr9, branco)
    t, lv = v("wage"); cx.t("wx.a", tw[2] + 6, 476, cx.fit(t.lower(), cx.f(ROBOTO, 8, "Regular"), 312 - tw[2] - 6), cx.f(ROBOTO, 8, "Regular"), cinza)
    for k in ("coleta", "cpu_pct", "gpu_pct", "vram_pct"):
        v.raw(k)
    return cx.fim((2, 0.4, 150))
