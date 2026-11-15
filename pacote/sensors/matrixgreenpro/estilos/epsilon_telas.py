# GAMMA EPSILON | estilos/epsilon_telas.py | versão 1.0.0 | 15/11/2026 09:30 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.0.0 15/11/2026 09:30 criação: telas de gráficos, de status dos backups e de andamento do backup
# Telas do GAMMA EPSILON além da principal (que é o GAMMA DELTA). Todas mantêm o cabeçalho e a escala N0/N1/N2,
# para um alerta ficar visível em qualquer tela; à direita da escala ficam o nome da tela e a posição na rotação.
#   graficos  = 5 gráficos de 24 h na largura toda: temperatura, uso, memória, rede e ping;
#   backups   = cada rotina de backup: estado, última execução, duração, resultado e próxima execução;
#   andamento = o backup rodando agora: percentual da pasta atual, pastas feitas, velocidade e tempo restante.
# escolher() decide a tela: alerta vermelho > backup rodando > alerta âmbar > rotação (uma tela por período).
import os
import time

from .alerta import mix
from .base import OK, WARN, CRIT, NA, NEUTRAL, font, JB, ROBOTO
from .graficos import Grafico, _fmt, _pk
from .reator_grupos import _base
from .reator_delta2 import _rodape

F_NOME = font(JB, 12, "Bold")          # nomes das rotinas: a JetBrains Mono tem a seta →

NOMES = {"principal": "PRINCIPAL", "graficos": "GRÁFICOS 24 H", "backups": "BACKUPS", "andamento": "BACKUP"}


