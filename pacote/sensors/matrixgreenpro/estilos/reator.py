# MATRIX GREEN PRO | estilo NÚCLEO DO REATOR (família 06) | versão 3.6.0 | 02/11/2026 19:40 (-03) | percentuais entre parênteses (P['pct']='paren') e informações à esquerda (P['flow'])
# histórico: 3.5.0 02/11/2026 19:05 percentuais no registro (P['pct'])
# histórico: 3.4.0 02/11/2026 18:40 indicador de alerta selecionável (P['alert']), escala N0/N1/N2
# histórico: 3.3.0 02/11/2026 18:05 indicador de alerta selecionável
# histórico: 3.2.0 02/11/2026 17:40 subtítulo opcional e layout losango
# histórico: 3.1.0-alfa 01/11/2026 09:20 motor com variantes
# histórico: 3.0.0-alfa2 01/11/2026 00:55 criação do estilo 06 original (Cherenkov, favo 4-5-4)
#
# Motor da família 06. Uma paleta + um layout de núcleo:
#   favo13 = favo de mel 4-5-4 (06 original e 06-C SALA LIMPA)
#   favo19 = favo de mel 3-4-5-4-3 com 19 células (GAMMA, ex 06-A URÂNIO)
#   losango = 14 células em losango 2-3-4-3-2 (variantes GAMMA SONAR)
#   anel   = 12 células em anel ao redor de um núcleo grande (06-B FUSÃO)
# Abaixo do núcleo, o registro completo das leituras (todas as métricas).
import math

from .base import (Canvas, VM, font, JB, ROBOTO, W, H, OK, WARN, CRIT, NA, LOST, NEUTRAL, bloom, strip_status, iface_row)

CHERENKOV = {
    "bg": (2, 6, 15), "accent": (46, 168, 255), "ice": (159, 226, 255), "white": (235, 244, 255),
    "sub": (110, 140, 175), "dim": (50, 70, 95), "amber": (255, 176, 0), "red": (255, 52, 70),
    "cells": {OK: ((6, 33, 61), (46, 168, 255)), WARN: ((61, 42, 0), (255, 176, 0)),
              CRIT: ((70, 0, 12), (255, 52, 70)), NA: ((10, 15, 24), (30, 42, 58)),
              NEUTRAL: ((10, 22, 40), (58, 90, 128))},
    "title": "NÚCLEO", "subtitle": "REATOR MGP-1", "bloom": (3, 0.7, 120), "deco": None,
}


def short(s):
    s = s.replace("RPM", "").replace("°C", "°")
    return s if len(s) <= 5 else s[:5]


def hexagon(cx, cy, r, flat=False):
    a0 = 0 if flat else -90
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(a0, a0 + 360, 60)]


