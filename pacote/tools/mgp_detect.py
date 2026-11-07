#!/usr/bin/env python3
# MATRIX GREEN PRO | versão 3.1.0 | 01/11/2026 10:55 (-03) | linha painel.estilo no modelo
# histórico: 2.1.0 31/10/2026 23:45 Ethernet não obrigatória por padrão
# histórico: 2.0.0 31/10/2026 23:40 criação: detecção de discos (UUID) e rede
# Gera ~/.config/matrixgreenpro/config.yaml com os volumes identificados de
# forma PERSISTENTE (UUID do sistema de arquivos), nunca por /dev/sdX.
# Uso: .venv/bin/python3 tools/mgp_detect.py [--forcar] [--mostrar]
import json
import os
import subprocess
import sys
import time
from pathlib import Path

CFG = Path(os.environ.get("MGP_CONFIG", str(Path.home() / ".config" / "matrixgreenpro" / "config.yaml")))


def ts():
    return time.strftime("[%d/%m/%Y %H:%M:%S]")


def log(m):
    print(f"{ts()} {m}", flush=True)


def lsblk():
    out = subprocess.run(["lsblk", "-J", "-b", "-o",
                          "NAME,PATH,UUID,LABEL,SIZE,MOUNTPOINTS,TRAN,TYPE,FSTYPE,MODEL,ROTA"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["blockdevices"]


def best_fs(disk):
    """Maior sistema de arquivos com UUID dentro do disco (partições, LUKS e LVM inclusos)."""
    cands = []

    def walk(n):
        if n.get("uuid") and n.get("fstype") not in (None, "swap", "crypto_LUKS", "LVM2_member", "vfat"):
            mps = [m for m in (n.get("mountpoints") or []) if m]
            cands.append((int(n.get("size") or 0), n["uuid"], mps[0] if mps else "", n.get("label") or ""))
        for ch in n.get("children") or []:
            walk(ch)
    walk(disk)
    root = [c for c in cands if c[2] == "/"]
    if root:
        return root[0]
    return max(cands) if cands else None


def detect_disks():
    disks = [d for d in lsblk() if d.get("type") == "disk"]
    found = {"M.2": None, "2T": None, "4T": None}
    for d in disks:
        size = int(d.get("size") or 0)
        fs = best_fs(d)
        if not fs:
            continue
        name = d.get("name", "")
        info = {"dev": d.get("path"), "modelo": (d.get("model") or "").strip(), "tam": size,
                "uuid": fs[1], "montagem": fs[2], "rotulo": fs[3]}
        if name.startswith("nvme") and (found["M.2"] is None or fs[2] == "/"):
            found["M.2"] = info
        elif 1.7e12 <= size <= 2.3e12 and found["2T"] is None:
            found["2T"] = info
        elif 3.5e12 <= size <= 4.5e12 and found["4T"] is None:
            found["4T"] = info
    return found


def detect_net():
    eth = wifi = None
    for i in sorted(os.listdir("/sys/class/net")):
        if i == "lo" or not os.path.exists(f"/sys/class/net/{i}/device"):
            continue
        if os.path.isdir(f"/sys/class/net/{i}/wireless") or os.path.isdir(f"/sys/class/net/{i}/phy80211"):
            wifi = wifi or i
        else:
            eth = eth or i
    return eth, wifi


def render_yaml(disks, eth, wifi):
    def dk(nome, d):
        if not d:
            mnt = "/" if nome == "M.2" else ""
            return (f'  - nome: "{nome}"\n    uuid: ""        # ⚠️ NÃO DETECTADO: preencha com o UUID (lsblk -f)\n'
                    f'    montagem: "{mnt}"\n')
        return (f'  - nome: "{nome}"\n    uuid: "{d["uuid"]}"   # {d["dev"]} {d["modelo"]} '
                f'{d["tam"] / 1e12:.2f} TB {d["rotulo"]}\n    montagem: "{d["montagem"]}"\n')
    return f"""# MATRIX GREEN PRO | versão 3.1.0 | gerado em {time.strftime('%d/%m/%Y %H:%M:%S')} por mgp_detect.py
# Configuração do painel. Edite à vontade: o instalador nunca sobrescreve
# este arquivo (use --forcar no mgp_detect.py para regenerar).
painel:
  demo: false              # true = dados demonstrativos (cabeçalho mostra DEMO)
  demo_cenario: normal     # normal | atencao | critico
  estilo: matrix           # matrix | gamma | gamma-escala | gamma-barra | gamma-banner | gamma-faixa | gamma-sonar | gamma-raiox | gamma-uv | pcb
  refresh_full_s: 300

cpu:
  temp_sensor: auto        # ex.: k10temp/Tctl  (veja scripts/diagnosticar.sh)
  fan: auto                # ex.: nct6798/fan2; auto usa CPU_FAN do config.yaml do programa
  temp_warn: auto          # auto = conforme o modelo detectado (Ryzen 7000/9000: 88/94 °C)
  temp_crit: auto
  fan_stop_ok_below_c: 60  # 0 RPM abaixo desta temperatura = modo semipassivo (normal)

gpu:
  index: 0
  temp_warn: auto          # auto = limite de desaceleração NVML - 10 °C
  temp_crit: auto          # auto = limite de desaceleração NVML - 3 °C
  vram_warn: 90
  vram_crit: 97

fps:
  mangohud_dir: /tmp/mgp-mangohud
  max_age_s: 3.5

ram: {{warn: 85, crit: 95}}

# Três volumes, identificados por UUID (persistente). Desmontado = OFF.
discos:
{dk("M.2", disks["M.2"])}{dk("2T", disks["2T"])}{dk("4T", disks["4T"])}disco_warn: 85
disco_crit: 95
disco_livre_warn_gb: 50
disco_livre_crit_gb: 10

rede:
  ethernet: "{eth or ''}"
  wifi: "{wifi or 'nenhuma'}"
  ethernet_obrigatoria: false   # true = Ethernet caída gera aviso mesmo com Wi-Fi ativo

ping: {{host: 8.8.8.8, intervalo_s: 5, warn_ms: 80, crit_ms: 200}}

clima:
  cidade: "RIO DO SUL"
  latitude: -27.2139
  longitude: -49.6428
  intervalo_min: 15
  desatualizado_min: 45

energia:
  fonte: auto              # auto | none | hwmon | arquivo | tasmota | shelly_gen2
  arquivo: ""              # arquivo com watts (uma linha), atualizado por outro programa
  tipo_arquivo: tomada     # tomada | psu | estimativa
  host: ""                 # IP da tomada inteligente (tasmota/shelly_gen2)
  psu_watts: 0             # capacidade da fonte para alertas (0 = sem alerta)

histerese: {{temperatura: 3, percentual: 2, ping_ms: 15}}
"""


def main():
    force = "--forcar" in sys.argv
    show = "--mostrar" in sys.argv
    disks = detect_disks()
    eth, wifi = detect_net()
    for k, d in disks.items():
        if d:
            log(f"disco {k}: {d['dev']} {d['modelo']} {d['tam'] / 1e12:.2f} TB uuid={d['uuid']} "
                f"montagem={d['montagem'] or 'DESMONTADO'}")
        else:
            log(f"disco {k}: NÃO DETECTADO (preencha o UUID manualmente)")
    log(f"rede: ethernet={eth or 'nenhuma'} wifi={wifi or 'nenhuma'}")
    text = render_yaml(disks, eth, wifi)
    if show:
        print(text)
        return
    if CFG.exists() and not force:
        log(f"configuração existente preservada: {CFG}")
        return
    CFG.parent.mkdir(parents=True, exist_ok=True)
    if CFG.exists():
        bak = CFG.with_suffix(f".yaml.bak-{time.strftime('%Y%m%d-%H%M%S')}")
        CFG.rename(bak)
        log(f"backup da configuração anterior: {bak}")
    CFG.write_text(text, encoding="utf-8")
    log(f"configuração gerada: {CFG}")


if __name__ == "__main__":
    main()