def escolher(vm, agora=None):
    """Tela a desenhar agora e a lista da rotação. MGP_EPSILON_TELA (ou vm['_tela']) fixa uma tela (prévias)."""
    rot = vm.get("rotacao") or {}
    telas = [t for t in rot.get("telas", ["principal", "graficos", "backups"]) if t in NOMES and t != "andamento"]
    telas = telas or ["principal"]
    fixa = os.environ.get("MGP_EPSILON_TELA") or vm.get("_tela")
    if fixa in NOMES:
        return fixa, telas
    lv = (vm.get("hdr_status") or ("", OK))[1]
    if lv == CRIT:
        return "principal", telas
    if (vm.get("backup") or {}).get("ativo"):
        return "andamento", telas
    if lv == WARN:
        return "principal", telas
    agora = time.time() if agora is None else agora
    periodo = max(10.0, float(rot.get("periodo_s", 60)))
    return telas[int(agora // periodo) % len(telas)], telas


def indicador(c, P, F, tela, telas):
    """Posição na rotação no cabeçalho: um ponto por tela (o atual cheio); no andamento, BACKUP."""
    if tela == "andamento":
        c.text("hdr.tela", 172, 17, "BACKUP", F["xs"], P["amber"], anchor="ms")
        return
    n = len(telas)
    if n < 2:
        return
    x0 = 172 - (n - 1) * 5
    for i, t in enumerate(telas):
        x = x0 + i * 10
        if t == tela:
            c.d.ellipse((x - 3, 10, x + 3, 16), fill=P["accent"])
        else:
            c.d.ellipse((x - 3, 10, x + 3, 16), outline=P["dim"])


def _topo(c, v, P, F, tela, telas):
    """Nome da tela e relógio à direita da escala N0/N1/N2."""
    c.text("tela.nome", 314, 42, NOMES[tela], font(ROBOTO, 15, "Bold"), P["accent"], anchor="rs")
    t, _ = v("clock")
    pos = f"{telas.index(tela) + 1}/{len(telas)}  " if tela in telas else ""
    c.text("tela.pos", 314, 57, pos + t, F["xs"], P["sub"], anchor="rs")


def _titulo(c, P, F, nome, y, x1=314):
    b = c.text(f"tit.{nome}", 6, y, nome, F["g"], P["accent"])
    c.line((b[2] + 5, y - 3, x1, y - 3), P["dim"])
    return b


# ------------------------------------------------------------------ tela de gráficos
def _legenda(c, F, y, itens):
    """Legenda à direita: 'CPU 57° ▲84°' de cada série, na cor da série, da direita para a esquerda."""
    x = 314
    for nome, atual, pico, cor in reversed(itens):
        b = c.text(f"{nome}.pk", x, y, "▲" + pico, F["xs"], cor, anchor="rs")
        b = c.text(f"{nome}.at", b[0] - 4, y, atual, F["sb"], cor, anchor="rs")
        lab = nome.split(".")[-1].upper()
        if lab != "MS":                                        # o ping tem uma série só: sem rótulo
            b = c.text(f"{nome}.lab", b[0] - 4, y, lab, F["xs"], cor, anchor="rs")
        x = b[0] - 12
    return x


def graficos(vm, P):
    v, c, col, F, _ = _base(vm, P)
    h = v.raw("hist") or {}
    s = lambda k: h.get(k) or []
    verde, branco = P["accent"], P["white"]
    v.raw("hdr_status")

    def pico(k, tipo):
        p = _pk(h, k)
        if p is None:
            return "--"
        return f"{p:.0f}ms" if tipo == "ms" else _fmt(tipo, p)

    def atual(chave, tira=""):
        t, _ = v(chave)
        return t.replace(tira, "") if tira else t

    gb_vram, gb_ram = ("gb", h.get("vram_total")), ("gb", h.get("ram_total"))
    topo_rede = max([x for k in ("down_max", "up_max") for x in s(k) if x is not None] or [0.0])
    topo_ping = max([x for x in s("ping_max") if x is not None] or [0.0])
    blocos = [
        ("TEMPERATURA", 20.0, 100.0, [("cpu_t", verde, True), ("gpu_t", branco, False)],
         [("gr.temp.cpu", atual("cpu_temp", "C"), pico("cpu_t", "temp"), verde),
          ("gr.temp.gpu", atual("gpu_temp", "C"), pico("gpu_t", "temp"), branco)], "temp"),
        ("USO", 0.0, 100.0, [("cpu_u", verde, True), ("gpu_u", branco, False)],
         [("gr.uso.cpu", atual("cpu_util"), pico("cpu_u", "pct"), verde),
          ("gr.uso.gpu", atual("gpu_util"), pico("gpu_u", "pct"), branco)], "pct"),
        ("MEMÓRIA", 0.0, 100.0, [("vram", verde, True), ("ram", branco, False)],
         [("gr.mem.vram", atual("vram_pct_txt"), pico("vram", gb_vram), verde),
          ("gr.mem.ram", f"{round(v.raw('ram_pct') or 0)}%", pico("ram", gb_ram), branco)], gb_vram),
        ("REDE", 0.0, max(topo_rede * 1.1, 100e3), [("down", verde, True), ("up", branco, False)],
         [("gr.rede.↓", atual("net_down"), pico("down", "rede"), verde),
          ("gr.rede.↑", atual("net_up"), pico("up", "rede"), branco)], "rede"),
        ("PING", 0.0, max(topo_ping * 1.15, 40.0), [("ping", verde, True)],
         [("gr.ping.ms", atual("ping"), pico("ping", "ms"), verde)], "ms"),
    ]
    y, alt, passo = 76, 54, 80
    for nome, vmin, vmax, series, legenda, _tipo in blocos:
        _titulo(c, P, F, nome, y, x1=_legenda(c, F, y, legenda))
        g = Grafico(c, P, 6, 309, y + 4, y + 4 + alt, vmin, vmax)
        for k, cor, area in series:
            g.serie(s(k), cor, area)
        if nome == "PING":
            for lim, cor in ((20.0, P["amber"]), (100.0, P["red"])):     # limites do ping, quando cabem
                if lim < vmax:
                    ly = g.y(lim)
                    for x in range(6, 315, 6):
                        c.line((x, ly, min(x + 2, 314), ly), mix(cor, P["bg"], 0.35))
        y += passo
    for i, rot in enumerate(("-24H", "-18H", "-12H", "-6H", "AGORA")):
        x = 6 + round(308 * i / 4)
        c.text(f"gr.eixo{i}", x, y - 10, rot, F["xs"], P["sub"], anchor="ls" if i == 0 else "rs" if i == 4 else "ms")
    return c, v


# ------------------------------------------------------------------ tela de status dos backups
def backups(vm, P):
    v, c, col, F, _ = _base(vm, P)
    b = v.raw("backup") or {}
    v.raw("hdr_status")
    y = 82
    if b.get("nd"):
        c.text("bk.nd", 6, y + 10, "ROTINAS N/D (systemctl sem resposta)", F["xs"], P["sub"])
        return c, v, y + 20
    if not b.get("rotinas"):
        c.text("bk.vazio", 6, y + 10, "NENHUMA ROTINA DE BACKUP NO PC", F["xs"], P["sub"])
        c.text("bk.vazio2", 6, y + 24, "configure backup.rotinas no config.yaml", F["xs"], P["sub"])
        return c, v, y + 30
    for i, r in enumerate(b["rotinas"][:4]):
        t, lv = r["estado"]
        eb = c.text(f"bk{i}.est", 314, y, t, F["sb"], P["accent"] if lv == OK else P["sub"], anchor="rs")
        tb = c.text(f"bk{i}.nome", 6, y, c.fit(r["rotulo"], F_NOME, eb[0] - 16), F_NOME, P["accent"])
        c.line((tb[2] + 5, y - 4, eb[0] - 6, y - 4), P["dim"])
        y += 15
        lb = c.text(f"bk{i}.ult.lab", 6, y, "ÚLTIMA", F["xs"], P["sub"])
        ub = c.text(f"bk{i}.ult", lb[2] + 5, y, r["ultima"], F["sb"], P["white"])
        if r.get("duracao"):
            c.text(f"bk{i}.dur", ub[2] + 6, y, r["duracao"], F["xs"], P["sub"])
        if r.get("em"):
            c.text(f"bk{i}.em", 314, y, "EM " + r["em"], F["xs"], P["sub"], anchor="rs")
        y += 14
        t, lv = r["resultado"]
        if lv == WARN:
            bb = c.d.textbbox((6, y), t, font=F["sb"], anchor="ls")
            c.rect((bb[0] - 2, bb[1] - 1, bb[2] + 1, bb[3] + 1), fill=P["amber"])
            c.text(f"bk{i}.res", 6, y, c.fit(t, F["sb"], 300), F["sb"], P["bg"])
        else:
            c.text(f"bk{i}.res", 6, y, c.fit(t, F["sb"], 300), F["sb"], col(lv))
        y += 14
        lb = c.text(f"bk{i}.prox.lab", 6, y, "PRÓXIMA", F["xs"], P["sub"])
        c.text(f"bk{i}.prox", lb[2] + 5, y, r["proxima"], F["sb"], P["white"])
        y += 22
    _rodape(c, v, P, col, F, y - 10)
    return c, v, y


# ------------------------------------------------------------------ tela de andamento do backup
def andamento(vm, P):
    v, c, col, F, _ = _base(vm, P)
    b = v.raw("backup") or {}
    v.raw("hdr_status")
    a = b.get("ativo") or {}
    amb = P["amber"]
    y = 84
    if not a:                                                   # nenhuma rotina rodando (só nas prévias)
        c.text("an.nenhum", 6, y + 10, "NENHUM BACKUP RODANDO AGORA", F["sb"], P["sub"])
        _rodape(c, v, P, col, F, y + 20)
        return c, v, y + 20
    c.text("an.tit", 6, y, "BACKUP EM ANDAMENTO", F["h"], amb)
    c.text("an.ini", 314, y, "DESDE " + a.get("inicio", "N/D"), F["xs"], P["sub"], anchor="rs")
    y += 20
    f_rot = font(JB, 15, "Bold")
    c.text("an.rot", 6, y, c.fit(a.get("rotulo", "?"), f_rot, 300), f_rot, P["white"])
    y += 46
    pct = a.get("pct")
    if a.get("detalhado") and pct is not None:
        pb = c.text("an.pct", 6, y, f"{round(pct)}%", font(JB, 40, "Bold"), P["accent"])
        c.text("an.pasta.lab", pb[2] + 10, y - 20, "PASTA", F["xs"], P["sub"])
        c.text("an.pasta", pb[2] + 10, y - 4, c.fit(a.get("pasta") or "?", F["sb"], 314 - pb[2] - 12), F["sb"], P["white"])
        y += 10
        c.hbar(6, y, 308, 12, pct, P["accent"], mix(P["accent"], P["bg"], 0.85), seg=4, gap=1)
        y += 30
        idx, tot = a.get("indice"), a.get("total")
        if idx and tot:
            c.text("an.pastas.lab", 6, y, "PASTAS", F["xs"], P["sub"])
            c.text("an.pastas", 314, y, f"{idx} DE {tot}", F["sb"], P["white"], anchor="rs")
            y += 6
            w = (308 - (tot - 1) * 2) / tot
            for i in range(tot):
                x = 6 + i * (w + 2)
                cor = P["accent"] if i < idx - 1 else amb if i == idx - 1 else mix(P["accent"], P["bg"], 0.8)
                c.rect((round(x), y, round(x + w) - 1, y + 7), fill=cor)
            y += 26
        for i, (lab, chave) in enumerate((("COPIADO", "copiado"), ("VELOCIDADE", "velocidade"),
                                          ("RESTANTE", "restante"), ("DECORRIDO", "decorrido"))):
            c.text(f"an.{chave}.lab", 6, y, lab, F["xs"], P["sub"])
            c.text(f"an.{chave}", 314, y, a.get(chave, "N/D"), F["sb"], P["white"], anchor="rs")
            y += 15
    else:                                                       # rotina sem arquivo de andamento: só o tempo
        c.text("an.pct", 6, y, a.get("decorrido", "N/D"), font(JB, 32, "Bold"), P["accent"])
        y += 10
        fase = int(time.time()) % 8                             # barra listrada: andamento desconhecido
        for x in range(6 - 16 + fase * 2, 314, 16):
            c.poly([(max(6, x), y), (min(314, x + 8), y), (min(314, x + 14), y + 11), (max(6, x + 6), y + 11)],
                   fill=mix(amb, P["bg"], 0.35))
        c.rect((6, y, 314, y + 11), outline=mix(amb, P["bg"], 0.5))
        y += 30
        c.text("an.semdet", 6, y, "SEM PERCENTUAL: A ROTINA NÃO", F["xs"], P["sub"])
        c.text("an.semdet2", 6, y + 14, "GRAVA O ARQUIVO DE ANDAMENTO", F["xs"], P["sub"])
        y += 32
    # as outras rotinas, em uma linha cada
    outras = [r for r in b.get("rotinas", []) if r.get("unidade") != a.get("unidade")]
    if outras:
        y += 4
        _titulo(c, P, F, "OUTRAS ROTINAS", y)
        for i, r in enumerate(outras[:3]):
            y += 15
            t, lv = r["resultado"]
            nb = c.text(f"an.o{i}.nome", 6, y, c.fit(r["rotulo"], F["sb"], 130), F["sb"], P["white"])
            c.text(f"an.o{i}.res", 314, y, c.fit(t, F["xs"], 314 - nb[2] - 10), F["xs"], amb if lv == WARN else P["sub"], anchor="rs")
    _rodape(c, v, P, col, F, y)
    return c, v, y