def cell_values(v, slv, cool=False):
    """Todos os valores que podem ocupar células, com rótulo curto e nível."""
    disks = (v.raw("disks", []) + [{"name": "---", "pct_txt": "N/D", "lvl": NA}] * 3)[:3]
    hl = v.raw("health", {})
    e, w = v.raw("eth", {}), v.raw("wifi", {})
    es, ws = (e or {}).get("state", ("N/D", NA)), (w or {}).get("state", ("N/D", NA))
    rede = "ETH" if es[0] == "ATIVA" else "WIFI" if ws[0] == "ATIVA" else "ON" if "ON" in (es[0], ws[0]) else (
        "OFF" if "OFF" in (es[0], ws[0]) else "N/D")
    cl, cll = v("coleta")
    coleta = "OK" if cll == OK else ("FALH" if "FALHOU" in cl else "PARC")
    load = v("cpu_load")
    pw, pwl = v("power")
    return {
        "cpu": ("CPU", v("cpu_util")), "cput": ("CPU°", v("cpu_temp")), "cfan": ("BOMBA", v("pump")) if cool else ("C.FAN", v("cpu_fan")),
        "gpu": ("GPU", v("gpu_util")), "gput": ("GPU°", v("gpu_temp")), "gfan": ("G.FAN", v("gpu_fan_pct")),
        "vram": ("VRAM", v("vram_pct_txt")),
        "ram": ("RAM", (f"{round(v.raw('ram_pct') or 0)}%", v("ram_used")[1])),
        "d0": (disks[0]["name"], (disks[0]["pct_txt"], disks[0]["lvl"])),
        "d1": (disks[1]["name"], (disks[1]["pct_txt"], disks[1]["lvl"])),
        "d2": (disks[2]["name"], (disks[2]["pct_txt"], disks[2]["lvl"])),
        "ping": ("PING", v("ping")), "fps": ("FPS", v("fps")), "gpuw": ("GPU W", v("gpu_w")),
        "rede": ("REDE", (rede, hl.get("conexao", NA))), "pwr": ("TOT W", (pw, pwl)),
        "coleta": ("COLETA", (coleta, cll)),
        "tplaca": ("PLACA", v("t_placa")), "tram": ("RAM°", v("t_ram")), "tssd": ("SSD°", v("t_ssd")), "load": ("LOAD", (load[0].split("/")[0], NEUTRAL)),
        "core": ("CORE", ({OK: "OK", WARN: "ATEN", CRIT: "CRIT"}.get(slv, "N/D"),
                          slv if slv in (OK, WARN, CRIT) else NA)),
    }


