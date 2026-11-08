# MATRIX GREEN PRO | indicadores de aviso e alerta do cabeçalho | versão 3.6.0 | 08/11/2026 13:31 (-03) | criação original
# histórico: 3.6.0 08/11/2026 13:31 brilho do nome na resolução real da tela (escala da 5,2")
# histórico: 3.5.0 n3_esq sem tarja, com brilho no nome e sem LIVE | 3.4.0 02/11/2026 18:40 escalas N0/N1/N2 | 3.3.0 02/11/2026 18:05 escala, barra, banner e faixa
# Três desenhos modernos para o "status" do canto superior direito, mais uma proposta com a
# escala em outro lugar (faixa de largura total sob o cabeçalho). Em CRÍTICO o vermelho pisca:
# a fase vem de vm["blink"] (True/False) ou, se ausente, do relógio (1 s aceso, 1 s apagado).
#   escala  : 15 marcas (5 verdes, 5 âmbar, 5 vermelhas) como medidor de nível; a marca ativa fica mais alta
#   barra   : barra em degradê verde, âmbar e vermelho com ponteiro triangular
#   banner  : caixa com ícone de alerta; crítico vira caixa vermelha cheia (inspirada em banner de terminal)
#   n3_dir / n3_esq : escala de 3 níveis N0 NORMAL, N1 AVISO, N2 ALERTA empilhada num canto (estilo terminal de eventos)
#   n3_abas : três abas N0 N1 N2 no cabeçalho; a ativa se expande com o nome
#   n3_linha: uma linha de terminal no cabeçalho: > [N1] AVISO // OBSERVAR
#   n3_eventos: escala à esquerda e, à direita, a lista dos itens em alerta
#   faixa   : escala de 31 marcas na largura toda, no lugar da divisória do cabeçalho (proposta)
import time

from .base import OK, WARN, CRIT, LOST, W, font, JB, strip_status


def mix(a, b, t):
    """Mistura a cor a com b (t=0 -> a, t=1 -> b)."""
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


def counts(v):
    h = v.raw("health", {}) or {}
    return (sum(1 for x in h.values() if x == CRIT), sum(1 for x in h.values() if x in (WARN, LOST)))


def label(st, ncrit, nwarn, lvl):
    if "SEM DADOS" in st:
        return "SEM DADOS"
    if lvl == CRIT:
        return f"{ncrit} CRÍTICO{'S' if ncrit > 1 else ''}" + (f" +{nwarn}" if nwarn else "")
    if lvl == WARN:
        return f"{nwarn} AVISO{'S' if nwarn > 1 else ''}"
    return "SISTEMA OK"


def position(lvl, ncrit, nwarn, n):
    """Posição 0..n-1 na escala: verde no início, âmbar no meio, vermelho no fim (a contagem avança a marca)."""
    z = n // 3
    if lvl == CRIT:
        return min(n - 1, 2 * z + min(max(ncrit, 1), z) - 1 + (n - 3 * z))
    if lvl == WARN:
        return z + min(max(nwarn, 1), z) - 1
    return z // 2


def zone_color(i, n, P):
    z = n // 3
    return P["accent"] if i < z else P["amber"] if i < 2 * z else P["red"]


