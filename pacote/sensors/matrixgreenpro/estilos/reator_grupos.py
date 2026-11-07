# GAMMA GAMMA | motor por grupos | versão 1.7.0 | 07/11/2026 19:00 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.7.1 07/11/2026 19:10 gancho P['extra'] (gráficos do GAMMA DELTA)
# histórico: 1.7.0 07/11/2026 19:00 opções do GAMMA DELTA na paleta (colmeia_x, texto_y, baias_uso, rodape_enxuto)
# histórico: 1.6.0 07/11/2026 14:15 selo de estilo e versão
# Base: GAMMA BETA (escala N0/N1/N2, percentuais entre parênteses, informações coladas à esquerda).
# Reorganiza a colmeia e o texto por grupos: CPU, GPU, RAM, DISCOS, REFRIGERAÇÃO, REDE e SISTEMA.
# Três variantes de colmeia:
#   colmeia = uma colmeia de 19 células, cada grupo numa região contígua, rótulos dos grupos nas margens
#   mini    = uma mini-colmeia por grupo, com título; o texto abaixo traz os detalhes
#   painel  = colmeia grande de 24 células com quase tudo; o texto só traz o que não cabe nela
#   resumo  = GAMMA GAMMA definitivo: 7 colmeias (CORE no centro e o resumo OK/ATEN/CRIT de cada grupo ao redor);
#             todos os números ficam no painel de texto, por grupo
import math

from .base import Canvas, VM, font, JB, ROBOTO, W, OK, WARN, CRIT, NA, LOST, NEUTRAL, bloom, iface_row
from .reator import cell_values, hexagon, short

GRUPOS = ("CPU", "GPU", "RAM", "DISCOS", "REFRIGERAÇÃO", "REDE", "SISTEMA")


def _base(vm_dict, P):
    v = VM(vm_dict)
    c = Canvas(P["bg"])
    if P.get("deco"):
        P["deco"](c, P)
    LV = {OK: P["ice"], WARN: P["amber"], CRIT: P["red"], NA: P["sub"], LOST: P["amber"], NEUTRAL: P["white"]}
    col = lambda lv: LV.get(lv, P["white"])
    F = {
        "h": font(ROBOTO, 11, "Bold"), "hs": font(ROBOTO, 9, "Bold"), "g": font(ROBOTO, 9, "Bold"),
        "hv": font(JB, 11, "Bold"), "hvs": font(JB, 10, "Bold"), "xl": font(JB, 20, "Bold"),
        "m": font(JB, 14, "Bold"), "sb": font(JB, 12, "Bold"), "s": font(JB, 12, "Regular"),
        "xs": font(JB, 11, "Regular"),
    }
    tb = c.text("hdr.title", 6, 17, P["title"], font(ROBOTO, 15, "Bold"), P["accent"])
    if P.get("subtitle"):
        tb = c.text("hdr.sub", tb[2] + 6, 17, P["subtitle"], F["xs"], P["sub"])
    if v.raw("demo"):
        c.text("hdr.demo", tb[2] + 8, 17, "DEMO", F["xs"], P["amber"])
    from .base import selo_versao
    selo_versao(c, P, font(JB, 11, "Bold"))
    st, slv = v("hdr_status")
    c.line((0, 24, W, 24), P["dim"])
    from .alerta import draw_status
    vals = cell_values(v, slv, True)
    vals.update({"rad": ("RAD", v("cpu_fan")), "sqi": ("INF", v("fan_sqi")), "sql": ("LAT", v("fan_sql")),
                 "sqt": ("TRA", v("fan_sqt"))})
    draw_status(c, v, P, P.get("alert", "n3_esq"), vm_dict.get("blink"), st, slv, col, vals)
    return v, c, col, F, vals


