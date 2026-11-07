# GAMMA v2 HACKING "ROOT" | versão 0.1.0 | 07/11/2026 20:15 (-03) | criação original (Claude, para Lucas Tavares)
# A tela é uma sessão de terminal: cada grupo é a saída de um comando digitado no prompt (status, sensors, df,
# fans, ip, date), com etiquetas no estilo do systemd ([  OK  ], [ AVISO], [FALHA]), barras ASCII e cursor
# piscando no fim. Linhas de varredura de monitor CRT no fundo.
from .v2_base import Ctx, P, mix, JB, OK, WARN, CRIT, NA, LOST

LH = 14                      # altura de linha


class Term:
    def __init__(self, cx, y=14):
        self.cx, self.y, self.n = cx, y, 0
        self.f = cx.f(JB, 11, "Regular")
        self.fb = cx.f(JB, 11, "Bold")

    def linha(self, partes, x=4):
        """partes: lista de (texto, cor) ou (texto, cor, negrito)."""
        for p in partes:
            s, cor = p[0], p[1]
            if s:
                b = self.cx.t(f"l{self.n}.{x}", x, self.y, s, self.fb if len(p) > 2 and p[2] else self.f, cor)
                x = b[2]
        self.y += LH
        self.n += 1
        return x

    def cmd(self, comando):
        P_ = self.cx.P
        self.linha([("root@gamma", P_["accent"], True), (":~# ", P_["sub"]), (comando, P_["white"], True)])


def _barra(pct, n=20):
    if pct is None:
        return "[" + "?" * n + "]"
    k = round(n * pct / 100)
    return "[" + "#" * k + "." * (n - k) + "]"


