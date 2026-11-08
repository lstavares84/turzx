# MATRIX GREEN PRO | versão 3.6.0 | 07/11/2026 21:00 (-03) | demonstração do LOG de alertas
# histórico: 3.5.0 07/11/2026 20:20 demonstração de mudanças bruscas e do registro
# histórico: 3.4.0 07/11/2026 19:10 histórico de 24 h para os gráficos (historico.py)
# histórico: 3.3.0 07/11/2026 19:00 demonstração com uso da baia montada
# histórico: 3.2.0 02/11/2026 17:40 estilos gamma* e apelido uranio
# histórico: 3.1.0 01/11/2026 10:50 estilo selecionável (matrix, uranio, pcb)
# histórico: 2.1.0 31/10/2026 23:50 estado da coleta por coletor, isolamento de falhas
# histórico: 2.0.0 31/10/2026 23:30 cenários demo normal/atencao/critico
# histórico: 1.0.0 31/10/2026 22:40 criação inicial
# Motor do painel: coleta -> modelo de visão -> quadro 320x480 -> envia à tela
# somente os retângulos que mudaram (economiza a banda USB da revisão A).
# Exposto ao programa como sensor personalizado "MatrixGreenProPanel".
import math
import os
import threading
import time

from PIL import ImageChops

from . import collectors as col
from . import settings
from .render import draw_frame, W, H
from .viewmodel import ViewModel

# Faixas horizontais usadas na comparação de quadros (limites das seções, ver render.Y).
BANDS = [(0, 21), (21, 78), (78, 167), (167, 204), (204, 283), (283, 361), (361, 410), (410, 454), (454, 480)]


def demo_snapshot(scenario="normal"):
    """Dados DEMONSTRATIVOS (o cabeçalho exibe DEMO). Usados só no modo demo e nas prévias.
    Cenários: normal | atencao | critico. O layout é idêntico nos três."""
    now = time.time()
    att, crit = scenario == "atencao", scenario == "critico"
    eth_rates = (0.0, 0.0) if crit else (12.4e6, 1.8e6)
    wifi = ({"exists": False} if att else
            {"exists": True, "name": "wlp4s0", "up": True, "signal": -54, "ip": "192.168.0.21",
             "rate_down": 3.2e6 if crit else 18e3, "rate_up": 0.4e6 if crit else 2e3, "rx": 1.2e9, "tx": 0.3e9})
    s = {
        "demo": True,
        "cpu": {"util": 100 if crit else (87 if att else 28), "ghz": 5.12 if crit else 4.85,
                "temp": 96 if crit else (84 if att else 57),
                "fan": 2150 if crit else (1780 if att else 1240),
                "temps": {"placa": {"c": 34, "visto": True}, "ram": {"c": 32, "visto": True}, "ssd": {"c": 40, "visto": True}},
                "cool": {"bomba": {"rpm": 5600, "visto": True},
                         "radiador": {"rpm": 2150 if crit else (1780 if att else 1240), "visto": True},
                         "sq_inf": {"rpm": 1350, "visto": True}, "sq_lat": {"rpm": 1380, "visto": True},
                         "sq_tras": {"rpm": 1420, "visto": True}},
                "load": (24.31, 18.70, 9.92) if crit else ((9.84, 7.12, 4.05) if att else (0.82, 1.20, 0.91))},
        "gpu": {"present": True, "util": 99 if crit else (97 if att else 74),
                "temp": 74 if crit else (71 if att else 67), "mhz": 2655,
                "vram_used": 9.1 if crit else (10.9 if att else 6.4), "vram_total": 12.0,
                "fan_rpm": None if att else (2210 if crit else 1800), "fan_pct": 78 if crit else (72 if att else 68),
                "power": 284 if crit else (261 if att else 212), "power_limit": 300},
        "fps": None if crit else (96 if att else 142),
        "ram": ({"used": 28.6, "avail": 2.7, "total": 31.3, "pct": 91.4} if crit else
                {"used": 12.4, "avail": 18.9, "total": 31.3, "pct": 39.6}),
        "disks": [
            {"nome": "M.2", "state": "OK", "total": 1000e9, "used": 420e9, "free": 580e9, "pct": 42.0, "temp": 41.0, "hdd": False},
            {"nome": "2T", "state": "OK", "total": 2000e9, "used": 1760e9 if att else 1400e9,
             "free": 240e9 if att else 600e9, "pct": 88.0 if att else 70.0, "temp": 52.0 if att else 30.0, "hdd": True},
            {"nome": "4T", "state": "OK", "total": 4000e9, "used": 3960e9 if crit else 3100e9,
             "free": 40e9 if crit else 900e9, "pct": 99.0 if crit else 77.5, "temp": 57.0 if crit else 33.0, "hdd": True},
        ],
        "baias": [{"n": 1, "estado": "MONT", "bytes": 12000138625024, "modelo": "WDC WD120EFGX-68CPHN0", "dev": "sdc",
                   "usado": 6.24e12, "total": 11.99e12},
                  {"n": 2, "estado": "DESM", "bytes": 500107862016, "modelo": "TOSHIBA MK5076GSX", "dev": "sdd"},
                  {"n": 3, "estado": "DESM", "bytes": 8001563222016, "modelo": "ST8000DM004-2U9188", "dev": "sde"},
                  {"n": 4, "estado": "LIVRE", "bytes": None, "modelo": "", "dev": None}],
        "net": {"down": eth_rates[0] + (wifi.get("rate_down") or 0), "up": eth_rates[1] + (wifi.get("rate_up") or 0),
                "rx": 284.1e9, "tx": 38.2e9, "default": "wlp4s0" if crit else "enp5s0",
                "eth": {"exists": True, "name": "enp5s0", "up": not crit, "speed": 1000, "ip": "192.168.0.10",
                        "rate_down": eth_rates[0], "rate_up": eth_rates[1], "rx": 282.9e9, "tx": 37.9e9},
                "wifi": wifi},
        "os": "DEBIAN 13 TRIXIE",
        "uptime": 2 * 86400 + 5 * 3600 + 18 * 60,
        "ping": {"ok": True, "ms": 95.0} if att else ({"ok": True, "ms": 34.0} if crit else {"ok": True, "ms": 18.0}),
        "weather": {"state": "OK", "temp": 22.0, "desc": "NUBLADO", "ts": now - 600},
        "power": {"state": "ND"},
        "coleta": {"esperados": 8, "falhas": []},
    }
    from .historico import demo_series
    s["hist"] = demo_series(s, scenario)          # 24 h fictícias para os gráficos do GAMMA DELTA
    m = lambda minutos: now - 60 * minutos         # LOG de alertas fictício (o painel real registra as mudanças de cor)
    W_, C_, O_ = 1, 2, 0
    s["demo_alertas"] = {
        "normal": [(m(52), "GPU 81°C ÂMBAR", W_), (m(49), "GPU 76°C VERDE", O_)],
        "atencao": [(m(1), "CPU 84°C ÂMBAR", W_), (m(2), "PING 95ms ÂMBAR", W_), (m(3), "VRAM 91% ÂMBAR", W_),
                    (m(5), "2T 88% ÂMBAR", W_), (m(6), "2T TEMP 52°C ÂMBAR", W_)],
        "critico": [(m(0), "CPU 96°C VERMELHO", C_), (m(1), "4T 99% VERMELHO", C_), (m(2), "4T TEMP 57°C ÂMBAR", W_),
                    (m(3), "RAM 91% ÂMBAR", W_), (m(4), "PING 34ms ÂMBAR", W_)],
    }.get(scenario, [])
    s["demo_brusco"] = {"atencao": {"cpu_temp", "gpu_util", "net_down", "fps"},
                        "critico": {"cpu_util", "cpu_temp", "ram_used", "ram_avail", "gpu_w"}}.get(scenario, set())
    return s