def _cell(c, P, col, vals, key, cx, cy, r, f_lab, f_val):
    CELL = dict(P["cells"]); CELL[LOST] = CELL[WARN]
    lab, (t, lv) = vals[key]
    k = lv if lv in CELL else NEUTRAL
    fill, edge = CELL[k if t != "N/D" else NA]
    c.poly(hexagon(cx, cy, r), fill=fill, outline=edge, width=2 if lv in (OK, WARN, CRIT) else 1)
    dy = r * 0.18
    c.text(f"hex.{key}.lab", cx, cy - dy, lab, f_lab, P["sub"] if lv != NEUTRAL else P["white"], anchor="ms")
    c.text(f"hex.{key}.val", cx, cy + dy + (8 if r < 20 else 9), short(t), f_val, col(lv), anchor="ms")


def _colmeia(c, P, col, vals, F, layout, r, gap, cy0, f_lab=None, f_val=None, cx=160):
    """layout: lista de linhas; cada célula é (deslocamento em meias-colunas, chave). Devolve a base da colmeia."""
    sx, sy = math.sqrt(3) * r + gap, 1.5 * r + gap
    for ri, row in enumerate(layout):
        for off, key in row:
            _cell(c, P, col, vals, key, cx + off * sx / 2, cy0 + ri * sy, r,
                  f_lab or (F["h"] if r >= 20 else F["hs"]), f_val or (F["hv"] if r >= 20 else F["hvs"]))
    return cy0 + (len(layout) - 1) * sy + r


def _rotulo(c, P, F, nome, x, y, anchor="ls"):
    c.text(f"grp.{nome}", x, y, nome, F["g"], P["accent"], anchor=anchor)


def _titulo(c, P, F, nome, y):
    """Divisória com o nome do grupo: 'DISCOS ─────────'. Ocupa 10 px."""
    b = c.text(f"tit.{nome}", 6, y + 7, nome, F["g"], P["accent"])
    c.line((b[2] + 5, y + 4, 314, y + 4), P["dim"])
    return y + 9


def _pair(c, P, col, name, x, y, lab, val, fv, lv, F, right=False):
    wl = c.width(lab, F["xs"]) + 4 if lab else 0
    wv = c.width(val, fv)
    if right:
        x = x - wl - wv
    if lab:
        c.text(name + ".lab", x, y, lab, F["xs"], P["sub"])
    c.text(name + ".val", x + wl, y, val, fv, col(lv))
    return x, x + wl + wv


def _paren(s):
    return f"({s})" if str(s).endswith("%") else s