def draw_status(c, v, P, mode, blink, st, slv, col, vals=None):
    if blink is None:
        blink = int(time.time()) % 2 == 0
    ncrit, nwarn = counts(v)
    lvl = slv if slv in (OK, WARN, CRIT) else OK
    text = label(st, ncrit, nwarn, lvl)
    crit = lvl == CRIT
    on = blink or not crit                      # fase acesa (só o crítico alterna)
    f_lab = font(JB, 11, "Bold")
    ink = {OK: P["ice"], WARN: P["amber"], CRIT: P["red"]}[lvl]
    dark = mix(ink, P["bg"], 0.82)

    if mode.startswith("n3_"):
        _n3(c, v, P, mode, on, crit, lvl, ncrit, nwarn, text, vals or {})
        return

    if mode == "escala":
        n, pw, gap, x1 = 15, 7, 2, 314
        x0 = x1 - (n * (pw + gap) - gap)
        c.text("hdr.status", 314, 11, text, f_lab, ink if on else dark, anchor="rs")
        p = position(lvl, ncrit, nwarn, n)
        for i in range(n):
            zc = zone_color(i, n, P)
            lit = i <= p
            colr = zc if lit else mix(zc, P["bg"], 0.84)
            if crit and lit and i >= 2 * (n // 3) and not on:
                colr = mix(zc, P["bg"], 0.70)
            top = 13 if i == p else 16
            x = x0 + i * (pw + gap)
            c.rect((x, top, x + pw - 1, 21), fill=colr)

    elif mode == "barra":
        x0, x1, y0, y1 = 181, 314, 13, 17
        c.text("hdr.status", 314, 10, text, f_lab, ink if on else dark, anchor="rs")
        p = position(lvl, ncrit, nwarn, 30) / 29.0
        px = x0 + p * (x1 - x0)
        for x in range(x0, x1 + 1):
            t = (x - x0) / (x1 - x0)
            base = mix(P["accent"], P["amber"], t / 0.5) if t < 0.5 else mix(P["amber"], P["red"], (t - 0.5) / 0.5)
            reached = x <= px
            fade = 0.0 if reached else 0.82
            if crit and reached and t >= 0.66 and not on:
                fade = 0.6
            c.line((x, y0, x, y1), mix(base, P["bg"], fade))
        if on:
            c.poly([(px, 19), (px - 4, 24), (px + 4, 24)], fill=ink)
        else:
            c.poly([(px, 19), (px - 4, 24), (px + 4, 24)], outline=ink)

    elif mode == "banner":
        f_b = font(JB, 12, "Bold")
        txt = ("ALERTA " + text) if crit and "SEM DADOS" not in text else text
        w = int(c.width(txt, f_b)) + 30
        x0, y0, y1 = 314 - w, 3, 21
        if crit:
            c.rect((0, 23, W - 1, 24), fill=P["red"] if on else mix(P["red"], P["bg"], 0.7))   # linha de alerta
            fill = P["red"] if on else mix(P["red"], P["bg"], 0.78)
            c.rect((x0, y0, 314, y1), fill=fill, outline=P["red"])
            tcol, icol = (P["bg"], P["bg"]) if on else (P["red"], P["red"])
        else:
            c.rect((x0, y0, 314, y1), fill=dark, outline=ink)
            tcol = icol = ink
        cx, cy = x0 + 11, 12
        if lvl == OK:
            c.d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=icol)
        else:                                       # triângulo de alerta com ponto de exclamação
            c.poly([(cx, cy - 6), (cx - 6, cy + 5), (cx + 6, cy + 5)], outline=icol)
            c.line((cx, cy - 2, cx, cy + 1), icol)
            c.d.point((cx, cy + 3), fill=icol)
        c.text("hdr.status", 314 - 6, 16, txt, f_b, tcol, anchor="rs")

    elif mode == "faixa":
        n, pw, gap = 31, 8, 2
        x0 = 6
        c.text("hdr.status", 314, 17, text, f_lab, ink if on else dark, anchor="rs")
        p = position(lvl, ncrit, nwarn, n)
        for i in range(n):
            zc = zone_color(i, n, P)
            lit = i <= p
            colr = zc if lit else mix(zc, P["bg"], 0.86)
            if crit and lit and i >= 2 * (n // 3) and not on:
                colr = mix(zc, P["bg"], 0.70)
            top = 20 if i == p else 22
            x = x0 + i * (pw + gap)
            c.rect((x, top, x + pw - 1, 26), fill=colr)


# ---------------------------------------------------------------- escala N0 / N1 / N2 (terminal de eventos)
NIVEIS = [("N0", "NORMAL", "PRONTO", OK), ("N1", "AVISO", "OBSERVAR", WARN), ("N2", "ALERTA", "INTERVIR", CRIT)]
HEALTH_CELL = {"cpu_temp": "cput", "gpu_temp": "gput", "vram": "vram", "ram": "ram", "disk0": "d0", "disk1": "d1",
               "disk2": "d2", "conexao": "rede", "ping": "ping", "cpu_fan": "cfan", "gpu_fan": "gfan", "energia": "pwr"}


def glow(c, x, y, s, f, color, radius=2, gain=1.0, anchor="ls"):
    """Halo suave atrás do texto (nome 'brilhando'), somado à imagem antes de desenhar o texto nítido."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    k = getattr(c, "k", 1)                                     # tudo na resolução real da tela
    x, y = x * k, y * k
    bx = c.d.raw.textbbox((x, y), s, font=f, anchor=anchor) if hasattr(c.d, "raw") else c.d.textbbox((x, y), s, font=f, anchor=anchor)
    m = round(8 * k)
    x0, y0, x1, y1 = max(0, int(bx[0]) - m), max(0, int(bx[1]) - m), min(c.img.width, int(bx[2]) + m), min(c.img.height, int(bx[3]) + m)
    layer = Image.new("RGB", (x1 - x0, y1 - y0), (0, 0, 0))
    ImageDraw.Draw(layer).text((x - x0, y - y0), s, font=f, fill=color, anchor=anchor)
    layer = layer.filter(ImageFilter.GaussianBlur(radius * k)).point(lambda p: min(255, int(p * gain)))
    c.img.paste(ImageChops.add(c.img.crop((x0, y0, x1, y1)), layer), (x0, y0))


def _cor(P, lv):
    return {OK: P["accent"], WARN: P["amber"], CRIT: P["red"]}[lv]


def _linha(c, P, name, x0, y0, w, lv, active, on, left, right="", f=None, h=11, sub=None, limpo=False):
    """Uma linha de terminal: barra colorida, fundo e borda quando ativa, texto à esquerda e à direita.
    limpo=True: sem tarja; só a barra à esquerda e o nome brilhando (piscam em N2)."""
    col = _cor(P, lv)
    bg = P["bg"]
    crit = lv == CRIT
    if limpo:
        acesa = active and (on or not crit)
        c.rect((x0, y0, x0 + 2, y0 + h - 1), fill=col if acesa else mix(col, bg, 0.80 if not active else 0.6))
        tcol = col if acesa else mix(col, bg, 0.50 if not active else 0.55)
        if acesa:
            glow(c, x0 + 7, y0 + h - 2, left, f, col)
        c.text(f"{name}.t", x0 + 7, y0 + h - 2, left, f, tcol)
        if right:
            if acesa:
                glow(c, x0 + w - 4, y0 + h - 2, right, f, col, anchor="rs")
            c.text(f"{name}.n", x0 + w - 4, y0 + h - 2, right, f, tcol, anchor="rs")
        return
    c.rect((x0, y0, x0 + 2, y0 + h - 1), fill=col if active else mix(col, bg, 0.80))
    if active and lv != OK:
        fill = mix(col, bg, 0.52 if (crit and on) else 0.80)
        edge = col if (on or not crit) else mix(col, bg, 0.45)
        c.rect((x0 + 3, y0, x0 + w - 1, y0 + h - 1), fill=fill, outline=edge)
    tcol = col if active else mix(col, bg, 0.50)
    b = c.text(f"{name}.t", x0 + 7, y0 + h - 2, left, f, tcol)
    if sub:
        c.text(f"{name}.s", b[2] + 5, y0 + h - 2, sub, f, mix(P["sub"], bg, 0.15 if active else 0.5))
    if right:
        c.text(f"{name}.n", x0 + w - 4, y0 + h - 2, right, f, tcol, anchor="rs")


def _live(c, P, lvl, on, crit, f):
    col = _cor(P, lvl)
    c.d.ellipse((307, 8, 313, 14), fill=col if on or not crit else mix(col, P["bg"], 0.75))
    c.text("hdr.status", 302, 14, "LIVE", f, P["sub"], anchor="rs")


def _escala(c, P, x0, y0, w, lvl, on, ncrit, nwarn, text, f, limpo=False):
    for i, (cod, nome, _, nv) in enumerate(NIVEIS):
        ativo = nv == lvl
        n = ncrit if nv == CRIT else nwarn if nv == WARN else 0
        nome = "SEM DADOS" if (ativo and nv == CRIT and "SEM DADOS" in text) else nome
        _linha(c, P, f"n3.{cod}", x0, y0 + i * 12, w, nv, ativo, on, f"{cod} {nome}",
               str(n) if ativo and n and nome != "SEM DADOS" else "", f, limpo=limpo)


def _n3(c, v, P, mode, on, crit, lvl, ncrit, nwarn, text, vals):
    f = font(JB, 11, "Bold")
    if mode in ("n3_dir", "n3_eventos"):
        _live(c, P, lvl, on, crit, f)
    if mode == "n3_dir":
        _escala(c, P, 228, 27, 88, lvl, on, ncrit, nwarn, text, f)
    elif mode == "n3_esq":                       # sem tarja, sem LIVE: barra e nome brilhando
        _escala(c, P, 4, 27, 88, lvl, on, ncrit, nwarn, text, f, limpo=True)
    elif mode == "n3_eventos":
        _escala(c, P, 4, 27, 88, lvl, on, ncrit, nwarn, text, f)
        h = v.raw("health", {}) or {}
        itens = [(k, x) for k, x in h.items() if x in (CRIT, WARN, LOST) and HEALTH_CELL.get(k) in vals]
        itens.sort(key=lambda kx: 0 if kx[1] == CRIT else 1)
        linhas = []
        for k, x in itens:
            lab, (tx, _) = vals[HEALTH_CELL[k]]
            linhas.append((lab if lab != "REDE" else "REDE", tx, CRIT if x == CRIT else WARN))
        if not linhas:
            _linha(c, P, "ev.0", 228, 27, 88, OK, True, True, "> PRONTO", "", f)
        else:
            if len(linhas) > 3:
                extra = len(linhas) - 2
                linhas = linhas[:2] + [("+%d" % extra, "MAIS", WARN)]
            for i, (lab, tx, lv2) in enumerate(linhas):
                s = c.fit(f"{lab} {tx.replace('RPM', '')}", f, 72)
                _linha(c, P, f"ev.{i}", 228, 27 + i * 12, 88, lv2, True, on, s, "", f)
    elif mode == "n3_abas":
        n = ncrit if crit else nwarn if lvl == WARN else 0
        itens = []
        for cod, nome, _, nv in NIVEIS:
            ativo = nv == lvl
            nome2 = "SEM DADOS" if (ativo and crit and "SEM DADOS" in text) else nome
            s = f"{cod} {nome2}" + (f" {n}" if ativo and n and "SEM DADOS" not in nome2 else "") if ativo else cod
            itens.append((s, nv, ativo))
        ws = [int(c.width(s, f)) + 12 for s, _, _ in itens]
        x = 314 - (sum(ws) + 4)
        for (s, nv, ativo), w in zip(itens, ws):
            col = _cor(P, nv)
            if ativo:
                fill = mix(col, P["bg"], 0.52 if (crit and on) else 0.80)
                c.rect((x, 4, x + w - 1, 20), fill=fill, outline=col if (on or not crit) else mix(col, P["bg"], 0.45))
                c.text(f"n3.{s[:2]}", x + 6, 16, s, f, col)
            else:
                c.rect((x, 4, x + w - 1, 20), outline=mix(col, P["bg"], 0.78))
                c.text(f"n3.{s[:2]}", x + 6, 16, s, f, mix(col, P["bg"], 0.55))
            x += w + 2
    elif mode == "n3_linha":
        cod, nome, suf, nv = NIVEIS[{OK: 0, WARN: 1, CRIT: 2}[lvl]]
        if "SEM DADOS" in text:
            nome, suf = "SEM DADOS", "VERIFICAR"
        w = int(c.width(f"> [{cod}] {nome} // {suf}", f)) + 14
        x0 = 314 - w
        col = _cor(P, lvl)
        c.rect((x0, 4, x0 + 2, 20), fill=col)
        if lvl != OK:
            fill = mix(col, P["bg"], 0.52 if (crit and on) else 0.80)
            c.rect((x0 + 3, 4, 314, 20), fill=fill, outline=col if (on or not crit) else mix(col, P["bg"], 0.45))
        b = c.text("n3.a", x0 + 8, 16, f"> [{cod}] {nome}", f, col)
        c.text("hdr.status", b[2] + 5, 16, f"// {suf}", f, mix(P["sub"], P["bg"], 0.1))