class Engine:
    def __init__(self):
        self.cfg = settings.load()
        if self.cfg.get("_erro"):
            col.log("config.yaml do painel inválido, usando padrões: " + self.cfg["_erro"], "error")
        self.demo = bool(self.cfg["painel"].get("demo"))
        self.scenario = os.environ.get("MGP_DEMO_SCENARIO", str(self.cfg["painel"].get("demo_cenario", "normal")))
        if self.demo:
            self.cpu = self.gpu = None
            cpu_l, gpu_l = (80, 90), (80, 87)
        else:
            self.cpu = col.Cpu(self.cfg)
            self.gpu = col.Gpu(self.cfg)
            self.fps = col.Fps(self.cfg)
            self.disks = col.Disks(self.cfg)
            self.baias = col.Baias(self.cfg)
            self.net = col.Net(self.cfg)
            self.ping = col.Ping(self.cfg)
            self.weather = col.Weather(self.cfg)
            self.power = col.Power(self.cfg)
            from .historico import Historico
            self.hist = Historico()
            cpu_l, gpu_l = self.cpu.thresholds(), self.gpu.thresholds()
            col.log(f"CPU '{self.cpu.model}' limites {cpu_l}; GPU backend={self.gpu.backend} limites {gpu_l}; "
                    f"ETH={self.net.eth} WIFI={self.net.wifi}; energia={self.power.kind}")
        self.vm = ViewModel(self.cfg, cpu_l, gpu_l)
        from .estilos import renderer, ALIASES
        pedido = os.environ.get("MGP_ESTILO", self.cfg["painel"].get("estilo", "matrix"))
        self.estilo, self.draw = renderer(pedido)
        if str(pedido).lower() not in (self.estilo, *ALIASES):
            col.log(f"estilo '{pedido}' desconhecido; usando '{self.estilo}'", "warning")
        col.log(f"estilo do painel: {self.estilo}")
        self.prev = None
        self.last_full = 0.0
        self.lock = threading.Lock()

    def snapshot(self):
        """Lê todos os coletores. Cada um é isolado: a falha de um não derruba os outros
        e é registrada no estado da coleta (independente da saúde do computador)."""
        if self.demo:
            return demo_snapshot(self.scenario)
        falhas, esperados = [], 0
        s = {}

        def get(key, fn, label, default, counted=True):
            nonlocal esperados
            esperados += 1 if counted else 0
            try:
                s[key] = fn()
            except Exception as e:
                s[key] = default
                if counted:
                    falhas.append(label)
                col.log(f"coleta {label}: {type(e).__name__}: {e}", "warning")

        get("cpu", self.cpu.read, "CPU", {"util": None})
        get("ram", col.ram, "RAM", {"used": 0.0, "avail": 0.0, "total": 0.0, "pct": 0.0})
        get("gpu", self.gpu.read, "GPU", {"present": True, "lost": True}, counted=self.gpu.backend != "none")
        get("fps", self.fps.read, "FPS", None, counted=False)          # FPS só existe com jogo aberto
        get("disks", self.disks.read, "DISCOS", [{"nome": "---", "state": "ND"}] * 3)
        get("baias", self.baias.read, "BAIAS", None, counted=False)     # recurso opcional: só existe com o gabinete USB
        get("net", self.net.read, "REDE", {"eth": {"exists": False}, "wifi": {"exists": False}})
        get("ping", self.ping.read, "PING", {"ok": None})
        get("weather", self.weather.read, "CLIMA", {"state": "ND"})
        get("power", self.power.read, "ENERGIA", {"state": "ND"}, counted=self.power.kind != "none")
        s["os"], s["uptime"] = col.os_name(), col.uptime_s()

        # sensores que existiam e pararam, dados vencidos e coletores com erro
        c = s["cpu"]
        if c.get("temp_lost"):
            falhas.append("CPU°C")
        if c.get("fan_lost"):
            falhas.append("FAN")
        if self.gpu.backend != "none" and s["gpu"].get("lost") and "GPU" not in falhas:
            falhas.append("GPU")
        if self.disks.worker.error or any(d.get("state") == "ND" for d in s["disks"]):
            falhas.append("DISCOS") if "DISCOS" not in falhas else None
        pg = s["ping"]
        if (pg.get("noprobe") or self.ping.worker.error or pg.get("ok") is None) and "PING" not in falhas:
            falhas.append("PING")
        w = s["weather"]
        if w.get("state") == "STALE" or (w.get("state") == "ND" and (
                self.weather.err or time.time() - self.weather.started > 60)):
            falhas.append("CLIMA") if "CLIMA" not in falhas else None
        if s["power"].get("state") == "LOST" and "ENERGIA" not in falhas:
            falhas.append("ENERGIA")
        s["coleta"] = {"esperados": esperados, "falhas": falhas}
        try:
            s["hist"] = self.hist.add(s)                        # gráficos de 24 h (só o GAMMA DELTA desenha)
        except Exception as e:
            s["hist"] = None
            col.log(f"histórico: {type(e).__name__}: {e}", "warning")
        return s

    def frame(self):
        return self.draw(self.vm.build(self.snapshot()))

    def push(self, lcd):
        """Desenha e envia somente as regiões alteradas."""
        try:  # se a fila USB estiver congestionada, pula este ciclo (sem perder a diferença)
            from library import config as tcfg
            if tcfg.update_queue.qsize() > 40:
                return
        except Exception:
            pass
        with self.lock:
            img = self.frame()
            now = time.time()
            full = (self.prev is None or
                    now - self.last_full > float(self.cfg["painel"].get("refresh_full_s", 300)))
            if full:
                lcd.DisplayPILImage(img, 0, 0)
                self.last_full = now
            else:
                for y0, y1 in BANDS:
                    a = self.prev.crop((0, y0, W, y1))
                    b = img.crop((0, y0, W, y1))
                    box = ImageChops.difference(a, b).getbbox()
                    if box:
                        x0, by0, x1, by1 = box
                        lcd.DisplayPILImage(b.crop((x0, by0, x1, by1)), x0, y0 + by0)
            self.prev = img