def draw_frame(vm):
    cx = Ctx(vm, "ROOT")
    v, c = cx.v, cx.c
    for y in range(0, 480, 3):                               # varredura do CRT
        c.line((0, y, 319, y), mix(P["bg"], (0, 0, 0), 0.5))
    T = Term(cx)
    w, s_, a = P["white"], P["sub"], P["accent"]
    col = cx.col
    val = lambda k, lado=0: ((v(k)[0]).ljust(lado), col(v(k)[1], w))

    T.cmd("gamma status" + ("  --demo" if cx.demo else ""))
    tag = {OK: "[  OK  ]", WARN: "[ AVISO]", CRIT: "[FALHA ]"}[cx.lvl]
    cor = cx.cor_nivel()
    T.linha([(tag, cor if cx.on else mix(cor, P["bg"], 0.6), True), (f" {({OK: 'N0', WARN: 'N1', CRIT: 'N2'}[cx.lvl])} ", cor, True),
             (cx.rotulo.lower(), cor)])
    T.cmd("sensors --all")
    t, lv = v("cpu_util")
    T.linha([("cpu   ", s_), (t.ljust(5), col(lv, w)), val("cpu_temp", 7), val("cpu_ghz", 8), ("load ", s_),
             (v("cpu_load")[0], col(v("cpu_load")[1], w))])
    T.linha([("      ", s_), (_barra(cx.pct("cpu_pct")), mix(a, P["bg"], 0.3))])
    T.linha([("gpu   ", s_), val("gpu_util", 5), val("gpu_temp", 7), val("gpu_mhz", 8), (v("gpu_w")[0] + "W", col(v("gpu_w")[1], w)),
             (v("gpu_wlim")[0].replace("LIM ", "/"), s_)])
    T.linha([("      fan ", s_), val("gpu_fan_pct", 5), ("fps ", s_), val("fps")])
    t, lv = v("vram_pct_txt")
    T.linha([("vram  ", s_), val("vram_txt", 12), (_barra(cx.pct("vram_pct"), 16), col(lv, mix(a, P["bg"], 0.3))), (" " + t, col(lv, w))])
    rp, rl = cx.ram_pct_txt()
    t, lv = v("ram_used"); t2, _ = v("ram_total")
    T.linha([("ram   ", s_), ((t + t2).ljust(12), col(lv, w)), (_barra(cx.pct("ram_pct"), 16), col(rl, mix(a, P["bg"], 0.3))), (" " + rp, col(rl, w))])
    T.linha([("      avail ", s_), val("ram_avail", 8), ("temp ", s_), val("t_ram")])

    T.cmd("df -h --temp")
    for d in cx.discos():
        T.linha([(d["name"].lower().ljust(5), a, True), (d["use"].ljust(13), col(d.get("use_lvl", NA), w)),
                 (d["pct_txt"].ljust(5), col(d["lvl"], w)), (d["free"].ljust(7), col(d["lvl"], s_)),
                 (d.get("temp_txt", "N/D"), col(d.get("temp_lvl", NA), w))])
    for bb in cx.baias()[:4]:
        uso = bb.get("use") or bb["cap"] or "-"
        T.linha([(f"bay{bb['n']} ", a), (uso.ljust(13), col(bb["lvl"], w)), ((bb.get("pct_txt") or "").ljust(5), col(bb.get("pct_lvl", NA), w)),
                 (bb["palavra"].lower(), col(bb["lvl"], s_))])

    T.cmd("fans; temps")
    x = 4
    T.linha([("pump ", s_), (cx.sem_rpm(v("pump")[0]).ljust(5), col(v("pump")[1], w)), ("rad ", s_),
             (cx.sem_rpm(v("cpu_fan")[0]).ljust(5), col(v("cpu_fan")[1], w)), ("inf ", s_),
             (cx.sem_rpm(v("fan_sqi")[0]).ljust(5), col(v("fan_sqi")[1], w)), ("lat ", s_),
             (cx.sem_rpm(v("fan_sql")[0]).ljust(5), col(v("fan_sql")[1], w)), ("tra ", s_), (cx.sem_rpm(v("fan_sqt")[0]), col(v("fan_sqt")[1], w))])
    T.linha([("board ", s_), val("t_placa", 6), ("ssd ", s_), val("t_ssd")])

    T.cmd("ip -s link; ping -c1 1.1.1.1")
    for k, tag2 in (("eth", "eth "), ("wifi", "wifi")):
        d = cx.iface(k)
        x = T.linha([(tag2 + " ", a), (d["state"][0].ljust(6), col(d["state"][1], w)),
                     (cx.fit(d["info"][0].lower(), T.f, 120).ljust(20), col(d["info"][1], s_) if d["info"][1] != 9 else s_),
                     (d["rates"][0], w)])
    T.linha([("rx ", s_), val("net_rx", 9), ("tx ", s_), val("net_tx", 9), ("↓", w), (v("net_down")[0], w)])
    T.linha([("ping ", s_), val("ping", 7), (v("inet")[0].lower(), col(v("inet")[1], w)), ("  ↑", w), (v("net_up")[0], w)])

    T.cmd("date; uptime; curl wttr")
    t, _ = v("date"); t2, _ = v("clock")
    T.linha([(t.lower() + " ", w), (t2, a, True), ("  up ", s_), val("uptime")])
    T.linha([(cx.fit(v("os")[0].lower(), T.f, 150) + "  ", s_), ("(" + cx.fit(v("wage")[0].lower(), T.f, 140) + ")", s_)])
    cid = cx.fit(v.raw("city", "").lower(), T.f, 110) + " "
    tt = v("wtemp")[0] + " "
    resto = 310 - T.f.getlength(cid + tt)
    T.linha([(cid, s_), (tt, col(v("wtemp")[1], w)), (cx.fit(v("wdesc")[0].lower(), T.f, resto), col(v("wdesc")[1], w))])
    xe = T.linha([("root@gamma", a, True), (":~# ", s_)])
    if cx.blink:
        c.rect((xe + 1, T.y - LH - 9, xe + 7, T.y - LH + 2), fill=a)
    cx.selo_versao(314, 472, cx.f(JB, 8, "Regular"), mix(P["sub"], P["bg"], 0.2))
    for k in ("coleta", "gpu_pct"):
        v.raw(k)
    return cx.fim((2, 0.8, 100))
