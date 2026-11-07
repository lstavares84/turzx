# GAMMA v2 MINIMALISTA "SILÊNCIO" | versão 0.1.0 | 07/11/2026 20:05 (-03) | criação original (Claude, para Lucas Tavares)
# Nenhuma linha, nenhuma caixa, nenhum brilho. Uma frase diz o estado ("Tudo certo", "5 avisos"), quatro números
# grandes e finos dizem o essencial, e o resto fica pequeno e quieto, agrupado só por espaço em branco.
# A cor só aparece quando algo pede atenção: o verde é reservado ao ponto do estado.
from .v2_base import Ctx, P, mix, JB, ROBOTO, OK, WARN, CRIT, NA, NEUTRAL


def draw_frame(vm):
    cx = Ctx(vm, "SILÊNCIO")
    v, c = cx.v, cx.c
    quieto, claro = P["sub"], mix(P["white"], P["bg"], 0.12)
    cor = lambda lv: P["amber"] if lv in (WARN, 4) else P["red"] if lv == CRIT else claro
    thin = lambda n: cx.f(ROBOTO, n, "Thin")
    light = lambda n: cx.f(ROBOTO, n, "Light")
    r10, j10 = cx.f(ROBOTO, 10, "Regular"), cx.f(JB, 10, "Regular")

    # ---- a frase do estado
    frase = {OK: "Tudo certo", WARN: f"{cx.nwarn} aviso{'s' if cx.nwarn > 1 else ''}",
             CRIT: f"{cx.ncrit} crítico{'s' if cx.ncrit > 1 else ''}"}[cx.lvl]
    if "SEM DADOS" in cx.st:
        frase = "Sem dados"
    pc = cx.cor_nivel()
    if cx.on:
        c.d.ellipse((14, 31, 22, 39), fill=pc)
    else:
        c.d.ellipse((14, 31, 22, 39), outline=pc)
    cx.t("st.frase", 32, 41, frase, light(22), claro if cx.lvl == OK else pc)
    if cx.demo:
        cx.t("st.demo", 306, 41, "demonstração", r10, P["amber"], anchor="rs")
    cx.selo_versao(306, 16, cx.f(ROBOTO, 9, "Light"), mix(P["sub"], P["bg"], 0.3))

    # ---- quatro números grandes
    rp, rl = cx.ram_pct_txt()
    grandes = [("processador", v("cpu_temp")), ("placa de vídeo", v("gpu_temp")),
               ("memória", (rp, rl)), ("memória de vídeo", v("vram_pct_txt"))]
    for i, (lab, (t, lv)) in enumerate(grandes):
        x, y = 14 + (i % 2) * 150, 104 + (i // 2) * 66
        cx.t(f"big{i}.v", x, y, t.replace("°C", "°"), thin(46), cor(lv) if lv in (WARN, CRIT, 4) else P["white"])
        cx.t(f"big{i}.l", x + 2, y + 15, lab, r10, quieto)

    # ---- o resto, pequeno: rótulo minúsculo e valor
    y = 214
    def linha(itens, y, x=14):
        for nome, lab, chave in itens:
            if lab:
                b = cx.t(nome + ".l", x, y, lab, r10, quieto)
                x = b[2] + 4
            t, lv = v(chave)
            b = cx.t(nome + ".v", x, y, t.replace("RPM", ""), j10, cor(lv))
            x = b[2] + 12
        return x

    linha((("cpu.u", "uso", "cpu_util"), ("cpu.f", "", "cpu_ghz"), ("cpu.l", "carga", "cpu_load")), y)
    y += 16
    x = linha((("gpu.u", "vídeo", "gpu_util"), ("gpu.f", "", "gpu_mhz"), ("gpu.w", "", "gpu_w")), y)
    t, _ = v("gpu_wlim"); b = cx.t("gpu.lim", x - 10, y, "/" + t.replace("LIM ", ""), j10, quieto)
    linha((("gpu.fan", "fan", "gpu_fan_pct"), ("gpu.fps", "fps", "fps")), y, b[2] + 10)
    y += 16
    x = linha((("vram", "vram", "vram_txt"),), y)
    t, _ = v("ram_used"); t2, _ = v("ram_total")
    b = cx.t("ram.l", x, y, "ram", r10, quieto)
    b = cx.t("ram.v", b[2] + 4, y, t + t2, j10, cor(v("ram_used")[1]))
    linha((("ram.d", "livre", "ram_avail"),), y, b[2] + 12)

    y += 22
    for i, d in enumerate(cx.discos()):
        cx.t(f"d{i}.n", 14, y, d["name"].lower(), r10, quieto)
        ub = cx.t(f"d{i}.u", 50, y, d["use"], j10, cor(d.get("use_lvl", NA)))
        pb = cx.t(f"d{i}.p", ub[2] + 8, y, d["pct_txt"], j10, cor(d["lvl"]))
        cx.t(f"d{i}.f", pb[2] + 10, y, f"{d['free']} livre" if d["free"] != "--" else "", r10, cor(d["lvl"]) if d["lvl"] in (WARN, CRIT) else quieto)
        cx.t(f"d{i}.t", 306, y, d.get("temp_txt", "N/D").replace("°C", "°"), j10, cor(d.get("temp_lvl", NA)), anchor="rs")
        y += 15
    bs = cx.baias()
    if bs:
        b = cx.t("bay.l", 14, y, "gabinete", r10, quieto)
        x = 64
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") if bb.get("use") else (bb["cap"] or bb["palavra"].lower())
            nb = cx.t(f"bay{i}.n", x, y, str(bb["n"]), r10, quieto)
            sb = cx.t(f"bay{i}.v", nb[2] + 3, y, s, j10, claro if bb["estado"] == "MONT" else quieto)
            x = sb[2] + 12
        y += 15

    y += 15
    linha((("pump", "bomba", "pump"), ("rad", "radiador", "cpu_fan"), ("inf", "inf", "fan_sqi"),
           ("lat", "lat", "fan_sql"), ("tra", "tra", "fan_sqt")), y)
    y += 16
    linha((("placa", "placa", "t_placa"), ("tram", "ram", "t_ram"), ("tssd", "ssd", "t_ssd")), y)

    y += 22
    t, _ = v("net_down"); b = cx.t("net.d", 14, y, "↓ " + t, j10, claro)
    t, _ = v("net_up"); b = cx.t("net.u", b[2] + 10, y, "↑ " + t, j10, claro)
    linha((("png", "ping", "ping"),), y, b[2] + 14)
    t, lv = v("inet"); cx.t("inet", 306, y, t.lower(), r10, cor(lv) if lv in (WARN, CRIT) else quieto, anchor="rs")
    y += 16
    for k, tag in (("eth", "cabo"), ("wifi", "wi-fi")):
        d = cx.iface(k)
        b = cx.t(f"{k}.l", 14, y, tag, r10, quieto)
        sb = cx.t(f"{k}.s", 50, y, d["state"][0].lower(), j10, cor(d["state"][1]))
        rb = cx.t(f"{k}.r", 306, y, d["rates"][0], j10, quieto, anchor="rs")
        cx.t(f"{k}.i", sb[2] + 8, y, cx.fit(d["info"][0].lower(), j10, (rb[0] if d["rates"][0] else 306) - sb[2] - 16), j10,
             cor(d["info"][1]) if d["info"][1] in (WARN, CRIT) else quieto)
        y += 15
    linha((("rx", "recebido", "net_rx"), ("tx", "enviado", "net_tx")), y)

    # ---- rodapé: hora fina, data e tempo em texto pequeno
    t, _ = v("clock"); cx.t("sys.clock", 12, 466, t[:5], thin(40), P["white"])
    t, _ = v("date"); cx.t("sys.date", 306, 438, t.lower(), r10, claro, anchor="rs")
    t, lv = v("wtemp"); tb = cx.t("wx.t", 306, 453, t, j10, claro, anchor="rs")
    cx.t("wx.c", 306, 467, cx.fit(v.raw("city", "").title(), r10, 140), r10, quieto, anchor="rs")
    t, lv = v("uptime"); b = cx.t("sys.up", 116, 452, "ligado há " + t, r10, quieto)
    t, lv = v("wdesc"); cx.t("wx.d", tb[0] - 8, 453, cx.fit(t.lower(), r10, tb[0] - 16 - b[2]), r10, quieto, anchor="rs")
    t, _ = v("os"); cx.t("sys.os", 116, 466, cx.fit(t.lower(), r10, 80), r10, mix(quieto, P["bg"], 0.3))
    t, lv = v("wage"); cx.t("wx.age", 306, 478, cx.fit(t.lower(), cx.f(ROBOTO, 8, "Regular"), 140), cx.f(ROBOTO, 8, "Regular"),
                            mix(quieto, P["bg"], 0.3), anchor="rs")
    for k in ("coleta", "cpu_pct", "gpu_pct", "vram_pct"):
        v.raw(k)
    return cx.fim(None)
