#!/usr/bin/env python3
# MATRIX GREEN PRO | versão 3.8.0 | 07/11/2026 19:40 (-03) | estilos gamma-delta e gamma-gamma-coluna
# histórico: 3.3.0 02/11/2026 18:10 prévias com fase de piscar (aceso e apagado) nos estilos de alerta
# histórico: 3.2.0 02/11/2026 17:45 estilos gamma (4) e pcb
# histórico: 3.1.0 01/11/2026 11:00 estilos uranio e pcb
# histórico: 2.1.0 01/11/2026 00:00 nomes MatrixGreenPro-Normal/Atencao/Critico, testes de coleta
# histórico: 2.0.0 31/10/2026 23:30 prévias normal/atencao/critico + montagem
# histórico: 1.0.0 31/10/2026 22:55 criação inicial
# Gera prévias PNG 320x480 (retrato) com o MESMO código que desenha na tela,
# e valida limites e sobreposições dos elementos.
# Uso: .venv/bin/python3 tools/mgp_preview.py [pasta_saida]
import itertools
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from library.sensors.matrixgreenpro import panel, render  # noqa: E402
from library.sensors.matrixgreenpro.viewmodel import ViewModel  # noqa: E402
from library.sensors.matrixgreenpro.settings import DEFAULTS  # noqa: E402


def ts():
    return time.strftime("[%d/%m/%Y %H:%M:%S]")


def worst_case():
    s = panel.demo_snapshot("critico")
    s["cpu"].update(util=100, ghz=5.75, temp=105, fan=9999, load=(128.4, 99.99, 100.0))
    s["gpu"].update(util=100, temp=105, mhz=3105, vram_used=23.9, vram_total=24.0, fan_rpm=9999,
                    fan_pct=100, power=600, power_limit=600)
    s["fps"] = 9999
    s["ram"] = {"used": 127.9, "avail": 0.1, "total": 128.0, "pct": 99.9}
    s["disks"][0] = {"nome": "M.2", "state": "OK", "total": 4000e9, "used": 3999e9, "free": 1e9, "pct": 100}
    s["disks"][2] = {"nome": "4T", "state": "OK", "total": 4000e9, "used": 3990e9, "free": 10e9, "pct": 99.8}
    s["net"].update(down=999.9e6, up=999.9e6, rx=99.99e12, tx=99.99e12)
    s["net"]["eth"] = {"exists": True, "name": "enp10s0f1", "up": True, "speed": 2500, "ip": "192.168.100.200",
                       "rate_down": 999.9e6, "rate_up": 999.9e6}
    s["net"]["wifi"] = {"exists": True, "name": "wlp10s0f3", "up": True, "signal": -100, "ip": "192.168.100.201",
                        "rate_down": 999.9e6, "rate_up": 999.9e6}
    s["net"]["default"] = "enp10s0f1"
    s["uptime"] = 99 * 86400 + 23 * 3600 + 59 * 60
    s["ping"] = {"ok": True, "ms": 999.0}
    s["weather"] = {"state": "STALE", "temp": -10.0, "desc": "TEMPORAL GRANIZO", "ts": time.time() - 7200}
    s["power"] = {"state": "OK", "w": 1600, "tag": "TOMADA"}
    s["ping"] = {"ok": False, "ms": None}
    s["coleta"] = {"esperados": 9, "falhas": ["CPU°C", "FAN", "GPU", "DISCOS", "PING", "CLIMA"]}
    return s


def all_nd():
    s = panel.demo_snapshot()
    s["cpu"] = {"util": 3, "ghz": None, "temp": None, "fan": None, "load": (0.1, 0.2, 0.3)}
    s["gpu"] = {"present": False}
    s["fps"] = None
    s["disks"] = [{"nome": "M.2", "state": "CFG"}, {"nome": "2T", "state": "OFF"}, {"nome": "4T", "state": "ND"}]
    s["net"]["eth"] = {"exists": False}
    s["net"]["wifi"] = {"exists": False}
    s["ping"] = {"ok": None, "ms": None}
    s["weather"] = {"state": "ND"}
    s["power"] = {"state": "ND"}
    s["coleta"] = {"esperados": 4, "falhas": ["CPU", "REDE", "PING", "CLIMA"]}
    return s


def check(elements, name):
    errs = []
    for n, (x0, y0, x1, y1) in elements:
        if x0 < 0 or y0 < 0 or x1 > render.W or y1 > render.H:
            errs.append(f"{n} fora da tela {x0,y0,x1,y1}")
    texts = [(n, b) for n, b in elements if not n.endswith(("bar", "band")) and not n.startswith("sep")]
    for (na, a), (nb, b) in itertools.combinations(texts, 2):
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            errs.append(f"sobreposição: {na} x {nb}")
    for e in errs:
        print(f"{ts()} [{name}] ERRO {e}")
    print(f"{ts()} [{name}] {len(elements)} elementos, {len(errs)} problema(s)")
    return errs


