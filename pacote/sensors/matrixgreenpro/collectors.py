# MATRIX GREEN PRO | versão 2.7.0 | 07/11/2026 22:03 (-03) | discos e baias montados via VeraCrypt, LUKS ou LVM
# histórico: 2.6.0 07/11/2026 21:00 motivos de redução de clock da GPU (NVML)
# histórico: 2.5.0 07/11/2026 20:15 dispositivo de cada disco (para o total sem duplicar)
# histórico: 2.4.0 07/11/2026 19:00 uso das baias montadas (ocupado, total, percentual)
# histórico: 2.3.0 02/11/2026 21:50 temperaturas de placa, RAM e SSD (Cpu.temps)
# histórico: 2.2.0 02/11/2026 21:30 leitura de bomba e ventoinhas por papel (Cpu.cool)
# histórico: 2.1.0 31/10/2026 23:45 erro do clima exposto para o estado da coleta
# histórico: 2.0.0 31/10/2026 23:10 tráfego por interface, rota padrão, limite de potência da GPU
# histórico: 1.0.0 31/10/2026 22:40 criação inicial
# Coletores de métricas. Regras:
#  * nenhum coletor bloqueia a transmissão para a tela: tudo que pode demorar
#    (GPU, ping, clima, discos, energia por HTTP) roda em thread própria;
#  * nada é inventado: sem medição o valor é None e a tela mostra N/D;
#  * valor antigo nunca é exibido como atual (cada leitura tem carimbo de tempo).
import csv
import glob
import io
import json
import os
import re
import shutil
import socket
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

import psutil

from . import settings

_LOG = None


def log(msg, level="info"):
    global _LOG
    if _LOG is None:
        try:
            from library.log import logger as _l
            _LOG = _l
        except Exception:
            import logging
            _LOG = logging.getLogger("matrixgreenpro")
    getattr(_LOG, level, _LOG.info)("[MatrixGreenPro] " + msg)


# ---------------------------------------------------------------- utilidades
class Worker(threading.Thread):
    """Executa fn() periodicamente e guarda (timestamp, resultado)."""

    def __init__(self, name, fn, interval):
        super().__init__(name=f"mgp-{name}", daemon=True)
        self.fn, self.interval = fn, max(0.5, float(interval))
        self.value, self.ts, self.error = None, 0.0, None
        self._lock = threading.Lock()

    def run(self):
        while True:
            t0 = time.time()
            try:
                v = self.fn()
                with self._lock:
                    self.value, self.ts, self.error = v, time.time(), None
            except Exception as e:  # registra uma vez por tipo de erro
                msg = f"{type(e).__name__}: {e}"
                if msg != self.error:
                    log(f"coletor {self.name}: {msg}", "warning")
                with self._lock:
                    self.value, self.ts, self.error = None, time.time(), msg
            time.sleep(max(0.2, self.interval - (time.time() - t0)))

    def get(self, max_age=None):
        with self._lock:
            if max_age is not None and time.time() - self.ts > max_age:
                return None
            return self.value


def _num(s):
    try:
        s = str(s).strip()
        if not s or s.startswith("[") or s.upper() in ("N/A", "NA"):
            return None
        return float(s)
    except Exception:
        return None


def _read(path, default=None):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception:
        return default


def _hwmon_fans():
    """Lê direto do sysfs: {chip: {"fan1": rpm, ...}}. O psutil só numera por posição (fan7 viraria a 6ª)."""
    out = {}
    for d in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
        try:
            nome = Path(d, "name").read_text().strip()
        except Exception:
            continue
        for f in sorted(glob.glob(d + "/fan*_input")):
            try:
                out.setdefault(nome, {})[os.path.basename(f)[:-6]] = int(Path(f).read_text().strip())
            except Exception:
                pass
    return out


def _hwmon_temps():
    """Lê do sysfs: {chip: [(rótulo, °C), ...]} somando todos os dispositivos de mesmo nome (ex.: 2 pentes spd5118)."""
    out = {}
    for d in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
        try:
            nome = Path(d, "name").read_text().strip()
        except Exception:
            continue
        for f in sorted(glob.glob(d + "/temp*_input")):
            base = f[:-6]
            try:
                v = int(Path(f).read_text().strip()) / 1000.0
            except Exception:
                continue
            try:
                lab = Path(base + "_label").read_text().strip()
            except Exception:
                lab = os.path.basename(base)
            out.setdefault(nome, []).append((lab, v))
    return out


def _fisicos(nome, sysroot="/sys", prof=0):
    """Dispositivo e tudo o que está embaixo dele: 'dm-1' (VeraCrypt, LUKS ou LVM) -> {'dm-1', 'sde1'}.
    Segue /sys/block/<nome>/slaves até chegar às partições físicas."""
    out = {nome}
    if prof > 6:
        return out
    try:
        for s in os.listdir(f"{sysroot}/block/{nome}/slaves"):
            out |= _fisicos(s, sysroot, prof + 1)
    except OSError:
        pass
    return out


