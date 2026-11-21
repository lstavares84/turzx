#!/usr/bin/env python3
# GAMMA NOBREAK | nobreak/nobreak_tela.py | versão 0.2.0 | 21/11/2026 10:31 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 0.2.0 21/11/2026 10:31 tag MINERANDO pelo processo do minerador; dados separados por minerando ou não
# histórico: 0.1.0 21/11/2026 10:17 criação: tela de 5,2" em paisagem só com o nobreak Ragtech 4162, log em CSV
#
# Tela exclusiva do nobreak na TURZX / Turing de 5,2" (720x1280, revisão TUR_USB, USB 1cbe:0050), em PAISAGEM
# (1280x720). A cada ciclo (padrão 1 s): lê o nobreak, grava uma linha no CSV do dia, desenha o quadro e envia.
#   leitura: ragtech_read.py do repositório ragtech_4162 (somente leitura, protocolo do driver "ragtech" do NUT);
#            este programa NUNCA envia comando de escrita ao nobreak, só usa a função poll() do leitor.
#   tela:    biblioteca do turing-smart-screen-python (LcdCommTuringUSB), sem uma segunda instância do programa.
#   cores:   só os próprios alarmes do nobreak decidem âmbar e vermelho (nenhum limite inventado aqui).
#   log:     ~/.local/state/nobreak/nobreak-AAAA-MM-DD.csv (uma linha por leitura) e nobreak-eventos.log.
#   mineração: o computador está minerando quando um processo da lista MINERADORES está rodando (nome do processo
#            ou do executável, sem diferenciar maiúsculas). A lista muda com --mineradores ou NOBREAK_MINERADORES.
# Uso:
#   python3 nobreak_tela.py                      tela + log (o serviço systemd roda assim)
#   python3 nobreak_tela.py --previa saida.png   desenha um quadro com a leitura real e sai (não usa a tela)
#   python3 nobreak_tela.py --demo --previa x.png quadro com dados de demonstração
#   python3 nobreak_tela.py --sem-tela           só lê e grava o log
import argparse
import collections
import csv
import importlib.util
import math
import os
import random
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault("TZ", "America/Sao_Paulo")
time.tzset()

RAIZ_GITHUB = Path(__file__).resolve().parents[2]
LEITOR_PADRAO = RAIZ_GITHUB / "ragtech_4162" / "ragtech_read.py"
TURING_PADRAO = Path.home() / "Documentos" / "Projetos" / "turing-smart-screen-linux"
ESTADO = Path(os.environ.get("NOBREAK_ESTADO", Path.home() / ".local" / "state" / "nobreak"))
W, H = 1280, 720
JANELA = 900                      # pontos guardados para os gráficos (15 min a 1 leitura por segundo)

# paleta GAMMA (a mesma do tema da tela de 3,5")
BG, PAINEL, LINHA = (3, 10, 4), (8, 22, 10), (35, 75, 35)
VERDE, GELO, BRANCO, SUB = (120, 255, 90), (190, 255, 170), (230, 255, 225), (110, 170, 110)
AMBAR, VERMELHO = (255, 190, 0), (255, 60, 50)

# processos de mineração reconhecidos (nomes usuais dos mineradores, inclusive os que o Kryptex usa por baixo)
MINERADORES = ["kryptex", "xmrig", "lolminer", "gminer", "t-rex", "nbminer", "teamredminer", "srbminer-multi",
               "bzminer", "rigel", "onezerominer", "nanominer", "excavator", "ethminer", "wildrig"]
CINZA = (70, 95, 70)

# alarmes do próprio nobreak (texto do ragtech_read.py) -> nível
CRITICOS = {"bateria esgotada", "sobrecarga", "saida anormal", "falha inversor", "curto-circuito", "superaquecimento",
            "sem bateria"}
AVISOS = {"bateria fraca", "bateria velha", "bateria anormal", "rede baixa", "rede alta", "sem rede", "autoteste"}


def ts():
    return time.strftime("%d/%m/%Y %H:%M:%S")


def log(msg):
    print(f"[{ts()}] {msg}", flush=True)


