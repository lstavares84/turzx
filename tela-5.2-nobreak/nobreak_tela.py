#!/usr/bin/env python3
# GAMMA NOBREAK | tela-5.2-nobreak/nobreak_tela.py | versão 0.5.0 | 21/11/2026 18:15 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 0.5.0 21/11/2026 18:15 potência real = carga do firmware x 840 W (antes: tensão x corrente da saída, que é
#            potência aparente em VA e dava 848 "W" contra 587 W reais na tomada medidora); log, médias, gráficos e
#            acumulado refeitos com a regra nova
# histórico: 0.4.0 21/11/2026 17:41 energia gasta, receita estimada da mineração e saldo, acumulados em acumulado.json
#            (continuam de onde pararam); cotação automática do dólar (AwesomeAPI, a cada 10 min, com cache);
#            MINERANDO pisca
# histórico: 0.3.0 21/11/2026 10:44 histórico retomado do log ao reiniciar; gráficos por tempo (sem dado = em branco);
#            mínimo, média e máximo do dia e faixa de operação de cada variável (ANEEL PRODIST e fabricante);
#            classificação da rede (adequada, precária, crítica) e tempo do dia em cada faixa
# histórico: 0.2.0 21/11/2026 10:31 tag MINERANDO pelo processo do minerador; dados separados por minerando ou não
# histórico: 0.1.0 21/11/2026 10:17 criação: tela de 5,2" em paisagem só com o nobreak Ragtech 4162, log em CSV
#
# Tela exclusiva do nobreak na TURZX / Turing de 5,2" (720x1280, revisão TUR_USB, USB 1cbe:0050), em PAISAGEM
# (1280x720). A cada ciclo (padrão 1 s): lê o nobreak, grava uma linha no CSV do dia, desenha o quadro e envia.
#   leitura: ragtech_read.py do repositório ragtech_4162 (somente leitura, protocolo do driver "ragtech" do NUT);
#            este programa NUNCA envia comando de escrita ao nobreak, só usa a função poll() do leitor.
#   tela:    biblioteca do turing-smart-screen-python (LcdCommTuringUSB), sem uma segunda instância do programa.
#   faixas:  rede elétrica pela ANEEL, PRODIST Módulo 8 (Anexo VIII da REN 956/2021): tensão de atendimento
#            (Anexo 8.A, tabelas 4 e 5) e frequência (itens 65 e 66); saída, potência e carga pelo fabricante
#            (fichas do Ragtech NEP 1200, modelo 4162: saída 115 V +/- 2 %, 1200 VA / 840 W). A classificação
#            aqui é da leitura instantânea, indicativa: a apuração oficial da ANEEL usa médias de 10 minutos.
#   alarmes: os do próprio nobreak também decidem âmbar e vermelho.
#   log:     ~/.local/state/nobreak/nobreak-AAAA-MM-DD.csv (uma linha por leitura) e nobreak-eventos.log.
#            Ao reiniciar, o dia (mínimos, médias, máximos, tempos, quedas) e os últimos 15 min dos gráficos
#            voltam do log; o período desligado ou sem leitura fica em branco nos gráficos.
#   dinheiro: acumulado desde a primeira execução em ~/.local/state/nobreak/acumulado.json (gravado a cada 30 s e
#            ao sair; ao iniciar, continua de onde parou). Gasto = energia medida na saída do nobreak enquanto minera
#            x tarifa; gerado = receita ESTIMADA pelo hashrate do SRBMiner (receita de referência por dia a um
#            hashrate de referência), o mesmo modelo do painel do chat da mineração; tarifa, receita de referência e
#            câmbio de reserva vêm de ~/mineracao/painel.conf. Saldo = gerado - gasto. O dólar vem da AwesomeAPI
#            (economia.awesomeapi.com.br, gratuita, com atraso de alguns minutos), consultada a cada 10 min.
#   mineração: o computador está minerando quando um processo da lista MINERADORES está rodando (nome do processo
#            ou do executável, sem diferenciar maiúsculas). A lista muda com --mineradores ou NOBREAK_MINERADORES.
# Uso:
#   python3 nobreak_tela.py                      tela + log (o serviço systemd roda assim)
#   python3 nobreak_tela.py --previa saida.png   desenha um quadro com o log de hoje e sai (não usa a tela nem a porta)
#   python3 nobreak_tela.py --demo --previa x.png quadro com dados de demonstração
#   python3 nobreak_tela.py --sem-tela           só lê e grava o log
import argparse
import collections
import csv
import glob
import importlib.util
import json
import math
import os
import random
import re
import sys
import threading
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault("TZ", "America/Sao_Paulo")
time.tzset()

RAIZ_GITHUB = Path(__file__).resolve().parents[2]
LEITOR_PADRAO = RAIZ_GITHUB / "ragtech_4162" / "ragtech_read.py"
TURING_PADRAO = Path.home() / "Documentos" / "Projetos" / "turing-smart-screen-linux"
ESTADO = Path(os.environ.get("NOBREAK_ESTADO", Path.home() / ".local" / "state" / "nobreak"))
W, H = 1280, 720
JANELA_S = 900                    # janela dos gráficos: 15 minutos
LACUNA_S = 5                      # sem leitura por mais que isso: o gráfico fica em branco nesse trecho

# paleta GAMMA (a mesma do tema da tela de 3,5")
BG, PAINEL, LINHA = (3, 10, 4), (8, 22, 10), (35, 75, 35)
VERDE, GELO, BRANCO, SUB = (120, 255, 90), (190, 255, 170), (230, 255, 225), (110, 170, 110)
AMBAR, VERMELHO, CINZA = (255, 190, 0), (255, 60, 50), (70, 95, 70)

# processos de mineração reconhecidos (nomes usuais dos mineradores, inclusive os que o Kryptex usa por baixo)
MINERADORES = ["kryptex", "xmrig", "lolminer", "gminer", "t-rex", "nbminer", "teamredminer", "srbminer-multi",
               "bzminer", "rigel", "onezerominer", "nanominer", "excavator", "ethminer", "wildrig"]

# alarmes do próprio nobreak (texto do ragtech_read.py) -> nível
CRITICOS = {"bateria esgotada", "sobrecarga", "saida anormal", "falha inversor", "curto-circuito", "superaquecimento",
            "sem bateria"}
AVISOS = {"bateria fraca", "bateria velha", "bateria anormal", "rede baixa", "rede alta", "sem rede", "autoteste"}

# ---- faixas de operação
# ANEEL, PRODIST Módulo 8, Anexo 8.A, tabelas 4 (220/127) e 5 (380/220): tensão de leitura em volts
PRODIST_TENSAO = {220: {"adequada": (202, 231), "precaria": (191, 233)},
                  127: {"adequada": (117, 133), "precaria": (110, 135)}}
PRODIST_FREQ = {"normal": (59.9, 60.1), "disturbio": (59.5, 60.5)}     # itens 65 e 66
FAB_SAIDA_V = (115 * 0.98, 115 * 1.02)                                # saída 115 V, regulação +/- 2 %
FAB_POTENCIA_W, FAB_CARGA = 840, 100                                  # 1200 VA / 840 W