def _bloco_base(dev, sysroot="/sys"):
    """/dev/sdb1 -> 'sdb'; /dev/nvme0n1p2 -> 'nvme0n1'; /dev/mapper/veracrypt1 (dm-1 sobre sde1) -> 'sde'.
    None se não for um disco simples (RAID, vários discos, etc.)."""
    try:
        n = os.path.basename(os.path.realpath(dev))
        fis = sorted(x for x in _fisicos(n, sysroot) if not x.startswith("dm-"))
        if n.startswith("dm-") and len(fis) == 1:              # criptografia ou LVM sobre uma partição só
            n = fis[0]
        sp = os.path.realpath(f"{sysroot}/class/block/{n}")
        if os.path.exists(sp + "/partition"):
            n = os.path.basename(os.path.dirname(sp))
        return n if os.path.exists(f"{sysroot}/class/block/{n}") else None
    except Exception:
        return None


def _temp_bloco(base, sysroot="/sys"):
    """Temperatura (°C) do disco: sensor hwmon do NVMe ou do módulo drivetemp (HDD/SSD SATA). None se não houver."""
    if not base:
        return None
    sb = f"{sysroot}/class/block/{base}"
    for pat in (sb + "/device/hwmon*/temp1_input", sb + "/device/hwmon/hwmon*/temp1_input"):
        for f in glob.glob(pat):
            try:
                v = int(Path(f).read_text().strip()) / 1000.0
            except Exception:
                continue
            if 0 < v < 120:
                return v
    return None


def _disco_rotativo(base, sysroot="/sys"):
    """True = HDD (limites de temperatura próprios); False = SSD/NVMe; None = desconhecido."""
    try:
        return Path(f"{sysroot}/block/{base}/queue/rotational").read_text().strip() == "1"
    except Exception:
        return None


