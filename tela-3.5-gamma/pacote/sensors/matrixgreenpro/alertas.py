# MATRIX GREEN PRO | alertas.py | versão 1.1.0 | 07/11/2026 21:58 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.1.0 07/11/2026 21:58 o LOG só registra âmbar e vermelho (a volta ao verde não entra)
# LOG de alertas: registra cada vez que um indicador de saúde entra em âmbar ou vermelho (a volta ao verde não
# entra), com a hora, o nome, a leitura daquele momento e a nova cor. Os níveis já chegam confirmados
# (subida só depois de 2 s, em viewmodel.py), então ruído de leitura não entra aqui.
from .alerts import OK, WARN, CRIT, LOST

MAX_REG = 20

# indicador de saúde -> (nome no LOG, chave do modelo de visão com a leitura)
NOMES = {
    "cpu_temp": ("CPU", "cpu_temp"), "cpu_uso": ("CPU USO", "cpu_util"), "carga": ("CARGA", "cpu_load"),
    "cpu_fan": ("RAD", "cpu_fan"), "pump": ("BOMBA", "pump"), "fan_sqi": ("SQUAMA", "fan_sqi"),
    "fan_sql": ("SQUAMA LAT", "fan_sql"), "fan_sqt": ("TRA", "fan_sqt"),
    "t_placa": ("PLACA", "t_placa"), "t_ram": ("RAM TEMP", "t_ram"), "t_ssd": ("NVME", "t_ssd"),
    "gpu_temp": ("GPU", "gpu_temp"), "gpu_clock": ("GPU CLOCK", "gpu_mhz"), "gpu_fan": ("GPU FAN", "gpu_fan_pct"),
    "vram": ("VRAM", "vram_pct_txt"), "ram": ("RAM", "ram_used"), "conexao": ("REDE", None),
    "ping": ("PING", "ping"), "energia": ("ENERGIA", "power"),
}
COR = {OK: "VERDE", WARN: "ÂMBAR", LOST: "ÂMBAR", CRIT: "VERMELHO"}


def _nome_valor(chave, vm):
    if chave.startswith("disk"):                               # disk0, disk0_t ...
        i = int(chave[4])
        dd = (vm.get("disks") or [{}] * 3)[i] if i < len(vm.get("disks") or []) else {}
        nome = dd.get("name", f"DISCO {i + 1}")
        if chave.endswith("_t"):
            return f"{nome} TEMP", dd.get("temp_txt", "")
        return nome, dd.get("pct_txt", "")
    nome, k = NOMES.get(chave, (chave.upper(), None))
    if k == "ram_used":
        p = vm.get("ram_pct")
        return nome, f"{round(p)}%" if p is not None else ""
    val = vm.get(k, ("", None))[0] if k else ""
    return nome, str(val).replace("RPM", "")


class Alertas:
    def __init__(self):
        self.ant = {}                                          # indicador -> último nível visto
        self.registro = []                                     # (instante, texto, nível), do mais novo ao mais antigo

    def atualizar(self, health, vm, now):
        for k, lv in health.items():
            lv = WARN if lv == LOST else lv
            if lv not in (OK, WARN, CRIT):
                continue
            a = self.ant.get(k)
            self.ant[k] = lv
            if a is None:
                if lv == OK:
                    continue                                   # início do painel: só registra o que já começa em alerta
                a = OK
            if lv != a and lv in (WARN, CRIT):
                nome, val = _nome_valor(k, vm)
                self.registro.insert(0, (now, f"{nome} {val} {COR[lv]}".replace("  ", " "), lv))
                del self.registro[MAX_REG:]
        return list(self.registro)