def _texto(c, v, P, col, F, vals, y, enxuto=False, step=13):
    """Registro por grupos. enxuto=True (painel): só o que não está na colmeia."""
    v.raw("cpu_pct"); v.raw("gpu_pct"); v.raw("vram_pct")
    # CPU
    y = _titulo(c, P, F, "CPU", y) + step - 2
    t, lv = v("cpu_ghz"); _, xe = _pair(c, P, col, "cpu.ghz", 6, y, "FREQ", t, F["sb"], lv, F)
    t, lv = v("cpu_load")
    _pair(c, P, col, "cpu.load", 314, y, "LOAD", t, F["s"], lv, F, right=True)
    # GPU
    y = _titulo(c, P, F, "GPU", y + 5) + step - 2
    t, lv = v("gpu_mhz"); _, xe = _pair(c, P, col, "gpu.mhz", 6, y, "FREQ", t, F["sb"], lv, F)
    t, lv = v("vram_txt"); _, xe = _pair(c, P, col, "gpu.vram", xe + 10, y, "VRAM", t, F["sb"], lv, F)
    if not enxuto:
        pt, pl = vals["vram"][1]
        c.text("gpu.vrampct", xe + 5, y, _paren(pt), F["sb"], col(pl))
    if enxuto:
        t, _ = v("gpu_wlim"); c.text("gpu.wlim", 314, y, t, F["xs"], P["sub"], anchor="rs")
        v.raw("gpu_w"); v.raw("gpu_fan_rpm")
        v.raw("gpu_fan_pct"); v.raw("fps")
    else:
        y += step
        t, lv = v("gpu_w"); _, xe = _pair(c, P, col, "gpu.w", 6, y, "W", t, F["sb"], lv, F)
        t, _ = v("gpu_wlim"); b = c.text("gpu.wlim", xe + 6, y, t, F["xs"], P["sub"])
        t, lv = v("fps"); _, xe = _pair(c, P, col, "gpu.fps", b[2] + 12, y, "FPS", t, F["sb"], lv, F)
        v.raw("gpu_fan_rpm")
        t, lv = v("gpu_fan_pct"); _pair(c, P, col, "gpu.fan", 314, y, "FAN", t, F["sb"], lv, F, right=True)
    # RAM
    y = _titulo(c, P, F, "RAM", y + 5) + step - 2
    t, lv = v("ram_used"); _, xe = _pair(c, P, col, "ram.used", 6, y, "USO", t, F["sb"], lv, F)
    t2, _ = v("ram_total"); rb = c.text("ram.total", xe + 1, y, t2, F["sb"], P["white"])
    pb = rb
    if not enxuto:
        pt, pl = vals["ram"][1]
        pb = c.text("ram.pct", rb[2] + 6, y, _paren(pt), F["sb"], col(pl))
    t, lv = v("ram_avail"); _pair(c, P, col, "ram.avail", pb[2] + 12, y, "DISP", t, F["sb"], lv, F)
    # DISCOS
    y = _titulo(c, P, F, "DISCOS", y + 5)
    for i, d in enumerate(v.raw("disks", [])[:3]):
        y += step
        c.text(f"dsk{i}.name", 6, y, d["name"], F["sb"], P["white"])
        ub = c.text(f"dsk{i}.use", 44, y, d["use"], F["s"], col(d.get("use_lvl", NEUTRAL)))
        x = ub[2] + 6
        if not enxuto:
            pbx = c.text(f"dsk{i}.pct", x, y, _paren(d["pct_txt"]), F["sb"], col(d["lvl"]))
            x = pbx[2] + 10
        fb = c.text(f"dsk{i}.free", x, y, d["free"], F["sb"], col(d["lvl"]))
        c.text(f"dsk{i}.freelab", fb[2] + 4, y, "LIVRE", F["xs"], P["sub"])
    # REFRIGERAÇÃO (no painel tudo já está na colmeia)
    if enxuto:
        for k in ("pump", "cpu_fan", "t_placa", "t_ram", "t_ssd"):
            v.raw(k)
        for k in ("fan_sqi", "fan_sql", "fan_sqt"):
            v.raw(k)
    else:
        y = _titulo(c, P, F, "REFRIGERAÇÃO", y + 5) + step - 2
        x = 6
        for nome, lab, chave in (("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("sqi", "INF", "fan_sqi"),
                                 ("sql", "LAT", "fan_sql"), ("sqt", "TRA", "fan_sqt")):
            t, lv = v(chave)
            _, x = _pair(c, P, col, "fan." + nome, x, y, lab, t.replace("RPM", ""), F["s"], lv, F)
            x += 8
    # REDE
    y = _titulo(c, P, F, "REDE", y + 5) + step - 1
    t, _ = v("net_down"); b = c.text("net.down", 6, y, "↓" + t, F["sb"], P["white"])
    t, _ = v("net_up"); b = c.text("net.up", b[2] + 8, y, "↑" + t, F["sb"], P["white"])
    t, lv = v("net_tx"); tb = _pair(c, P, col, "net.tx", 314, y, "TX", t, F["s"], lv, F, right=True)
    t, lv = v("net_rx"); _pair(c, P, col, "net.rx", tb[0] - 8, y, "RX", t, F["s"], lv, F, right=True)
    for key, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        y += step
        iface_row(c, v, key, y, 6, tag, 44, 314, F["xs"], F["sb"], F["xs"], F["xs"], col, P["sub"],
                  c_info=P["white"], c_rates=P["white"])
    # SISTEMA
    y = _titulo(c, P, F, "SISTEMA", y + 5) + 20
    t, _ = v("clock"); c.text("sys.clock", 6, y, t, F["xl"], P["accent"])
    t, _ = v("date"); c.text("sys.date", 314, y - 9, t, F["sb"], P["white"], anchor="rs")
    t, lv = v("uptime"); _pair(c, P, col, "sys.up", 314, y + 4, "UP", t, F["s"], lv, F, right=True)
    y += step + 1
    t, _ = v("os"); ob = c.text("sys.os", 6, y, t, F["xs"], P["sub"])
    t, lv = v("wage"); ab = c.text("wx.age", 314, y + 1, t, F["xs"], col(lv) if lv != NA else P["sub"], anchor="rs")
    t, lv = v("wdesc"); c.text("wx.desc", ab[0] - 8, y + 1, c.fit(t, F["xs"], ab[0] - ob[2] - 18), F["xs"],
                               col(lv) if lv != NA else P["sub"], anchor="rs")
    y += step
    t, lv = v("ping"); b = c.text("png.val", 6, y, "PING " + t, F["sb"], col(lv))
    t, lv = v("inet"); c.text("inet", b[2] + 6, y, t, F["xs"], col(lv))
    t, lv = v("wtemp"); b = c.text("wx.temp", 314, y, t, F["sb"], col(lv), anchor="rs")
    c.text("wx.city", b[0] - 5, y, v.raw("city", ""), F["xs"], P["sub"], anchor="rs")
    return _rodape(c, v, P, col, F, max(y + step, 474))


def _pior(niveis):
    """Pior nível entre os indicadores com dado. Sem dado nenhum: NA (N/D). LOST conta como atenção."""
    n = [x for x in niveis if x in (OK, WARN, CRIT, LOST)]
    return CRIT if CRIT in n else WARN if (WARN in n or LOST in n) else OK if OK in n else NA


def _resumos(v, vals):
    """Resumo de cada grupo com só 3 estados (OK, ATEN, CRIT) ou N/D quando não há dado."""
    lv = lambda *ks: [vals[k][1][1] for k in ks]
    grupos = {
        "g_cpu": ("CPU", lv("cpu", "cput")),
        "g_gpu": ("GPU", lv("gpu", "gput", "vram", "gpuw", "gfan")),
        "g_ram": ("RAM", lv("ram", "tram")),
        "g_dsk": ("DISCOS", lv("d0", "d1", "d2", "tssd") + [d.get("temp_lvl", NA) for d in v.raw("disks", [])]),
        "g_ref": ("REFR.", lv("cfan", "rad", "sqi", "sql", "sqt")),
        "g_rede": ("REDE", lv("ping", "rede") + [v("inet")[1]]),
    }
    out = {}
    for k, (nome, niveis) in grupos.items():
        n = _pior(niveis)
        out[k] = (nome, ({OK: "OK", WARN: "ATEN", CRIT: "CRIT"}.get(n, "N/D"), n))
    return out


def _titulo_dados(c, P, F, nome, y, desenhos):
    """Título do grupo com os dados-chave à direita (ocupa 11 px; economiza uma linha de texto por grupo).
    Cada item de 'desenhos' desenha alinhado à direita em x e devolve o novo x esquerdo."""
    x = 314
    for fn in desenhos:
        x = fn(x, y + 9) - 8
    b = c.text(f"tit.{nome}", 6, y + 7, nome, F["g"], P["accent"])
    c.line((b[2] + 5, y + 4, x + 3, y + 4), P["dim"])
    return y + 11


def _texto_resumo(c, v, P, col, F, vals, y, step=13, gap=4):
    """Painel numérico por grupo (todos os dados que saíram da colmeia estão aqui). Termina com o SISTEMA fixo embaixo."""
    v.raw("cpu_pct"); v.raw("gpu_pct"); v.raw("vram_pct"); v.raw("gpu_fan_rpm")
    for k in ("power", "power_tag", "coleta"):                  # removidos da tela
        v.raw(k)

    def linha(y, itens, x=6, folga=12):
        for nome, lab, chave in itens:
            t, lv = v(chave)
            _, x = _pair(c, P, col, nome, x, y, lab, t.replace("RPM", ""), F["sb"], lv, F)
            x += folga
        return x

    def par(nome, lab, chave):                                  # item de título: "LAB valor" à direita
        def f(x, yy):
            t, lv = v(chave)
            return _pair(c, P, col, nome, x, yy, lab, t.replace("RPM", ""), F["sb"], lv, F, right=True)[0]
        return f

    # CPU (LOAD no título)
    y = _titulo_dados(c, P, F, "CPU", y, [par("cpu.load", "LOAD", "cpu_load")]) + step - 2
    linha(y, (("cpu.util", "USO", "cpu_util"), ("cpu.temp", "TEMP", "cpu_temp"), ("cpu.ghz", "FREQ", "cpu_ghz")))
    # GPU (FPS e FAN no título)
    y = _titulo_dados(c, P, F, "GPU", y + gap + 1, [par("gpu.fan", "FAN", "gpu_fan_pct"), par("gpu.fps", "FPS", "fps")]) + step - 2
    linha(y, (("gpu.util", "USO", "gpu_util"), ("gpu.temp", "TEMP", "gpu_temp"), ("gpu.mhz", "FREQ", "gpu_mhz")))
    y += step
    t, lv = v("vram_txt"); _, xe = _pair(c, P, col, "gpu.vram", 6, y, "VRAM", t, F["sb"], lv, F)
    pt, pl = vals["vram"][1]; c.text("gpu.vrampct", xe + 5, y, _paren(pt), F["sb"], col(pl))
    t, _ = v("gpu_wlim"); b = c.text("gpu.wlim", 314, y, t, F["xs"], P["sub"], anchor="rs")
    t, lv = v("gpu_w"); _pair(c, P, col, "gpu.w", b[0] - 6, y, "W", t, F["sb"], lv, F, right=True)
    # RAM (TEMP no título)
    y = _titulo_dados(c, P, F, "RAM", y + gap + 1, [par("ram.temp", "TEMP", "t_ram")]) + step - 2
    t, lv = v("ram_used"); _, xe = _pair(c, P, col, "ram.used", 6, y, "USO", t, F["sb"], lv, F)
    t2, _ = v("ram_total"); rb = c.text("ram.total", xe + 1, y, t2, F["sb"], P["white"])
    pt, pl = vals["ram"][1]; pb = c.text("ram.pct", rb[2] + 6, y, _paren(pt), F["sb"], col(pl))
    t, lv = v("ram_avail"); _pair(c, P, col, "ram.avail", pb[2] + 12, y, "DISP", t, F["sb"], lv, F)
    # DISCOS (a temperatura de cada disco fica à direita da linha)
    y = _titulo(c, P, F, "DISCOS", y + gap)
    discos = v.raw("disks", [])[:3]
    for i, d in enumerate(discos):
        y += step
        c.text(f"dsk{i}.name", 6, y, d["name"], F["sb"], P["white"])
        ub = c.text(f"dsk{i}.use", 44, y, d["use"], F["s"], col(d.get("use_lvl", NEUTRAL)))
        pbx = c.text(f"dsk{i}.pct", ub[2] + 6, y, _paren(d["pct_txt"]), F["sb"], col(d["lvl"]))
        fb = c.text(f"dsk{i}.free", pbx[2] + 10, y, d["free"], F["sb"], col(d["lvl"]))
        c.text(f"dsk{i}.freelab", fb[2] + 4, y, "LIVRE", F["xs"], P["sub"])
        c.text(f"dsk{i}.temp", 314, y, d.get("temp_txt", "N/D"), F["sb"], col(d.get("temp_lvl", NA)), anchor="rs")
    v.raw("t_ssd")                                              # o NVMe aparece na linha do próprio disco
    # TERRAMASTER (só aparece quando o gabinete de baias foi encontrado): 2 colunas x 2 linhas
    baias = v.raw("baias", [])
    if baias:
        y = _titulo(c, P, F, "TERRAMASTER", y + gap + 3) + step - 2
        for i, b in enumerate(baias[:4]):
            x = 6 if i % 2 == 0 else 164
            if i and i % 2 == 0:
                y += step - 1
            bx = c.text(f"bay{i}.n", x, y, f"{b['n']}", F["sb"], P["accent"])
            if P.get("baias_uso") and b.get("use"):             # DELTA: ocupado/total e percentual, como nos discos
                ub = c.text(f"bay{i}.use", bx[2] + 5, y, b["use"], F["s"], P["white"])
                c.text(f"bay{i}.pct", ub[2] + 5, y, _paren(b["pct_txt"]), F["sb"], col(b.get("pct_lvl", OK)))
                continue
            if b["cap"]:
                bx = c.text(f"bay{i}.cap", bx[2] + 5, y, b["cap"], F["sb"], col(b["lvl"]))
            c.text(f"bay{i}.st", bx[2] + 5, y, b["palavra"], F["xs"], col(b["lvl"]))
    # REFRIGERAÇÃO
    y = _titulo(c, P, F, "REFRIGERAÇÃO", y + gap + 1) + step - 2
    linha(y, (("fan.pump", "BOMBA", "pump"), ("fan.rad", "RAD", "cpu_fan"), ("fan.placa", "PLACA", "t_placa")))
    y += step
    linha(y, (("fan.sqi", "SQUAMA INF", "fan_sqi"), ("fan.sql", "LAT", "fan_sql"), ("fan.sqt", "TRA", "fan_sqt")))
    # REDE (PING e internet no título)
    def inet_txt(x, yy):
        t, lv = v("inet"); return c.text("inet", x, yy, t, F["xs"], col(lv), anchor="rs")[0]
    y = _titulo_dados(c, P, F, "REDE", y + gap + 3, [inet_txt, par("png", "PING", "ping")]) + step - 1
    t, _ = v("net_down"); b = c.text("net.down", 6, y, "↓" + t, F["sb"], P["white"])
    t, _ = v("net_up"); c.text("net.up", b[2] + 8, y, "↑" + t, F["sb"], P["white"])
    t, lv = v("net_tx"); tb = _pair(c, P, col, "net.tx", 314, y, "TX", t, F["s"], lv, F, right=True)
    t, lv = v("net_rx"); _pair(c, P, col, "net.rx", tb[0] - 8, y, "RX", t, F["s"], lv, F, right=True)
    for key, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        y += step
        iface_row(c, v, key, y, 6, tag, 44, 314, F["xs"], F["sb"], F["xs"], F["xs"], col, P["sub"],
                  c_info=P["white"], c_rates=P["white"])
    # SISTEMA (à esquerda) e clima (canto inferior direito, sem moldura), alinhados no rodapé da tela
    enxuto = P.get("rodape_enxuto")                         # DELTA: sem a linha do sistema e a idade do clima
    ys = 419 + (14 if enxuto else 0)
    b = c.text("tit.SISTEMA", 6, ys + 7, "SISTEMA", F["g"], P["accent"])
    c.line((b[2] + 5, ys + 4, 196, ys + 4), P["dim"])
    t, _ = v("date"); c.text("sys.date", 6, ys + 21, t, F["sb"], P["white"])
    t, _ = v("clock"); c.text("sys.clock", 6, ys + 43, t, F["xl"], P["accent"])
    t, lv = v("uptime"); _pair(c, P, col, "sys.up", 196, ys + 43, "UP", t, F["s"], lv, F, right=True)
    if enxuto:
        v.raw("os"); v.raw("wage")
    else:
        t, _ = v("os"); c.text("sys.os", 6, ys + 58, c.fit(t, F["xs"], 190), F["xs"], P["sub"])
    c.text("wx.city", 314, ys + 7, c.fit(v.raw("city", ""), F["xs"], 100), F["xs"], P["sub"], anchor="rs")
    t, lv = v("wtemp"); c.text("wx.temp", 314, ys + 29, t, F["xl"], col(lv), anchor="rs")
    t, lv = v("wdesc"); c.text("wx.desc", 314, ys + 42, c.fit(t, F["xs"], 106), F["xs"],
                               col(lv) if lv != NA else P["sub"], anchor="rs")
    if not enxuto:
        t, lv = v("wage"); c.text("wx.age", 314, ys + 56, c.fit(t, F["xs"], 106), F["xs"],
                                  col(lv) if lv != NA else P["sub"], anchor="rs")
    return y


def _rodape(c, v, P, col, F, y):
    t, lv = v("power"); _, xe = _pair(c, P, col, "pwr", 6, y, "TOTAL W", t, F["sb"], lv, F)
    t, _ = v("power_tag"); tb = c.text("pwr.tag", xe + 6, y, t, F["xs"], P["sub"])
    t, lv = v("coleta"); c.text("coleta", 314, y, c.fit(t, F["xs"], 314 - tb[2] - 8), F["xs"], col(lv), anchor="rs")
    return y


def _fronteiras(c, P, lay, grupo, r, gap, cy0, brancas=False):
    """Fronteiras como num mapa: tracejado entre células de grupos diferentes, linha contínua na borda externa.
    As linhas correm no vão entre as células (hexágono de raio sx/√3, a meio caminho entre dois centros)."""
    sx, sy = math.sqrt(3) * r + gap, 1.5 * r + gap
    pos = {(ri, off): key for ri, row in enumerate(lay) for off, key in row}
    R = sx / math.sqrt(3)
    viz = [(-1, 1), (0, 2), (1, 1), (1, -1), (0, -2), (-1, -1)]    # aresta k: vértices k e k+1 (pontas para cima)
    for (ri, off), key in pos.items():
        pts = hexagon(160 + off * sx / 2, cy0 + ri * sy, R)
        for k, (dr, do) in enumerate(viz):
            a, b = pts[k], pts[(k + 1) % 6]
            nb = pos.get((ri + dr, off + do))
            if nb is None:
                c.line((a, b), P["dim"], 1)                        # costa: contorno externo
            elif brancas and grupo[nb] != grupo[key] and (ri, off) < (ri + dr, off + do):
                n = 5                                               # fronteira: traço e espaço alternados
                for i in range(0, n, 2):
                    p0 = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                    p1 = (a[0] + (b[0] - a[0]) * (i + 1) / n, a[1] + (b[1] - a[1]) * (i + 1) / n)
                    c.line((p0, p1), P["white"], 2)


def render_grupos(vm_dict, P, variante):
    v, c, col, F, vals = _base(vm_dict, P)
    if variante == "colmeia":
        # 3-4-5-4-3: CPU no alto à esquerda, GPU à direita, REFRIGERAÇÃO e RAM à esquerda, DISCOS e REDE embaixo
        lay = [[(-2, "cpu"), (0, "cput"), (2, "gpu")],
               [(-3, "cfan"), (-1, "rad"), (1, "gput"), (3, "vram")],
               [(-4, "tplaca"), (-2, "ram"), (0, "core"), (2, "gpuw"), (4, "fps")],
               [(-3, "tram"), (-1, "d0"), (1, "d1"), (3, "d2")],
               [(-2, "tssd"), (0, "rede"), (2, "ping")]]
        base = _colmeia(c, P, col, vals, F, lay, 19, 2, 46)
        # rótulos nas margens, ao lado de cada região (CPU dispensa: as células já dizem CPU e CPU°)
        _rotulo(c, P, F, "REFRIGERAÇÃO", 4, 80)
        _rotulo(c, P, F, "RAM", 86, 141, anchor="rs")
        _rotulo(c, P, F, "DISCOS", 104, 171, anchor="rs")
        _rotulo(c, P, F, "GPU", 234, 80)
        _rotulo(c, P, F, "REDE", 216, 171)
        y = base + 2
    elif variante == "mini":
        # uma mini-colmeia de 2 linhas por grupo, em duas faixas de três grupos
        r, gap = 17, 2
        sx, sy = math.sqrt(3) * r + gap, 1.5 * r + gap
        grupos = [
            ("CPU", 124, 34, [[(-1, "cpu"), (1, "cput")], [(0, "load")]]),
            ("GPU", 212, 34, [[(-2.5, "gpu"), (-0.5, "gput"), (1.5, "vram")], [(-1.5, "gpuw"), (0.5, "fps"), (2.5, "gfan")]]),
            ("RAM", 292, 34, [[(-0.5, "ram")], [(0.5, "tram")]]),
            ("REFRIGERAÇÃO", 62, 106, [[(-2.5, "cfan"), (-0.5, "rad"), (1.5, "tplaca")],
                                       [(-1.5, "sqi"), (0.5, "sql"), (2.5, "sqt")]]),
            ("DISCOS", 168, 106, [[(-1.5, "d0"), (0.5, "d1")], [(-0.5, "d2"), (1.5, "tssd")]]),
            ("REDE", 270, 106, [[(-0.5, "rede")], [(0.5, "ping")]]),
        ]
        base = 0
        for nome, cx, ty, lay in grupos:
            _rotulo(c, P, F, nome, cx, ty + 2, anchor="ms")
            for ri, row in enumerate(lay):
                for off, key in row:
                    _cell(c, P, col, vals, key, cx + off * sx / 2, ty + 6 + r + ri * sy, r, F["hs"], F["hvs"])
            base = max(base, ty + 6 + r + (len(lay) - 1) * sy + r)
        y = base + 1
    elif variante == "resumo":
        # 7 colmeias: CORE no centro e o resumo (OK, ATEN, CRIT) de cada grupo ao redor; números só no painel
        vals.update(_resumos(v, vals))
        lay = [[(-1, "g_cpu"), (1, "g_gpu")],
               [(-2, "g_ref"), (0, "core"), (2, "g_ram")],
               [(-1, "g_rede"), (1, "g_dsk")]]
        _colmeia(c, P, col, vals, F, lay, 21, 2, 49, f_lab=F["hs"], f_val=F["hv"], cx=P.get("colmeia_x", 160))
        _texto_resumo(c, v, P, col, F, vals, P.get("texto_y", 137))
        if P.get("extra"):                                      # desenho a mais do estilo (ex.: gráficos de 24 h)
            P["extra"](c, v, P, col, F)
        if P.get("bloom"):
            c.img = bloom(c.img, *P["bloom"])
        return c, v
    else:   # painel
        # 4-5-6-5-4 = 24 células
        lay = [[(-3, "cpu"), (-1, "cput"), (1, "gpu"), (3, "gput")],
               [(-4, "load"), (-2, "cfan"), (0, "core"), (2, "vram"), (4, "gfan")],
               [(-5, "rad"), (-3, "sqi"), (-1, "tplaca"), (1, "gpuw"), (3, "fps"), (5, "ram")],
               [(-4, "sql"), (-2, "sqt"), (0, "d0"), (2, "d1"), (4, "tram")],
               [(-3, "rede"), (-1, "ping"), (1, "d2"), (3, "tssd")]]
        base = _colmeia(c, P, col, vals, F, lay, 19, 2, 50)
        _rotulo(c, P, F, "REFRIGERAÇÃO", 4, 145)
        _rotulo(c, P, F, "GPU", 314, 50, anchor="rs")
        _rotulo(c, P, F, "RAM", 314, 112, anchor="rs")
        _rotulo(c, P, F, "DISCOS", 314, base - 6, anchor="rs")
        _rotulo(c, P, F, "REDE", 60, base - 6)
        y = base + 2
    _texto(c, v, P, col, F, vals, y, enxuto=(variante == "painel"))
    if P.get("bloom"):
        c.img = bloom(c.img, *P["bloom"])
    return c, v