_ENGINE = None
_ENGINE_ERR = None


def engine():
    global _ENGINE, _ENGINE_ERR
    if _ENGINE is None and _ENGINE_ERR is None:
        try:
            _ENGINE = Engine()
        except Exception as e:
            _ENGINE_ERR = f"{type(e).__name__}: {e}"
            col.log("falha ao iniciar o painel: " + _ENGINE_ERR, "error")
    return _ENGINE


# Classe base oficial (library/sensors/sensors_custom.py). Quando o programa
# carrega sensors_custom, ele já está em sys.modules e é reutilizado; em
# execução isolada (prévia, testes) não é importado, evitando import circular.
import sys as _sys
_sc = _sys.modules.get("library.sensors.sensors_custom")
_Base = getattr(_sc, "CustomDataSource", object) if _sc else object


class MatrixGreenProPanel(_Base):
    """Sensor personalizado: a cada INTERVAL do tema, atualiza o painel inteiro."""

    def as_numeric(self):
        eng = engine()
        if eng is not None:
            try:
                from library.display import display
                eng.push(display.lcd)
            except Exception as e:
                col.log(f"erro ao atualizar a tela: {type(e).__name__}: {e}", "error")
        return math.nan

    def as_string(self):
        return ""

    def last_values(self):
        return None