def potencia_real(d):
    """Potência real (W) consumida pela saída do nobreak: a carga que o firmware informa (% de 840 W).
    Tensão x corrente da saída é potência APARENTE (VA): em 21/11/2026 18:05 dava 848 VA, enquanto a tomada
    medidora na parede marcava 587 W e o firmware 68,8% x 840 = 578 W (a diferença de 1,6% são as perdas do
    nobreak). Sem a carga do firmware, fica a aparente (o valor de antes), que superestima o consumo."""
    fw = d.get("carga_fw_%")
    if fw is not None and fw >= 0:
        return round(float(fw) * FAB_POTENCIA_W / 100.0, 1)
    return round(d["saida_V"] * d["saida_A"], 1)
PAINEL_CONF = Path.home() / "mineracao" / "painel.conf"            # tarifa, receita de referência e câmbio de reserva
LOG_MINERADOR = str(Path.home() / "mineracao" / "logs" / "mineracao_*.log")
URL_COTACAO = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
COTACAO_S = 600                                                    # consulta o dólar a cada 10 min
VARS = ("entrada_V", "saida_V", "freq_Hz", "saida_A", "potencia_W", "carga_%", "bateria_%", "bateria_V", "temp_C")


def ts():
    return time.strftime("%d/%m/%Y %H:%M:%S")


def log(msg):
    print(f"[{ts()}] {msg}", flush=True)


def classe_rede(v, nominal):
    f = PRODIST_TENSAO[nominal]
    if f["adequada"][0] <= v <= f["adequada"][1]:
        return "adequada"
    if f["precaria"][0] <= v <= f["precaria"][1]:
        return "precaria"
    return "critica"


def classe_freq(f):
    if PRODIST_FREQ["normal"][0] <= f <= PRODIST_FREQ["normal"][1]:
        return "normal"
    if PRODIST_FREQ["disturbio"][0] <= f <= PRODIST_FREQ["disturbio"][1]:
        return "fora"
    return "critica"


COR_CLASSE = {"adequada": VERDE, "precaria": AMBAR, "critica": VERMELHO, "normal": VERDE, "fora": AMBAR}
NOME_CLASSE = {"adequada": "ADEQUADA", "precaria": "PRECÁRIA", "critica": "CRÍTICA", "normal": "NORMAL",
               "fora": "FORA"}


# ---------------------------------------------------------------- leitura
class Nobreak:
    def __init__(self, leitor, va=None):
        spec = importlib.util.spec_from_file_location("ragtech_read", leitor)
        self.rt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.rt)
        self.va, self.fd, self.modelo = va, None, None

    def ler(self):
        try:
            if self.fd is None:
                portas = sorted(Path("/dev/serial/by-id").glob("*Ragtech*"))
                if not portas:
                    return None, "nobreak não encontrado em /dev/serial/by-id"
                self.fd = self.rt.open_port(os.path.realpath(portas[0]))
            d, _ = self.rt.poll(self.fd, self.va)
            if not d:
                return None, "sem resposta do nobreak"
            # resposta embaralhada (por exemplo, dois programas lendo a porta ao mesmo tempo): o código do modelo
            # vem fora da tabela do leitor ou muda de uma leitura para outra; descarta em vez de gravar lixo
            if d["modelo"] == "Desconhecido" or (self.modelo is not None and d["modelo_id"] != self.modelo):
                return None, f"resposta inválida do nobreak (modelo {d['modelo_id']})"
            self.modelo = d["modelo_id"]
            return d, None
        except Exception as e:                       # cabo solto, porta ocupada: reabre no próximo ciclo
            self.fechar()
            return None, f"{type(e).__name__}: {e}"

    def fechar(self):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
        self.fd = None


class Demo:
    """Dados de demonstração: rede de 220 V, mineração no meio da janela, uma queda de energia e 1 min desligado."""

    def __init__(self):
        self.t, self.minerando = 0, False

    def ler(self):
        self.t += 1
        ob = 380 < self.t < 470
        self.minerando = 150 < self.t < 640
        vin = 0.0 if ob else 214 + 6 * math.sin(self.t / 40) + random.uniform(-0.8, 0.8)
        a = 1.9 + 0.5 * math.sin(self.t / 25) + random.uniform(-0.05, 0.05) + (2.4 if self.minerando else 0)
        bat = 100.0 if not ob else 100 - (self.t - 380) * 0.2
        d = {"modelo_id": 6, "modelo": "Easy 1200 TI", "firmware": 1.4,
             "entrada_V": round(vin, 1), "saida_V": round(115 + random.uniform(-0.4, 0.4), 1), "saida_A": round(a, 2),
             "carga_%": round(115 * a / 1200 * 100, 1), "carga_fw_%": round(115 * a / 1200 * 100),
             "freq_Hz": round(60 + random.uniform(-0.05, 0.05), 2), "bateria_%": round(bat, 1),
             "bateria_V": round(13.6 if not ob else 12.6 - (100 - bat) * 0.02, 2), "temp_C": 31,
             "status": "OB (bateria); sem rede" if ob else "OL (rede)"}
        return d, None

    def fechar(self):
        pass


class Mineracao:
    """Diz se algum minerador da lista está rodando, olhando /proc (nome do processo e do executável)."""

    def __init__(self, nomes):
        self.nomes = [n.strip().lower() for n in nomes if n.strip()]
        self.qual = ""

    def ativa(self):
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                comm = Path(f"/proc/{pid}/comm").read_text().strip().lower()
                arg0 = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")[0].decode(errors="ignore")
            except OSError:
                continue
            exe = os.path.basename(arg0).lower()
            for n in self.nomes:
                if comm == n[:15] or exe == n or exe.startswith(n + ".") or exe.startswith(n + "-"):
                    self.qual = os.path.basename(arg0) or comm
                    return True
        self.qual = ""
        return False


# ---------------------------------------------------------------- dinheiro: tarifa, receita, cotação e acumulado
def ler_painel_conf(p=PAINEL_CONF):
    """CHAVE=VALOR do painel.conf do chat da mineração (só os números usados aqui)."""
    cfg = {"TARIFA_BRL_KWH": None, "RECEITA_USD_DIA_REF": None, "HASH_REF_THS": None, "USD_BRL": None}
    try:
        for linha in Path(p).read_text(encoding="utf-8").splitlines():
            linha = linha.split("#", 1)[0].strip()
            if "=" in linha:
                k, v = (x.strip() for x in linha.split("=", 1))
                if k in cfg and v:
                    cfg[k] = float(v.replace(",", "."))
    except (OSError, ValueError):
        pass
    return cfg


_SRB_GPU = re.compile(r"\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\]\s+#0\s+.+?\s+([\d.]+)\s+([kMGTP]?)H/s\s+([\d.]+)W")
_MULT = {"": 1e-12, "k": 1e-9, "M": 1e-6, "G": 1e-3, "T": 1.0, "P": 1e3}       # -> TH/s


