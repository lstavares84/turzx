# GAMMA DELTA | motor do GAMMA DELTA e das variantes | versão 0.3.0 | 07/11/2026 21:46 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 0.3.0 07/11/2026 21:46 SQUAMA mostra INF ou LAT, a que tiver leitura
# histórico: 0.2.0 07/11/2026 21:14 valor em alerta com fundo na cor do nível (alerta_inverso); passa a desenhar o GAMMA DELTA oficial
# Base: GAMMA DELTA (colmeia à direita, gráficos de 24 h, baias com uso). Acrescenta:
#   total de TB de todos os HDs (discos + baias montadas, sem contar o mesmo dispositivo duas vezes);
#   marca das mudanças bruscas (brusco.py), visível por até 10 min depois que a leitura normaliza;
#   refrigeração numa linha só (SQUAMA INF e LAT são a mesma leitura: as ventoinhas estão em série);
#   sistema compacto e um registro com as últimas mudanças bruscas.
# Cada variante combina um lugar para o total (P["total"]), um formato de registro (P["registro"]) e uma forma
# de marcar a mudança brusca (P["marca"]).
#   total:    "coluna" (à direita das linhas dos discos), "titulo" (no título DISCOS), "barra" (linha própria)
#   registro: "esq", "faixa", "caixa", "dir", "barras", "tabela"
#   marca:    "cor", "sublinhado", "caixa", "ponto", "inverso"
import time

from .alerta import mix
from .base import W, OK, WARN, CRIT, NA, LOST, NEUTRAL, bloom, iface_row, font, JB, ROBOTO
from .reator_grupos import _base, _colmeia, _resumos, _titulo, _paren
from . import graficos


class Texto:
    """Desenho do painel: valor em alerta com fundo na cor do nível (P['alerta_inverso']) e, nas variantes de
    estudo, a marca de mudança brusca nas leituras marcadas."""

    def __init__(self, c, v, P, col, F, marcadas):
        self.c, self.v, self.P, self.col, self.F = c, v, P, col, F
        self.marcadas, self.modo = marcadas, P.get("marca", "cor")

    def marcada(self, chave, lv):
        return self.modo != "nenhuma" and chave in self.marcadas and lv in (OK, NEUTRAL)

    def valor(self, nome, x, y, s, fnt, chave, lv, anchor="ls"):
        """Escreve um valor; se a leitura está marcada, aplica a marca escolhida."""
        c, P = self.c, self.P
        if P.get("alerta_inverso") and lv in (WARN, CRIT, LOST):    # valor em alerta: fundo na cor do nível
            b = c.d.textbbox((x, y), s, font=fnt, anchor=anchor)
            c.rect((b[0] - 2, b[1] - 1, b[2] + 1, b[3] + 1), fill=P["red"] if lv == CRIT else P["amber"])  # não invade as linhas vizinhas
            return c.text(nome, x, y, s, fnt, P["bg"], anchor=anchor)
        if not self.marcada(chave, lv):
            return c.text(nome, x, y, s, fnt, self.col(lv), anchor=anchor)
        amb = P["amber"]
        if self.modo == "inverso":
            b = c.d.textbbox((x, y), s, font=fnt, anchor=anchor)
            c.rect((b[0] - 2, b[1] - 2, b[2] + 1, b[3] + 2), fill=amb)
            return c.text(nome, x, y, s, fnt, P["bg"], anchor=anchor)
        cor = amb if self.modo in ("cor", "sublinhado", "ponto") else self.col(lv)
        b = c.text(nome, x, y, s, fnt, cor, anchor=anchor)
        if self.modo == "sublinhado":
            c.line((b[0], b[3] + 2, b[2], b[3] + 2), amb, 1)
        elif self.modo == "caixa":
            c.rect((b[0] - 2, b[1] - 2, b[2] + 1, b[3] + 2), outline=amb)
        return b

    def par(self, nome, x, y, lab, chave, fv=None, right=False, troca=None, gap=4):
        F, c = self.F, self.c
        t, lv = self.v(chave)
        if troca:
            t = troca(t)
        fv = fv or F["sb"]
        wl = c.width(lab, F["xs"]) + gap if lab else 0
        wv = c.width(t, fv)
        if right:
            x -= wl + wv
        if lab:
            c.text(nome + ".lab", x, y, lab, F["xs"], self.P["sub"])
            if self.modo == "ponto" and self.marcada(chave, lv):
                c.d.ellipse((x - 5, y - 6, x - 2, y - 3), fill=self.P["amber"])
        self.valor(nome + ".val", x + wl, y, t, fv, chave, lv)
        return x, x + wl + wv


