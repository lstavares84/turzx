# GAMMA EPSILON | protótipo | versão 0.6.0 | 08/11/2026 12:31 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 0.6.0 08/11/2026 12:31 DISCO e TERRA no centro: cada disco encosta no centro do grupo, U, T e L para fora
# histórico: 0.5.0 08/11/2026 10:33 U, T e L de cada disco e de cada baia em volta da célula com o nome
# histórico: 0.4.0 08/11/2026 10:26 TERRAMASTER numa colmeia própria, separada de DISCOS; grupos reposicionados
# histórico: 0.3.0 08/11/2026 10:17 os detalhes do rodapé viram células: cada grupo cresce para fora (empacotamento automático)
# histórico: 0.2.0 08/11/2026 10:14 tudo o que o DELTA mostra, exceto os gráficos (detalhes no rodapé), DESM nas baias
# Proposta da versão EPSILON: todos os dados em células de colmeia, agrupados por categoria (CPU, GPU, RAM,
# DISCOS + TERRAMASTER, REFRIGERAÇÃO e REDE) ao redor de um CORE grande. As células de um grupo ficam juntas
# (vão de 2 px, como hoje); os grupos ficam separados entre si e do CORE por cerca de 2 mm (13 px: a tela de
# 3,5" tem cerca de 6,5 px por mm). A célula central de cada grupo traz o nome e o estado (OK, ATEN, CRIT); as
# outras trazem um dado cada. Cada grupo começa pelo anel em volta do centro e cresce para fora, célula a célula,
# sempre colada a uma célula do próprio grupo, dentro da tela e longe dos outros grupos e do CORE.
# Embaixo: LOG, relógio e clima. Estudo: não entra nos ZIPs.
import math
import re

from .base import font, JB, ROBOTO, OK, WARN, CRIT, NA, LOST, NEUTRAL, bloom
from .reator import hexagon
from .reator_gamma import GAMMA
from .reator_grupos import _base, _resumos
from .reator_delta2 import _registro, _sistema
from .alerta import mix, counts, label

P = dict(GAMMA, selo="EPSILON", alert="nenhum", nome_log="LOG")

R = 17                                   # raio das células de dados
GAP = 2                                  # vão entre células do mesmo grupo
SX = math.sqrt(3) * R + GAP              # distância entre vizinhas na mesma linha
SY = 1.5 * R + GAP                       # distância entre linhas
MM2 = 13                                 # 2 mm na tela de 3,5" (cerca de 6,5 px por mm)
D = 2 * (SX + math.sqrt(3) * R / 2) + MM2 - 4   # distância entre centros de grupos vizinhos
CX, CY = 160, 196                        # centro do CORE
Y_MAX = 416                              # nenhuma célula passa daqui (embaixo ficam LOG, relógio e clima)
VIZ = [(SX, 0), (SX / 2, SY), (-SX / 2, SY), (-SX, 0), (-SX / 2, -SY), (SX / 2, -SY)]
SEP = math.sqrt(3) * R + MM2 - 2         # distância mínima entre centros de células de grupos diferentes
# centro de cada grupo em relação ao CORE; posições achadas por busca: nos 3 estados, com 1 ou 4 baias montadas,
# cabe tudo e todo disco e toda baia encostam no centro do seu grupo
LUGARES = {"g_cpu": (-D / 2, -D * 0.866), "g_gpu": (D / 2, -D * 0.866), "g_ram": (D, 0),
           "g_ref": (-D * 1.15, -D * 0.57), "g_rede": (-D * 0.83, D * 0.51),
           "g_dsk": (D * 0.9, D * 1.48), "g_tm": (-D * 0.61, D * 1.45)}
ORDEM = ["g_cpu", "g_gpu", "g_ram", "g_ref", "g_rede", "g_tm", "g_dsk"]                  # ordem de crescimento


def _curto(t, tira=("GHz", "MHz", "MB/s", "KB/s", "GB/s", "B/s", "RPM", "ms", "dBm")):
    t = str(t).replace("°C", "°")
    for x in tira:
        t = t.replace(x, {"MB/s": "M", "KB/s": "K", "GB/s": "G", "B/s": "B", "dBm": "dB"}.get(x, ""))
    t = t.replace("GB", "G").replace("TB", "T")
    m = re.fullmatch(r"(-?\d+\.\d+)([A-Za-z°%]*)", t)
    if m and len(t) > 5:                                 # 284.1G -> 284G, 11.99T -> 12.0T (cabe na célula)
        x, un = float(m.group(1)), m.group(2)
        t = (f"{x:.0f}" if abs(x) >= 100 else f"{x:.1f}") + un
    return t


