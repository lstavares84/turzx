# GAMMA EPSILON | estudo da tela de mineração | versão 0.2.1 | 21/11/2026 17:41 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 0.2.1 21/11/2026 17:41 MINERANDO pisca
# histórico: 0.2.0 21/11/2026 17:45 fusões F, G e H: barras do E (valor e % do limite) com a produção do D, sem redundâncias
# histórico: 0.1.0 21/11/2026 17:30 criação: 5 mockups (A a E) com dados de demonstração
# Estudo da tela que o GAMMA EPSILON mostraria enquanto o PC minera (detecção pelo processo do minerador, como na
# tela do nobreak). Sem energia: potência na tomada, custo e nobreak ficam na tela de 5,2". Saúde do hardware em
# barras com as marcas de aviso (âmbar) e de limite (vermelho); produção do minerador (hashrate, shares, pool).
# Latência até a pool: âmbar acima de 100 ms, vermelho acima de 250 ms (proposta, sem norma).
# Os números são DEMONSTRATIVOS (o cenário segue o estado do cabeçalho); o minerador real ainda não foi definido.
#   A = barras horizontais na largura toda       B = colunas verticais lado a lado
#   C = hashrate em destaque, barras compactas    D = duas colunas: GPU | CPU e sistema
#   E = o mais perto do limite primeiro (% do limite)
#   F = fusão: barras do E ordenadas pelo limite (3 maiores) + produção do D
#   G = fusão: barras do E em ordem fixa (GPU, depois CPU e sistema) + produção do D
#   H = fusão: só as 4 barras mais perto do limite + o resto numa linha + produção do D com gráfico maior
import math
import os
import random

from .alerta import mix
from .base import OK, WARN, CRIT, font, JB, ROBOTO
from .graficos import Grafico
from .reator_grupos import _base
from .reator_gamma_delta import P as P_DELTA

P = dict(P_DELTA, selo="EPSILON")

# (chave, rótulo, unidade, mínimo, aviso, limite)
SAUDE = [("gpu_t", "GPU TEMP", "°C", 30, 80, 88), ("gpu_w", "GPU POTÊNCIA", "W", 0, 285, 297),
         ("gpu_fan", "GPU VENTOINHA", "%", 0, 90, 100), ("vram", "VRAM", "%", 0, 90, 97),
         ("cpu_t", "CPU TEMP", "°C", 30, 88, 94), ("cpu_u", "CPU USO", "%", 0, 90, 100), ("ram", "RAM", "%", 0, 90, 95)]
CURTO = {"gpu_t": "GPU°", "gpu_w": "GPU W", "gpu_fan": "FAN", "vram": "VRAM", "cpu_t": "CPU°", "cpu_u": "CPU%", "ram": "RAM"}


def demo(cen):
    rnd = random.Random({"normal": 1, "atencao": 2, "critico": 3}[cen])
    base = {"normal": 61.2, "atencao": 61.0, "critico": 60.5}[cen]
    serie = []
    for i in range(60):
        h = base + rnd.uniform(-0.8, 0.8)
        if cen == "atencao" and i > 50:
            h = 51 + rnd.uniform(-0.6, 0.6)
        if cen == "critico" and i > 48:
            h = 31 + rnd.uniform(-1.5, 1.5)
        if cen == "critico" and 20 < i < 24:
            h = None                                              # minerador reiniciou: sem leitura
        serie.append(h)
    d = {"normal": dict(gpu_t=63, gpu_w=212, gpu_fan=62, vram=41, cpu_t=58, cpu_u=18, ram=40, lim_w=300,
                        clock="1650/9501MHz", reducao="", ush=12, hr=61.2, media=61.0, ac=1243, rj=2, pool="POOL DEMO:4444",
                        lat=38, up="5h12m", alg="ALGORITMO DEMO", bomba=5600, rad=1240),
         "atencao": dict(gpu_t=84, gpu_w=288, gpu_fan=91, vram=41, cpu_t=61, cpu_u=22, ram=40, lim_w=300,
                         clock="1590/9501MHz", reducao="POTÊNCIA", ush=48, hr=51.0, media=61.0, ac=1871, rj=27, pool="POOL DEMO:4444",
                         lat=44, up="7h40m", alg="ALGORITMO DEMO", bomba=5600, rad=1780),
         "critico": dict(gpu_t=89, gpu_w=298, gpu_fan=100, vram=43, cpu_t=70, cpu_u=25, ram=41, lim_w=300,
                         clock="1210/9501MHz", reducao="TEMPERATURA", ush=190, hr=31.0, media=60.5, ac=2210, rj=73,
                         pool="POOL DEMO:4444", lat=140, up="9h03m", alg="ALGORITMO DEMO", bomba=5600, rad=2150)}[cen]
    d["serie"] = serie
    return d