def montage(out):
    """Montagem comparativa AMPLIADA (não é a resolução nativa): 6 estilos x 3 estados."""
    from PIL import Image, ImageDraw
    rows = [("MatrixGreenPro", "MATRIX GREEN PRO"), ("MatrixGreenPro-Gamma", "GAMMA"),
            ("MatrixGreenPro-GammaSonar", "GAMMA SONAR"), ("MatrixGreenPro-GammaRaioX", "GAMMA RAIO-X"),
            ("MatrixGreenPro-GammaUV", "GAMMA ULTRAVIOLETA"), ("MatrixGreenPro-PCB", "13-C PLACA DE CIRCUITO")]
    cols = [("Normal", "NORMAL"), ("Atencao", "ATENÇÃO"), ("Critico", "CRÍTICO")]
    gap, top = 16, 30
    m = Image.new("RGB", (3 * (320 + gap) + gap, len(rows) * (480 + top + gap) + gap), (24, 28, 24))
    d = ImageDraw.Draw(m)
    f = render.font(15, "Bold")
    for r, (pre, lab) in enumerate(rows):
        for k, (tag, tl) in enumerate(cols):
            x, y = gap + k * (320 + gap), gap + r * (480 + top + gap)
            m.paste(Image.open(out / f"{pre}-{tag}.png"), (x, y + top - 4))
            d.text((x, y + 2), f"{lab} · {tl}", font=f, fill=(210, 214, 210))
    m.save(out / "MatrixGreenPro-Comparativo-Estilos.png")


def estilos(out):
    """Estilos gamma (4) e 13-C (pcb): limites, sobreposição, glifos e cobertura das métricas."""
    import copy
    from library.sensors.matrixgreenpro.estilos import ESTILOS
    from library.sensors.matrixgreenpro.estilos.base import REQUIRED
    import importlib
    errs = 0
    cen = (("Normal", panel.demo_snapshot("normal")), ("Atencao", panel.demo_snapshot("atencao")),
           ("Critico", panel.demo_snapshot("critico")), ("CriticoApagado", panel.demo_snapshot("critico")),
           ("teste-pior-caso", worst_case()), ("teste-coleta-falhou", all_nd()))
    for key, (label, mod) in ESTILOS.items():
        if mod is None:
            continue
        draw = importlib.import_module(f"library.sensors.matrixgreenpro.estilos.{mod}").draw_frame
        for tag, snap in cen:
            vm = ViewModel(copy.deepcopy(DEFAULTS), (80, 90), (80, 87)).build(copy.deepcopy(snap))
            vm["blink"] = tag != "CriticoApagado"        # fase do piscar (estilos de alerta)
            c, v = draw(vm)
            assert c.img.size == (320, 480)
            camel = {"pcb": "PCB", "gamma": "Gamma", "gamma-sonar": "GammaSonar", "gamma-raiox": "GammaRaioX",
                     "gamma-uv": "GammaUV", "gamma-escala": "GammaEscala", "gamma-barra": "GammaBarra",
                     "gamma-banner": "GammaBanner", "gamma-faixa": "GammaFaixa", "gamma-n3": "GammaN3", "gamma-alpha": "GammaAlpha",
                     "gamma-n3-abas": "GammaN3Abas", "gamma-n3-linha": "GammaN3Linha",
                     "gamma-n3-eventos": "GammaN3Eventos", "gamma-beta": "GammaBeta", "gamma-gamma-colmeia": "GammaGammaColmeia",
                     "gamma-gamma-mini": "GammaGammaMini", "gamma-gamma-painel": "GammaGammaPainel", "gamma-gamma-coluna": "GammaGammaColuna", "gamma-delta": "GammaDelta", "gamma-gamma": "GammaGamma"}[key]
            nome = f"MatrixGreenPro-{camel}-{tag}" if not tag.startswith("teste") else f"{key}-{tag}"
            c.img.save(out / f"{nome}.png")
            e = check(c.texts, nome)
            for n, m, fn in c.glyph_issues:
                print(f"{ts()} [{nome}] ERRO glifo ausente em {n}: {m!r} ({fn})"); e.append(n)
            miss = REQUIRED - v.used
            if miss:
                print(f"{ts()} [{nome}] ERRO métricas omitidas: {sorted(miss)}"); e.append("cobertura")
            errs += len(e)
    return errs


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    total_err = 0
    for name, snap in (("MatrixGreenPro-Normal", panel.demo_snapshot("normal")),
                       ("MatrixGreenPro-Atencao", panel.demo_snapshot("atencao")),
                       ("MatrixGreenPro-Critico", panel.demo_snapshot("critico")),
                       ("teste-pior-caso", worst_case()),
                       ("teste-coleta-falhou", all_nd())):
        vm_b = ViewModel(DEFAULTS, (80, 90), (80, 87))
        img, el = render.draw_frame(vm_b.build(snap))
        assert img.size == (320, 480), "a prévia precisa ser 320x480 retrato"
        img.save(out / f"{name}.png")
        total_err += len(check(el, name))
        if name == "MatrixGreenPro-Normal":
            render.background(el).save(out / "background.png")
            with open(out / "layout_coordenadas.tsv", "w", encoding="utf-8") as f:
                f.write("elemento\tx0\ty0\tx1\ty1\n")
                for n, b in el:
                    f.write(n + "\t" + "\t".join(map(str, b)) + "\n")
    total_err += estilos(out)
    montage(out)
    print(f"{ts()} total de problemas: {total_err}")
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