def _celula(c, P, col, nome, x, y, lab, txt, lv, f_lab, f_val, centro=False, r=R):
    CELL = dict(P["cells"]); CELL[LOST] = CELL[WARN]
    k = lv if lv in CELL else NEUTRAL
    fill, edge = CELL[k if txt not in ("N/D", "--") else NA]
    c.poly(hexagon(x, y, r), fill=fill, outline=edge, width=2 if (centro or lv in (WARN, CRIT)) else 1)
    larg = math.sqrt(3) * r - 4
    c.text(f"{nome}.l", x, y - 2, c.fit(lab, f_lab, larg + 2), f_lab, P["accent"] if centro else P["sub"], anchor="ms")
    c.text(f"{nome}.v", x, y + 9, c.fit(txt, f_val, larg), f_val,
           col(lv) if lv in (WARN, CRIT, LOST, OK) else P["white"], anchor="ms")


def _tb(t):
    """'0.42/1.00TB' -> ('0.42T', '1.00T'); '120/980GB' -> ('120G', '980G')."""
    if "/" not in t:
        return t, ""
    a, b = t.split("/", 1)
    un = "T" if b.endswith("TB") else "G"
    return a + un, b.replace("TB", "T").replace("GB", "G")


FORA_DO_CENTRO = {}                      # discos ou baias que não couberam encostados no centro (para a busca de lugares)


def _empacotar(grupos, rc):
    """Posições de cada grupo: centro e depois a célula livre mais próxima da última, sempre vizinha de uma célula
    do próprio grupo. Um dado com 4º campo (o rótulo da célula-mãe, ex.: "M.2 U" -> "M.2") fica encostado na mãe,
    e a mãe é posta onde sobram vizinhas livres para as filhas. Devolve {grupo: [(x, y), ...]} e o que não coube."""
    todas, pos, falta = [], {}, {}
    FORA_DO_CENTRO.clear()

    def livre(x, y, gk):
        if x - R * 0.87 < 3 or x + R * 0.87 > 317 or y - R < 30 or y + R > Y_MAX:
            return False
        if math.hypot(x - CX, y - CY) < rc * 0.866 + R * 0.866 + MM2 - 2:
            return False
        for (ox, oy, og) in todas:
            d = math.hypot(x - ox, y - oy)
            if d < SX - 1 or (og != gk and d < SEP):
                return False
        return True

    for gk, gx, gy, dados in grupos:                         # 1º: o centro de cada grupo
        todas.append((gx, gy, gk)); pos[gk] = [(gx, gy)]
    def vizinhas(px, py):
        return [(round(px + ox, 2), round(py + oy, 2)) for ox, oy in VIZ]

    def formas(m, k):
        """Lugares para k filhas: cada uma encosta na mãe ou numa filha já posta (as encostadas na mãe primeiro)."""
        if k == 0:
            yield []
            return
        vistos = set()
        def rec(feitas):
            if len(feitas) == k:
                chave = frozenset(feitas)
                if chave not in vistos:
                    vistos.add(chave)
                    yield list(feitas)
                return
            for b in [m] + feitas:
                for q in vizinhas(*b):
                    if q != m and q not in feitas:
                        yield from rec(feitas + [q])
        yield from rec([])

    for gk, gx, gy, dados in grupos:                         # 2º: cresce cada grupo, um bloco por vez
        blocos = []                                          # célula-mãe seguida das filhas
        for d in dados:
            if len(d) > 3 and blocos and blocos[-1][0][0] == d[3]:
                blocos[-1].append(d)
            else:
                blocos.append([d])
        com_filhas = any(len(b) > 1 for b in blocos)         # grupo de discos: as mães em volta do centro
        maes, postas = [], 0
        for bl in blocos:
            k = len(bl) - 1
            anel = [q for q in vizinhas(gx, gy) if livre(*q, gk)] if com_filhas else []
            if anel:
                cand = anel
            else:
                cand = [q for q in {q for p in pos[gk] for q in vizinhas(*p)} if livre(*q, gk)]
            ux, uy = pos[gk][-1]
            melhor = None
            for (x, y) in cand:
                todas.append((x, y, gk))
                for fl in formas((x, y), k):
                    if not all(livre(*q, gk) for q in fl):
                        continue
                    longe = sum(1 for q in fl if math.hypot(q[0] - x, q[1] - y) > SX + 1)    # filhas fora da mãe
                    junto = sum(1 for (mx, my) in maes if math.hypot(x - mx, y - my) < SX + 1) if com_filhas else 0
                    fora = sum(math.hypot(q[0] - gx, q[1] - gy) for q in fl) / max(1, k)       # filhas para fora
                    if com_filhas:                       # mães separadas, filhas para fora
                        chave = (longe, junto, -round(fora / 4), round(math.hypot(x - ux, y - uy) / 4),
                                 -math.hypot(x - CX, y - CY))
                    else:                                # como antes: perto da última, do centro, longe do CORE
                        chave = (0, 0, round(math.hypot(x - ux, y - uy) / 4), round(math.hypot(x - gx, y - gy) / 4),
                                 -math.hypot(x - CX, y - CY))
                    if melhor is None or chave < melhor[0]:
                        melhor = (chave, [(x, y)] + fl)
                todas.pop()
            if melhor is None:
                break
            for q in melhor[1]:
                pos[gk].append(q); todas.append((q[0], q[1], gk))
            maes.append(melhor[1][0])
            if com_filhas and not anel:
                FORA_DO_CENTRO[gk] = FORA_DO_CENTRO.get(gk, 0) + 1
            postas += len(bl)
        falta[gk] = len(dados) - postas
    return pos, falta