class Hashrate:
    """Último hashrate do SRBMiner-MULTI lido do próprio log (tabela "#0 ... 192.58 TH/s 249.8W" a cada 30 s)."""

    def __init__(self, padrao=LOG_MINERADOR):
        self.padrao, self.ths, self.t, self.lido = padrao, None, 0.0, 0.0

    def atual(self, agora):
        if agora - self.lido >= 10:                      # relê o fim do log a cada 10 s
            self.lido = agora
            arqs = sorted(glob.glob(self.padrao), key=os.path.getmtime)
            if arqs:
                try:
                    with open(arqs[-1], "rb") as f:
                        f.seek(max(0, os.path.getsize(arqs[-1]) - 200_000))
                        texto = f.read().decode(errors="ignore")
                    for m in _SRB_GPU.finditer(re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", texto)):
                        self.t = time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"))
                        self.ths = float(m.group(2)) * _MULT[m.group(3)]
                except OSError:
                    pass
        return self.ths if self.ths is not None and agora - self.t <= 120 else None   # velho = não conta


class Cotacao:
    """Dólar comercial (venda) da AwesomeAPI, consultado em segundo plano a cada 10 min, com cache em arquivo.
    Sem internet: usa o último valor guardado; sem nada guardado: o câmbio fixo do painel.conf."""

    def __init__(self, pasta, reserva=None, consulta=True):
        self.arq = Path(pasta) / "cotacao.json"
        self.valor, self.hora, self.fonte = reserva, None, "painel.conf (fixo)" if reserva else ""
        try:
            c = json.loads(self.arq.read_text(encoding="utf-8"))
            self.valor, self.hora, self.fonte = c["valor"], c["hora"], c["fonte"]
        except (OSError, ValueError, KeyError):
            pass
        if consulta:
            threading.Thread(target=self._laco, daemon=True).start()

    def _laco(self):
        while True:
            try:
                req = urllib.request.Request(URL_COTACAO, headers={"User-Agent": "gamma-nobreak/0.4"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    c = json.loads(r.read().decode())["USDBRL"]
                self.valor = float(c["bid"])
                self.hora = int(c.get("timestamp") or time.time())
                self.fonte = "AwesomeAPI"
                tmp = self.arq.with_suffix(".tmp")
                tmp.write_text(json.dumps({"valor": self.valor, "hora": self.hora, "fonte": self.fonte}), encoding="utf-8")
                tmp.replace(self.arq)
            except Exception as e:
                log(f"cotação do dólar indisponível: {type(e).__name__}: {e}")
            time.sleep(COTACAO_S)


class Financas:
    """Energia, gasto, receita estimada e saldo acumulados desde a primeira execução (acumulado.json)."""

    def __init__(self, pasta, gravar=True):
        self.arq, self.gravar = Path(pasta) / "acumulado.json", gravar
        self.a = {"desde": time.time(), "kwh_total": 0.0, "brl_total": 0.0, "kwh_min": 0.0, "brl_min": 0.0,
                  "usd_receita": 0.0, "s_min": 0.0}
        try:
            self.a.update(json.loads(self.arq.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
        self.cfg, self.cfg_t, self.salvo_t = ler_painel_conf(), time.time(), 0.0
        if self.a.get("potencia") != "carga_fw" and self.gravar:
            self.recalcular_energia()

    def recalcular_energia(self):
        """Uma vez só: refaz energia e gasto acumulados com a potência real, a partir dos CSV desde 'desde'
        (o acumulado antigo usava a potência aparente). A receita estimada não muda."""
        tarifa = self.cfg["TARIFA_BRL_KWH"] or 0.0
        k_tot = k_min = 0.0
        dia = time.strftime("%Y-%m-%d", time.localtime(self.a["desde"]))
        hoje = time.strftime("%Y-%m-%d")
        t_ant = None
        while dia <= hoje:
            p = self.arq.parent / f"nobreak-{dia}.csv"
            try:
                with open(p, newline="", encoding="utf-8") as f:
                    for r in csv.DictReader(f, delimiter=";"):
                        try:
                            t = time.mktime(time.strptime(r["data_hora"], "%d/%m/%Y %H:%M:%S"))
                            w = potencia_real({"carga_fw_%": float(r["carga_fw_%"]), "saida_V": float(r["saida_V"]),
                                               "saida_A": float(r["saida_A"])})
                        except (ValueError, KeyError):
                            continue
                        if t >= self.a["desde"] and t_ant is not None and 0 < t - t_ant <= LACUNA_S:
                            kwh = w * (t - t_ant) / 3.6e6
                            k_tot += kwh
                            if r.get("minerando") == "sim":
                                k_min += kwh
                        t_ant = t
            except OSError:
                pass
            dia = time.strftime("%Y-%m-%d", time.localtime(time.mktime(time.strptime(dia, "%Y-%m-%d")) + 86400 + 3600))
        log(f"acumulado refeito com a potência real: {self.a['kwh_total']:.3f} -> {k_tot:.3f} kWh "
            f"(minerando {self.a['kwh_min']:.3f} -> {k_min:.3f} kWh)")
        self.a.update(kwh_total=k_tot, brl_total=k_tot * tarifa, kwh_min=k_min, brl_min=k_min * tarifa, potencia="carga_fw")
        self.salvar()

    def somar(self, potencia_w, minerando, ths, dt, agora):
        if agora - self.cfg_t > 60:                      # o painel.conf pode mudar (tarifa, referência)
            self.cfg, self.cfg_t = ler_painel_conf(), agora
        tarifa = self.cfg["TARIFA_BRL_KWH"] or 0.0
        kwh = potencia_w * dt / 3.6e6
        self.a["kwh_total"] += kwh
        self.a["brl_total"] += kwh * tarifa
        if minerando:
            self.a["kwh_min"] += kwh
            self.a["brl_min"] += kwh * tarifa
            self.a["s_min"] += dt
            ref, href = self.cfg["RECEITA_USD_DIA_REF"], self.cfg["HASH_REF_THS"]
            if ths and ref and href:
                self.a["usd_receita"] += ths / href * ref / 86400 * dt
        if agora - self.salvo_t >= 30:
            self.salvar(agora)

    def salvar(self, agora=None):
        if not self.gravar:
            return
        self.salvo_t = agora or time.time()
        tmp = self.arq.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.a, indent=1), encoding="utf-8")
        tmp.replace(self.arq)                            # troca atômica: nunca fica um arquivo pela metade


# ---------------------------------------------------------------- estado do dia, eventos e log
class Registro:
    CAMPOS = ["data_hora", "minerando", "entrada_V", "saida_V", "saida_A", "potencia_W", "carga_%", "carga_fw_%",
              "freq_Hz", "bateria_%", "bateria_V", "temp_C", "status", "modelo", "firmware"]
    COMPARAR = ("potencia_W", "carga_%", "saida_A", "temp_C", "entrada_V")

    def __init__(self, pasta, nominal=220, gravar=True, retomar=True):
        self.pasta = Path(pasta)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.nominal, self.gravar = nominal, gravar
        self.hist = collections.deque()                 # (instante, leitura) dos últimos 15 min
        self.eventos = collections.deque(maxlen=7)
        self.flags_ant, self.min_ant, self.ob_desde, self.ultima_queda = None, None, None, None
        self.t_ant, self.leituras, self.falhas = None, 0, 0
        self._zerar_dia(time.strftime("%Y-%m-%d"))
        self._carregar_eventos()
        if retomar:
            self._retomar()

    def _zerar_dia(self, dia):
        self.dia, self.quedas, self.s_bateria = dia, 0, 0.0
        self.st = {}                                    # variável -> [mínimo, máximo, soma, quantidade]
        self.cmp = {True: {}, False: {}}                # somas do dia por categoria: minerando e sem mineração
        self.s_classe = {"adequada": 0.0, "precaria": 0.0, "critica": 0.0}
        self.leituras = 0

    # ---- somas
    def _dt(self, t):
        if self.t_ant is None:
            return 1.0
        gap = t - self.t_ant
        return gap if 0 < gap <= LACUNA_S else 1.0      # desligado não conta como tempo medido

    def _acumular(self, d, minerando, dt):
        ob = d["status"].startswith("OB")
        for k in VARS:
            if k == "entrada_V" and ob:                 # sem rede a entrada lê 0: não entra nas estatísticas
                continue
            v = float(d[k])
            s = self.st.setdefault(k, [v, v, 0.0, 0])
            s[0], s[1], s[2], s[3] = min(s[0], v), max(s[1], v), s[2] + v, s[3] + 1
        c = self.cmp[minerando]
        c["s"] = c.get("s", 0.0) + dt
        for k in self.COMPARAR:
            if k == "entrada_V" and ob:
                continue
            c[k] = c.get(k, 0.0) + float(d[k])
            c[k + "#"] = c.get(k + "#", 0) + 1
        c["pico"] = max(c.get("pico", 0.0), float(d["potencia_W"]))
        if ob:
            self.s_bateria += dt
        else:
            self.s_classe[classe_rede(float(d["entrada_V"]), self.nominal)] += dt
        self.leituras += 1

    def media(self, minerando, k):
        c = self.cmp[minerando]
        return c[k] / c[k + "#"] if c.get(k + "#") else None

    def estat(self, k):
        s = self.st.get(k)
        return (s[0], s[2] / s[3], s[1]) if s and s[3] else None

    # ---- retomada depois de reiniciar
    def _ler_csv(self, p):
        try:
            with open(p, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f, delimiter=";"):
                    if "minerando" not in r:
                        return
                    try:
                        t = time.mktime(time.strptime(r["data_hora"], "%d/%m/%Y %H:%M:%S"))
                        d = {k: float(r[k]) for k in VARS if k in r}
                        d.update(status=r["status"], modelo=r["modelo"], firmware=r["firmware"],
                                 minerando=r["minerando"], **{"carga_fw_%": float(r["carga_fw_%"])})
                        d["potencia_W"] = potencia_real(d)       # linhas antigas guardaram a aparente (VA)
                    except (ValueError, KeyError):
                        continue
                    yield t, d
        except OSError:
            return

    def _retomar(self):
        agora = time.time()
        ontem = time.strftime("%Y-%m-%d", time.localtime(agora - 86400))
        for t, d in self._ler_csv(self.pasta / f"nobreak-{ontem}.csv"):     # só para a janela dos gráficos
            if t >= agora - JANELA_S:
                self.hist.append((t, d))
        for t, d in self._ler_csv(self.pasta / f"nobreak-{self.dia}.csv"):
            self._acumular(d, d["minerando"] == "sim", self._dt(t))
            self.t_ant = t
            if t >= agora - JANELA_S:
                self.hist.append((t, d))
        self.t_ant = None                                 # a primeira leitura nova não soma o tempo desligado
        ev = self.pasta / "nobreak-eventos.log"
        if ev.exists():
            hoje = time.strftime("%d/%m/%Y")
            for linha in ev.read_text(encoding="utf-8").splitlines():
                if linha.startswith(hoje) and "FOI PARA A BATERIA" in linha:
                    self.quedas += 1
                    self.ultima_queda = time.mktime(time.strptime(linha[:19], "%d/%m/%Y %H:%M:%S"))
        if self.leituras:
            log(f"dia retomado do log: {self.leituras} leituras, {len(self.hist)} pontos nos gráficos")

    def _carregar_eventos(self):
        p = self.pasta / "nobreak-eventos.log"
        if p.exists():
            for linha in p.read_text(encoding="utf-8").splitlines()[-7:]:
                self.eventos.append(linha)

    def evento(self, texto, t=None):
        linha = f"{time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(t or time.time()))} {texto}"
        self.eventos.append(linha)
        if self.gravar:
            with open(self.pasta / "nobreak-eventos.log", "a", encoding="utf-8") as f:
                f.write(linha + "\n")
            log(f"evento: {texto}")

    def falha(self, motivo):
        self.falhas += 1
        if self.flags_ant != "FALHA":
            self.evento(f"LEITURA FALHOU: {motivo}")
            self.flags_ant = "FALHA"

    def anotar(self, d, minerando=False, qual="", agora=None):
        agora = agora or time.time()
        hoje = time.strftime("%Y-%m-%d", time.localtime(agora))
        if hoje != self.dia:                              # virada do dia: zera as somas do dia
            self._zerar_dia(hoje)
        d = dict(d)
        d["potencia_W"] = potencia_real(d)
        d["minerando"] = "sim" if minerando else "não"
        if self.min_ant is not None and minerando != self.min_ant:
            self.evento(f"COMEÇOU A MINERAR ({qual}, {d['potencia_W']:.0f} W)" if minerando
                        else f"PAROU DE MINERAR ({d['potencia_W']:.0f} W)", agora)
        self.min_ant = minerando
        ob = d["status"].startswith("OB")
        flags = tuple(sorted(x.strip() for x in d["status"].split(";")[1:] if x.strip()))
        estado = ("OB" if ob else "OL",) + flags
        if self.flags_ant is not None and estado != self.flags_ant:
            ant = set(self.flags_ant[1:]) if self.flags_ant != "FALHA" else set()
            if self.flags_ant == "FALHA":
                self.evento("leitura voltou", agora)
            if ob and (self.flags_ant == "FALHA" or self.flags_ant[0] != "OB"):
                self.evento(f"FOI PARA A BATERIA (entrada {d['entrada_V']} V, bateria {d['bateria_%']}%)", agora)
            elif not ob and self.flags_ant != "FALHA" and self.flags_ant[0] == "OB":
                dur = agora - self.ob_desde if self.ob_desde else 0
                self.evento(f"VOLTOU PARA A REDE depois de {_dur(dur)} (bateria {d['bateria_%']}%)", agora)
            for f in sorted(set(flags) - ant):
                self.evento(f"alarme: {f}", agora)
            for f in sorted(ant - set(flags)):
                self.evento(f"alarme encerrado: {f}", agora)
        if ob and self.ob_desde is None:
            self.ob_desde = agora
            self.quedas += 1
            self.ultima_queda = agora
        if not ob:
            self.ob_desde = None
        self._acumular(d, minerando, self._dt(agora))
        self.flags_ant, self.t_ant = estado, agora
        self.hist.append((agora, d))
        while self.hist and self.hist[0][0] < agora - JANELA_S:
            self.hist.popleft()
        if self.gravar:
            self._csv(d, agora)
        return d

    def _csv(self, d, agora):
        p = self.pasta / f"nobreak-{self.dia}.csv"
        if p.exists():                                    # CSV de uma versão anterior (sem a coluna minerando)
            with open(p, encoding="utf-8") as f:
                if f.readline().strip().split(";") != self.CAMPOS:
                    p.rename(p.with_name(p.stem + "-sem-mineracao.csv"))
        novo = not p.exists()
        with open(p, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            if novo:
                w.writerow(self.CAMPOS)
            w.writerow([time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(agora))] +
                       [d.get(k, "") for k in self.CAMPOS[1:]])


def _dur(s):
    s = int(s)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}min{s % 60:02d}s"
    return f"{s // 3600}h{s % 3600 // 60:02d}min"


def _n(x, casas=1):
    """Número com vírgula decimal."""
    return f"{x:.{casas}f}".replace(".", ",")


# ---------------------------------------------------------------- desenho
class Fontes:
    def __init__(self, turing):
        r = Path(turing) / "res" / "fonts"
        self.jb = str(r / "jetbrains-mono" / "JetBrainsMonoNL-{}.ttf")
        self.rb = str(r / "roboto" / "Roboto-{}.ttf")
        self.cache = {}

    def __call__(self, fam, tam, peso="Bold"):
        k = (fam, tam, peso)
        if k not in self.cache:
            self.cache[k] = ImageFont.truetype((self.jb if fam == "jb" else self.rb).format(peso), tam)
        return self.cache[k]


def _nivel(flags):
    if any(f in CRITICOS for f in flags):
        return VERMELHO
    if any(f in AVISOS for f in flags):
        return AMBAR
    return None


def _dinheiro(x, moeda="R$", casas=2):
    """1234.5 -> 'R$ 1.234,50' (padrão brasileiro); negativo com sinal na frente."""
    if x is None:
        return f"{moeda} --"
    s = f"{abs(x):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{'-' if x < 0 else ''}{moeda} {s}"


def desenhar(reg, F, ultimo, erro, intervalo, minerando=False, qual="", agora=None, fin=None, cot=None, ths=None):
    agora = agora or time.time()
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    txt = lambda xy, s, f, c, a="ls": dr.text(xy, s, font=f, fill=c, anchor=a)

    def cabe(s, f, w):
        while s and dr.textlength(s, font=f) > w:
            s = s[:-1]
        return s

    d = ultimo
    flags = [x.strip() for x in d["status"].split(";")[1:] if x.strip()] if d else []
    ob = bool(d) and d["status"].startswith("OB")
    alerta = _nivel(flags)
    cls_in = classe_rede(d["entrada_V"], reg.nominal) if d and not ob else None
    cls_f = classe_freq(d["freq_Hz"]) if d else None

    # ---- cabeçalho: título, mineração, estado da rede, relógio
    txt((20, 46), "NOBREAK", F("jb", 34), VERDE)
    tx0, tx1 = 220, 520
    aceso = int(agora) % 2 == 0                      # MINERANDO pisca: 1 s aceso, 1 s apagado (esmaecido)
    cor_m = (GELO if aceso else (60, 95, 60)) if minerando else CINZA
    dr.rounded_rectangle((tx0, 10, tx1, 60), 8, fill=(18, 52, 22) if minerando and aceso else BG, outline=cor_m, width=3)
    txt(((tx0 + tx1) // 2, 46), "MINERANDO" if minerando else "SEM MINERAÇÃO", F("jb", 28), cor_m, "ms")
    if not d:
        cor_st, rot = VERMELHO, "SEM LEITURA"
    elif ob:
        cor_st, rot = AMBAR, "NA BATERIA"
    else:
        cor_st, rot = COR_CLASSE[cls_in], f"REDE {NOME_CLASSE[cls_in]}"
    if alerta == VERMELHO:
        cor_st = VERMELHO
    bx0, bx1 = 540, 960
    dr.rounded_rectangle((bx0, 10, bx1, 60), 8, fill=tuple(int(c * 0.25) for c in cor_st), outline=cor_st, width=3)
    txt(((bx0 + bx1) // 2, 47), rot, F("jb", 30), cor_st, "ms")
    txt((1260, 44), time.strftime("%H:%M:%S", time.localtime(agora)), F("jb", 34), VERDE, "rs")
    txt((1260, 64), time.strftime("%d/%m/%Y", time.localtime(agora)), F("jb", 14, "Regular"), SUB, "rs")
    dr.line((0, 72, W, 72), fill=LINHA, width=2)

    # ---- blocos: valor, mínimo / média / máximo do dia e a faixa de operação
    def bloco(x, y, w, h, rotulo, k, unid, casas=1, cor=BRANCO, faixa="", situ=None, pct=None, valor=None):
        dr.rounded_rectangle((x, y, x + w, y + h), 10, fill=PAINEL, outline=LINHA, width=2)
        txt((x + 14, y + 27), rotulo, F("rb", 19), SUB)
        if situ:
            txt((x + w - 12, y + 25), situ[0], F("jb", 13), situ[1], "rs")
        valor = valor if valor is not None else (_n(d[k], casas) if d else "--")
        fu = F("jb", 22)
        for tam in (56, 50, 44, 38):                       # o número diminui até caber com a unidade
            f = F("jb", tam)
            if dr.textlength(valor, font=f) + 6 + dr.textlength(unid, font=fu) <= w - 28:
                break
        b = dr.textbbox((x + 14, y + 84), valor, font=f, anchor="ls")
        txt((x + 14, y + 84), valor, f, cor)
        txt((b[2] + 6, y + 84), unid, fu, SUB)
        if pct is not None:
            bw = w - 28
            dr.rectangle((x + 14, y + 92, x + 14 + bw, y + 98), fill=(16, 40, 18))
            fw = int(bw * max(0, min(100, pct)) / 100)
            if fw:
                dr.rectangle((x + 14, y + 92, x + 14 + fw, y + 98), fill=cor if cor != BRANCO else VERDE)
        e = reg.estat(k) if k else None
        fl, fv = F("rb", 12), F("jb", 15)
        cols = (x + 14, x + w / 2, x + w - 14)
        for (c, anc), nome in zip(((cols[0], "ls"), (cols[1], "ms"), (cols[2], "rs")), ("mín", "média", "máx")):
            txt((c, y + 114), nome, fl, SUB, anc)
        if e:
            for (c, anc), val in zip(((cols[0], "ls"), (cols[1], "ms"), (cols[2], "rs")), e):
                txt((c, y + 132), _n(val, casas), fv, BRANCO, anc)
        else:
            txt((cols[1], y + 132), "sem dados hoje", fv, SUB, "ms")
        fx = F("jb", 13, "Regular")
        txt((x + 14, y + h - 9), cabe(faixa or "sem faixa", fx, w - 28), fx, SUB if faixa else CINZA)

    y1, h1, w1, g = 82, 162, 199, 12
    nominal = reg.nominal
    pt = PRODIST_TENSAO[nominal]["adequada"]
    sit_in = (NOME_CLASSE[cls_in], COR_CLASSE[cls_in]) if cls_in else (("SEM REDE", AMBAR) if ob else None)
    cor_in = COR_CLASSE[cls_in] if cls_in and cls_in != "adequada" else (AMBAR if ob else BRANCO)
    bloco(20, y1, w1, h1, "ENTRADA", "entrada_V", "V", 1, cor_in, f"ANEEL {pt[0]} a {pt[1]} V", sit_in)
    sv = d["saida_V"] if d else None
    fora_s = sv is not None and not (FAB_SAIDA_V[0] <= sv <= FAB_SAIDA_V[1])
    bloco(20 + (w1 + g), y1, w1, h1, "SAÍDA", "saida_V", "V", 1, AMBAR if fora_s else BRANCO,
          f"fabr. {_n(FAB_SAIDA_V[0])} a {_n(FAB_SAIDA_V[1])} V",
          (("FORA", AMBAR) if fora_s else ("OK", VERDE)) if d else None)
    pf = PRODIST_FREQ["normal"]
    bloco(20 + 2 * (w1 + g), y1, w1, h1, "FREQUÊNCIA", "freq_Hz", "Hz", 2,
          COR_CLASSE[cls_f] if cls_f and cls_f != "normal" else BRANCO, f"ANEEL {_n(pf[0])} a {_n(pf[1])} Hz",
          (NOME_CLASSE[cls_f], COR_CLASSE[cls_f]) if cls_f else None)
    bloco(20 + 3 * (w1 + g), y1, w1, h1, "CORRENTE", "saida_A", "A", 2, BRANCO,
          f"{_n(d['saida_V'] * d['saida_A'], 0)} VA de 1200 VA" if d else "")
    pw = d["potencia_W"] if d else None
    cor_p = VERMELHO if (pw and pw > FAB_POTENCIA_W) or "sobrecarga" in flags else BRANCO
    bloco(20 + 4 * (w1 + g), y1, w1, h1, "POTÊNCIA", "potencia_W", "W", 0, cor_p, f"fabr. até {FAB_POTENCIA_W} W",
          (("ACIMA", VERMELHO) if cor_p == VERMELHO else ("OK", VERDE)) if d else None)
    cg = d["carga_%"] if d else None
    cor_c = VERMELHO if (cg and cg > FAB_CARGA) or "sobrecarga" in flags else BRANCO
    bloco(20 + 5 * (w1 + g), y1, w1, h1, "CARGA", "carga_%", "%", 0, cor_c,
          f"fabr. até {FAB_CARGA}%", (f"FW {d['carga_fw_%']:.0f}%", SUB) if d else None, pct=cg)

    # ---- linha 2: bateria, temperatura, rede no dia e médias por mineração
    y2, h2 = 256, 162
    cor_bat = VERMELHO if {"bateria esgotada", "sem bateria"} & set(flags) else \
        AMBAR if {"bateria fraca", "bateria anormal", "bateria velha"} & set(flags) or ob else VERDE
    bloco(20, y2, 260, h2, "BATERIA", "bateria_%", "%", 0, cor_bat,
          (f"agora {_n(d['bateria_V'], 2)} V | 12 V 7 Ah" if d else "12 V 7 Ah"), pct=d["bateria_%"] if d else None)
    bloco(292, y2, 199, h2, "BATERIA V", "bateria_V", "V", 2, BRANCO, "")
    bloco(503, y2, 160, h2, "TEMP.", "temp_C", "°C", 0, VERMELHO if "superaquecimento" in flags else BRANCO, "")

    x3, x4 = 675, 960
    dr.rounded_rectangle((x3, y2, x4 - 12, y2 + h2), 10, fill=PAINEL, outline=LINHA, width=2)
    txt((x3 + 14, y2 + 27), "REDE HOJE", F("rb", 19), SUB)
    total = sum(reg.s_classe.values()) + reg.s_bateria
    pctc = lambda s: f"{100 * s / total:.1f}%".replace(".", ",") if total else "--"
    linhas = [("adequada", pctc(reg.s_classe["adequada"]), VERDE),
              ("precária", pctc(reg.s_classe["precaria"]), AMBAR if reg.s_classe["precaria"] else BRANCO),
              ("crítica", pctc(reg.s_classe["critica"]), VERMELHO if reg.s_classe["critica"] else BRANCO),
              ("quedas", (f"{reg.quedas} às {time.strftime('%H:%M', time.localtime(reg.ultima_queda))}"
                          if reg.ultima_queda else "nenhuma"), AMBAR if reg.quedas else BRANCO),
              ("na bateria", _dur(reg.s_bateria), AMBAR if reg.s_bateria else BRANCO)]
    if ob and reg.ob_desde:
        linhas[4] = ("NA BATERIA HÁ", _dur(agora - reg.ob_desde), AMBAR)
    if flags:                                         # alarme do nobreak no lugar da última linha
        fl_ = flags[0].upper() + (f" +{len(flags) - 1}" if len(flags) > 1 else "")
        linhas[4] = ("alarme", fl_, alerta or AMBAR)
    for i, (a, b, cor) in enumerate(linhas):
        yy = y2 + 52 + i * 23
        txt((x3 + 14, yy), a, F("rb", 17, "Regular"), SUB if cor in (BRANCO, VERDE) else cor)
        txt((x4 - 26, yy), cabe(b, F("jb", 17), x4 - 26 - (x3 + 130)), F("jb", 17), cor, "rs")

    dr.rounded_rectangle((x4, y2, 1260, y2 + h2), 10, fill=PAINEL, outline=LINHA, width=2)
    txt((x4 + 14, y2 + 27), "MÉDIAS", F("rb", 19), SUB)
    c1, c2 = 1142, 1246
    txt((c1, y2 + 27), "MINERANDO", F("jb", 13), GELO, "rs")
    txt((c2, y2 + 27), "SEM", F("jb", 13), SUB, "rs")
    fmt = lambda x, f: "--" if x is None else f.format(x)
    tab = [("tempo", _dur(reg.cmp[True].get("s", 0)), _dur(reg.cmp[False].get("s", 0))),
           ("potência", fmt(reg.media(True, "potencia_W"), "{:.0f} W"), fmt(reg.media(False, "potencia_W"), "{:.0f} W")),
           ("pico", fmt(reg.cmp[True].get("pico"), "{:.0f} W"), fmt(reg.cmp[False].get("pico"), "{:.0f} W")),
           ("carga", fmt(reg.media(True, "carga_%"), "{:.0f}%"), fmt(reg.media(False, "carga_%"), "{:.0f}%")),
           ("temperatura", fmt(reg.media(True, "temp_C"), "{:.0f}°C"), fmt(reg.media(False, "temp_C"), "{:.0f}°C"))]
    for i, (a, b1, b2) in enumerate(tab):
        yy = y2 + 52 + i * 24
        txt((x4 + 14, yy), a, F("rb", 17, "Regular"), SUB)
        txt((c1, yy), b1, F("jb", 17), GELO if minerando else BRANCO, "rs")
        txt((c2, yy), b2, F("jb", 17), BRANCO if not minerando else SUB, "rs")

    # ---- dinheiro acumulado: gasto de energia minerando, receita estimada, saldo e cotação do dólar
    yf0, yf1 = 428, 504
    dr.rounded_rectangle((20, yf0, 1260, yf1), 10, fill=PAINEL, outline=LINHA, width=2)
    if fin:
        a, dol = fin.a, (cot.valor if cot else None)
        usd = lambda brl: brl / dol if dol else None
        brl = lambda u: u * dol if dol else None
        tarifa = fin.cfg["TARIFA_BRL_KWH"]
        desde = time.strftime("%d/%m/%Y %H:%M", time.localtime(a["desde"]))
        txt((34, yf0 + 22), f"ACUMULADO desde {desde}", F("rb", 15), SUB)
        txt((34, yf0 + 45), f"{_dur(a['s_min'])} minerando", F("jb", 14, "Regular"), GELO if minerando else SUB)
        txt((34, yf0 + 66), cabe(f"nobreak {_n(a['kwh_total'], 1)} kWh = {_dinheiro(a['brl_total'])}",
                                 F("jb", 13, "Regular"), 270), F("jb", 13, "Regular"), SUB)
        saldo_u = a["usd_receita"] - (usd(a["brl_min"]) or 0) if dol else None
        saldo_r = brl(a["usd_receita"]) - a["brl_min"] if dol else None
        cols = [(330, "GASTO (energia minerando)", _dinheiro(a["brl_min"]), _dinheiro(usd(a["brl_min"]), "US$"),
                 f"{_n(a['kwh_min'], 2)} kWh x {_dinheiro(tarifa, 'R$', 3)}" if tarifa else "sem tarifa no painel.conf",
                 BRANCO),
                (580, "GERADO (estimado)", _dinheiro(brl(a["usd_receita"])), _dinheiro(a["usd_receita"], "US$", 4),
                 f"agora {_n(ths, 1)} TH/s" if ths else "minerador sem hashrate recente", GELO),
                (830, "SALDO", _dinheiro(saldo_r), _dinheiro(saldo_u, "US$"),
                 "gerado - gasto", (VERDE if (saldo_r or 0) >= 0 else VERMELHO))]
        for x, rot, v1, v2, nota, cor in cols:
            txt((x, yf0 + 22), rot, F("rb", 15), SUB)
            b = dr.textbbox((x, yf0 + 48), v1, font=F("jb", 24), anchor="ls")
            txt((x, yf0 + 48), v1, F("jb", 24), cor)
            txt((b[2] + 10, yf0 + 48), v2, F("jb", 16), cor)
            txt((x, yf0 + 67), nota, F("jb", 13, "Regular"), SUB)
        xc = 1080
        txt((xc, yf0 + 22), "DÓLAR", F("rb", 15), SUB)
        txt((xc, yf0 + 48), _dinheiro(dol, "R$", 4) if dol else "R$ --", F("jb", 22), BRANCO)
        quando = time.strftime("%H:%M", time.localtime(cot.hora)) if cot and cot.hora else ""
        txt((xc, yf0 + 67), cabe(f"{cot.fonte} {quando}".strip() if cot else "", F("jb", 13, "Regular"), 170),
            F("jb", 13, "Regular"), SUB)

    # ---- gráficos dos últimos 15 minutos, por tempo: sem leitura = em branco
    yg0, yg1 = 518, 680
    pts = [p for p in reg.hist if p[0] >= agora - JANELA_S]
    t0 = agora - JANELA_S

    def grafico(x0, x1, titulo, series, vmin=None, vmax=None, unid="", refs=()):
        dr.rounded_rectangle((x0, yg0 - 4, x1, yg1 + 22), 10, fill=PAINEL, outline=LINHA, width=2)
        txt((x0 + 14, yg0 + 20), titulo, F("rb", 18), SUB)
        gx0, gx1, gy0, gy1 = x0 + 14, x1 - 14, yg0 + 32, yg1 - 4
        X = lambda t: gx0 + (gx1 - gx0) * (t - t0) / JANELA_S
        vals = [v for _, s, _ in series for _, v in s if v is not None]
        if not vals:
            txt(((gx0 + gx1) // 2, (gy0 + gy1) // 2), "sem leituras nos últimos 15 min", F("jb", 16, "Regular"), SUB, "mm")
            return
        lo = min(vals + [r for r, _ in refs]) if vmin is None else vmin
        hi = max(vals + [r for r, _ in refs]) if vmax is None else vmax
        if hi - lo < 1e-6:
            lo, hi = lo - 1, hi + 1
        pad = (hi - lo) * 0.08
        lo, hi = lo - pad, hi + pad
        Y = lambda v: gy1 - (v - lo) / (hi - lo) * (gy1 - gy0)
        for i in range(1, len(pts)):                      # trechos minerando: faixa de fundo destacada
            (ta, da), (tb, db) = pts[i - 1], pts[i]
            if da.get("minerando") == "sim" and db.get("minerando") == "sim" and tb - ta <= LACUNA_S:
                dr.rectangle((X(ta), gy0, max(X(ta) + 1, X(tb)), gy1), fill=(16, 44, 30))
        for k in range(1, 3):                             # marcas a cada 5 min
            xx = gx0 + (gx1 - gx0) * k / 3
            for yy in range(gy0, gy1, 6):
                dr.point((xx, yy), fill=LINHA)
        for rv, rc in refs:                               # limites da faixa de operação
            yy = Y(rv)
            for xx in range(gx0, gx1, 10):
                dr.line((xx, yy, min(xx + 5, gx1), yy), fill=rc, width=1)
        for nome, s, cor in series:
            trecho, t_ant = [], None
            for t, v in s + [(None, None)]:
                if v is None or (t_ant is not None and t - t_ant > LACUNA_S):
                    if len(trecho) > 1:
                        dr.line(trecho, fill=cor, width=2)
                    elif len(trecho) == 1:
                        dr.point(trecho[0], fill=cor)
                    trecho = []
                if v is not None:
                    trecho.append((X(t), Y(v)))
                t_ant = t
        txt((x1 - 14, yg0 + 20), f"{_n(lo + pad)} a {_n(hi - pad)}{unid}", F("jb", 14, "Regular"), SUB, "rs")
        xl = x0 + 14 + dr.textlength(titulo, font=F("rb", 18)) + 12
        for nome, _, cor in series:
            txt((xl, yg0 + 20), nome, F("jb", 15), cor)
            xl += dr.textlength(nome, font=F("jb", 15)) + 10
        txt((gx0, yg1 + 16), "-15 min", F("jb", 13, "Regular"), SUB)
        txt((gx1, yg1 + 16), "agora", F("jb", 13, "Regular"), SUB, "rs")

    def serie(k):
        return [(t, (None if k == "entrada_V" and p["status"].startswith("OB") else p[k])) for t, p in pts]

    grafico(20, 432, "TENSÃO", [("ENTRADA", serie("entrada_V"), VERDE), ("SAÍDA", serie("saida_V"), BRANCO)],
            unid=" V", refs=[(pt[0], AMBAR), (pt[1], AMBAR)])
    grafico(444, 846, "POTÊNCIA", [("W", serie("potencia_W"), VERDE)], vmin=0, unid=" W")
    grafico(858, 1260, "BATERIA", [("V", serie("bateria_V"), VERDE)], unid=" V")

    # ---- rodapé
    pasta = str(reg.pasta).replace(str(Path.home()), "~")
    modelo = f"Ragtech {d['modelo']} fw {d['firmware']} | " if d else ""
    estado = f"{modelo}a cada {intervalo:g} s | {reg.leituras} leituras hoje, {reg.falhas} falhas | {pasta}"
    if erro:
        estado = f"ÚLTIMA LEITURA FALHOU: {erro}"
    fr = F("jb", 13, "Regular")
    b = dr.textbbox((20, 715), estado, font=fr, anchor="ls")
    txt((20, 715), estado, fr, VERMELHO if erro else SUB)
    if reg.eventos:                                       # último evento à direita, só no espaço que sobra
        txt((1260, 715), cabe(reg.eventos[-1], fr, 1260 - b[2] - 24), fr, AMBAR, "rs")
    return im


# ---------------------------------------------------------------- tela
def abrir_tela(turing, brilho):
    sys.path.insert(0, str(turing))
    os.chdir(ESTADO)                                 # library.log grava "log.log" na pasta atual
    from library.lcd.lcd_comm_turing_usb import LcdCommTuringUSB
    from library.lcd.lcd_comm import Orientation
    lcd = LcdCommTuringUSB()
    lcd.InitializeComm()
    lcd.SetBrightness(brilho)
    lcd.SetOrientation(Orientation.LANDSCAPE)
    return lcd


def main():
    ap = argparse.ArgumentParser(description="Tela do nobreak Ragtech na TURZX de 5,2\" em paisagem")
    ap.add_argument("--intervalo", type=float, default=1.0, help="segundos entre leituras (padrão 1)")
    ap.add_argument("--brilho", type=int, default=30)
    ap.add_argument("--va", type=int, default=1200, help="VA do nobreak (NEP 1200 = 1200)")
    ap.add_argument("--rede", type=int, choices=(220, 127), default=220, help="tensão nominal da tomada (padrão 220)")
    ap.add_argument("--leitor", default=str(LEITOR_PADRAO))
    ap.add_argument("--turing", default=str(TURING_PADRAO))
    ap.add_argument("--previa", help="grava um quadro em PNG e sai (não usa a tela)")
    ap.add_argument("--demo", action="store_true", help="dados de demonstração")
    ap.add_argument("--sem-tela", action="store_true", help="só lê e grava o log")
    ap.add_argument("--mineradores", default=os.environ.get("NOBREAK_MINERADORES", ",".join(MINERADORES)),
                    help="nomes de processo de mineração, separados por vírgula")
    a = ap.parse_args()

    ESTADO.mkdir(parents=True, exist_ok=True)
    import signal                                     # systemctl stop manda SIGTERM: sai pelo finally e grava o acumulado
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    F = Fontes(a.turing)
    mina = Mineracao(a.mineradores.split(","))

    if a.demo:                                        # 15 min fictícios, com 1 min desligado, sem tocar no log real
        reg = Registro(ESTADO, a.rede, gravar=False, retomar=False)
        fonte, agora = Demo(), time.time()
        d = None
        for i in range(900):
            d, _ = fonte.ler()
            if 700 <= i < 760:                        # computador desligado: sem leitura
                continue
            d = reg.anotar(d, fonte.minerando, "xmrig", agora - 900 + i)
        fin = Financas(ESTADO, gravar=False)
        fin.a = {"desde": agora - 3 * 86400, "kwh_total": 21.4, "brl_total": 21.4 * 0.869, "kwh_min": 15.6,
                 "brl_min": 15.6 * 0.869, "usd_receita": 6.41, "s_min": 2.1 * 86400}
        fin.cfg = {"TARIFA_BRL_KWH": 0.869, "RECEITA_USD_DIA_REF": 3.05, "HASH_REF_THS": 190, "USD_BRL": 5.32}
        cot = Cotacao(ESTADO / "demo-sem-cache", 5.3412, consulta=False)
        cot.hora, cot.fonte = agora - 240, "AwesomeAPI"
        desenhar(reg, F, d, None, a.intervalo, fonte.minerando, "xmrig", agora, fin=fin, cot=cot,
                 ths=188.6 if fonte.minerando else None).save(a.previa or "demo.png")
        log(f"prévia de demonstração gravada: {a.previa or 'demo.png'}")
        return 0

    if a.previa:                                      # só o log: não disputa a porta com o serviço
        reg = Registro(ESTADO, a.rede, gravar=False)
        d = reg.hist[-1][1] if reg.hist else None
        fin = Financas(ESTADO, gravar=False)
        cot = Cotacao(ESTADO, fin.cfg["USD_BRL"], consulta=False)
        desenhar(reg, F, d, None if d else "sem leituras recentes no log", a.intervalo,
                 bool(d) and d.get("minerando") == "sim", fin=fin, cot=cot).save(a.previa)
        log(f"prévia gravada a partir do log: {a.previa}")
        return 0
    fonte = Nobreak(a.leitor, a.va)
    reg = Registro(ESTADO, a.rede)
    fin = Financas(ESTADO)
    cot = Cotacao(ESTADO, fin.cfg["USD_BRL"])
    hr = Hashrate()
    t_ant = None

    lcd = None
    if not a.sem_tela:
        lcd = abrir_tela(a.turing, a.brilho)
        log("tela de 5,2\" aberta em paisagem (1280x720)")
    log(f"lendo o nobreak a cada {a.intervalo:g} s; rede de {a.rede} V; log em {ESTADO}")
    ultimo = None
    try:
        while True:
            t0 = time.time()
            d, erro = fonte.ler()
            m = mina.ativa()
            ths = hr.atual(t0) if m else None
            if d:
                ultimo = reg.anotar(d, m, mina.qual)
                dt = (t0 - t_ant) if t_ant and t0 - t_ant <= LACUNA_S else 0.0   # lacuna (desligado): não soma
                fin.somar(ultimo["potencia_W"], m, ths, dt, t0)
                t_ant = t0
            else:
                reg.falha(erro)
            if lcd:
                try:
                    lcd.DisplayPILImage(desenhar(reg, F, ultimo if d else None, erro, a.intervalo, m, mina.qual,
                                                 fin=fin, cot=cot, ths=ths))
                except Exception as e:
                    log(f"falha ao enviar à tela: {type(e).__name__}: {e}")
                    time.sleep(5)
                    try:
                        lcd = abrir_tela(a.turing, a.brilho)
                    except Exception as e2:
                        log(f"tela indisponível: {type(e2).__name__}: {e2}")
            time.sleep(max(0.0, a.intervalo - (time.time() - t0)))
    except KeyboardInterrupt:
        pass
    finally:
        fin.salvar()
        fonte.fechar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
