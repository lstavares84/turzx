# GAMMA v2 ESPIONAGEM "DOSSIÊ" | versão 0.1.0 | 07/11/2026 20:20 (-03) | criação original (Claude, para Lucas Tavares)
# Ficha de agente datilografada: cabeçalho "CONFIDENCIAL", campos com sublinhado pontilhado, carimbo girado com o
# veredito (LIMPO, SOB VIGILÂNCIA, COMPROMETIDO), tarjas de censura nos identificadores que não interessam ao
# leitor e um rodapé de transmissão. Tipografia de máquina de escrever (Generale Mono e Roboto Mono).
from PIL import Image, ImageDraw

from .v2_base import Ctx, P, mix, JB, ROBOTO_MONO, GENERALE, OK, WARN, CRIT, NA


def _campo(cx, nome, x, y, w, rotulo, chave=None, texto=None, lv=None, f=None, fl=None):
    """Campo de ficha: rótulo, linha pontilhada até o valor, valor alinhado à direita."""
    fl = fl or cx.f(ROBOTO_MONO, 9, "Regular")
    f = f or cx.f(ROBOTO_MONO, 11, "Bold")
    if chave:
        texto, lv = cx.v(chave)
    b = cx.t(nome + ".r", x, y, rotulo, fl, P["sub"])
    vb = cx.t(nome + ".v", x + w, y, texto, f, cx.col(lv, P["white"]), anchor="rs")
    for xx in range(int(b[2]) + 3, int(vb[0]) - 3, 3):
        cx.c.d.point((xx, y), fill=P["dim"])
    return vb