def draw_frame(vm_dict):
    v, c, col, F, vals = _base(vm_dict, P)
    vals.update(_resumos(v, vals))
    for k in ("cpu_pct", "gpu_pct", "vram_pct", "gpu_fan_rpm", "power", "power_tag", "coleta", "os", "wage",
              "t_ssd", "fan_sql"):
        v.raw(k)
    f_lab, f_val = font(ROBOTO, 7, "Bold"), font(JB, 8, "Bold")
    g = lambda k: v(k)
    t = lambda k: tuple(g(k))

    rp, rl = vals["ram"][1]
    ld, ll = g("cpu_load")
    cargas = (ld.split("/") + ["", "", ""])[:3]
    vu, vl = g("vram_txt"); vu_a, vu_b = _tb(vu) if "/" in vu else (vu, "")
    ru, rlv = g("ram_used"); rt, _ = g("ram_total")
    lim = g("gpu_wlim")[0].replace("LIM ", "").replace("W", "")
    k_sq = "fan_sqi" if v.raw("fan_sqi", ("N/D", NA))[1] not in (NA, LOST) else "fan_sql"

    dsk = []
    for d in v.raw("disks", [])[:3]:
        if d.get("pct") is None:
            dsk.append((d["name"], "DESM" if d.get("use") == "DESMONTADO" else "N/D", NEUTRAL))
            continue
        a, b = _tb(d["use"])
        nd = d["name"]
        dsk += [(nd, d["pct_txt"], d["lvl"]), (nd + " U", a, NEUTRAL, nd), (nd + " T", b, NEUTRAL, nd),
                (nd + " L", d["free"].replace("GB", "G").replace("TB", "T"), d["lvl"], nd)]
    tm = []                                              # TERRAMASTER: colmeia própria (as baias são só informação)
    baias = (v.raw("baias", []) or [])[:4]
    for bb in baias:
        nb = f"B{bb['n']}"
        if bb.get("use"):
            a, b = _tb(bb["use"])
            tm += [(nb, bb["pct_txt"], bb.get("pct_lvl", OK)), (nb + " U", a, NEUTRAL, nb), (nb + " T", b, NEUTRAL, nb)]
        else:
            tm.append((nb, {"DESM": "DESM", "LIVRE": "LIVRE"}.get(bb["estado"], bb["cap"] or bb["curta"]), NEUTRAL))
    montadas = sum(1 for bb in baias if bb["estado"] == "MONT")
    vals["g_tm"] = ("TERRA", (f"{montadas}/{len(baias)}", NEUTRAL))
    tot = v.raw("total_hd")
    if tot:
        dsk += [("TOTAL", tot["pct_txt"], OK), ("TOT U", tot["uso"].replace("TB", "T"), NEUTRAL, "TOTAL"),
                ("TOT T", tot["total"].replace("TB", "T"), NEUTRAL, "TOTAL")]

    inet_t, inet_l = g("inet")
    eth, wifi = v.raw("eth", {}), v.raw("wifi", {})
    def iface(d, nome):
        st = d.get("state", ("N/D", NA))
        info = (d.get("info", ("", NA))[0] or "").split()
        extra = info[1] if len(info) > 1 else ""
        out = [(nome, st[0], st[1])]
        if extra and st[0] not in ("N/D", "OFF"):
            out.append(("LINK" if nome == "ETH" else "SINAL", extra.replace("SEM", "-"), d["info"][1]))
        return out
    grupos_dados = {
        "g_cpu": [("USO",) + t("cpu_util"), ("TEMP",) + t("cpu_temp"), ("GHz",) + t("cpu_ghz"),
                  ("LD 1", cargas[0], ll), ("LD 5", cargas[1], ll), ("LD 15", cargas[2], ll)],
        "g_gpu": [("USO",) + t("gpu_util"), ("TEMP",) + t("gpu_temp"), ("MHz",) + t("gpu_mhz"),
                  ("VRAM",) + t("vram_pct_txt"), ("VR U", vu_a, vl), ("VR T", vu_b, NEUTRAL),
                  ("WATTS",) + t("gpu_w"), ("LIM", lim + "W" if lim else "", NEUTRAL), ("FAN",) + t("gpu_fan_pct"),
                  ("FPS",) + t("fps")],
        "g_ram": [("USO", rp, rl), ("USADO", ru + "G", rlv), ("TOTAL", rt.replace("/", "").replace("GB", "G"), NEUTRAL),
                  ("DISP",) + t("ram_avail"), ("TEMP",) + t("t_ram")],
        "g_dsk": dsk,
        "g_tm": tm,
        "g_rede": [("DOWN",) + t("net_down"), ("UP",) + t("net_up"), ("PING",) + t("ping"),
                   ("NET", "ON" if inet_l == OK else "OFF" if inet_l == CRIT else inet_t, inet_l),
                   ("RX",) + t("net_rx"), ("TX",) + t("net_tx")] + iface(eth, "ETH") + iface(wifi, "WIFI"),
        "g_ref": [("BOMBA",) + t("pump"), ("RAD",) + t("cpu_fan"), ("SQUAM",) + t(k_sq), ("TRA",) + t("fan_sqt"),
                  ("PLACA",) + t("t_placa")],
    }
    lugares = LUGARES
    ordem = [g for g in ORDEM if g != "g_tm" or tm]      # sem o gabinete, sem a colmeia
    rc = (D - SX - math.sqrt(3) * R / 2 - MM2) / 0.866
    grupos = [(gk, CX + lugares[gk][0], CY + lugares[gk][1], grupos_dados[gk]) for gk in ordem]
    pos, falta = _empacotar(grupos, rc)

    # CORE
    lv_core = vals["core"][1][1]
    fill, edge = dict(P["cells"]).get(lv_core if lv_core in (OK, WARN, CRIT) else NEUTRAL, P["cells"][NEUTRAL])
    on = vm_dict.get("blink", True) or lv_core != CRIT
    c.poly(hexagon(CX, CY, rc), fill=fill, outline=edge if on else mix(edge, P["bg"], 0.6), width=3)
    st, slv = v("hdr_status")
    lvl = slv if slv in (OK, WARN, CRIT) else OK
    c.text("core.l", CX, CY - 18, "CORE", font(ROBOTO, 11, "Bold"), P["sub"], anchor="ms")
    c.text("core.n", CX, CY + 10, {OK: "N0", WARN: "N1", CRIT: "N2"}[lvl], font(JB, 26, "Bold"),
           col(lv_core) if lv_core != OK else P["accent"], anchor="ms")
    nc, nw = counts(v)
    c.text("core.r", CX, CY + 26, c.fit(label(st, nc, nw, lvl), font(JB, 9, "Bold"), 2 * rc * 0.8),
           font(JB, 9, "Bold"), col(lv_core) if lv_core != OK else P["ice"], anchor="ms")

    for gk, gx, gy, dados in grupos:
        nome, (tt, lv) = vals[gk]
        _celula(c, P, col, f"{gk}.c", gx, gy, nome.replace("DISCOS", "DISCO").replace("REFR.", "REFR"), tt, lv,
                f_lab, f_val, centro=True)
        for i, ((lab, txt, lvl_, *_), (x, y)) in enumerate(zip(dados, pos[gk][1:])):
            _celula(c, P, col, f"{gk}.{i}", x, y, lab, _curto(txt), lvl_, f_lab, f_val)
    v.raw("eth"); v.raw("wifi")
    if any(falta.values()):                                  # aviso no protótipo se algum dado não coube
        c.text("falta", 6, 40, "não coube: " + " ".join(f"{k[2:]}+{n}" for k, n in falta.items() if n),
               font(JB, 8, "Regular"), P["amber"])

    # rodapé: LOG, relógio e clima
    b = c.text("tit.REG", 6, 431, "LOG", F["g"], P["accent"])
    c.line((b[2] + 5, 427, 206, 427), P["dim"])
    _registro(c, v, P, F, 6, 433, 206, 4, "barras")
    _sistema(c, v, P, col, F, 314, 432, alinhar="rs")
    if P.get("bloom"):
        c.img = bloom(c.img, *P["bloom"])
    return c, v