# ---------------------------------------------------------------- leitura
class Nobreak:
    def __init__(self, leitor, va=None):
        spec = importlib.util.spec_from_file_location("ragtech_read", leitor)
        self.rt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.rt)
        self.va, self.fd = va, None

    def ler(self):
        try:
            if self.fd is None:
                portas = sorted(Path("/dev/serial/by-id").glob("*Ragtech*"))
                if not portas:
                    return None, "nobreak não encontrado em /dev/serial/by-id"
                self.fd = self.rt.open_port(os.path.realpath(portas[0]))
            d, _ = self.rt.poll(self.fd, self.va)
            return (d, None) if d else (None, "sem resposta do nobreak")
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
    """Dados de demonstração (quadro de prévia): rede normal com uma queda curta no meio da janela."""

    def __init__(self):
        self.t, self.minerando = 0, False

    def ler(self):
        self.t += 1
        ob = 380 < self.t % 900 < 470
        self.minerando = 150 < self.t % 900 < 640
        vin = 0.0 if ob else 118 + 3 * math.sin(self.t / 40) + random.uniform(-0.6, 0.6)
        a = 1.9 + 0.5 * math.sin(self.t / 25) + random.uniform(-0.05, 0.05) + (2.4 if self.minerando else 0)
        bat = 100.0 if not ob else 100 - (self.t % 900 - 380) * 0.2
        d = {"hora": time.strftime("%Y-%m-%d %H:%M:%S"), "modelo_id": 6, "modelo": "Easy 1200 TI", "firmware": 1.2,
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


# ---------------------------------------------------------------- estado, eventos e log
class Registro:
    CAMPOS = ["data_hora", "minerando", "entrada_V", "saida_V", "saida_A", "potencia_W", "carga_%", "carga_fw_%", "freq_Hz",
              "bateria_%", "bateria_V", "temp_C", "status", "modelo", "firmware"]

    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.hist = collections.deque(maxlen=JANELA)
        self.eventos = collections.deque(maxlen=7)
        self.flags_ant, self.ob_desde, self.ultima_queda = None, None, None
        self.dia, self.quedas, self.s_bateria = time.strftime("%Y-%m-%d"), 0, 0.0
        self.t_ant, self.leituras, self.falhas = None, 0, 0
        self.min_max = {}
        self.min_ant = None
        self.cmp = {True: {}, False: {}}          # somas do dia por categoria: minerando e sem mineração
        self._carregar_eventos()
        self._retomar_dia()

    COMPARAR = ("potencia_W", "carga_%", "saida_A", "temp_C", "entrada_V")

    def _somar(self, minerando, d, dt):
        c = self.cmp[minerando]
        c["s"] = c.get("s", 0.0) + dt
        c["n"] = c.get("n", 0) + 1
        for k in self.COMPARAR:
            if k == "entrada_V" and str(d.get("status", "")).startswith("OB"):
                continue
            c[k] = c.get(k, 0.0) + float(d[k])
            c[k + "#"] = c.get(k + "#", 0) + 1
        c["pico"] = max(c.get("pico", 0.0), float(d["potencia_W"]))

    def media(self, minerando, k):
        c = self.cmp[minerando]
        return c[k] / c[k + "#"] if c.get(k + "#") else None

    def _retomar_dia(self):
        """Depois de reiniciar, recupera do CSV e do log de eventos de hoje as somas, os mínimos e máximos e as quedas."""
        p = self.pasta / f"nobreak-{self.dia}.csv"
        if p.exists():
            try:
                with open(p, newline="", encoding="utf-8") as f:
                    linhas = list(csv.DictReader(f, delimiter=";"))
                t_ant = None
                for r in linhas:
                    if "minerando" not in r:
                        break
                    t = time.mktime(time.strptime(r["data_hora"], "%d/%m/%Y %H:%M:%S"))
                    dt = min(t - t_ant, 10) if t_ant else 1.0
                    t_ant = t
                    d = {k: float(r[k]) for k in self.COMPARAR}
                    d["potencia_W"], d["status"] = float(r["potencia_W"]), r["status"]
                    self._somar(r["minerando"] == "sim", d, dt)
                    for k in ("entrada_V", "saida_V", "potencia_W", "freq_Hz", "bateria_V", "temp_C"):
                        if k == "entrada_V" and r["status"].startswith("OB"):
                            continue
                        v = float(r[k]); lo, hi = self.min_max.get(k, (v, v))
                        self.min_max[k] = (min(lo, v), max(hi, v))
                    if r["status"].startswith("OB"):
                        self.s_bateria += dt
            except (ValueError, KeyError, OSError) as e:
                log(f"não consegui retomar o CSV de hoje: {e}")
        ev = self.pasta / "nobreak-eventos.log"
        if ev.exists():
            hoje = time.strftime("%d/%m/%Y")
            for linha in ev.read_text(encoding="utf-8").splitlines():
                if linha.startswith(hoje) and "FOI PARA A BATERIA" in linha:
                    self.quedas += 1
                    self.ultima_queda = time.mktime(time.strptime(linha[:19], "%d/%m/%Y %H:%M:%S"))

    def _carregar_eventos(self):
        p = self.pasta / "nobreak-eventos.log"
        if p.exists():
            for linha in p.read_text(encoding="utf-8").splitlines()[-7:]:
                self.eventos.append(linha)

    def evento(self, texto):
        linha = f"{ts()} {texto}"
        self.eventos.append(linha)
        with open(self.pasta / "nobreak-eventos.log", "a", encoding="utf-8") as f:
            f.write(linha + "\n")
        log(f"evento: {texto}")

    def falha(self, motivo):
        self.falhas += 1
        if self.flags_ant != "FALHA":
            self.evento(f"LEITURA FALHOU: {motivo}")
            self.flags_ant = "FALHA"

    def anotar(self, d, minerando=False, qual=""):
        agora = time.time()
        hoje = time.strftime("%Y-%m-%d")
        if hoje != self.dia:                          # virada do dia: zera os contadores do dia
            self.dia, self.quedas, self.s_bateria, self.min_max = hoje, 0, 0.0, {}
            self.cmp = {True: {}, False: {}}
        d = dict(d)
        d["potencia_W"] = round(d["saida_V"] * d["saida_A"], 1)
        d["minerando"] = "sim" if minerando else "não"
        if self.min_ant is not None and minerando != self.min_ant:
            self.evento(f"COMEÇOU A MINERAR ({qual}, {d['potencia_W']:.0f} W)" if minerando
                        else f"PAROU DE MINERAR ({d['potencia_W']:.0f} W)")
        self.min_ant = minerando
        self._somar(minerando, d, min(agora - self.t_ant, 10) if self.t_ant else 1.0)
        ob = d["status"].startswith("OB")
        flags = tuple(sorted(x.strip() for x in d["status"].split(";")[1:] if x.strip()))
        estado = ("OB" if ob else "OL",) + flags
        if self.flags_ant is not None and estado != self.flags_ant:
            ant = set(self.flags_ant[1:]) if self.flags_ant != "FALHA" else set()
            if self.flags_ant == "FALHA":
                self.evento("leitura voltou")
            if ob and (self.flags_ant == "FALHA" or self.flags_ant[0] != "OB"):
                self.evento(f"FOI PARA A BATERIA (entrada {d['entrada_V']} V, bateria {d['bateria_%']}%)")
            elif not ob and self.flags_ant != "FALHA" and self.flags_ant[0] == "OB":
                dur = agora - self.ob_desde if self.ob_desde else 0
                self.evento(f"VOLTOU PARA A REDE depois de {_dur(dur)} (bateria {d['bateria_%']}%)")
            for f in sorted(set(flags) - ant):
                self.evento(f"alarme: {f}")
            for f in sorted(ant - set(flags)):
                self.evento(f"alarme encerrado: {f}")
        if ob and (self.ob_desde is None):
            self.ob_desde = agora
            self.quedas += 1
            self.ultima_queda = agora
        if not ob:
            self.ob_desde = None
        if ob and self.t_ant:
            self.s_bateria += min(agora - self.t_ant, 10)
        self.flags_ant, self.t_ant = estado, agora
        self.leituras += 1
        for k in ("entrada_V", "saida_V", "potencia_W", "freq_Hz", "bateria_V", "temp_C"):
            v = d[k]
            lo, hi = self.min_max.get(k, (v, v))
            if not (k == "entrada_V" and ob):         # sem rede a entrada lê 0: não é mínimo de tensão da rede
                self.min_max[k] = (min(lo, v), max(hi, v))
        self.hist.append((agora, d))
        self._csv(d)
        return d

    def _csv(self, d):
        p = self.pasta / f"nobreak-{self.dia}.csv"
        if p.exists():                                # CSV de uma versão anterior (sem a coluna minerando)
            with open(p, encoding="utf-8") as f:
                if f.readline().strip().split(";") != self.CAMPOS:
                    p.rename(p.with_name(p.stem + "-sem-mineracao.csv"))
        novo = not p.exists()
        with open(p, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            if novo:
                w.writerow(self.CAMPOS)
            w.writerow([ts()] + [d.get(k, "") for k in self.CAMPOS[1:]])


def _dur(s):
    s = int(s)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}min{s % 60:02d}s"
    return f"{s // 3600}h{s % 3600 // 60:02d}min"


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


def desenhar(reg, F, ultimo, erro, intervalo, minerando=False, qual=""):
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    txt = lambda xy, s, f, c, a="ls": dr.text(xy, s, font=f, fill=c, anchor=a)

    d = ultimo
    flags = [x.strip() for x in d["status"].split(";")[1:] if x.strip()] if d else []
    ob = bool(d) and d["status"].startswith("OB")
    alerta = _nivel(flags)

    # ---- cabeçalho
    txt((20, 44), "NOBREAK", F("jb", 34), VERDE)
    tx0, tx1 = 250, 600                               # tag da mineração
    cor_m = GELO if minerando else CINZA
    dr.rounded_rectangle((tx0, 8, tx1, 58), 8, fill=(18, 52, 22) if minerando else BG, outline=cor_m, width=3)
    txt(((tx0 + tx1) // 2, 46), "MINERANDO" if minerando else "SEM MINERAÇÃO", F("jb", 30), cor_m, "ms")
    if erro and not d:
        cor_st, rot = VERMELHO, "SEM LEITURA"
    elif ob:
        cor_st, rot = AMBAR, "NA BATERIA"
    else:
        cor_st, rot = VERDE, "NA REDE"
    if alerta == VERMELHO:
        cor_st = VERMELHO
    bx0, bx1 = 640, 940
    dr.rounded_rectangle((bx0, 8, bx1, 58), 8, fill=tuple(int(c * 0.25) for c in cor_st), outline=cor_st, width=3)
    txt(((bx0 + bx1) // 2, 46), rot, F("jb", 32), cor_st, "ms")
    txt((1260, 44), time.strftime("%H:%M:%S"), F("jb", 34), VERDE, "rs")
    txt((1260, 64), time.strftime("%d/%m/%Y"), F("jb", 14, "Regular"), SUB, "rs")
    dr.line((0, 70, W, 70), fill=LINHA, width=2)

    # ---- blocos grandes (linha 1)
    def bloco(x, y, w, h, rotulo, valor, unid, cor=BRANCO, extra=None, pct=None):
        dr.rounded_rectangle((x, y, x + w, y + h), 10, fill=PAINEL, outline=LINHA, width=2)
        txt((x + 14, y + 30), rotulo, F("rb", 20), SUB)
        fu = F("jb", 24)
        for tam in (62, 56, 50, 44, 38):                # o número diminui até caber com a unidade
            f = F("jb", tam)
            if dr.textlength(valor, font=f) + 6 + dr.textlength(unid, font=fu) <= w - 28:
                break
        b = dr.textbbox((x + 14, y + 104), valor, font=f, anchor="ls")
        txt((x + 14, y + 104), valor, f, cor)
        txt((b[2] + 6, y + 104), unid, fu, SUB)
        if extra:
            fe = F("jb", 17, "Regular")
            while extra and dr.textlength(extra, font=fe) > w - 28:
                extra = extra[:-1]
            txt((x + 14, y + h - 14), extra, fe, SUB)
        if pct is not None:
            bw = w - 28
            dr.rectangle((x + 14, y + h - 44, x + 14 + bw, y + h - 34), fill=(16, 40, 18))
            fw = int(bw * max(0, min(100, pct)) / 100)
            if fw:
                dr.rectangle((x + 14, y + h - 44, x + 14 + fw, y + h - 34), fill=cor if cor != BRANCO else VERDE)

    mm = reg.min_max
    faixa = lambda k, u: f"{mm[k][0]:g} a {mm[k][1]:g} {u}" if k in mm else ""
    v = (lambda k, fmt="{:.1f}": fmt.format(d[k])) if d else (lambda k, fmt=None: "--")
    y1, h1, w1, g = 84, 168, 199, 12
    cor_in = AMBAR if ob or {"rede baixa", "rede alta", "sem rede"} & set(flags) else BRANCO
    cor_carga = VERMELHO if "sobrecarga" in flags else BRANCO
    bloco(20 + 0 * (w1 + g), y1, w1, h1, "ENTRADA", v("entrada_V"), "V", cor_in, faixa("entrada_V", "V"))
    bloco(20 + 1 * (w1 + g), y1, w1, h1, "SAÍDA", v("saida_V"), "V", BRANCO, faixa("saida_V", "V"))
    bloco(20 + 2 * (w1 + g), y1, w1, h1, "FREQUÊNCIA", v("freq_Hz", "{:.2f}"), "Hz", BRANCO, faixa("freq_Hz", "Hz"))
    bloco(20 + 3 * (w1 + g), y1, w1, h1, "CORRENTE", v("saida_A", "{:.2f}"), "A", BRANCO,
          f"{d['saida_V'] * d['saida_A']:.0f} VA" if d else "")
    bloco(20 + 4 * (w1 + g), y1, w1, h1, "POTÊNCIA", (f"{d['saida_V'] * d['saida_A']:.0f}" if d else "--"), "W",
          cor_carga, (f"pico hoje {mm['potencia_W'][1]:.0f} W" if "potencia_W" in mm else ""))
    bloco(20 + 5 * (w1 + g), y1, w1, h1, "CARGA", v("carga_%", "{:.0f}"), "%", cor_carga,
          f"firmware {d['carga_fw_%']}%" if d else "", pct=d["carga_%"] if d else None)

    # ---- linha 2: bateria, temperatura, contadores e alarmes
    y2, h2 = 264, 168
    cor_bat = VERMELHO if {"bateria esgotada", "sem bateria"} & set(flags) else \
        AMBAR if {"bateria fraca", "bateria anormal", "bateria velha"} & set(flags) or ob else VERDE
    bloco(20, y2, 410, h2, "BATERIA", v("bateria_%", "{:.0f}"), "%", cor_bat,
          (f"{d['bateria_V']:.2f} V   " if d else "") + faixa("bateria_V", "V"), pct=d["bateria_%"] if d else None)
    cor_t = VERMELHO if "superaquecimento" in flags else BRANCO
    bloco(442, y2, 199, h2, "TEMPERATURA", (f"{d['temp_C']}" if d else "--"), "°C", cor_t, faixa("temp_C", "°C"))

    x3, x4 = 653, 940
    dr.rounded_rectangle((x3, y2, x4 - 12, y2 + h2), 10, fill=PAINEL, outline=LINHA, width=2)
    txt((x3 + 14, y2 + 30), "HOJE", F("rb", 20), SUB)
    linhas = [("quedas de energia", str(reg.quedas)), ("tempo na bateria", _dur(reg.s_bateria)),
              ("última queda", time.strftime("%H:%M", time.localtime(reg.ultima_queda)) if reg.ultima_queda else "nenhuma")]
    if ob and reg.ob_desde:
        linhas.insert(0, ("NA BATERIA HÁ", _dur(time.time() - reg.ob_desde)))
    if flags:                                         # alarmes do nobreak na última linha
        fl = flags[0].upper() + (f" +{len(flags) - 1}" if len(flags) > 1 else "")
        linhas = linhas[:3] + [("alarme", fl)]
    else:
        linhas = linhas[:3] + [("alarmes", "nenhum")]
    for i, (a, b) in enumerate(linhas):
        yy = y2 + 62 + i * 28
        cor = AMBAR if a.startswith("NA BATERIA") else (alerta or AMBAR) if a == "alarme" else \
            VERDE if b == "nenhum" and a == "alarmes" else BRANCO
        txt((x3 + 14, yy), a, F("rb", 19, "Regular"), SUB if cor in (BRANCO, VERDE) else cor)
        fb = F("jb", 20)
        while dr.textlength(b, font=fb) > x4 - 26 - (x3 + 170) and len(b) > 3:
            b = b[:-2] + "…"
        txt((x4 - 26, yy), b, fb, cor, "rs")

    # comparação do dia: minerando x sem mineração
    dr.rounded_rectangle((x4, y2, 1260, y2 + h2), 10, fill=PAINEL, outline=LINHA, width=2)
    txt((x4 + 14, y2 + 30), "MÉDIAS", F("rb", 20), SUB)
    c1, c2 = 1150, 1246
    txt((c1, y2 + 30), "MINERANDO", F("jb", 15), GELO, "rs")
    txt((c2, y2 + 30), "SEM", F("jb", 15), SUB, "rs")
    fmt = lambda x, f: "--" if x is None else f.format(x)
    tab = [("tempo", _dur(reg.cmp[True].get("s", 0)), _dur(reg.cmp[False].get("s", 0))),
           ("potência", fmt(reg.media(True, "potencia_W"), "{:.0f} W"), fmt(reg.media(False, "potencia_W"), "{:.0f} W")),
           ("pico", fmt(reg.cmp[True].get("pico"), "{:.0f} W"), fmt(reg.cmp[False].get("pico"), "{:.0f} W")),
           ("carga", fmt(reg.media(True, "carga_%"), "{:.0f}%"), fmt(reg.media(False, "carga_%"), "{:.0f}%")),
           ("temperatura", fmt(reg.media(True, "temp_C"), "{:.0f}°C"), fmt(reg.media(False, "temp_C"), "{:.0f}°C"))]
    for i, (a, b1, b2) in enumerate(tab):
        yy = y2 + 56 + i * 24
        txt((x4 + 14, yy), a, F("rb", 18, "Regular"), SUB)
        txt((c1, yy), b1, F("jb", 18), GELO if minerando else BRANCO, "rs")
        txt((c2, yy), b2, F("jb", 18), BRANCO if not minerando else SUB, "rs")

    # ---- gráficos dos últimos 15 minutos
    yg0, yg1 = 450, 676
    pts = list(reg.hist)

    def grafico(x0, x1, titulo, series, vmin=None, vmax=None, unid=""):
        dr.rounded_rectangle((x0, yg0 - 4, x1, yg1 + 26), 10, fill=PAINEL, outline=LINHA, width=2)
        txt((x0 + 14, yg0 + 22), titulo, F("rb", 19), SUB)
        gx0, gx1, gy0, gy1 = x0 + 14, x1 - 14, yg0 + 34, yg1 - 4
        vals = [val for _, s, _ in series for val in s if val is not None]
        if not vals:
            txt(((gx0 + gx1) // 2, (gy0 + gy1) // 2), "aguardando leituras", F("jb", 18, "Regular"), SUB, "mm")
            return
        lo = min(vals) if vmin is None else vmin
        hi = max(vals) if vmax is None else vmax
        if hi - lo < 1e-6:
            lo, hi = lo - 1, hi + 1
        pad = (hi - lo) * 0.08
        lo, hi = lo - pad, hi + pad
        for k in range(1, 3):                           # marcas a cada 5 min
            xx = gx1 - (gx1 - gx0) * k / 3
            for yy in range(gy0, gy1, 6):
                dr.point((xx, yy), fill=LINHA)
        Y = lambda val: gy1 - (val - lo) / (hi - lo) * (gy1 - gy0)
        mins = [p[1].get("minerando") == "sim" for p in pts]   # trechos minerando: faixa de fundo destacada
        off0 = JANELA - len(mins)
        i0 = None
        for i, m in enumerate(mins + [False]):
            if m and i0 is None:
                i0 = i
            elif not m and i0 is not None:
                xa = gx0 + (gx1 - gx0) * (i0 + off0) / (JANELA - 1)
                xb = gx0 + (gx1 - gx0) * (i - 1 + off0) / (JANELA - 1)
                dr.rectangle((xa, gy0, max(xa + 1, xb), gy1), fill=(16, 44, 30))
                i0 = None
        n = JANELA
        for nome, s, cor in series:
            trecho = []
            for i, val in enumerate(list(s)[-n:] + [None]):
                if val is None:
                    if len(trecho) > 1:
                        dr.line(trecho, fill=cor, width=2)
                    trecho = []
                else:
                    off = n - len(s)
                    trecho.append((gx0 + (gx1 - gx0) * (i + off) / (n - 1), Y(val)))
        txt((x1 - 14, yg0 + 22), f"{lo + pad:.1f} a {hi - pad:.1f}{unid}", F("jb", 15, "Regular"), SUB, "rs")
        xl = x0 + 14 + dr.textlength(titulo, font=F("rb", 19)) + 14
        for nome, _, cor in series:
            txt((xl, yg0 + 22), nome, F("jb", 16), cor)
            xl += dr.textlength(nome, font=F("jb", 16)) + 12
        txt((gx0, yg1 + 20), "-15 min", F("jb", 14, "Regular"), SUB)
        txt((gx1, yg1 + 20), "agora", F("jb", 14, "Regular"), SUB, "rs")

    serie = lambda k: [p[1][k] if not (k == "entrada_V" and p[1]["status"].startswith("OB")) else None for p in pts]
    grafico(20, 432, "TENSÃO", [("ENTRADA", serie("entrada_V"), VERDE), ("SAÍDA", serie("saida_V"), BRANCO)], unid=" V")
    grafico(444, 846, "POTÊNCIA", [("W", serie("potencia_W"), VERDE)], vmin=0, unid=" W")
    grafico(858, 1260, "BATERIA", [("V", serie("bateria_V"), VERDE)], unid=" V")

    # ---- rodapé
    pasta = str(reg.pasta).replace(str(Path.home()), "~")
    modelo = f"Ragtech {d['modelo']} fw {d['firmware']} | " if d else ""
    estado = f"{modelo}a cada {intervalo:g} s | {reg.leituras} leituras, {reg.falhas} falhas | log {pasta}/nobreak-{reg.dia}.csv"
    if erro:
        estado = f"ÚLTIMA LEITURA FALHOU: {erro}"
    fr = F("jb", 14, "Regular")
    b = dr.textbbox((20, 714), estado, font=fr, anchor="ls")
    txt((20, 714), estado, fr, VERMELHO if erro else SUB)
    if reg.eventos:                                   # último evento à direita, só no espaço que sobra
        ev = reg.eventos[-1]
        while ev and dr.textlength(ev, font=fr) > 1260 - b[2] - 24:
            ev = ev[:-1]
        txt((1260, 714), ev, fr, AMBAR, "rs")
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
    ap.add_argument("--leitor", default=str(LEITOR_PADRAO))
    ap.add_argument("--turing", default=str(TURING_PADRAO))
    ap.add_argument("--previa", help="grava um quadro em PNG e sai (não usa a tela)")
    ap.add_argument("--demo", action="store_true", help="dados de demonstração")
    ap.add_argument("--sem-tela", action="store_true", help="só lê e grava o log")
    ap.add_argument("--mineradores", default=os.environ.get("NOBREAK_MINERADORES", ",".join(MINERADORES)),
                    help="nomes de processo de mineração, separados por vírgula")
    a = ap.parse_args()

    ESTADO.mkdir(parents=True, exist_ok=True)
    F = Fontes(a.turing)
    fonte = Demo() if a.demo else Nobreak(a.leitor, a.va)
    reg = Registro(ESTADO / ("demo" if a.demo else ""))
    mina = Mineracao(a.mineradores.split(","))
    minerando = lambda: fonte.minerando if a.demo else mina.ativa()

    if a.previa:
        n = 600 if a.demo else 3
        d, erro = None, None
        for _ in range(n):
            d, erro = fonte.ler()
            m = minerando()
            if d:
                d = reg.anotar(d, m, mina.qual) if not a.demo else _anotar_demo(reg, d, m)
        fonte.fechar()
        desenhar(reg, F, d, erro, a.intervalo, m, mina.qual).save(a.previa)
        log(f"prévia gravada: {a.previa}" + (f" | erro: {erro}" if erro else ""))
        return 0

    lcd = None
    if not a.sem_tela:
        lcd = abrir_tela(a.turing, a.brilho)
        log("tela de 5,2\" aberta em paisagem (1280x720)")
    log(f"lendo o nobreak a cada {a.intervalo:g} s; log em {ESTADO}")
    ultimo = None
    try:
        while True:
            t0 = time.time()
            d, erro = fonte.ler()
            m = minerando()
            if d:
                ultimo = reg.anotar(d, m, mina.qual)
            else:
                reg.falha(erro)
            if lcd:
                try:
                    lcd.DisplayPILImage(desenhar(reg, F, ultimo if d else None, erro, a.intervalo, m, mina.qual))
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
        fonte.fechar()
    return 0


def _anotar_demo(reg, d, m):
    """Na demonstração, espalha as leituras pelos últimos 15 min sem gravar o CSV real."""
    reg._csv = lambda d: None
    return reg.anotar(d, m, "xmrig")


if __name__ == "__main__":
    sys.exit(main())
