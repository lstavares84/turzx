# MATRIX GREEN PRO | versão 3.7.0 | 07/11/2026 20:15 (-03) | ping verde até 20 ms, âmbar até 100 ms, vermelho acima
# histórico: 3.6.0 07/11/2026 14:10 terramaster (baias do DAS USB)
# histórico: 3.3.0 02/11/2026 21:30 cpu.fans (mapa de bomba e ventoinhas) e fans.yaml
# histórico: 3.2.0 02/11/2026 17:40 estilos gamma*
# histórico: 3.1.0 01/11/2026 10:50 opção painel.estilo
# histórico: 2.1.0 31/10/2026 23:40 Ethernet não obrigatória por padrão
# histórico: 2.0.0 31/10/2026 23:10 limites de espaço livre | 1.0.0 31/10/2026 22:40 criação inicial
# Leitura da configuração do painel (~/.config/matrixgreenpro/config.yaml),
# com valores padrão embutidos. Nenhum valor ausente derruba o painel.
import copy
import os
from pathlib import Path

try:
    import yaml
except Exception:  # PyYAML já é dependência do programa; isto é só proteção
    yaml = None

CONFIG_PATH = Path(os.environ.get(
    "MGP_CONFIG", str(Path.home() / ".config" / "matrixgreenpro" / "config.yaml")))
CACHE_DIR = Path(os.environ.get(
    "MGP_CACHE", str(Path.home() / ".cache" / "matrixgreenpro")))

DEFAULTS = {
    "painel": {
        "demo": False,            # True = dados demonstrativos (cabeçalho mostra DEMO)
        "refresh_full_s": 300,    # redesenho completo periódico (corrige ruído de USB)
        "estilo": "matrix",       # matrix | gamma | gamma-escala | gamma-barra | gamma-banner | gamma-faixa | gamma-sonar | gamma-raiox | gamma-uv | pcb
    },
    "cpu": {
        "temp_sensor": "auto",    # ex.: "k10temp/Tctl"
        "fan": "auto",            # ex.: "nct6798/fan2"; "auto" usa CPU_FAN do config.yaml do programa
        "temp_warn": "auto",
        "temp_crit": "auto",
        # mapa papel -> entrada do chip (use tools/mgp_mapear_fans.py para descobrir; grava fans.yaml)
        "fans": {"bomba": "fan1", "radiador": "fan2", "sq_inf": "fan3", "sq_lat": "fan4", "sq_tras": "fan5"},
        # temperaturas extras: papel -> "chip/rótulo" do hwmon ("*" = maior valor do chip)
        "temps": {"placa": "nct6799/SYSTIN", "ram": "spd5118/*", "ssd": "nvme/Composite"},
        "temps_limites": {"ram": [50, 55], "ssd": [70, 80]},      # aviso, crítico (°C); placa é só informativa
        "fan_stop_ok_below_c": 60,  # ventoinha a 0 RPM abaixo disto = modo semipassivo, não é falha
    },
    "gpu": {
        "index": 0,
        "temp_warn": "auto",      # auto = limite de desaceleração da NVML - 10 °C
        "temp_crit": "auto",      # auto = limite de desaceleração da NVML - 3 °C
        "vram_warn": 90,
        "vram_crit": 97,
        "intervalo_s": 1.5,
    },
    "fps": {
        "mangohud_dir": "/tmp/mgp-mangohud",
        "max_age_s": 3.5,
    },
    "ram": {"warn": 85, "crit": 95},
    "discos": [
        {"nome": "M.2", "uuid": "", "montagem": "/"},
        {"nome": "2T", "uuid": "", "montagem": ""},
        {"nome": "4T", "uuid": "", "montagem": ""},
    ],
    "disco_warn": 85,
    "disco_crit": 95,
    "disco_livre_warn_gb": 50,    # além do percentual: pouco espaço absoluto também alerta
    "disco_livre_crit_gb": 10,
    "disco_intervalo_s": 10,
    # gabinete DAS USB com baias (TerraMaster D4): reconhecido sozinho; ativo: "auto" ou "nao"
    # mapa: porta do hub -> número da baia (use tools/mgp_baias.py para conferir); inverter: True = baia 1 é a última porta
    "terramaster": {"ativo": "auto", "hub": "0bda:0423", "ponte": "174c:235c", "baias": 4, "inverter": False, "mapa": {}},
    "disco_temp_limites": {"hdd": [50, 55], "ssd": [70, 80]},   # aviso, crítico (°C); HDD via módulo drivetemp, NVMe direto
    # ethernet_obrigatoria: True = Ethernet desconectada gera aviso mesmo com o Wi-Fi ativo.
    # Sem nenhum enlace (nem Ethernet nem Wi-Fi) é sempre crítico.
    "rede": {"ethernet": "auto", "wifi": "auto", "ethernet_obrigatoria": False},
    "ping": {"host": "8.8.8.8", "intervalo_s": 5, "warn_ms": 20, "crit_ms": 100},
    "clima": {
        "cidade": "RIO DO SUL",
        "latitude": -27.2139,
        "longitude": -49.6428,
        "intervalo_min": 15,
        "desatualizado_min": 45,
    },
    "energia": {
        "fonte": "auto",          # auto | none | hwmon | arquivo | tasmota | shelly_gen2
        "arquivo": "",
        "tipo_arquivo": "tomada", # tomada | psu | estimativa
        "host": "",
        "intervalo_s": 2,
        "max_age_s": 10,
        "psu_watts": 0,           # capacidade nominal da fonte para alertas (0 = sem alerta)
    },
    "histerese": {"temperatura": 3, "percentual": 2, "ping_ms": 5},
}


def _merge(base, extra):
    if not isinstance(extra, dict):
        return base
    for k, v in extra.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge(base[k], v)
        else:
            base[k] = v
    return base


def load():
    cfg = copy.deepcopy(DEFAULTS)
    if yaml is not None and CONFIG_PATH.is_file():
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                _merge(cfg, yaml.safe_load(f) or {})
        except Exception as e:  # configuração inválida: segue com padrões e registra
            cfg["_erro"] = f"{type(e).__name__}: {e}"
    mapa = CONFIG_PATH.parent / "fans.yaml"          # gerado por tools/mgp_mapear_fans.py; vale no lugar do padrão
    if yaml is not None and mapa.is_file():
        try:
            with open(mapa, encoding="utf-8") as f:
                m = (yaml.safe_load(f) or {}).get("fans")
            if isinstance(m, dict):
                cfg["cpu"]["fans"] = m
        except Exception as e:
            cfg["_erro"] = f"fans.yaml: {type(e).__name__}: {e}"
    if os.environ.get("MGP_DEMO") == "1":
        cfg["painel"]["demo"] = True
    return cfg