def nivel(v, aviso, limite):
    return CRIT if v >= limite else WARN if v >= aviso else OK


def _cor(P, lv):
    return {OK: P["accent"], WARN: P["amber"], CRIT: P["red"]}[lv]


def barra(c, P, x, y, w, h, v, vmin, aviso, limite, topo=None):
    """Barra com a faixa até o topo (padrão: 10% acima do limite), marca âmbar no aviso e vermelha no limite."""
    topo = topo or limite + (limite - vmin) * 0.1
    pos = lambda val: x + (w - 1) * max(0.0, min(1.0, (val - vmin) / (topo - vmin)))
    lv = nivel(v, aviso, limite)
    cor = _cor(P, lv)
    c.rect((x, y, x + w - 1, y + h - 1), fill=mix(P["accent"], P["bg"], 0.88))
    c.rect((x, y, round(pos(v)), y + h - 1), fill=cor)
    for val, mc in ((aviso, P["amber"]), (limite, P["red"])):
        mx = round(pos(val))
        c.line((mx, y - 2, mx, y + h + 1), mc, 1)
    return lv


def vbarra(c, P, x, y0, y1, w, v, vmin, aviso, limite):
    topo = limite + (limite - vmin) * 0.1
    pos = lambda val: y1 - (y1 - y0) * max(0.0, min(1.0, (val - vmin) / (topo - vmin)))
    lv = nivel(v, aviso, limite)
    c.rect((x, y0, x + w - 1, y1), fill=mix(P["accent"], P["bg"], 0.88))
    c.rect((x, round(pos(v)), x + w - 1, y1), fill=_cor(P, lv))
    for val, mc in ((aviso, P["amber"]), (limite, P["red"])):
        my = round(pos(val))
        c.line((x - 2, my, x + w + 1, my), mc, 1)
    return lv


def _txt(chave, m):
    v = m[chave]
    if chave == "gpu_w":
        return f"{v}/{m['lim_w']}W"
    un = next(s[2] for s in SAUDE if s[0] == chave)
    return f"{v}{un}"


def _queda(m):
    q = 100.0 * (m["media"] - m["hr"]) / m["media"] if m["media"] else 0.0
    return q, (CRIT if q >= 30 else WARN if q >= 15 else OK)


def _rej(m):
    t = m["ac"] + m["rj"]
    r = 100.0 * m["rj"] / t if t else 0.0
    return r, (CRIT if r >= 2 else WARN if r >= 1 else OK)


def _topo(c, P, F, m, cabecalho=True):
    import time
    aceso = int(time.time()) % 2 == 0                           # pisca: 1 s aceso, 1 s apagado (esmaecido)
    c.text("mn.tit", 314, 42, "MINERANDO", font(ROBOTO, 15, "Bold"), P["amber"] if aceso else mix(P["amber"], P["bg"], 0.8),
           anchor="rs")
    c.text("mn.up", 314, 57, "HÁ " + m["up"], F["xs"], P["sub"], anchor="rs")
    if cabecalho:                                               # nas fusões sai: repetia o MINERANDO
        c.text("hdr.tela", 172, 17, "MINERAÇÃO", F["xs"], P["amber"], anchor="ms")


def _titulo(c, P, F, nome, y, x0=6, x1=314):
    b = c.text(f"tit.{nome}", x0, y, nome, F["g"], P["accent"])
    c.line((b[2] + 5, y - 3, x1, y - 3), P["dim"])


