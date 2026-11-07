#!/usr/bin/env python3
# MATRIX GREEN PRO | mapeador de ventoinhas | versão 1.0.0 | 02/11/2026 21:40 (-03) | criação original (Claude, para Lucas Tavares)
# Descobre qual entrada do chip (fan1, fan2...) é cada ventoinha e grava ~/.config/matrixgreenpro/fans.yaml.
# Método: você desconecta UM cabo de cada vez, por poucos segundos, e a ferramenta vê qual entrada caiu para 0.
# A bomba NÃO é desconectada: é a entrada que sobra girando (e fica assim sem risco para o water cooler).
# Uso: .venv/bin/python3 tools/mgp_mapear_fans.py            (depois: systemctl --user restart turing-smart-screen)
#      .venv/bin/python3 tools/mgp_mapear_fans.py --ver      só mostra as leituras atuais
import glob
import os
import sys
import time
from pathlib import Path

CONF = Path(os.environ.get("MGP_CONFIG", str(Path.home() / ".config" / "matrixgreenpro" / "config.yaml"))).parent
PAPEIS = [("radiador", "as 3 ventoinhas do radiador (Eskimo)"), ("sq_inf", "as 3 ventoinhas de baixo (Squama inferior)"),
          ("sq_lat", "a ventoinha lateral (Squama)"), ("sq_tras", "a ventoinha traseira (Squama)")]


def ts():
    return time.strftime("[%d/%m/%Y %H:%M:%S]")


def log(m):
    print(f"{ts()} {m}", flush=True)


def ler():
    out = {}
    for d in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
        try:
            nome = Path(d, "name").read_text().strip()
        except Exception:
            continue
        if not nome.startswith(("nct", "it8", "it87", "f71", "w83")):
            continue
        for f in sorted(glob.glob(d + "/fan*_input")):
            try:
                out[f"{nome}/{os.path.basename(f)[:-6]}"] = int(Path(f).read_text().strip())
            except Exception:
                pass
    return out


def media(n=4):
    acc = {}
    for _ in range(n):
        for k, v in ler().items():
            acc.setdefault(k, []).append(v)
        time.sleep(1)
    return {k: sum(v) / len(v) for k, v in acc.items()}


def main():
    base = media(3)
    if not base:
        log("ERRO: nenhum chip de ventoinhas encontrado. Rode antes: sudo modprobe nct6775")
        return 1
    log("leituras atuais (RPM): " + ", ".join(f"{k.split('/')[1]}={int(v)}" for k, v in base.items()))
    if "--ver" in sys.argv:
        return 0
    giram = {k for k, v in base.items() if v > 100}
    mapa = {}
    for papel, desc in PAPEIS:
        print()
        log(f"⚠️ AÇÃO MANUAL: desconecte do conector da placa o cabo de {desc}. Depois de desconectar, pressione Enter.")
        input()
        atual = media(3)
        caiu = [k for k in giram if k not in mapa.values() and atual.get(k, 0) < 0.2 * base[k]]
        log(f"⚠️ AÇÃO MANUAL: reconecte o cabo agora e pressione Enter.")
        input()
        if len(caiu) == 1:
            mapa[papel] = caiu[0]
            log(f"{papel} = {caiu[0]}")
        else:
            log(f"AVISO: não consegui identificar {papel} (entradas que caíram: {caiu or 'nenhuma'}). Pulando; ele ficará sem leitura.")
        time.sleep(4)
    restantes = [k for k in giram if k not in mapa.values()]
    if len(restantes) == 1:
        mapa["bomba"] = restantes[0]
        log(f"bomba = {restantes[0]} (a única entrada que sobrou girando)")
    elif restantes:
        mapa["bomba"] = max(restantes, key=lambda k: base[k])
        log(f"AVISO: sobraram {len(restantes)} entradas girando; assumi a mais rápida como bomba: {mapa['bomba']}")
    else:
        log("AVISO: nenhuma entrada sobrou para a bomba; ela ficará sem leitura (N/D)")
    CONF.mkdir(parents=True, exist_ok=True)
    destino = CONF / "fans.yaml"
    with open(destino, "w", encoding="utf-8") as f:
        f.write(f"# mapa de ventoinhas gerado por mgp_mapear_fans.py em {time.strftime('%d/%m/%Y %H:%M')} (-03)\nfans:\n")
        for papel in ("bomba", "radiador", "sq_inf", "sq_lat", "sq_tras"):
            if papel in mapa:
                f.write(f"  {papel}: {mapa[papel]}\n")
    log(f"mapa gravado em {destino}")
    log("⚠️ AÇÃO MANUAL: aplique com: systemctl --user restart turing-smart-screen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
