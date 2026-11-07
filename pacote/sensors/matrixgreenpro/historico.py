# MATRIX GREEN PRO | historico.py | versão 1.2.0 | 07/11/2026 19:40 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.2.0 07/11/2026 19:40 capacidade de VRAM e RAM nas séries (pico em GB)
# histórico: 1.1.0 07/11/2026 19:30 temperaturas de CPU e GPU; máximo de cada intervalo (para o pico de 24 h)
# histórico: 1.0.0 07/11/2026 19:10 criação: VRAM, RAM e rede
# Histórico das últimas 24 h para os gráficos do GAMMA DELTA: temperatura da CPU e da GPU (°C), VRAM e RAM (%)
# e rede (download e upload, B/s). O dia é dividido em N intervalos iguais (um por pixel do gráfico); cada
# intervalo guarda a média (a linha) e o máximo (o pico) das leituras.
# Grava em ~/.local/state/matrixgreenpro/historico.json quando um intervalo fecha, para sobreviver a reinícios.
# Intervalo sem leitura (PC desligado, sensor ausente) fica None e aparece como falha na linha.
import json
import math
import os
import random
import time

JANELA = 24 * 3600
N = 148                                     # intervalos, um por pixel do gráfico (9,7 min cada)
CHAVES = ("cpu_t", "gpu_t", "vram", "ram", "down", "up")
ARQUIVO = os.environ.get("MGP_HISTORICO") or os.path.expanduser("~/.local/state/matrixgreenpro/historico.json")


def _capacidade(s):
    """Capacidade atual de VRAM e RAM em GB (para mostrar o pico em GB a partir do percentual guardado)."""
    g, r = s.get("gpu") or {}, s.get("ram") or {}
    return {"vram_total": g.get("vram_total") or None, "ram_total": r.get("total") or None}


def _leitura(s):
    """Valores do snapshot que entram no histórico (None quando não há dado)."""
    c, g, r, n = s.get("cpu") or {}, s.get("gpu") or {}, s.get("ram") or {}, s.get("net") or {}
    vram = None
    if g.get("vram_used") is not None and g.get("vram_total"):
        vram = 100.0 * g["vram_used"] / g["vram_total"]
    ram = r.get("pct") if r.get("total") else None
    return {"cpu_t": c.get("temp"), "gpu_t": g.get("temp"), "vram": vram, "ram": ram,
            "down": n.get("down"), "up": n.get("up")}


class Historico:
    def __init__(self, arquivo=ARQUIVO, n=N, janela=JANELA):
        self.arquivo, self.n, self.passo = arquivo, n, janela / n
        self.b = {}                          # índice do intervalo -> {chave: [soma, contagem, máximo]}
        self.atual = None
        self.cap = {}
        self._carregar()

    def _carregar(self):
        try:
            with open(self.arquivo, encoding="utf-8") as f:
                d = json.load(f)
            if abs(float(d.get("passo", 0)) - self.passo) < 1e-6:
                self.b = {int(k): v for k, v in d.get("b", {}).items()}
        except Exception:
            self.b = {}

    def _gravar(self):
        try:
            os.makedirs(os.path.dirname(self.arquivo), exist_ok=True)
            tmp = self.arquivo + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"passo": self.passo, "b": self.b}, f)
            os.replace(tmp, self.arquivo)    # troca atômica: nunca fica um arquivo pela metade
        except Exception:
            pass

    def add(self, s, t=None):
        """Acrescenta as leituras do snapshot e devolve as séries para desenhar."""
        t = time.time() if t is None else t
        i = int(t // self.passo)
        if self.atual is not None and i != self.atual:
            for k in [k for k in self.b if k <= i - self.n]:
                del self.b[k]
            self._gravar()
        self.atual = i
        self.cap = _capacidade(s)
        acc = self.b.setdefault(i, {})
        for k, x in _leitura(s).items():
            if x is not None:
                a = acc.setdefault(k, [0.0, 0, float(x)])
                if len(a) < 3:                                  # arquivo da versão 1.0.0 (sem máximo)
                    a.append(a[0] / a[1] if a[1] else float(x))
                a[0] += float(x)
                a[1] += 1
                a[2] = max(a[2], float(x))
        return self.series(t)

    def series(self, t=None):
        """{chave: médias, chave_max: máximos} dos últimos N intervalos (o último é o atual)."""
        t = time.time() if t is None else t
        i = int(t // self.passo)
        out = {k: [] for k in CHAVES}
        out.update({k + "_max": [] for k in CHAVES})
        for j in range(i - self.n + 1, i + 1):
            acc = self.b.get(j, {})
            for k in CHAVES:
                a = acc.get(k)
                ok = a and a[1]
                out[k].append(a[0] / a[1] if ok else None)
                out[k + "_max"].append((a[2] if len(a) > 2 else a[0] / a[1]) if ok else None)
        out["passo"] = self.passo
        out.update(self.cap)
        return out


def demo_series(s, scenario="normal", n=N):
    """Séries DEMONSTRATIVAS de 24 h (sempre as mesmas): terminam nos valores atuais do snapshot de demonstração.
    Desenho: madrugada calma, trabalho de dia, jogo à noite; a rede tem picos de download."""
    rnd = random.Random({"normal": 1, "atencao": 2, "critico": 3}.get(scenario, 1))
    agora = _leitura(s)
    out = {k: [] for k in CHAVES}
    out.update({k + "_max": [] for k in CHAVES})
    for j in range(n):
        h = 24.0 * j / n                                    # 0 = 24 h atrás, n-1 = agora
        noite = math.exp(-((h - 20.5) / 2.2) ** 2)           # jogo à noite
        dia = 0.5 + 0.5 * math.sin((h - 6) / 24 * 2 * math.pi)
        if 5.0 <= h < 6.2:                                  # o PC ficou desligado por ~1 h
            for k in out:
                out[k].append(None)
            continue
        val = {"cpu_t": 38 + 10 * dia + 30 * noite + rnd.uniform(-2, 2),
               "gpu_t": 34 + 6 * dia + 36 * noite + rnd.uniform(-1.5, 1.5),
               "vram": min(99.0, 12 + 18 * dia + 60 * noite + rnd.uniform(-3, 3)),
               "ram": min(99.0, 28 + 10 * dia + 14 * noite + rnd.uniform(-1.5, 1.5))}
        pico = rnd.random() < 0.06
        val["down"] = max(0.0, (0.3e6 + 2.5e6 * dia + (rnd.uniform(8e6, 22e6) if pico else 0)) * rnd.uniform(0.6, 1.4))
        val["up"] = max(0.0, (0.08e6 + 0.5e6 * dia + (rnd.uniform(1e6, 3e6) if pico else 0)) * rnd.uniform(0.6, 1.4))
        for k, x in val.items():
            out[k].append(x)
            folga = rnd.uniform(1.2, 2.2) if k in ("down", "up") else 1.0
            out[k + "_max"].append(min(99.0, x + rnd.uniform(0, 4)) if k in ("vram", "ram") else
                                   x + rnd.uniform(0, 5) if k in ("cpu_t", "gpu_t") else x * folga)
    for k in CHAVES:                                        # último ponto = valor atual da demonstração
        if agora[k] is not None:
            out[k][-1] = agora[k]
            out[k + "_max"][-1] = max(agora[k], out[k + "_max"][-1] or 0)
    out["passo"] = JANELA / n
    out.update(_capacidade(s))
    return out