def _reducao(c, P, F, m, x, y, nome="mn.red"):
    if m["reducao"]:
        t = "CLOCK ↓ " + m["reducao"]
        b = c.d.textbbox((x, y), t, font=F["xs"], anchor="ls")
        cor = P["red"] if m["reducao"] == "TEMPERATURA" else P["amber"]
        c.rect((b[0] - 2, b[1] - 1, b[2] + 1, b[3] + 1), fill=cor)
        return c.text(nome, x, y, t, F["xs"], P["bg"])
    return c.text(nome, x, y, "CLOCK " + m["clock"], F["xs"], P["sub"])


def _valor(c, P, nome, x, y, t, f, lv, anchor="ls"):
    if lv in (WARN, CRIT):
        b = c.d.textbbox((x, y), t, font=f, anchor=anchor)
        c.rect((b[0] - 2, b[1] - 1, b[2] + 1, b[3] + 1), fill=_cor(P, lv))
        return c.text(nome, x, y, t, f, P["bg"], anchor=anchor)
    return c.text(nome, x, y, t, f, P["white"], anchor=anchor)


def _grafico(c, P, F, m, y0, y1, x0=6, larg=309, rotulo=True):
    vals = [v for v in m["serie"] if v is not None]
    g = Grafico(c, P, x0, larg, y0, y1, 0.0, max(vals) * 1.15)
    g.serie(m["serie"], P["accent"], True)
    ly = g.y(m["media"])
    for x in range(x0, x0 + larg, 5):
        c.line((x, ly, min(x + 2, x0 + larg - 1), ly), mix(P["white"], P["bg"], 0.4))
    if rotulo:
        c.text("mn.gr.lab", x0 + 2, y0 + 9, "HASHRATE 60 MIN", F["xs"], P["sub"])
        c.text("mn.gr.med", x0 + larg - 3, y0 + 9, f"MÉDIA {m['media']:.1f}", F["xs"], P["sub"], anchor="rs")


def _producao_linhas(c, P, F, m, y):
    r, lr = _rej(m)
    b = c.text("mn.sh.lab", 6, y, "SHARES", F["xs"], P["sub"])
    b = c.text("mn.sh", b[2] + 5, y, f"{m['ac']} A  {m['rj']} R", F["sb"], P["white"])
    _valor(c, P, "mn.rej", 314, y, f"REJ {r:.2f}%", F["sb"], lr, anchor="rs")
    y += 15
    b = c.text("mn.pool.lab", 6, y, "POOL", F["xs"], P["sub"])
    c.text("mn.pool", b[2] + 5, y, c.fit(m["pool"], F["sb"], 170), F["sb"], P["white"])
    _valor(c, P, "mn.lat", 314, y, f"{m['lat']}ms", F["sb"], CRIT if m["lat"] > 250 else WARN if m["lat"] > 100 else OK, anchor="rs")
    return y


def _hashrate(c, P, F, m, x, y, f, anchor="ls"):
    q, lq = _queda(m)
    hb = _valor(c, P, "mn.hr", x, y, f"{m['hr']:.1f}", f, lq, anchor=anchor)
    ub = c.text("mn.hr.un", hb[2] + 4, y, "MH/s", F["sb"], P["sub"])
    seta = f"▼{q:.0f}%" if q >= 1 else "ESTÁVEL"
    c.text("mn.hr.var", ub[2] + 8, y, seta, F["sb"], _cor(P, lq) if lq != OK else P["sub"])
    return hb


