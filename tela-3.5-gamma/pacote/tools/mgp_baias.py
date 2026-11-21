#!/usr/bin/env python3
# MATRIX GREEN PRO | mgp_baias.py | versão 1.0.0 | 07/11/2026 14:20 (-03) | criação original (Claude, para Lucas Tavares)
"""Mostra as baias do gabinete USB (TerraMaster) como o tema as enxerga. Só lê; não altera nada.
Use para conferir se a baia 1, 2, 3 e 4 do tema são as mesmas do gabinete. Se estiver trocado, ajuste no
config.yaml: terramaster: {inverter: true} ou {mapa: {"1": 4, "2": 3, "3": 2, "4": 1}} (porta do hub -> baia)."""
import sys
import time
from pathlib import Path

for base in (Path(__file__).resolve().parent.parent, Path.cwd()):
    if (base / "library" / "sensors").is_dir():
        sys.path.insert(0, str(base))
        break
from library.sensors.matrixgreenpro import collectors as col, settings  # noqa: E402
from library.sensors.matrixgreenpro.viewmodel import cap_txt  # noqa: E402


def log(msg):
    print(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] {msg}")


def main():
    cfg = settings.load()
    b = col.Baias(cfg).leitura() if str(cfg.get("terramaster", {}).get("ativo", "auto")).lower() not in ("nao", "não") else None
    if b is None:
        log("gabinete não encontrado (hub 0bda:0423 com pontes 174c:235c). Ligado, com o cabo USB 3 conectado?")
        return 1
    log(f"gabinete encontrado: {len(b)} baias")
    for x in b:
        if x["estado"] == "LIVRE":
            log(f"baia {x['n']}: LIVRE (nenhum disco)")
        else:
            nome = {"MONT": "MONTADO", "DESM": "DESMONTADO"}[x["estado"]]
            log(f"baia {x['n']}: {nome:<10} {cap_txt(x['bytes']):>6}  {x['modelo']}  (/dev/{x['dev']})")
    log("conferir: a baia 1 do tema é a baia 1 do gabinete? Se não, use terramaster.inverter ou terramaster.mapa no config.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
