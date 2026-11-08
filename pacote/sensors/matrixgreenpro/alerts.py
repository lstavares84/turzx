# MATRIX GREEN PRO | versão 2.1.0 | 07/11/2026 21:00 (-03) | Confirma (subida só após 2 s) e Sustentado (limite por 5 min)
# histórico: 2.0.0 31/10/2026 23:05 V2: paleta preto/branco/verde/amarelo, N/D neutro
# histórico: 1.0.0 31/10/2026 22:40 criação inicial
# Estados visuais e histerese (evita piscar entre verde/amarelo/vermelho).

OK, WARN, CRIT, NA, LOST = 0, 1, 2, 3, 4
# NA   = sensor inexistente no hardware (cinza claro, não é alerta nem saudável)
# LOST = sensor que existia e deixou de responder ou dado desatualizado (amarelo)

PALETTE = {
    "bg": (0x00, 0x00, 0x00),      # fundo principal
    "bg2": (0x07, 0x10, 0x07),     # fundo secundário (faixa do cabeçalho, trilho das barras)
    "white": (0xFF, 0xFF, 0xFF),   # rótulos de seção e números neutros
    "green": (0x00, 0xFF, 0x00),   # identidade + estado saudável
    "yellow": (0xFF, 0xD0, 0x00),  # atenção (e um único detalhe de identidade: "PRO")
    "red": (0xFF, 0x30, 0x30),     # exclusivamente crítico
    "div": (0x17, 0x40, 0x17),     # divisórias
    "aux": (0xB0, 0xB8, 0xB0),     # textos auxiliares e N/D
}

# NEUTRAL = número sem semântica de saúde (frequência, carga, tráfego...)
NEUTRAL = 9

LEVEL_COLOR = {
    OK: PALETTE["green"],
    WARN: PALETTE["yellow"],
    CRIT: PALETTE["red"],
    NA: PALETTE["aux"],
    LOST: PALETTE["yellow"],
    NEUTRAL: PALETTE["white"],
}


def color(level):
    return LEVEL_COLOR.get(level, PALETTE["white"])


def worst(levels):
    """Pior nível de um grupo para o trilho lateral da seção (N/D e neutros não pioram)."""
    lv = [x for x in levels if x in (OK, WARN, CRIT, LOST)]
    if not lv:
        return NA
    if CRIT in lv:
        return CRIT
    if WARN in lv or LOST in lv:
        return WARN
    return OK


class Hyst:
    """Classificador com histerese: sobe de nível ao atingir o limite e só
    desce quando o valor recua 'hyst' unidades abaixo dele."""

    def __init__(self, warn, crit, hyst=2.0):
        self.warn = None if warn is None else float(warn)
        self.crit = None if crit is None else float(crit)
        self.hyst = float(hyst)
        self.level = OK

    def set_limits(self, warn, crit):
        self.warn = None if warn is None else float(warn)
        self.crit = None if crit is None else float(crit)

    def update(self, value):
        if value is None:
            self.level = OK
            return NA
        v = float(value)
        lvl = self.level
        # subida imediata
        if self.crit is not None and v >= self.crit:
            lvl = CRIT
        elif self.warn is not None and v >= self.warn and lvl < WARN:
            lvl = WARN
        # descida somente após recuar a margem de histerese
        if lvl == CRIT and (self.crit is None or v < self.crit - self.hyst):
            lvl = WARN
        if lvl == WARN and (self.warn is None or v < self.warn - self.hyst):
            lvl = OK
        self.level = lvl
        return lvl


class Streak:
    """Conta falhas consecutivas (ex.: ping) para não alarmar por um pacote perdido."""

    def __init__(self, warn_after=1, crit_after=3):
        self.n = 0
        self.warn_after, self.crit_after = warn_after, crit_after

    def update(self, failed):
        self.n = self.n + 1 if failed else 0
        if self.n >= self.crit_after:
            return CRIT
        if self.n >= self.warn_after:
            return WARN
        return OK


class Confirma:
    """Filtro contra ruído de leitura: o nível só SOBE depois de se manter por 'seg' segundos; desce na hora
    (a descida já tem a histerese da Hyst). A primeira leitura vale de imediato (início do painel)."""

    def __init__(self, seg=2.0):
        self.seg = float(seg)
        self.nivel, self.cand, self.desde = None, None, None

    def update(self, lv, now):
        if lv not in (OK, WARN, CRIT):
            self.nivel = self.cand = None
            return lv
        if self.nivel is None or lv <= self.nivel:
            self.nivel, self.cand = lv, None
            return lv
        if self.cand != lv:
            self.cand, self.desde = lv, now
        if now - self.desde >= self.seg:
            self.nivel, self.cand = lv, None
        return self.nivel


class Sustentado:
    """Aviso quando o valor fica no limite ou acima dele por 'janela' segundos seguidos (ex.: CPU 90 % por 5 min)."""

    def __init__(self, limite, janela=300.0):
        self.limite, self.janela = float(limite), float(janela)
        self.desde = None

    def update(self, valor, now):
        if valor is None:
            self.desde = None
            return NA
        if float(valor) < self.limite:
            self.desde = None
            return OK
        if self.desde is None:
            self.desde = now
        return WARN if now - self.desde >= self.janela else OK