# ------------------------------------------------------------------ A: barras horizontais na largura toda
def _A(c, P, F, m):
    y = 82
    _titulo(c, P, F, "SAÚDE DO HARDWARE", y)
    y += 16
    for k, lab, un, vmin, av, lim in SAUDE:
        c.text(f"a.{k}.lab", 6, y, lab, F["xs"], P["sub"])
        lv = nivel(m[k], av, lim)
        c.text(f"a.{k}.val", 314, y, _txt(k, m), F["sb"], _cor(P, lv) if lv != OK else P["white"], anchor="rs")
        barra(c, P, 6, y + 4, 309, 6, m[k], vmin, av, lim)
        y += 22
    _reducao(c, P, F, m, 6, y + 2)
    c.text("a.cool", 314, y + 2, f"BOMBA {m['bomba']}  RAD {m['rad']}", F["xs"], P["sub"], anchor="rs")
    y += 20
    _titulo(c, P, F, "PRODUÇÃO", y)
    c.text("a.alg", 314, y, m["alg"], F["xs"], P["sub"], anchor="rs")
    y += 20
    _hashrate(c, P, F, m, 6, y, F["xl"])
    y += 16
    _producao_linhas(c, P, F, m, y)
    _grafico(c, P, F, m, y + 24, 452)


# ------------------------------------------------------------------ B: colunas verticais lado a lado
def _B(c, P, F, m):
    y = 82
    _titulo(c, P, F, "SAÚDE DO HARDWARE", y)
    y0, y1, w, gap = 106, 222, 30, 13
    x = 6 + 3
    for k, lab, un, vmin, av, lim in SAUDE:
        lv = vbarra(c, P, x, y0, y1, w, m[k], vmin, av, lim)
        t = _txt(k, m).replace(f"/{m['lim_w']}W", "W")
        c.text(f"b.{k}.val", x + w / 2, y0 - 6, t, font(JB, 10, "Bold"), _cor(P, lv) if lv != OK else P["white"], anchor="ms")
        c.text(f"b.{k}.lab", x + w / 2, y1 + 13, CURTO[k], font(JB, 9, "Regular"), P["sub"], anchor="ms")
        x += w + gap
    y = y1 + 30
    _reducao(c, P, F, m, 6, y)
    c.text("b.cool", 314, y, f"BOMBA {m['bomba']}  RAD {m['rad']}", F["xs"], P["sub"], anchor="rs")
    y += 20
    _titulo(c, P, F, "PRODUÇÃO", y)
    c.text("b.alg", 314, y, m["alg"], F["xs"], P["sub"], anchor="rs")
    y += 22
    _hashrate(c, P, F, m, 6, y, F["xl"])
    y += 16
    y = _producao_linhas(c, P, F, m, y)
    _grafico(c, P, F, m, y + 10, 452)


# ------------------------------------------------------------------ C: hashrate em destaque, barras compactas
def _C(c, P, F, m):
    y = 108
    q, lq = _queda(m)
    hb = _valor(c, P, "c.hr", 6, y, f"{m['hr']:.1f}", font(JB, 40, "Bold"), lq)
    c.text("c.un", hb[2] + 6, y - 22, "MH/s", F["sb"], P["sub"])
    c.text("c.var", hb[2] + 6, y - 4, f"▼{q:.0f}%" if q >= 1 else "ESTÁVEL", F["sb"], _cor(P, lq) if lq != OK else P["sub"])
    c.text("c.alg", 314, y - 22, m["alg"], F["xs"], P["sub"], anchor="rs")
    c.text("c.med", 314, y - 4, f"MÉDIA 15M {m['media']:.1f}", F["xs"], P["sub"], anchor="rs")
    _grafico(c, P, F, m, y + 8, y + 150, rotulo=False)
    y = _producao_linhas(c, P, F, m, y + 168)
    y += 20
    _titulo(c, P, F, "SAÚDE DO HARDWARE", y)
    y += 15
    col = 0
    for i, (k, lab, un, vmin, av, lim) in enumerate(SAUDE):
        x = 6 if i % 2 == 0 else 164
        lv = nivel(m[k], av, lim)
        c.text(f"c.{k}.lab", x, y, CURTO[k], F["xs"], P["sub"])
        c.text(f"c.{k}.val", x + 150, y, _txt(k, m).replace(f"/{m['lim_w']}W", "W"), F["sb"],
               _cor(P, lv) if lv != OK else P["white"], anchor="rs")
        barra(c, P, x, y + 4, 150, 5, m[k], vmin, av, lim)
        if i % 2 == 1:
            y += 21
    _reducao(c, P, F, m, 164, y)
    return y