# ---------------------------------------------------------------- CPU
class Cpu:
    def __init__(self, cfg):
        self.cfg = cfg["cpu"]
        psutil.cpu_percent(None)  # primeira chamada inicializa a referência
        self.model = self._model()
        self.ever_temp = False
        self.ever_fan = False
        self.ever_temps = set()  # papéis de temperatura (placa, ram, ssd) que já tiveram leitura
        self.ever_rpm = set()    # papéis (bomba, radiador...) que já giraram: 0 RPM depois disso é falha

    @staticmethod
    def _model():
        for line in (_read("/proc/cpuinfo", "") or "").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
        return ""

    def thresholds(self):
        """Limites térmicos a partir do modelo real (Tjmax publicado pela AMD/Intel)."""
        w, c = self.cfg.get("temp_warn"), self.cfg.get("temp_crit")
        m = self.model.lower()
        dw, dc = 80, 90  # genérico conservador
        if "ryzen" in m:
            mm = re.search(r"ryzen\s+\d+\s+(?:pro\s+)?(\d)(\d)\d\d", m)
            gen = int(mm.group(1)) if mm else 0
            if gen in (7, 8, 9):   # Zen 4/5 desktop: Tjmax 95 °C, opera perto do limite por projeto
                dw, dc = 88, 94
            elif gen in (3, 5):    # Zen 2/3: Tjmax 90-95 °C (5800X3D 90 °C)
                dw, dc = 80, 88
        return (dw if w == "auto" else float(w), dc if c == "auto" else float(c))

    def temp(self):
        try:
            temps = psutil.sensors_temperatures()
        except Exception:
            return None
        want = str(self.cfg.get("temp_sensor", "auto"))
        if want != "auto" and "/" in want:
            chip, label = want.split("/", 1)
            for e in temps.get(chip, []):
                if e.label == label:
                    return e.current
            return None
        for chip, labels in (("k10temp", ("Tctl", "Tdie", "Tccd1")),
                             ("zenpower", ("Tdie", "Tctl")),
                             ("coretemp", ("Package id 0",))):
            entries = temps.get(chip, [])
            for lab in labels:
                for e in entries:
                    if e.label == lab:
                        return e.current
            if entries:
                return entries[0].current
        return None

    def fan(self):
        try:
            fans = psutil.sensors_fans()
        except Exception:
            return None
        if not fans:
            return None
        want = str(self.cfg.get("fan", "auto"))
        if want == "auto":
            try:
                from library import config as tcfg
                v = str(tcfg.CONFIG_DATA["config"].get("CPU_FAN", "AUTO"))
                if v.upper() != "AUTO":
                    want = v
            except Exception:
                pass
        if want != "auto" and want.upper() != "AUTO" and "/" in want:
            chip, label = want.split("/", 1)
            for i, e in enumerate(fans.get(chip, []), 1):
                if e.label == label or f"fan{i}" == label:
                    return e.current
            return None
        for chip, entries in fans.items():
            for e in entries:
                if "cpu" in (e.label or "").lower():
                    return e.current
        for chip, entries in fans.items():  # Super I/O: fan2 costuma ser CPU_FAN; fan1 como reserva
            if chip.startswith(("nct", "it8", "it87", "f71")) and entries:
                return (entries[1] if len(entries) > 1 and entries[1].current > 0 else entries[0]).current
        return None

    def cool(self):
        """Bomba e ventoinhas por papel, conforme cpu.fans (ex.: bomba: nct6799/fan1). None = sem mapa."""
        mapa = self.cfg.get("fans")
        if not isinstance(mapa, dict) or not mapa:
            return None
        leit = _hwmon_fans()
        sio = [n for n in leit if n.startswith(("nct", "it8", "it87", "f71", "w83"))]
        out = {}
        for papel, ref in mapa.items():
            if not ref:
                continue
            chip, _, fan = str(ref).rpartition("/")
            chip = chip or (sio[0] if sio else "")
            rpm = leit.get(chip, {}).get(fan)
            if rpm is not None and rpm > 0:
                self.ever_rpm.add(papel)
            out[papel] = {"rpm": rpm, "visto": papel in self.ever_rpm}
        return out

    def temps(self):
        """Temperaturas por papel, conforme cpu.temps (ex.: ram: spd5118/*). '*' = maior valor entre os sensores do chip."""
        mapa = self.cfg.get("temps")
        if not isinstance(mapa, dict) or not mapa:
            return None
        leit = _hwmon_temps()
        out = {}
        for papel, ref in mapa.items():
            if not ref:
                continue
            chip, _, lab = str(ref).partition("/")
            vals = [v for l, v in leit.get(chip, []) if lab in ("*", "") or l == lab]
            vals = [v for v in vals if 0 < v < 120]          # 0 e 105 são entradas sem sensor, não temperatura
            v = max(vals) if vals else None
            if v is not None:
                self.ever_temps.add(papel)
            out[papel] = {"c": v, "visto": papel in self.ever_temps}
        return out

    def read(self):
        f = None
        try:
            fr = psutil.cpu_freq()
            f = fr.current / 1000.0 if fr and fr.current else None
        except Exception:
            pass
        t, fan = self.temp(), self.fan()
        cool = self.cool()
        if cool and (cool.get("radiador") or {}).get("rpm") is not None:
            fan = cool["radiador"]["rpm"]      # com water cooler, a ventoinha do radiador faz o papel de CPU_FAN
        lost_t = t is None and self.ever_temp
        lost_f = fan is None and self.ever_fan
        self.ever_temp |= t is not None
        self.ever_fan |= fan is not None
        try:
            la = os.getloadavg()
        except Exception:
            la = None
        return {"util": psutil.cpu_percent(None), "ghz": f, "temp": t, "fan": fan,
                "load": la, "temp_lost": lost_t, "fan_lost": lost_f, "cool": cool,
                "temps": self.temps()}