def _titulo_dados(T, nome, y, desenhos):
    c, P, F = T.c, T.P, T.F
    x = 314
    for fn in desenhos:
        x = fn(x, y + 9) - 8
    b = c.text(f"tit.{nome}", 6, y + 7, nome, F["g"], P["accent"])
    c.line((b[2] + 5, y + 4, x + 3, y + 4), P["dim"])
    return y + 11


def _hora(ts):
    return time.strftime("%H:%M", time.localtime(ts))


def render(vm, P):
    v, c, col, F, vals = _base(vm, P)
    vals.update(_resumos(v, vals))
    lay = [[(-1, "g_cpu"), (1, "g_gpu")], [(-2, "g_ref"), (0, "core"), (2, "g_ram")], [(-1, "g_rede"), (1, "g_dsk")]]
    _colmeia(c, P, col, vals, F, lay, 21, 2, 49, f_lab=F["hs"], f_val=F["hv"], cx=P["colmeia_x"])
    graficos.desenhar(c, v, P, col, F)
    T = Texto(c, v, P, col, F, v.raw("brusco") or set())
    for k in ("cpu_pct", "gpu_pct", "vram_pct", "gpu_fan_rpm", "power", "power_tag", "coleta", "os", "wage", "t_ssd"):
        v.raw(k)
    step, gap = 13, 4
    par = lambda nome, lab, chave: (lambda x, yy: T.par(nome, x, yy, lab, chave, right=True, troca=lambda t: t.replace("RPM", ""))[0])

    def linha(y, itens, x=6, folga=12):
        for nome, lab, chave in itens:
            _, x = T.par(nome, x, y, lab, chave, troca=lambda t: t.replace("RPM", ""))
            x += folga
        return x

    y = P.get("texto_y", 151) + P.get("desce", 0)
    # CPU
    y = _titulo_dados(T, "CPU", y, [par("cpu.load", "LOAD", "cpu_load")]) + step - 2
    linha(y, (("cpu.util", "USO", "cpu_util"), ("cpu.temp", "TEMP", "cpu_temp"), ("cpu.ghz", "FREQ", "cpu_ghz")))
    # GPU
    y = _titulo_dados(T, "GPU", y + gap + 1, [par("gpu.fan", "FAN", "gpu_fan_pct"), par("gpu.fps", "FPS", "fps")]) + step - 2
    linha(y, (("gpu.util", "USO", "gpu_util"), ("gpu.temp", "TEMP", "gpu_temp"), ("gpu.mhz", "FREQ", "gpu_mhz")))
    y += step
    _, xe = T.par("gpu.vram", 6, y, "VRAM", "vram_txt")
    pt, pl = v("vram_pct_txt"); T.valor("gpu.vrampct", xe + 5, y, _paren(pt), F["sb"], "vram_pct_txt", pl)
    t, _ = v("gpu_wlim"); b = c.text("gpu.wlim", 314, y, t, F["xs"], P["sub"], anchor="rs")
    T.par("gpu.w", b[0] - 6, y, "W", "gpu_w", right=True)
    # RAM
    yr = y + gap + 1
    y = _titulo_dados(T, "RAM", yr, [par("ram.temp", "TEMP", "t_ram")]) + step - 2
    if P.get("ram_barra"):                                      # barra de uso da RAM junto da palavra RAM
        rp_, rl_ = vals["ram"][1]
        cor = {WARN: P["amber"], CRIT: P["red"]}.get(rl_, P["accent"])
        xr = 6 + int(c.width("RAM", F["g"]))
        bx = xr + 24                                            # mesma distância da barra do título DISCOS (DELTA 6)
        c.rect((xr + 1, yr + 1, bx + 63, yr + 9), fill=P["bg"])   # refaz o trecho: linha curta, vão e barra
        c.line((xr + 5, yr + 4, bx - 5, yr + 4), P["dim"])
        c.hbar(bx, yr + 1, 60, 7, v.raw("ram_pct") or 0, cor, mix(cor, P["bg"], 0.85), seg=3, gap=1)
    _, xe = T.par("ram.used", 6, y, "USO", "ram_used")
    t2, _ = v("ram_total"); rb = c.text("ram.total", xe + 1, y, t2, F["sb"], P["white"])
    rp, rl = vals["ram"][1]; pb = T.valor("ram.pct", rb[2] + 6, y, _paren(rp), F["sb"], "ram_used", rl)
    T.par("ram.avail", pb[2] + 12, y, "DISP", "ram_avail")

    # DISCOS (com o total)
    tot = v.raw("total_hd")
    modo_t = P.get("total", "coluna")
    if modo_t == "mapa" and tot:                                # mapa de capacidade: cada HD é um trecho proporcional
        def f_mapa(x, yy):
            b = c.text("tot.livre", x, yy, f"{tot['livre']} LIVRE", F["xs"], P["accent"], anchor="rs")
            b2 = c.text("tot.uso", b[0] - 6, yy, f"{tot['uso']}/{tot['total']}", F["sb"], P["white"], anchor="rs")
            x1, x0 = int(b2[0]) - 6, 54
            cap = sum(p_[1] for p_ in tot["partes"]) or 1
            xx = x0
            for k, (nm, cp, us, lv) in enumerate(tot["partes"]):
                w = max(3, round((x1 - x0) * cp / cap)) if k < len(tot["partes"]) - 1 else x1 - xx
                cor = {WARN: P["amber"], CRIT: P["red"]}.get(lv, P["accent"])
                c.rect((xx, yy - 9, xx + w - 2, yy - 1), fill=mix(cor, P["bg"], 0.85), outline=mix(cor, P["bg"], 0.5))
                c.rect((xx + 1, yy - 8, xx + 1 + max(0, round((w - 4) * us / max(1, cp))), yy - 2), fill=cor)
                xx += w
            return x0 - 4
        y = _titulo_dados(T, "DISCOS", y + gap, [f_mapa])
    elif modo_t == "rosca" and tot and P.get("rosca_hex"):      # título curto: o hexágono ocupa o canto direito
        y = y + gap
        b = c.text("tit.DISCOS", 6, y + 7, "DISCOS", F["g"], P["accent"])
        c.line((b[2] + 5, y + 4, 206, y + 4), P["dim"])
        y += 9
    elif modo_t in ("barra", "barra_disco") and tot:            # barra do total dentro do título DISCOS
        def f_bar(x, yy):
            b = c.text("tot.livre", x, yy, f"{tot['livre']} LIVRE", F["xs"], P["accent"], anchor="rs")
            b2 = c.text("tot.uso", b[0] - 6, yy, f"{tot['uso']}/{tot['total']}", F["sb"], P["white"], anchor="rs")
            c.hbar(int(b2[0]) - 66, yy - 8, 60, 7, tot["pct"], P["accent"], mix(P["accent"], P["bg"], 0.85), seg=3, gap=1)
            return int(b2[0]) - 66
        y = _titulo_dados(T, "DISCOS", y + gap, [f_bar])
    elif modo_t == "titulo" and tot:
        def f_tot(x, yy):
            b = c.text("tot.livre", x, yy, f"{tot['livre']} LIVRE", F["xs"], P["sub"], anchor="rs")
            b2 = c.text("tot.pct", b[0] - 6, yy, f"({tot['pct_txt']})", F["sb"], P["white"], anchor="rs")
            b3 = c.text("tot.uso", b2[0] - 4, yy, f"{tot['uso']}/{tot['total']}", F["sb"], P["accent"], anchor="rs")
            return c.text("tot.lab", b3[0] - 4, yy, "TOTAL", F["xs"], P["sub"], anchor="rs")[0]
        y = _titulo_dados(T, "DISCOS", y + gap, [f_tot])
    else:
        y = _titulo(c, P, F, "DISCOS", y + gap)
    discos = v.raw("disks", [])[:3]
    y0d = y
    coluna = modo_t == "coluna" and tot
    rosca = modo_t == "rosca" and tot
    for i, d in enumerate(discos):
        y += step
        c.text(f"dsk{i}.name", 6, y, d["name"], F["sb"], P["white"])
        ub = c.text(f"dsk{i}.use", 44, y, d["use"], F["s"], col(d.get("use_lvl", NEUTRAL)))
        if modo_t == "barra_disco":                             # barrinha de ocupação em cada disco
            cor = {WARN: P["amber"], CRIT: P["red"]}.get(d["lvl"], P["accent"])
            c.hbar(int(ub[2]) + 6, y - 8, 36, 7, d.get("pct"), cor, mix(cor, P["bg"], 0.85), seg=3, gap=1)
            pbx = T.valor(f"dsk{i}.pct", int(ub[2]) + 46, y, d["pct_txt"], F["sb"], None, d["lvl"])
        else:
            pbx = T.valor(f"dsk{i}.pct", ub[2] + 6, y, _paren(d["pct_txt"]), F["sb"], None, d["lvl"])
        fb = T.valor(f"dsk{i}.free", pbx[2] + 10, y, d["free"], F["sb"], None, d["lvl"])
        if rosca:
            v.raw("disks")
        elif not coluna:
            c.text(f"dsk{i}.freelab", fb[2] + 4, y, "LIVRE", F["xs"], P["sub"])
            T.valor(f"dsk{i}.temp", 314, y, d.get("temp_txt", "N/D"), F["sb"], None, d.get("temp_lvl", NA), anchor="rs")
        else:
            v.raw("disks")
    if rosca and P.get("rosca_hex"):                            # hexágono do total: o contorno se enche com o uso
        import math
        from .reator import hexagon
        r = 27
        # centro vertical exato entre a linha do título RAM e a linha do título seguinte (TERRAMASTER ou REFRIGERAÇÃO)
        linha_sup = yr + 4
        linha_inf = (y + gap + 3 + 4) if v.raw("baias", []) else (y + gap + 1 + 4)
        cxh, cyh = 277, (linha_sup + linha_inf) / 2
        pts = hexagon(cxh, cyh, r)
        topo = min(range(6), key=lambda k: pts[k][1])          # começa no vértice de cima, sentido horário
        pts = pts[topo:] + pts[:topo]
        c.poly(pts, fill=mix(P["accent"], P["bg"], 0.93))
        lados = [(pts[k], pts[(k + 1) % 6]) for k in range(6)]
        c.line(pts + [pts[0]], mix(P["accent"], P["bg"], 0.78), 5)
        resto = 6 * tot["pct"] / 100
        cor = P["accent"]
        for a, b in lados:
            if resto <= 0:
                break
            t = min(1.0, resto)
            c.line((a, (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)), cor, 5)
            resto -= 1
        c.text("tot.pct", cxh, cyh + 5, tot["pct_txt"], font(JB, 13, "Bold"), P["white"], anchor="ms")
        c.text("tot.uso", cxh, cyh + 15, tot["uso"], font(JB, 8, "Regular"), P["sub"], anchor="ms")
    elif rosca:                                                 # rosca do total à direita das linhas dos discos
        cxr, cyr, r = 236, (y0d + y) / 2 + 1, 17
        c.d.ellipse((cxr - r, cyr - r, cxr + r, cyr + r), outline=mix(P["accent"], P["bg"], 0.82), width=6)
        c.d.arc((cxr - r, cyr - r, cxr + r, cyr + r), -90, -90 + 360 * tot["pct"] / 100, fill=P["accent"], width=6)
        c.text("tot.pct", cxr, cyr + 4, tot["pct_txt"], font(JB, 9, "Bold"), P["white"], anchor="ms")
        c.text("tot.livre", 314, y0d + step, tot["livre"], F["sb"], P["accent"], anchor="rs")
        c.text("tot.l2", 314, y0d + 2 * step, "LIVRE", F["xs"], P["sub"], anchor="rs")
        c.text("tot.tot", 314, y0d + 3 * step, f"de {tot['total']}", font(JB, 9, "Regular"), P["sub"], anchor="rs")
        c.text("tot.uso", cxr, y0d + 3 * step + 10, "", F["xs"], P["sub"]) if False else None
    if coluna:                                                  # bloco do total no lugar da temperatura (N/D no PC)
        xc = 222
        c.line((xc - 6, y0d + 3, xc - 6, y + 3), P["dim"])
        grande = P.get("total_grande")
        if grande:
            c.text("tot.livre", 314, y0d + step + 3, tot["livre"], font(JB, 16, "Bold"), P["accent"], anchor="rs")
            c.text("tot.l2", 314, y0d + 2 * step + 4, f"LIVRE de {tot['total']}", F["xs"], P["sub"], anchor="rs")
            c.text("tot.uso", 314, y0d + 3 * step + 3, f"{tot['uso']} em uso", F["xs"], P["white"], anchor="rs")
        else:
            for k, (lab, val, cor) in enumerate((("TOTAL", tot["total"], P["white"]), ("USO", f"{tot['uso']}", P["accent"]),
                                                 ("LIVRE", tot["livre"], P["white"]))):
                yy = y0d + (k + 1) * step
                c.text(f"tot.{k}l", xc, yy, lab, F["xs"], P["sub"])
                c.text(f"tot.{k}v", 314, yy, val, F["sb"], cor, anchor="rs")
    elif modo_t == "coluna":
        v.raw("total_hd")
    v.raw("t_ssd")
    # TERRAMASTER
    baias = v.raw("baias", [])
    if baias:
        y = _titulo(c, P, F, "TERRAMASTER", y + gap + 3) + step - 2
        for i, b in enumerate(baias[:4]):
            x = 6 if i % 2 == 0 else 164
            if i and i % 2 == 0:
                y += step - 1
            bx = c.text(f"bay{i}.n", x, y, f"{b['n']}", F["sb"], P["accent"])
            if b.get("use"):
                ub = c.text(f"bay{i}.use", bx[2] + 5, y, b["use"], F["s"], P["white"])
                T.valor(f"bay{i}.pct", ub[2] + 5, y, _paren(b["pct_txt"]), F["sb"], None, b.get("pct_lvl", OK))
                continue
            if b["cap"]:
                bx = c.text(f"bay{i}.cap", bx[2] + 5, y, b["cap"], F["sb"], col(b["lvl"]))
            c.text(f"bay{i}.st", bx[2] + 5, y, b["palavra"], F["xs"], col(b["lvl"]))
    # REFRIGERAÇÃO numa linha (INF e LAT em série: uma leitura só)
    y = _titulo_dados(T, "REFRIGERAÇÃO", y + gap + 1, [par("fan.placa", "PLACA", "t_placa")]) + step - 2
    # INF e LAT estão em série: mostra a que tem leitura (no PC, a entrada mapeada como INF lê 0 e nunca girou)
    rpm_txt = lambda k: v.raw(k, ("N/D", NA))
    k_sq = "fan_sqi" if rpm_txt("fan_sqi")[1] not in (NA, LOST) else "fan_sql"
    v("fan_sqi"); v("fan_sql")
    linha(y, (("fan.pump", "BOMBA", "pump"), ("fan.rad", "RAD", "cpu_fan"), ("fan.sq", "SQUAMA", k_sq),
              ("fan.sqt", "TRA", "fan_sqt")), folga=10)
    # REDE
    def inet_txt(x, yy):
        t, lv = v("inet")
        if P.get("inet_onoff"):                                 # INTERNET ON / OFF (instável continua por extenso)
            t = "INTERNET ON" if lv == OK else "INTERNET OFF" if lv == CRIT else t
        return T.valor("inet", x, yy, t, F["xs"], None, lv, anchor="rs")[0]
    y = _titulo_dados(T, "REDE", y + gap + 3, [inet_txt, par("png", "PING", "ping")]) + step - 1
    t, lv = v("net_down"); b = T.valor("net.down", 6, y, "↓" + t, F["sb"], "net_down", NEUTRAL)
    t, lv = v("net_up"); T.valor("net.up", b[2] + 8, y, "↑" + t, F["sb"], "net_up", NEUTRAL)
    t, lv = v("net_tx"); tb = T.par("net.tx", 314, y, "TX", "net_tx", fv=F["s"], right=True)
    T.par("net.rx", tb[0] - 8, y, "RX", "net_rx", fv=F["s"], right=True)
    for key, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        y += step
        iface_row(c, v, key, y, 6, tag, 44, 314, F["xs"], F["sb"], F["xs"], F["xs"], col, P["sub"],
                  c_info=P["white"], c_rates=P["white"])

    _rodape(c, v, P, col, F, y + 6)
    if P.get("bloom"):
        c.img = bloom(c.img, *P["bloom"])
    return c, v