# ------------------------------------------------------------------ D: duas colunas, GPU | CPU e sistema
def _D(c, P, F, m):
    y = 82
    _titulo(c, P, F, "GPU", y, 6, 155)
    _titulo(c, P, F, "CPU E SISTEMA", y, 165, 314)
    lados = ((6, [s for s in SAUDE if s[0] in ("gpu_t", "gpu_w", "gpu_fan", "vram")]),
             (165, [s for s in SAUDE if s[0] in ("cpu_t", "cpu_u", "ram")]))
    for x0, itens in lados:
        yy = y + 15
        for k, lab, un, vmin, av, lim in itens:
            lv = nivel(m[k], av, lim)
            c.text(f"d.{k}.lab", x0, yy, lab.replace("GPU ", "").replace("CPU ", ""), F["xs"], P["sub"])
            c.text(f"d.{k}.val", x0 + 149, yy, _txt(k, m), F["sb"], _cor(P, lv) if lv != OK else P["white"], anchor="rs")
            barra(c, P, x0, yy + 4, 149, 6, m[k], vmin, av, lim)
            yy += 23
    c.text("d.bomba", 165, y + 15 + 3 * 23, f"BOMBA {m['bomba']}", F["xs"], P["sub"])
    y = y + 15 + 4 * 23
    _reducao(c, P, F, m, 6, y)
    c.text("d.rad", 314, y, f"RAD {m['rad']}", F["xs"], P["sub"], anchor="rs")
    y += 22
    _titulo(c, P, F, "PRODUÇÃO", y)
    c.text("d.alg", 314, y, m["alg"], F["xs"], P["sub"], anchor="rs")
    y += 8
    q, lq = _queda(m)
    r, lr = _rej(m)
    caixas = (("HASHRATE", f"{m['hr']:.1f}", lq), ("MÉDIA 15M", f"{m['media']:.1f}", OK), ("REJEIÇÃO", f"{r:.1f}%", lr))
    for i, (lab, val, lv) in enumerate(caixas):
        x0 = 6 + i * 104
        c.rect((x0, y, x0 + 100, y + 38), outline=_cor(P, lv) if lv != OK else P["dim"])
        c.text(f"d.cx{i}.lab", x0 + 50, y + 12, lab, font(JB, 9, "Regular"), P["sub"], anchor="ms")
        c.text(f"d.cx{i}.val", x0 + 50, y + 32, val, F["m"], _cor(P, lv) if lv != OK else P["white"], anchor="ms")
    y += 56
    b = c.text("d.sh.lab", 6, y, "SHARES", F["xs"], P["sub"])
    c.text("d.sh", b[2] + 5, y, f"{m['ac']} A  {m['rj']} R", F["sb"], P["white"])
    _valor(c, P, "d.lat", 314, y, f"{c.fit(m['pool'], F['xs'], 110)} {m['lat']}ms", F["xs"],
           CRIT if m["lat"] > 250 else WARN if m["lat"] > 100 else OK, anchor="rs")
    _grafico(c, P, F, m, y + 10, 452)


# ------------------------------------------------------------------ E: o mais perto do limite primeiro
def _E(c, P, F, m):
    y = 82
    _titulo(c, P, F, "PERTO DO LIMITE", y)
    c.text("e.sub", 314, y, "% DO LIMITE", F["xs"], P["sub"], anchor="rs")
    ordem = sorted(SAUDE, key=lambda s: -(m[s[0]] - s[3]) / (s[5] - s[3]))
    y += 18
    for i, (k, lab, un, vmin, av, lim) in enumerate(ordem):
        frac = 100.0 * (m[k] - vmin) / (lim - vmin)
        lv = nivel(m[k], av, lim)
        grande = i < 3
        f = F["sb"] if grande else F["xs"]
        c.text(f"e.{k}.lab", 6, y, lab, f, P["white"] if grande else P["sub"])
        b = c.text(f"e.{k}.pct", 314, y, f"{frac:.0f}%", f, _cor(P, lv) if lv != OK else P["white"], anchor="rs")
        c.text(f"e.{k}.val", b[0] - 8, y, _txt(k, m), F["xs"], P["sub"], anchor="rs")
        h = 8 if grande else 4
        barra(c, P, 6, y + 4, 309, h, m[k], vmin, av, lim)
        y += 26 if grande else 19
    _reducao(c, P, F, m, 6, y)
    y += 20
    _titulo(c, P, F, "PRODUÇÃO", y)
    y += 20
    _hashrate(c, P, F, m, 6, y, F["xl"])
    c.text("e.med", 314, y, f"MÉDIA {m['media']:.1f}", F["xs"], P["sub"], anchor="rs")
    y = _producao_linhas(c, P, F, m, y + 16)
    _grafico(c, P, F, m, y + 10, 452, rotulo=False)


