# MATRIX GREEN PRO | brusco.py | versão 1.0.0 | 07/11/2026 20:15 (-03) | criação original (Claude, para Lucas Tavares)
# Detector de mudanças bruscas para o GAMMA DELTA. Para cada leitura que muda com frequência (uso, temperatura,
# frequência, carga, potência, ventoinhas, FPS, rede e ping) mantém uma linha de base lenta (média móvel
# exponencial de 2 minutos). Quando a leitura se afasta da base mais que o limite da métrica, ela fica marcada;
# a marca continua por 10 minutos depois que a leitura volta ao normal. Cada nova marca entra no registro.
# O espaço dos discos não entra: ele muda devagar. A marca é só visual: não altera a saúde nem o N0/N1/N2.
import math
import time

TAU = 120.0                  # constante de tempo da linha de base (s)
CAUDA = 600.0                # a marca dura 10 min depois de normalizar
MAX_REG = 20                 # eventos guardados


def _rel(frac, minimo):
    """Limite relativo à base, com piso absoluto."""
    return lambda b: max(minimo, abs(b) * frac)


def _abs(x):
    return lambda b: x


def _taxa(b):
    from .viewmodel import rate
    return rate(b, short=True)


# chave: (rótulo, como ler do snapshot, limite, formato, chaves do modelo de visão que ficam marcadas)
METRICAS = {
    "cpu_util": ("CPU USO", lambda s: s["cpu"].get("util"), _abs(50), lambda x: f"{round(x)}%", ("cpu_util",)),
    "cpu_temp": ("CPU TEMP", lambda s: s["cpu"].get("temp"), _abs(12), lambda x: f"{round(x)}°C", ("cpu_temp",)),
    "cpu_ghz": ("CPU FREQ", lambda s: s["cpu"].get("ghz"), _rel(0.35, 0.8), lambda x: f"{x:.2f}GHz", ("cpu_ghz",)),
    "cpu_load": ("CARGA", lambda s: (s["cpu"].get("load") or [None])[0], _rel(1.0, 2.0), lambda x: f"{x:.1f}", ("cpu_load",)),
    "gpu_util": ("GPU USO", lambda s: s["gpu"].get("util"), _abs(50), lambda x: f"{round(x)}%", ("gpu_util",)),
    "gpu_temp": ("GPU TEMP", lambda s: s["gpu"].get("temp"), _abs(12), lambda x: f"{round(x)}°C", ("gpu_temp",)),
    "gpu_mhz": ("GPU FREQ", lambda s: s["gpu"].get("mhz"), _rel(0.4, 400), lambda x: f"{round(x)}MHz", ("gpu_mhz",)),
    "gpu_w": ("GPU W", lambda s: s["gpu"].get("power"), _abs(100), lambda x: f"{round(x)}W", ("gpu_w",)),
    "gpu_fan": ("GPU FAN", lambda s: s["gpu"].get("fan_pct"), _abs(30), lambda x: f"{round(x)}%", ("gpu_fan_pct",)),
    "fps": ("FPS", lambda s: s.get("fps"), _rel(0.5, 20), lambda x: f"{round(x)}", ("fps",)),
    "vram": ("VRAM", lambda s: (100.0 * s["gpu"]["vram_used"] / s["gpu"]["vram_total"])
             if s["gpu"].get("vram_used") is not None and s["gpu"].get("vram_total") else None,
             _abs(25), lambda x: f"{round(x)}%", ("vram_txt", "vram_pct_txt")),
    "ram": ("RAM", lambda s: s["ram"].get("pct") if s["ram"].get("total") else None, _abs(20), lambda x: f"{round(x)}%",
            ("ram_used", "ram_avail")),
    "pump": ("BOMBA", lambda s: ((s["cpu"].get("cool") or {}).get("bomba") or {}).get("rpm"), _rel(0.3, 500),
             lambda x: f"{round(x)}RPM", ("pump",)),
    "rad": ("RAD", lambda s: ((s["cpu"].get("cool") or {}).get("radiador") or {}).get("rpm"), _rel(0.4, 400),
            lambda x: f"{round(x)}RPM", ("cpu_fan",)),
    "squama": ("SQUAMA", lambda s: ((s["cpu"].get("cool") or {}).get("sq_inf") or {}).get("rpm"), _rel(0.4, 400),
               lambda x: f"{round(x)}RPM", ("fan_sqi", "fan_sql")),
    "tra": ("TRASEIRA", lambda s: ((s["cpu"].get("cool") or {}).get("sq_tras") or {}).get("rpm"), _rel(0.4, 400),
            lambda x: f"{round(x)}RPM", ("fan_sqt",)),
    "t_placa": ("PLACA", lambda s: ((s["cpu"].get("temps") or {}).get("placa") or {}).get("c"), _abs(10), lambda x: f"{round(x)}°C", ("t_placa",)),
    "t_ram": ("RAM TEMP", lambda s: ((s["cpu"].get("temps") or {}).get("ram") or {}).get("c"), _abs(8), lambda x: f"{round(x)}°C", ("t_ram",)),
    "t_ssd": ("SSD TEMP", lambda s: ((s["cpu"].get("temps") or {}).get("ssd") or {}).get("c"), _abs(10), lambda x: f"{round(x)}°C", ("t_ssd",)),
    "down": ("DOWNLOAD", lambda s: s["net"].get("down"), lambda b: max(5e6, 3 * abs(b)), _taxa, ("net_down",)),
    "up": ("UPLOAD", lambda s: s["net"].get("up"), lambda b: max(2e6, 3 * abs(b)), _taxa, ("net_up",)),
    "ping": ("PING", lambda s: s["ping"].get("ms") if s["ping"].get("ok") else None, _rel(1.0, 50), lambda x: f"{round(x)}ms", ("ping",)),
}


class Brusco:
    def __init__(self, tau=TAU, cauda=CAUDA):
        self.tau, self.cauda = tau, cauda
        self.base, self.t, self.marca = {}, {}, {}      # marca: chave -> {"desde", "fim"}
        self.registro = []                               # (instante, texto) do mais novo para o mais antigo

    def atualizar(self, s, now=None):
        """Processa um snapshot. Devolve (chaves do modelo de visão marcadas, registro)."""
        now = time.time() if now is None else now
        for k, (rot, ler, lim, fmt, _) in METRICAS.items():
            try:
                x = ler(s)
            except Exception:
                x = None
            if x is None:
                continue
            x = float(x)
            b = self.base.get(k)
            if b is None:
                self.base[k], self.t[k] = x, now
                continue
            fora = abs(x - b) >= lim(b)
            m = self.marca.get(k)
            if fora:
                if m is None:
                    self.registro.insert(0, (now, f"{rot} {fmt(b)}→{fmt(x)}"))
                    del self.registro[MAX_REG:]
                    self.marca[k] = {"desde": now, "fim": None}
                else:
                    m["fim"] = None
            elif m is not None and m["fim"] is None:
                m["fim"] = now
            a = 1.0 - math.exp(-max(0.0, now - self.t[k]) / self.tau)
            self.base[k], self.t[k] = b + a * (x - b), now
        for k in [k for k, m in self.marca.items() if m["fim"] is not None and now - m["fim"] > self.cauda]:
            del self.marca[k]
        marcadas = {vk for k in self.marca for vk in METRICAS[k][4]}
        return marcadas, list(self.registro)