def _sistema(c, v, P, col, F, x, y, alinhar="ls", relogio=18):
    """Relógio, data, tempo ligado e clima, empilhados. Devolve a base da última linha."""
    rs = alinhar == "rs"
    t, _ = v("clock"); c.text("sys.clock", x, y, t, font(JB, relogio, "Bold"), P["accent"], anchor=alinhar)
    y += 11
    t, _ = v("date"); c.text("sys.date", x, y, t, F["xs"], P["white"], anchor=alinhar)
    y += 11
    t, lv = v("uptime"); c.text("sys.up", x, y, "UP " + t, F["xs"], P["sub"], anchor=alinhar)
    y += 11
    t, lv = v("wtemp"); tw = c.text("wx.temp", x, y, t, F["sb"], col(lv), anchor=alinhar)
    t2, l2 = v("wdesc")
    if rs:
        c.text("wx.desc", tw[0] - 5, y, c.fit(t2, F["xs"], 70), F["xs"], col(l2) if l2 != NA else P["sub"], anchor="rs")
    else:
        c.text("wx.desc", tw[2] + 5, y, c.fit(t2, F["xs"], 70), F["xs"], col(l2) if l2 != NA else P["sub"])
    y += 11
    c.text("wx.city", x, y, c.fit(v.raw("city", ""), F["xs"], 110), F["xs"], P["sub"], anchor=alinhar)
    return y