# ------------------------------------------------------------------ fusões F, G e H
def _barra_e(c, P, F, k, y, grande, x0=6, x1=314):
    """Linha do E: rótulo, valor e % do limite à direita, barra com as marcas de aviso e limite."""
    _, lab, un, vmin, av, lim = next(s for s in SAUDE if s[0] == k)
    m = c._m
    frac = 100.0 * (m[k] - vmin) / (lim - vmin)
    lv = nivel(m[k], av, lim)
    f = F["sb"] if grande else F["xs"]
    c.text(f"f.{k}.lab", x0, y, lab, f, P["white"] if grande else P["sub"])
    if un == "%":                                               # leitura já em %: o % do limite repetiria o número
        c.text(f"f.{k}.pct", x1, y, _txt(k, m), f, _cor(P, lv) if lv != OK else P["white"], anchor="rs")
    else:
        b = c.text(f"f.{k}.pct", x1, y, f"{frac:.0f}%", f, _cor(P, lv) if lv != OK else P["white"], anchor="rs")
        c.text(f"f.{k}.val", b[0] - 8, y, _txt(k, m), F["xs"], P["sub"], anchor="rs")
    barra(c, P, x0, y + 4, x1 - x0 + 1, 8 if grande else 4, m[k], vmin, av, lim)
    return y + (26 if grande else 19)


def _ordem(m):
    return sorted(SAUDE, key=lambda s: -(m[s[0]] - s[3]) / (s[5] - s[3]))


def _linha_extra(c, P, F, m, y):
    """Clock reduzido (ou o clock) à esquerda; bomba e radiador à direita."""
    _reducao(c, P, F, m, 6, y)
    lb = m["bomba"] < 1000
    c.text("f.cool", 314, y, f"BOMBA {m['bomba']}  RAD {m['rad']}", F["xs"], P["red"] if lb else P["sub"], anchor="rs")


def _producao_d(c, P, F, m, y, y_graf=452):
    """Produção do D: 3 caixas, shares e pool numa linha, última share, gráfico de 60 min (média tracejada)."""
    _titulo(c, P, F, "PRODUÇÃO", y)
    y += 8
    q, lq = _queda(m)
    r_, lr = _rej(m)
    caixas = (("HASHRATE MH/s", f"{m['hr']:.1f}", lq), ("MÉDIA 15 MIN", f"{m['media']:.1f}", OK), ("REJEIÇÃO", f"{r_:.1f}%", lr))
    for i, (lab, val, lv) in enumerate(caixas):
        x0 = 6 + i * 104
        c.rect((x0, y, x0 + 100, y + 38), outline=_cor(P, lv) if lv != OK else P["dim"])
        c.text(f"f.cx{i}.lab", x0 + 50, y + 12, lab, font(JB, 9, "Regular"), P["sub"], anchor="ms")
        c.text(f"f.cx{i}.val", x0 + 50, y + 32, val, F["m"], _cor(P, lv) if lv != OK else P["white"], anchor="ms")
    y += 54
    b = c.text("f.sh.lab", 6, y, "SHARES", F["xs"], P["sub"])
    c.text("f.sh", b[2] + 5, y, f"{m['ac']} A  {m['rj']} R", F["sb"], P["white"])
    lat_lv = CRIT if m["lat"] > 250 else WARN if m["lat"] > 100 else OK
    lb = _valor(c, P, "f.lat", 314, y, f"{m['lat']}ms", F["sb"], lat_lv, anchor="rs")
    c.text("f.pool", lb[0] - 6, y, c.fit(m["pool"], F["xs"], 110), F["xs"], P["sub"], anchor="rs")
    y += 15
    ush = m["ush"]
    lu = CRIT if ush >= 120 else WARN if ush >= 60 else OK
    b = c.text("f.ush.lab", 6, y, "ÚLTIMA SHARE", F["xs"], P["sub"])
    _valor(c, P, "f.ush", b[2] + 6, y, f"HÁ {ush}s" if ush < 60 else f"HÁ {ush // 60}m{ush % 60:02d}s", F["sb"], lu)
    vals = [v for v in m["serie"] if v is not None]
    g = Grafico(c, P, 6, 309, y + 8, y_graf, 0.0, max(vals) * 1.15)
    g.serie(m["serie"], P["accent"], True)
    ly = g.y(m["media"])
    for x in range(6, 315, 5):
        c.line((x, ly, min(x + 2, 314), ly), mix(P["white"], P["bg"], 0.4))
    c.text("f.gr.lab", 8, y + 17, "HASHRATE 60 MIN", F["xs"], P["sub"])