# ---------------------------------------------------------------- GPU NVIDIA
class Gpu:
    FIELDS = "name,utilization.gpu,temperature.gpu,clocks.gr,memory.used,memory.total,fan.speed,power.draw,power.limit"

    def __init__(self, cfg):
        self.cfg = cfg["gpu"]
        self.idx = int(self.cfg.get("index", 0))
        self.nv = None
        self.handle = None
        self.slowdown = None
        self.backend = "none"
        self.ever = False
        try:
            import pynvml  # pacote nvidia-ml-py
            pynvml.nvmlInit()
            self.nv = pynvml
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(self.idx)
            self.backend = "nvml"
            try:
                self.slowdown = pynvml.nvmlDeviceGetTemperatureThreshold(
                    self.handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SLOWDOWN)
            except Exception:
                self.slowdown = None
        except Exception:
            self.nv = None
            if shutil.which("nvidia-smi"):
                self.backend = "smi"
        self.worker = None
        if self.backend != "none":
            self.worker = Worker("gpu", self._read, self.cfg.get("intervalo_s", 1.5))
            self.worker.start()

    def thresholds(self):
        w, c = self.cfg.get("temp_warn"), self.cfg.get("temp_crit")
        if self.slowdown:
            dw, dc = self.slowdown - 10, self.slowdown - 3
        else:
            dw, dc = 80, 87  # NVIDIA GeForce: desaceleração típica entre 90 e 93 °C
        return (dw if w == "auto" else float(w), dc if c == "auto" else float(c))

    def _read(self):
        if self.backend == "nvml":
            nv, h = self.nv, self.handle
            d = {}

            def q(key, fn):
                try:
                    d[key] = fn()
                except Exception:
                    d[key] = None
            q("name", lambda: nv.nvmlDeviceGetName(h))
            q("util", lambda: nv.nvmlDeviceGetUtilizationRates(h).gpu)
            q("temp", lambda: nv.nvmlDeviceGetTemperature(h, nv.NVML_TEMPERATURE_GPU))
            q("mhz", lambda: nv.nvmlDeviceGetClockInfo(h, nv.NVML_CLOCK_GRAPHICS))
            mem = None
            try:
                mem = nv.nvmlDeviceGetMemoryInfo(h)
            except Exception:
                pass
            d["vram_used"] = mem.used / 1024 ** 3 if mem else None
            d["vram_total"] = mem.total / 1024 ** 3 if mem else None
            q("fan_pct", lambda: nv.nvmlDeviceGetFanSpeed(h))
            d["fan_rpm"] = None
            if hasattr(nv, "nvmlDeviceGetFanSpeedRPM"):
                try:
                    r = nv.nvmlDeviceGetFanSpeedRPM(h, 0)
                    d["fan_rpm"] = getattr(r, "speed", r) if not isinstance(r, (int, float)) else r
                except Exception:
                    d["fan_rpm"] = None
            q("power", lambda: nv.nvmlDeviceGetPowerUsage(h) / 1000.0)
            q("power_limit", lambda: nv.nvmlDeviceGetEnforcedPowerLimit(h) / 1000.0)
            # motivos de redução de clock (bits da NVML: 0x8 HW slowdown, 0x20 SW térmico, 0x40 HW térmico,
            # 0x80 HW power brake); o nome da função mudou nas versões novas da NVML
            fz = getattr(nv, "nvmlDeviceGetCurrentClocksEventReasons", None) or \
                getattr(nv, "nvmlDeviceGetCurrentClocksThrottleReasons", None)
            if fz:
                q("throttle", lambda: int(fz(h)))
            return d
        out = subprocess.run(
            ["nvidia-smi", f"--id={self.idx}", f"--query-gpu={self.FIELDS}",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=4).stdout.strip()
        p = [x.strip() for x in out.split(",")]
        if len(p) < 9:
            raise RuntimeError("saída inesperada do nvidia-smi")
        vu, vt = _num(p[4]), _num(p[5])
        return {"name": p[0], "util": _num(p[1]), "temp": _num(p[2]), "mhz": _num(p[3]),
                "vram_used": vu / 1024 if vu is not None else None,
                "vram_total": vt / 1024 if vt is not None else None,
                "fan_pct": _num(p[6]), "fan_rpm": None,  # nvidia-smi não expõe RPM
                "power": _num(p[7]), "power_limit": _num(p[8])}

    def read(self):
        if self.worker is None:
            return {"present": False}
        v = self.worker.get(max_age=6)
        if v is None:
            return {"present": True, "lost": self.ever}
        self.ever = True
        v = dict(v)
        v["present"] = True
        return v


# ---------------------------------------------------------------- FPS (MangoHud)
class Fps:
    """FPS real: lê a última linha do CSV que o MangoHud grava (e descarrega)
    a cada amostra quando output_folder/autostart_log/log_interval estão
    configurados. Não usa a taxa de atualização (Hz) do monitor."""

    def __init__(self, cfg):
        self.dir = cfg["fps"]["mangohud_dir"]
        self.max_age = float(cfg["fps"].get("max_age_s", 3.5))
        try:  # /tmp é limpo no boot; o MangoHud exige que output_folder exista
            os.makedirs(self.dir, exist_ok=True)
        except Exception:
            pass
        self._cleanup()

    def _cleanup(self):
        try:
            now = time.time()
            for f in glob.glob(os.path.join(self.dir, "*.csv")):
                if now - os.path.getmtime(f) > 86400:
                    os.remove(f)
        except Exception:
            pass

    def read(self):
        try:
            files = [f for f in glob.glob(os.path.join(self.dir, "*.csv"))
                     if not f.endswith("_summary.csv")]
            if not files:
                return None
            newest = max(files, key=os.path.getmtime)
            if time.time() - os.path.getmtime(newest) > self.max_age:
                return None
            with open(newest, "rb") as fh:
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                fh.seek(max(0, size - 2048))
                tail = fh.read().decode("utf-8", "ignore").splitlines()
            for line in reversed(tail):
                first = line.split(",", 1)[0].strip()
                v = _num(first)
                if v is not None and line.count(",") >= 10:
                    return v
        except Exception:
            return None
        return None


# ---------------------------------------------------------------- RAM
def ram():
    vm = psutil.virtual_memory()
    g = 1024 ** 3
    used = (vm.total - vm.available) / g  # definição do Linux: descontando cache recuperável
    return {"used": used, "avail": vm.available / g, "total": vm.total / g,
            "pct": 100.0 * (vm.total - vm.available) / vm.total}


# ---------------------------------------------------------------- Discos
class Disks:
    def __init__(self, cfg):
        self.items = list(cfg.get("discos", []))[:3]
        while len(self.items) < 3:
            self.items.append({"nome": "---", "uuid": "", "montagem": ""})
        self.worker = Worker("discos", self._read, cfg.get("disco_intervalo_s", 10))
        self.worker.start()

    @staticmethod
    def _mount_for(item):
        uuid = str(item.get("uuid") or "").strip()
        mnt = str(item.get("montagem") or "").strip()
        parts = psutil.disk_partitions(all=False)
        if uuid:
            link = f"/dev/disk/by-uuid/{uuid}"
            if not os.path.exists(link):
                return None, "OFF"  # disco ausente ou desconectado
            dev = os.path.basename(os.path.realpath(link))
            for p in parts:
                try:
                    if dev in _fisicos(os.path.basename(os.path.realpath(p.device))):   # também via VeraCrypt/LUKS/LVM
                        return p.mountpoint, "OK"
                except Exception:
                    continue
            return None, "OFF"  # presente porém desmontado
        if mnt:
            if os.path.ismount(mnt):
                return mnt, "OK"
            return None, "OFF"
        return None, "CFG"  # não configurado

    @staticmethod
    def _dev_for(item, mount):
        """Dispositivo do disco: pelo UUID (mesmo desmontado) ou pelo ponto de montagem."""
        uuid = str(item.get("uuid") or "").strip()
        if uuid and os.path.exists(f"/dev/disk/by-uuid/{uuid}"):
            return os.path.realpath(f"/dev/disk/by-uuid/{uuid}")
        if mount:
            for p in psutil.disk_partitions(all=False):
                if p.mountpoint == mount:
                    return p.device
        return None

    def _read(self):
        out = []
        for it in self.items:
            m, st = self._mount_for(it)
            d = {"nome": str(it.get("nome", "---"))[:4], "state": st}
            try:
                base = _bloco_base(self._dev_for(it, m)) if (m or st == "OFF") else None
                d["temp"] = _temp_bloco(base)
                d["hdd"] = _disco_rotativo(base) if base else None
                d["dev"] = base
            except Exception:
                d["temp"], d["hdd"] = None, None
            if m:
                u = shutil.disk_usage(m)
                d.update(total=u.total, used=u.used, free=u.free,
                         pct=100.0 * u.used / max(1, (u.used + u.free)))
            out.append(d)
        return out

    def read(self):
        v = self.worker.get(max_age=35)
        if v is None:
            return [{"nome": str(i.get("nome", "---"))[:4], "state": "ND"} for i in self.items]
        return v


# ---------------------------------------------------------------- Baias do TerraMaster (DAS USB)
class Baias:
    """Lê as baias de um gabinete DAS USB (ex.: TerraMaster D4). O gabinete aparece como um hub USB com uma ponte
    (ASMedia 174c:235c) por baia; a porta do hub identifica a baia. Baia sem disco = ponte sem dispositivo de bloco.
    Retorna None se o gabinete não foi encontrado (recurso desligado ou DAS desconectado)."""

    def __init__(self, cfg, sysroot="/sys"):
        self.c = dict(cfg.get("terramaster") or {})
        self.sys = sysroot
        self.on = str(self.c.get("ativo", "auto")).lower() not in ("nao", "não", "false", "0", "desligado")
        self.worker = None
        if self.on and sysroot == "/sys":
            self.worker = Worker("baias", self.leitura, cfg.get("disco_intervalo_s", 10))
            self.worker.start()

    def _id(self, dev):
        try:
            return (Path(f"{self.sys}/bus/usb/devices/{dev}/idVendor").read_text().strip().lower() + ":" +
                    Path(f"{self.sys}/bus/usb/devices/{dev}/idProduct").read_text().strip().lower())
        except Exception:
            return None

    def leitura(self):
        ponte = str(self.c.get("ponte", "174c:235c")).lower()
        hub_id = str(self.c.get("hub", "0bda:0423")).lower()
        n = int(self.c.get("baias", 4))
        hubs = {}
        for d in sorted(glob.glob(f"{self.sys}/bus/usb/devices/*")):
            nome = os.path.basename(d)
            if ":" in nome or "." not in nome or self._id(nome) != ponte:
                continue
            hub, porta = nome.rsplit(".", 1)
            hid = self._id(hub)
            if hub_id and hid and hid != hub_id:
                continue
            try:
                hubs.setdefault(hub, {})[int(porta)] = nome
            except ValueError:
                pass
        if not hubs:
            return None
        hub = max(hubs, key=lambda h: len(hubs[h]))
        mapa = {str(k): int(v) for k, v in (self.c.get("mapa") or {}).items()}
        por_baia = {}
        for porta, nome in hubs[hub].items():
            b = mapa.get(str(porta)) or ((n + 1 - porta) if self.c.get("inverter") else porta)
            por_baia[b] = nome
        montados = {}                                           # dispositivo -> pontos de montagem
        try:
            for p in psutil.disk_partitions(all=False):          # VeraCrypt, LUKS e LVM contam para o disco físico
                for nome in _fisicos(os.path.basename(os.path.realpath(p.device)), self.sys):
                    montados.setdefault(nome, []).append(p.mountpoint)
        except Exception:
            pass
        out = []
        for b in range(1, n + 1):
            item = {"n": b, "estado": "LIVRE", "bytes": None, "modelo": "", "dev": None}
            nome = por_baia.get(b)
            blocos = glob.glob(f"{self.sys}/bus/usb/devices/{nome}/{nome}:1.0/host*/target*/*:*/block/*") if nome else []
            if blocos:
                base = os.path.basename(blocos[0])
                try:
                    tam = int(Path(f"{self.sys}/block/{base}/size").read_text().strip()) * 512
                except Exception:
                    tam = 0
                if tam > 0:
                    mod = " ".join(_read(f"{self.sys}/block/{base}/device/{k}", "").strip() for k in ("vendor", "model")).strip()
                    pontos = [pt for m, pts in montados.items()
                              if m == base or (m.startswith(base) and m[len(base):].lstrip("p").isdigit()) for pt in pts]
                    item.update(estado="MONT" if pontos else "DESM", bytes=tam, modelo=mod, dev=base)
                    usado = total = 0                           # soma das partições montadas (cada ponto uma vez)
                    for pt in dict.fromkeys(pontos):
                        try:
                            u = shutil.disk_usage(pt)
                            usado, total = usado + u.used, total + u.used + u.free
                        except Exception:
                            pass
                    if total:
                        item.update(usado=usado, total=total)
            out.append(item)
        return out

    def read(self):
        if not self.on:
            return None
        return self.worker.get(max_age=35) if self.worker else self.leitura()


# ---------------------------------------------------------------- Rede
class Net:
    def __init__(self, cfg):
        c = cfg["rede"]
        self.eth = self._pick(c.get("ethernet", "auto"), wireless=False)
        self.wifi = self._pick(c.get("wifi", "auto"), wireless=True)
        self.prev = None

    @staticmethod
    def _is_wireless(i):
        return os.path.isdir(f"/sys/class/net/{i}/wireless") or os.path.isdir(f"/sys/class/net/{i}/phy80211")

    def _pick(self, want, wireless):
        want = str(want or "").strip()
        if want.lower() == "nenhuma":
            return None
        if want and want != "auto":
            return want
        try:  # aproveita ETH/WLO já definidos no config.yaml do programa
            from library import config as tcfg
            v = str(tcfg.CONFIG_DATA["config"].get("WLO" if wireless else "ETH", "") or "")
            if v and os.path.exists(f"/sys/class/net/{v}"):
                return v
        except Exception:
            pass
        for i in sorted(os.listdir("/sys/class/net")) if os.path.isdir("/sys/class/net") else []:
            if i == "lo" or not os.path.exists(f"/sys/class/net/{i}/device"):
                continue
            if self._is_wireless(i) == wireless:
                return i
        return None

    @staticmethod
    def _ipv4(i):
        try:
            for a in psutil.net_if_addrs().get(i, []):
                if a.family == socket.AF_INET:
                    return a.address
        except Exception:
            pass
        return None

    def _iface_info(self, i, wireless):
        if not i:
            return {"exists": False}
        if not os.path.exists(f"/sys/class/net/{i}"):
            return {"exists": False, "name": i}
        oper = _read(f"/sys/class/net/{i}/operstate", "unknown")
        # alguns drivers informam "unknown" com o enlace ativo: nesse caso vale o carrier
        up = oper == "up" or (oper == "unknown" and _read(f"/sys/class/net/{i}/carrier", "0") == "1")
        st = psutil.net_if_stats().get(i)
        d = {"exists": True, "name": i, "up": up, "ip": self._ipv4(i) if up else None,
             "speed": st.speed if st and st.speed and st.speed > 0 else None, "signal": None}
        if wireless and up:
            for line in (_read("/proc/net/wireless", "") or "").splitlines()[2:]:
                if line.strip().startswith(i + ":"):
                    try:
                        d["signal"] = float(line.split()[3].rstrip("."))
                    except Exception:
                        pass
        return d

    @staticmethod
    def default_iface():
        """Interface da rota padrão IPv4 (a que de fato leva à internet)."""
        best = None
        for line in (_read("/proc/net/route", "") or "").splitlines()[1:]:
            p = line.split()
            if len(p) > 6 and p[1] == "00000000" and int(p[3], 16) & 2:
                metric = int(p[6])
                if best is None or metric < best[1]:
                    best = (p[0], metric)
        return best[0] if best else None

    def read(self):
        now = time.time()
        pern = psutil.net_io_counters(pernic=True)
        out = {"eth": self._iface_info(self.eth, False), "wifi": self._iface_info(self.wifi, True),
               "default": self.default_iface()}
        cur = {}
        for key, i in (("eth", self.eth), ("wifi", self.wifi)):
            if i and i in pern:
                cur[key] = (pern[i].bytes_recv, pern[i].bytes_sent)
        for key, (rx, tx) in cur.items():
            d = out[key]
            d["rx"], d["tx"] = rx, tx
            d["rate_down"] = d["rate_up"] = None
            if self.prev and key in self.prev[1]:
                dt = now - self.prev[0]
                prx, ptx = self.prev[1][key]
                if dt > 0 and rx >= prx and tx >= ptx:
                    d["rate_down"], d["rate_up"] = (rx - prx) / dt, (tx - ptx) / dt
        self.prev = (now, cur)
        if cur:
            downs = [out[k].get("rate_down") for k in cur]
            ups = [out[k].get("rate_up") for k in cur]
            out["down"] = sum(x for x in downs if x is not None) if any(x is not None for x in downs) else None
            out["up"] = sum(x for x in ups if x is not None) if any(x is not None for x in ups) else None
            out["rx"] = sum(v[0] for v in cur.values())
            out["tx"] = sum(v[1] for v in cur.values())
        else:
            out.update(down=None, up=None, rx=None, tx=None)
        return out


# ---------------------------------------------------------------- Sistema
_OS_NAME = None


def os_name():
    global _OS_NAME
    if _OS_NAME is None:
        d = {}
        for line in (_read("/etc/os-release", "") or "").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                d[k] = v.strip().strip('"')
        _OS_NAME = " ".join(x for x in (d.get("ID", "linux").upper(), d.get("VERSION_ID", ""),
                                         d.get("VERSION_CODENAME", "").upper()) if x)
    return _OS_NAME


def uptime_s():
    try:
        return time.time() - psutil.boot_time()
    except Exception:
        return None


# ---------------------------------------------------------------- Ping
class Ping:
    def __init__(self, cfg):
        self.host = str(cfg["ping"].get("host", "8.8.8.8"))
        self.interval = float(cfg["ping"].get("intervalo_s", 5))
        self.has_ping = shutil.which("ping") is not None
        self.worker = Worker("ping", self._read, self.interval)
        self.worker.start()

    def _read(self):
        if self.has_ping:
            r = subprocess.run(["ping", "-n", "-c", "1", "-W", "2", self.host],
                               capture_output=True, text=True, timeout=5)
            m = re.search(r"time[=<]([\d.]+)\s*ms", r.stdout)
            return {"ok": bool(m), "ms": float(m.group(1)) if m else None}
        try:
            import ping3
            v = ping3.ping(self.host, timeout=2, unit="ms")
            return {"ok": bool(v), "ms": float(v) if v else None}
        except Exception:
            return {"ok": False, "ms": None, "noprobe": True}

    def read(self):
        v = self.worker.get(max_age=self.interval * 3 + 5)
        return v if v is not None else {"ok": None, "ms": None}


# ---------------------------------------------------------------- Clima (Open-Meteo)
WMO_PT = {
    0: "CÉU LIMPO", 1: "POUCAS NUVENS", 2: "PARC. NUBLADO", 3: "NUBLADO",
    45: "NEBLINA", 48: "NEBLINA GELO",
    51: "GAROA FRACA", 53: "GAROA", 55: "GAROA FORTE", 56: "GAROA GELADA", 57: "GAROA GELADA",
    61: "CHUVA FRACA", 63: "CHUVA", 65: "CHUVA FORTE", 66: "CHUVA GELADA", 67: "CHUVA GELADA",
    71: "NEVE FRACA", 73: "NEVE", 75: "NEVE FORTE", 77: "GRANIZO FINO",
    80: "PANCADAS", 81: "PANCADAS", 82: "PANCADAS FORTES", 85: "NEVE", 86: "NEVE FORTE",
    95: "TEMPORAL", 96: "TEMPORAL GRANIZO", 99: "TEMPORAL GRANIZO",
}


class Weather:
    URL = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           "&current=temperature_2m,weather_code&timezone=America%2FSao_Paulo")

    def __init__(self, cfg):
        c = cfg["clima"]
        self.city = str(c.get("cidade", ""))
        self.lat, self.lon = float(c["latitude"]), float(c["longitude"])
        self.interval = max(10.0, float(c.get("intervalo_min", 15))) * 60  # mínimo 10 min: uso responsável
        self.stale = float(c.get("desatualizado_min", 45)) * 60
        self.cache = settings.CACHE_DIR / "clima.json"
        self.data = self._load_cache()
        self.err = None
        self.started = time.time()
        self.lock = threading.Lock()
        threading.Thread(target=self._loop, name="mgp-clima", daemon=True).start()

    def _load_cache(self):
        try:
            d = json.loads(self.cache.read_text(encoding="utf-8"))
            if abs(d.get("lat", 0) - self.lat) < 0.01 and abs(d.get("lon", 0) - self.lon) < 0.01:
                return d
        except Exception:
            pass
        return None

    def _fetch(self):
        url = self.URL.format(lat=self.lat, lon=self.lon)
        req = urllib.request.Request(url, headers={"User-Agent": "MatrixGreenPro/1.0 (turing-smart-screen)"})
        with urllib.request.urlopen(req, timeout=10) as r:
            j = json.loads(r.read().decode("utf-8"))
        cur = j["current"]
        d = {"temp": float(cur["temperature_2m"]), "code": int(cur["weather_code"]),
             "ts": time.time(), "lat": self.lat, "lon": self.lon}
        try:
            self.cache.parent.mkdir(parents=True, exist_ok=True)
            self.cache.write_text(json.dumps(d), encoding="utf-8")
        except Exception:
            pass
        return d

    def _loop(self):
        if self.data and time.time() - self.data["ts"] < self.interval:
            time.sleep(self.interval - (time.time() - self.data["ts"]))
        while True:
            try:
                d = self._fetch()
                with self.lock:
                    self.data, self.err = d, None
                time.sleep(self.interval)
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                if msg != self.err:
                    log(f"clima indisponível: {msg}", "warning")
                self.err = msg
                time.sleep(120)  # nova tentativa em 2 min sem martelar a API

    def read(self):
        with self.lock:
            d = self.data
        if not d:
            return {"state": "ND"}
        age = time.time() - d["ts"]
        return {"state": "STALE" if age > self.stale else "OK", "temp": d["temp"],
                "desc": WMO_PT.get(d["code"], f"CÓD {d['code']}"), "age": age, "ts": d["ts"]}