def _registro(c, v, P, F, x0, y0, x1, n, modo, y_max=477):
    """LOG dos alertas: hora, item, leitura e a nova cor; a linha tem a cor do nível (âmbar, vermelho ou verde).
    Alertas com mais de 1 hora ficam esmaecidos."""
    reg = v.raw("registro") or []
    f = font(JB, 9, "Regular")
    agora = time.time()
    if not reg:
        c.text("reg.vazio", x0, y0 + 10, "nenhum alerta", f, P["sub"])
        return
    n = max(1, min(n, int((y_max - (y0 + 10)) // 11) + 1))
    for i, item in enumerate(reg[:n]):
        ts, txt = item[0], item[1]
        lv = item[2] if len(item) > 2 else WARN
        y = y0 + 10 + i * 11
        recente = agora - ts < 3600
        cor = {CRIT: P["red"], WARN: P["amber"], OK: P["accent"]}.get(lv, P["amber"])
        if not recente:
            cor = mix(cor, P["bg"], 0.45)
        if modo == "barras":
            c.rect((x0, y - 8, x0 + 2, y + 1), fill=cor)
            xx = x0 + 6
        else:
            xx = x0
        h = c.text(f"reg{i}.h", xx, y, _hora(ts), f, P["sub"])
        if modo == "tabela" and " " in txt:                     # colunas: hora, leitura, de -> para
            rot, mud = txt.rsplit(" ", 1)
            mb = c.text(f"reg{i}.m", x1, y, mud, font(JB, 9, "Bold"), cor, anchor="rs")
            c.text(f"reg{i}.t", h[2] + 8, y, c.fit(rot, f, mb[0] - h[2] - 14), f, P["white"] if recente else P["sub"])
        else:
            c.text(f"reg{i}.t", h[2] + 6, y, c.fit(txt, f, x1 - h[2] - 6), f, cor)


def _rodape(c, v, P, col, F, ytopo):
    """Sistema compacto e registro, conforme P['registro']."""
    modo = P.get("registro", "esq")
    yb = max(ytopo + 4, 412)
    if modo in ("esq", "caixa", "barras"):
        if modo == "caixa":
            c.rect((4, yb - 4, 206, 478), outline=P["dim"])
            c.text("tit.REG", 10, yb + 6, P.get("nome_log", "REGISTRO"), F["g"], P["accent"])
            _registro(c, v, P, F, 10, yb + 8, 200, 5, modo)
        else:
            b = c.text("tit.REG", 6, yb + 6, P.get("nome_log", "REGISTRO"), F["g"], P["accent"])
            c.line((b[2] + 5, yb + 3, 206, yb + 3), P["dim"])
            _registro(c, v, P, F, 6, yb + 8, 206, 5, modo)
        _sistema(c, v, P, col, F, 314, 432, alinhar="rs")              # ancorado no rodapé
    elif modo == "dir":
        _sistema(c, v, P, col, F, 6, 432)
        b = c.text("tit.REG", 116, yb + 6, P.get("nome_log", "REGISTRO"), F["g"], P["accent"])
        c.line((b[2] + 5, yb + 3, 314, yb + 3), P["dim"])
        _registro(c, v, P, F, 116, yb + 8, 314, 5, modo)
    else:                                                       # faixa e tabela: registro na largura toda
        b = c.text("tit.REG", 6, yb + 6, P.get("nome_log", "REGISTRO"), F["g"], P["accent"])
        t2, l2 = v("wdesc"); wd = c.text("wx.desc", 314, yb + 7, c.fit(t2, F["xs"], 70), F["xs"], col(l2) if l2 != NA else P["sub"], anchor="rs")
        t, lv = v("wtemp"); tw = c.text("wx.temp", wd[0] - 5, yb + 8, t, F["sb"], col(lv), anchor="rs")
        cb = c.text("wx.city", tw[0] - 5, yb + 7, c.fit(v.raw("city", ""), F["xs"], 80), F["xs"], P["sub"], anchor="rs")
        c.line((b[2] + 5, yb + 3, cb[0] - 6, yb + 3), P["dim"])
        _registro(c, v, P, F, 6, yb + 8, 314, 4, modo, y_max=464)
        y = 477
        t, _ = v("clock"); cb = c.text("sys.clock", 6, y, t, font(JB, 14, "Bold"), P["accent"])
        t, _ = v("date"); db = c.text("sys.date", cb[2] + 8, y, t, F["xs"], P["white"])
        t, lv = v("uptime"); c.text("sys.up", 314, y, "UP " + t, F["xs"], P["sub"], anchor="rs")