def _F(c, P, F, m):
    y = 82
    _titulo(c, P, F, "PERTO DO LIMITE", y)
    y += 18
    for i, s in enumerate(_ordem(m)):
        y = _barra_e(c, P, F, s[0], y, i < 3)
    _linha_extra(c, P, F, m, y)
    _producao_d(c, P, F, m, y + 20)


def _G(c, P, F, m):
    y = 82
    _titulo(c, P, F, "GPU", y)
    y += 17
    for k in ("gpu_t", "gpu_w", "gpu_fan", "vram"):
        y = _barra_e(c, P, F, k, y, False)
    y += 2
    _titulo(c, P, F, "CPU E SISTEMA", y)
    y += 17
    for k in ("cpu_t", "cpu_u", "ram"):
        y = _barra_e(c, P, F, k, y, False)
    _linha_extra(c, P, F, m, y)
    _producao_d(c, P, F, m, y + 20)


def _H(c, P, F, m):
    y = 82
    _titulo(c, P, F, "PERTO DO LIMITE", y)
    y += 18
    ordem = _ordem(m)
    for s in ordem[:4]:
        y = _barra_e(c, P, F, s[0], y, True)
    resto = "  ".join(f"{CURTO[s[0]]} {_txt(s[0], m).replace('/' + str(m['lim_w']) + 'W', 'W')}" for s in ordem[4:])
    c.text("h.resto", 6, y - 4, resto, F["xs"], P["sub"])
    y += 14
    _linha_extra(c, P, F, m, y)
    _producao_d(c, P, F, m, y + 20)


def draw_frame(vm_dict):
    v, c, col, F, _ = _base(vm_dict, P)
    v.raw("hdr_status")
    lv = (vm_dict.get("hdr_status") or ("", OK))[1]
    m = demo("critico" if lv == CRIT else "atencao" if lv == WARN else "normal")
    var = os.environ.get("MGP_MINERACAO") or vm_dict.get("_tela") or "A"
    c._m = m
    _topo(c, P, F, m, cabecalho=var in "ABCDE")
    {"A": _A, "B": _B, "C": _C, "D": _D, "E": _E, "F": _F, "G": _G, "H": _H}[var](c, P, F, m)
    _rodape_curto(c, v, P, col, F)
    return c, v


def _rodape_curto(c, v, P, col, F):
    """Relógio e data numa linha no pé da tela (o LOG completo fica na tela principal)."""
    y = 476
    c.line((6, y - 14, 314, y - 14), P["dim"])
    t, _ = v("clock")
    cb = c.text("sys.clock", 6, y, t, font(JB, 14, "Bold"), P["accent"])
    t, _ = v("date")
    c.text("sys.date", cb[2] + 8, y, t, F["xs"], P["white"])
    reg = v.raw("registro") or []
    if reg:
        item = reg[0]
        cor = P["red"] if item[2] == CRIT else P["amber"]
        c.text("sys.ult", 314, y, c.fit(item[1], F["xs"], 130), F["xs"], cor, anchor="rs")