def render(vm_dict, P, layout="favo13", flat=False):
    v = VM(vm_dict)
    c = Canvas(P["bg"])
    if P.get("deco"):
        P["deco"](c, P)
    LV = {OK: P["ice"], WARN: P["amber"], CRIT: P["red"], NA: P["sub"], LOST: P["amber"], NEUTRAL: P["white"]}
    col = lambda lv: LV.get(lv, P["white"])
    CELL = dict(P["cells"]); CELL[LOST] = CELL[WARN]
    f_h = font(ROBOTO, 11, "Bold")
    f_hv = font(JB, 13, "Bold")
    f_hvs = font(JB, 11, "Bold")
    f_xl = font(JB, 20, "Bold")
    f_m = font(JB, 14, "Bold")
    f_sb = font(JB, 12, "Bold")
    f_s = font(JB, 12, "Regular")
    f_xs = font(JB, 11, "Regular")

    # ---------- cabeçalho
    tb = c.text("hdr.title", 6, 17, P["title"], font(ROBOTO, 15, "Bold"), P["accent"])
    sb = c.text("hdr.sub", tb[2] + 6, 17, P["subtitle"], f_xs, P["sub"]) if P.get("subtitle") else tb
    if v.raw("demo"):
        c.text("hdr.demo", sb[2] + 8, 17, "DEMO", f_xs, P["amber"])
    from .base import selo_versao
    selo_versao(c, P, font(JB, 11, "Bold"))
    st, slv = v("hdr_status")
    mode = P.get("alert")
    if mode != "faixa":
        c.line((0, 24, W, 24), P["dim"])
    if mode:                                                     # indicador moderno (escala, barra, banner, faixa)
        from .alerta import draw_status
        draw_status(c, v, P, mode, vm_dict.get("blink"), st, slv, col, cell_values(v, slv, P.get("cool")))
    else:
        c.text("hdr.status", 314, 17, strip_status(st), f_sb, col(slv), anchor="rs")
    vals = cell_values(v, slv, P.get("cool"))
    if not P.get("cool"):
        for k in ("pump", "fan_sqi", "fan_sql", "fan_sqt"):
            v.raw(k)                                             # estilo sem a linha de bomba e ventoinhas

    def cell(key, cx, cy, r, fv):
        lab, (t, lv) = vals[key]
        k = lv if lv in CELL else NEUTRAL
        fill, edge = CELL[k if t != "N/D" else NA]
        c.poly(hexagon(cx, cy, r, flat), fill=fill, outline=edge, width=2 if lv in (OK, WARN, CRIT) else 1)
        dy = r * 0.18
        c.text(f"hex.{key}.lab", cx, cy - dy, lab, f_h, P["sub"] if lv != NEUTRAL else P["white"], anchor="ms")
        c.text(f"hex.{key}.val", cx, cy + dy + 9, short(t), fv, col(lv), anchor="ms")

    # ---------- núcleo
    if layout in ("favo13", "favo19", "losango"):
        if layout == "favo13":
            rows = [["cpu", "cput", "cfan", "gpu"], ["gput", "gfan", "core", "vram", "ram"], ["d0", "d1", "d2", "ping"]]
            r, gap, cy0, fv = 28, 4, 60, f_hv
        elif layout == "losango":
            rows = [["cpu", "gpu"], ["cput", "core", "gput"], ["cfan", "ram", "vram", "gfan"],
                    ["d0", "d1", "d2"], ["ping", "fps"]]
            r, gap, cy0, fv = 22, 3, 50, f_hvs
        else:
            rows = [["cpu", "cput", "gpu"], ["cfan", "load", "gput", "gfan"], ["ram", "vram", "core", "fps", "gpuw"],
                    ["d0", "d1", "d2", "ping"], ["rede", "pwr", "coleta"]]
            if P.get("temps"):      # PLACA, RAM° e SSD° no lugar de LOAD, TOT W e COLETA (já aparecem nas linhas de texto)
                rows[1][1], rows[4][1], rows[4][2] = "tplaca", "tram", "tssd"
            r, gap, cy0, fv = 22, 3, 50, f_hvs
        sx, sy = math.sqrt(3) * r + gap, 1.5 * r + gap
        for ri, row in enumerate(rows):
            x0 = (W - (len(row) - 1) * sx) / 2
            for ci, key in enumerate(row):
                cell(key, x0 + ci * sx, cy0 + ri * sy, r, fv)
        y = cy0 + (len(rows) - 1) * sy + r + 6
    else:                                                       # anel
        cx, cy, R = 160, 120, 72
        c.d.ellipse((cx - R - 6, cy - R - 6, cx + R + 6, cy + R + 6), outline=P["dim"], width=10)
        c.d.ellipse((cx - R + 26, cy - R + 26, cx + R - 26, cy + R - 26), outline=P["dim"], width=1)
        ring = ["cpu", "cput", "cfan", "gpu", "gput", "gfan", "vram", "ram", "d0", "d1", "d2", "ping"]
        for i, key in enumerate(ring):
            a = math.radians(-90 + i * 30)
            cell(key, cx + R * math.cos(a), cy + R * math.sin(a), 19, f_hvs)
        lab, (t, lv) = vals["core"]
        fill, edge = CELL[lv]
        c.poly(hexagon(cx, cy, 38, flat), fill=fill, outline=edge, width=3)
        c.text("core.lab", cx, cy - 8, P.get("core_label", "NÚCLEO"), f_h, P["sub"], anchor="ms")
        c.text("core.val", cx, cy + 14, t, font(JB, 18, "Bold"), col(lv), anchor="ms")
        y = cy + R + 19 + 6
    c.line((0, y, W, y), P["dim"])

    # ---------- registro detalhado
    compact = layout != "favo13"
    step = 13 if compact else 14
    cut = 2 if P.get("cool") else 0          # cool: uma linha a mais; folgas entre blocos ficam menores

    def pair(name, x, yy, lab, val, fv, lv, right=False):
        wl = c.width(lab, f_xs) + 4
        wv = c.width(val, fv)
        if right:
            x = x - wl - wv
        c.text(name + ".lab", x, yy, lab, f_xs, P["sub"])
        c.text(name + ".val", x + wl, yy, val, fv, col(lv))
        return x, x + wl + wv

    y += step + 1
    v.raw("cpu_pct"); v.raw("gpu_pct"); v.raw("vram_pct")   # percentuais já exibidos nas células
    t, lv = v("cpu_ghz"); pair("cpu.ghz", 6, y, "CPU", t, f_sb, lv)
    t, lv = v("cpu_load"); pair("cpu.load", 314, y, "LOAD", t, f_s, lv, right=True)
    y += step
    t, lv = v("gpu_mhz"); pair("gpu.mhz", 6, y, "GPU", t, f_sb, lv)
    t, lv = v("fps"); pair("gpu.fps", 314, y, "FPS", t, f_sb, lv, right=True)
    y += step
    paren = lambda s: f"({s})" if (P.get("pct") == "paren" and str(s).endswith("%")) else s
    t, lv = v("vram_txt"); _, xe = pair("gpu.vram", 6, y, "VRAM", t, f_sb, lv)
    if P.get("pct"):
        pt, pl = vals["vram"][1]
        c.text("gpu.vrampct", xe + 6, y, paren(pt), f_sb, col(pl))
    v.raw("gpu_fan_rpm")                                         # RPM da GPU não existe no driver NVIDIA (só o comando em %)
    t, lvf = v("gpu_fan_pct"); pair("gpu.fan", 314, y, "FAN", t, f_sb, lvf, right=True)
    y += step
    t, lv = v("gpu_w"); _, xe = pair("gpu.w", 6, y, "GPU W", t, f_sb, lv)
    t, _ = v("gpu_wlim")
    if P.get("flow"):                                            # informação trazida para a esquerda
        c.text("gpu.wlim", xe + 8, y, t, f_xs, P["sub"])
    else:
        c.text("gpu.wlim", 314, y, t, f_xs, P["sub"], anchor="rs")
    if P.get("cool"):                                            # bomba e ventoinhas (RPM), uma linha
        y += step
        x = 6
        for nome, lab, chave in (("pump", "BOMBA", "pump"), ("rad", "RAD", "cpu_fan"), ("sqi", "INF", "fan_sqi"),
                                 ("sql", "LAT", "fan_sql"), ("sqt", "TRA", "fan_sqt")):
            t, lv = v(chave); t = t.replace("RPM", "")
            _, x = pair("fan." + nome, x, y, lab, t, f_s, lv)
            x += 8
    y += step
    t, lv = v("ram_used"); _, xe = pair("ram.used", 6, y, "RAM", t, f_sb, lv)
    t2, _ = v("ram_total"); rb = c.text("ram.total", xe + 1, y, t2, f_sb, P["white"])
    pb = rb
    if P.get("pct"):
        pt, pl = vals["ram"][1]
        pb = c.text("ram.pct", rb[2] + 6, y, paren(pt), f_sb, col(pl))
    t, lv = v("ram_avail")
    if P.get("flow"):
        pair("ram.avail", pb[2] + 12, y, "DISP", t, f_sb, lv)
    else:
        pair("ram.avail", 314, y, "DISP", t, f_sb, lv, right=True)
    for i, d in enumerate(v.raw("disks", [])[:3]):
        y += step + (1 if (P.get("flow") and i == 0) else 0)       # 1 px extra: parênteses do RAM x texto longo do disco
        c.text(f"dsk{i}.name", 6, y, d["name"], f_sb, P["white"])
        ub = c.text(f"dsk{i}.use", 44, y, d["use"], f_s, col(d.get("use_lvl", NEUTRAL)))
        if P.get("flow"):                                        # percentual e espaço livre logo após o uso
            x = ub[2] + 6
            if P.get("pct"):
                pbx = c.text(f"dsk{i}.pct", x, y, paren(d["pct_txt"]), f_sb, col(d["lvl"]))
                x = pbx[2] + 10
            fb = c.text(f"dsk{i}.free", x, y, d["free"], f_sb, col(d["lvl"]))
            c.text(f"dsk{i}.freelab", fb[2] + 4, y, "LIVRE", f_xs, P["sub"])
        else:
            b = c.text(f"dsk{i}.freelab", 314, y, "LIVRE", f_xs, P["sub"], anchor="rs")
            fb = c.text(f"dsk{i}.free", b[0] - 4, y, d["free"], f_sb, col(d["lvl"]), anchor="rs")
            if P.get("pct"):
                c.text(f"dsk{i}.pct", fb[0] - 8, y, paren(d["pct_txt"]), f_sb, col(d["lvl"]), anchor="rs")
    y += (6 if not compact else 5) - cut
    c.line((0, y, W, y), P["dim"])
    y += step + 1 - cut
    t, lv = v("net_down"); c.text("net.down", 6, y, "↓" + t, f_m, P["white"])
    t, lv = v("net_up"); c.text("net.up", 160, y, "↑" + t, f_m, P["white"])
    y += step
    t, lv = v("net_rx"); pair("net.rx", 6, y, "RX", t, f_s, lv)
    t, lv = v("net_tx"); pair("net.tx", 160, y, "TX", t, f_s, lv)
    c.text("net.period", 314, y, "BOOT", f_xs, P["dim"] if P["dim"] != P["bg"] else P["sub"], anchor="rs")
    for key, tag in (("eth", "ETH"), ("wifi", "WIFI")):
        y += step
        iface_row(c, v, key, y, 6, tag, 44, 314, f_xs, f_sb, f_xs, f_xs, col, P["sub"],
                  c_info=P["white"], c_rates=P["white"])
    y += (6 if not compact else 5) - cut
    c.line((0, y, W, y), P["dim"])
    y += (24 if not compact else 22) - cut
    t, _ = v("clock"); c.text("sys.clock", 6, y, t, f_xl, P["accent"])
    t, _ = v("date"); c.text("sys.date", 314, y - 9, t, f_sb, P["white"], anchor="rs")
    t, lv = v("uptime"); pair("sys.up", 314, y + 4, "UP", t, f_s, lv, right=True)
    t, _ = v("os"); c.text("sys.os", 6, y + 13, t, f_xs, P["sub"])
    y += (29 if not compact else 27) - cut
    t, lv = v("ping"); b = c.text("png.val", 6, y, "PING " + t, f_sb, col(lv))
    t, lv = v("inet"); c.text("inet", b[2] + 6, y, t, f_xs, col(lv))
    t, lv = v("wtemp"); b = c.text("wx.temp", 314, y, t, f_sb, col(lv), anchor="rs")
    c.text("wx.city", b[0] - 5, y, v.raw("city", ""), f_xs, P["sub"], anchor="rs")
    y += 13
    t, lv = v("wdesc"); c.text("wx.desc", 6, y, t, f_xs, col(lv) if lv != NA else P["sub"])
    t, lv = v("wage"); c.text("wx.age", 314, y, t, f_xs, col(lv) if lv != NA else P["sub"], anchor="rs")
    baias = v.raw("baias", []) if P.get("baias") else []
    if baias:                                    # gabinete de baias presente: 2x2 baias no lugar do rodapé
        for k in ("power", "power_tag", "coleta"):
            v.raw(k)
        for i, b in enumerate(baias[:4]):
            x, yy = (6, 466) if i % 2 == 0 else (164, 466)
            yy += 12 * (i // 2)
            bx = c.text(f"bay{i}.n", x, yy, f"{b['n']}", f_sb, P["accent"])
            if b["cap"]:
                bx = c.text(f"bay{i}.cap", bx[2] + 5, yy, b["cap"], f_sb, col(b["lvl"]))
            c.text(f"bay{i}.st", bx[2] + 5, yy, b["palavra"], f_xs, col(b["lvl"]))
    else:
        y = 474
        t, lv = v("power"); _, xe = pair("pwr", 6, y, "TOTAL W", t, f_sb, lv)
        t, _ = v("power_tag"); tb = c.text("pwr.tag", xe + 6, y, t, f_xs, P["sub"])
        t, lv = v("coleta"); c.text("coleta", 314, y, c.fit(t, f_xs, 314 - tb[2] - 8), f_xs, col(lv), anchor="rs")
    if P.get("bloom"):
        c.img = bloom(c.img, *P["bloom"])
    return c, v


def draw_frame(vm_dict):
    return render(vm_dict, CHERENKOV, "favo13")