def _carimbo(cx, texto, cor, x, y, ang=-12):
    """Carimbo girado colado na imagem (moldura dupla e texto vazado)."""
    f = cx.f(ROBOTO_MONO, 15, "Bold")
    w = int(cx.c.width(texto, f)) + 18
    im = Image.new("RGBA", (w, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, 29), outline=cor + (255,), width=2)
    d.rectangle((3, 3, w - 4, 26), outline=cor + (200,), width=1)
    d.text((w // 2, 21), texto, font=f, fill=cor + (255,), anchor="ms")
    im = im.rotate(ang, expand=True, resample=Image.BICUBIC)
    cx.c.img.paste(im, (x - im.width // 2, y - im.height // 2), im)


def draw_frame(vm):
    cx = Ctx(vm, "DOSSIÊ")
    v, c = cx.v, cx.c
    tw = lambda n: cx.f(GENERALE, n, "A")
    rm9, rm10, rm11 = cx.f(ROBOTO_MONO, 9, "Regular"), cx.f(ROBOTO_MONO, 10, "Regular"), cx.f(ROBOTO_MONO, 11, "Bold")
    tarja = mix(P["sub"], P["bg"], 0.55)

    # ---- cabeçalho de classificação
    c.rect((0, 0, 319, 16), fill=mix(P["red"], P["bg"], 0.55) if cx.lvl == CRIT else mix(P["accent"], P["bg"], 0.82))
    cx.t("hdr.cl", 160, 12, "CONFIDENCIAL  ACESSO RESTRITO", cx.f(ROBOTO_MONO, 9, "Bold"), P["white"], anchor="ms")
    cx.t("hdr.f", 8, 38, "FICHA  GAMMA", tw(16), P["accent"])
    cx.t("hdr.p", 8, 52, "processo nº 0711-26  agente: estação", rm9, P["sub"])
    if cx.demo:
        cx.t("hdr.demo", 312, 52, "SIMULADO", rm9, P["amber"], anchor="rs")
    cx.selo_versao(312, 30, rm9, P["sub"])
    c.line((8, 58, 312, 58), P["dim"])

    # ---- veredito: carimbo
    ver = {OK: "LIMPO", WARN: "SOB VIGILÂNCIA", CRIT: "COMPROMETIDO"}[cx.lvl]
    cor = cx.cor_nivel()
    cx.t("st.r", 8, 74, "situação", rm9, P["sub"])
    cx.t("st.n", 8, 90, f"{({OK: 'N0', WARN: 'N1', CRIT: 'N2'}[cx.lvl])}  {cx.rotulo.lower()}", rm11, cor)
    if cx.on:
        _carimbo(cx, ver, cor, 236, 82)
    else:
        cx.t("st.carimbo.off", 236, 87, "", rm9, cor)

    # ---- seções da ficha
    def secao(y, titulo):
        fs = cx.f(ROBOTO_MONO, 11, "Bold")                    # a Generale não tem Ç nem Õ
        cx.t(f"sec.{titulo}", 8, y, titulo, fs, P["accent"])
        c.line((8 + cx.c.width(titulo, fs) + 6, y - 4, 312, y - 4), P["dim"])
        return y + 14

    y = secao(112, "1  PROCESSAMENTO")
    _campo(cx, "cpu.t", 8, y, 146, "temperatura", "cpu_temp")
    _campo(cx, "cpu.u", 166, y, 146, "atividade", "cpu_util")
    y += 13
    _campo(cx, "cpu.f", 8, y, 146, "frequência", "cpu_ghz", f=rm10)
    _campo(cx, "cpu.l", 166, y, 146, "carga", "cpu_load", f=rm10)
    y += 13
    _campo(cx, "gpu.t", 8, y, 146, "vídeo temp.", "gpu_temp")
    _campo(cx, "gpu.u", 166, y, 146, "vídeo uso", "gpu_util")
    y += 13
    _campo(cx, "gpu.f", 8, y, 146, "vídeo freq.", "gpu_mhz", f=rm10)
    t, _ = v("gpu_wlim"); tw_, lw = v("gpu_w")
    _campo(cx, "gpu.w", 166, y, 146, "consumo", texto=f"{tw_}W{t.replace('LIM ', '/')}", lv=lw, f=rm10)
    y += 13
    _campo(cx, "gpu.fan", 8, y, 146, "ventoinha", "gpu_fan_pct", f=rm10)
    _campo(cx, "gpu.fps", 166, y, 146, "quadros/s", "fps", f=rm10)

    y = secao(y + 20, "2  MEMÓRIA")
    t, lv = v("vram_txt"); p, pl = v("vram_pct_txt")
    _campo(cx, "vram", 8, y, 146, "vídeo", texto=f"{t} {p}", lv=pl, f=rm10)
    t, lv = v("ram_used"); t2, _ = v("ram_total"); rp, rl = cx.ram_pct_txt()
    _campo(cx, "ram", 166, y, 146, "ram", texto=f"{t}{t2} {rp}", lv=rl, f=rm10)
    y += 13
    _campo(cx, "ram.d", 8, y, 146, "ram livre", "ram_avail", f=rm10)
    _campo(cx, "ram.t", 166, y, 146, "ram temp.", "t_ram", f=rm10)

    y = secao(y + 20, "3  ARQUIVOS")
    for i, d in enumerate(cx.discos()):
        cx.t(f"d{i}.n", 8, y, d["name"], rm11, P["white"])
        ub = cx.t(f"d{i}.u", 42, y, d["use"], rm10, cx.col(d.get("use_lvl", NA), P["white"]))
        pb = cx.t(f"d{i}.p", ub[2] + 6, y, d["pct_txt"], rm11, cx.col(d["lvl"], P["white"]))
        cx.t(f"d{i}.f", pb[2] + 8, y, f"{d['free']} livres", rm9, cx.col(d["lvl"], P["sub"]))
        cx.t(f"d{i}.t", 312, y, d.get("temp_txt", "N/D"), rm11, cx.col(d.get("temp_lvl", NA), P["white"]), anchor="rs")
        y += 13
    bs = cx.baias()
    if bs:
        x = 8
        for i, bb in enumerate(bs[:4]):
            s = bb.get("pct_txt") or bb["cap"] or ""
            nb = cx.t(f"bay{i}.n", x, y, f"cx{bb['n']}", rm9, P["sub"])
            vb = cx.t(f"bay{i}.v", nb[2] + 3, y, f"{s} {bb['curta'].lower()}".strip(), rm9, cx.col(bb["lvl"], P["white"]))
            x = vb[2] + 10
        y += 13

    y = secao(y + 8, "4  CLIMATIZAÇÃO")
    x = 8
    for nome, lab, k in (("pump", "bomba", "pump"), ("rad", "rad", "cpu_fan"), ("inf", "inf", "fan_sqi"),
                         ("lat", "lat", "fan_sql"), ("tra", "tra", "fan_sqt")):
        _, x = cx.par("f." + nome, x, y, lab, k, rm9, rm10, troca=cx.sem_rpm, gap=3)
        x += 8
    y += 13
    _campo(cx, "placa", 8, y, 146, "placa-mãe", "t_placa", f=rm10)
    _campo(cx, "ssd", 166, y, 146, "ssd", "t_ssd", f=rm10)

    y = secao(y + 20, "5  COMUNICAÇÕES")
    t, _ = v("net_down"); b = cx.t("n.d", 8, y, "↓" + t, cx.f(JB, 10, "Bold"), P["white"])
    t, _ = v("net_up"); b = cx.t("n.u", b[2] + 8, y, "↑" + t, cx.f(JB, 10, "Bold"), P["white"])
    _, xe = cx.par("png", 312, y, "ping", "ping", rm9, rm10, right=True)
    t, lv = v("inet"); cx.t("inet", _ - 8, y, t.lower(), rm9, cx.col(lv), anchor="rs")
    y += 13
    for k, tag in (("eth", "cabo"), ("wifi", "rádio")):
        d = cx.iface(k)
        cx.t(f"{k}.r", 8, y, tag, rm9, P["sub"])
        sb = cx.t(f"{k}.s", 44, y, d["state"][0].lower(), rm10, cx.col(d["state"][1], P["white"]))
        if d["info"][1] in (WARN, CRIT, NA) or not d["info"][0]:              # problema ou ausência: por extenso
            cx.t(f"{k}.i", sb[2] + 8, y, cx.fit(d["info"][0].lower(), rm9, 110), rm9, cx.col(d["info"][1]))
        else:                                                                # identificador comum: censurado
            ib = cx.c.d.textbbox((sb[2] + 8, y), d["info"][0], font=rm9)
            c.rect((sb[2] + 8, y - 8, min(ib[2], sb[2] + 90), y + 1), fill=tarja)
        cx.t(f"{k}.rt", 312, y, d["rates"][0], cx.f(JB, 9, "Regular"), P["white"], anchor="rs")
        y += 12
    _, xe = cx.par("rx", 8, y, "recebido", "net_rx", rm9, rm10)
    cx.par("tx", xe + 10, y, "enviado", "net_tx", rm9, rm10)

    # ---- rodapé de transmissão
    c.line((8, 438, 312, 438), P["dim"])
    t, _ = v("date"); t2, _ = v("clock")
    cx.t("sys.ts", 8, 454, f"{t2}", tw(18), P["accent"])
    cx.t("sys.date", 8, 468, t.lower(), rm9, P["white"])
    t, lv = v("uptime"); cx.t("sys.up", 116, 452, "em campo há " + t, rm9, P["sub"])
    t, _ = v("os"); cx.t("sys.os", 116, 466, cx.fit("disfarce: " + t.lower(), rm9, 100), rm9, P["sub"])
    t, lv = v("wtemp"); cx.t("wx.t", 312, 454, t, rm11, cx.col(lv, P["white"]), anchor="rs")
    cx.t("wx.c", 312, 442, cx.fit(v.raw("city", "").lower(), rm9, 90), rm9, P["sub"], anchor="rs")
    t, lv = v("wdesc"); cx.t("wx.d", 312, 466, cx.fit(t.lower(), rm9, 90), rm9, P["white"], anchor="rs")
    t, lv = v("wage"); cx.t("wx.a", 312, 478, cx.fit(t.lower(), cx.f(ROBOTO_MONO, 8, "Regular"), 120), cx.f(ROBOTO_MONO, 8, "Regular"), P["sub"], anchor="rs")
    cx.t("sys.fim", 8, 478, "fim da transmissão", cx.f(ROBOTO_MONO, 8, "Regular"), mix(P["sub"], P["bg"], 0.3))
    for k in ("coleta", "cpu_pct", "gpu_pct", "vram_pct"):
        v.raw(k)
    return cx.fim((2, 0.5, 150))