# ---------------------------------------------------------------- Energia
PSU_HWMON = ("corsairpsu", "nzxt_e500", "nzxtpsu", "seasonic", "hpsu")


class Power:
    """Somente medições legítimas. Fonte e natureza (TOMADA/PSU/EST) sempre exibidas."""

    def __init__(self, cfg):
        self.c = cfg["energia"]
        self.kind = str(self.c.get("fonte", "auto")).lower()
        self.hwmon = None
        if self.kind in ("auto", "hwmon"):
            self.hwmon = self._find_psu_hwmon()
            if self.hwmon:
                self.kind = "hwmon"
            elif self.kind == "auto":
                self.kind = "arquivo" if self.c.get("arquivo") else "none"
        self.worker = None
        if self.kind in ("tasmota", "shelly_gen2", "hwmon", "arquivo"):
            self.worker = Worker("energia", self._read, self.c.get("intervalo_s", 2))
            self.worker.start()

    @staticmethod
    def _find_psu_hwmon():
        for d in glob.glob("/sys/class/hwmon/hwmon*"):
            name = _read(os.path.join(d, "name"), "")
            if any(name.startswith(p) for p in PSU_HWMON):
                for f in sorted(glob.glob(os.path.join(d, "power*_input"))):
                    lab = (_read(f.replace("_input", "_label"), "") or "").lower()
                    if "total" in lab or "input" in lab or f.endswith("power1_input"):
                        return f
        return None

    def _read(self):
        if self.kind == "hwmon":
            return {"w": int(_read(self.hwmon)) / 1e6, "tag": "PSU"}
        if self.kind == "arquivo":
            p = self.c.get("arquivo")
            if time.time() - os.path.getmtime(p) > float(self.c.get("max_age_s", 10)):
                return None
            tag = {"tomada": "TOMADA", "psu": "PSU", "estimativa": "EST"}.get(
                str(self.c.get("tipo_arquivo", "tomada")).lower(), "EST")
            return {"w": float(_read(p).split()[0].replace(",", ".")), "tag": tag}
        host = self.c.get("host")
        if self.kind == "tasmota":
            with urllib.request.urlopen(f"http://{host}/cm?cmnd=Status%208", timeout=3) as r:
                j = json.loads(r.read().decode())
            return {"w": float(j["StatusSNS"]["ENERGY"]["Power"]), "tag": "TOMADA"}
        if self.kind == "shelly_gen2":
            with urllib.request.urlopen(f"http://{host}/rpc/Switch.GetStatus?id=0", timeout=3) as r:
                j = json.loads(r.read().decode())
            return {"w": float(j["apower"]), "tag": "TOMADA"}
        return None

    def read(self):
        if self.worker is None:
            return {"state": "ND"}
        v = self.worker.get(max_age=float(self.c.get("max_age_s", 10)) + 5)
        if v is None:
            return {"state": "LOST", "tag": self.kind.upper()[:6]}
        return {"state": "OK", **v}
