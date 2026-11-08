# MATRIX GREEN PRO | versão 2.2.0 | 07/11/2026 21:46 (-03) | alerta fica no mínimo 5 min; Hyst com limite estrito (acima de)
# histórico: 2.1.0 07/11/2026 21:00 Confirma (subida só após 2 s) e Sustentado (limite por 5 min)
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

    def __init__(self, warn, crit, hyst=2.0, estrito=False):
        self.warn = None if warn is None else float(warn)
        self.crit = None if crit is None else float(crit)
        self.hyst = float(hyst)
        self.estrito = estrito          # True: o limite é "acima de" (ex.: ping verde até 20 ms, inclusive)
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
        passa = (lambda lim: v > lim) if self.estrito else (lambda lim: v >= lim)
        abaixo = (lambda lim: v <= lim - self.hyst) if self.estrito else (lambda lim: v < lim - self.hyst)
        # subida imediata
        if self.crit is not None and passa(self.crit):
            lvl = CRIT
        elif self.warn is not None and passa(self.warn) and lvl < WARN:
            lvl = WARN
        # descida somente após recuar a margem de histerese
        if lvl == CRIT and (self.crit is None or abaixo(self.crit)):
            lvl = WARN
        if lvl == WARN and (self.warn is None or abaixo(self.warn)):
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
    """Filtro do nível de alerta:
    - contra ruído: o nível só SOBE depois de se manter por 'seg' segundos (0 = na hora, para leituras lentas);
    - para dar tempo de ver: âmbar e vermelho ficam no mínimo 'manter' segundos; depois disso o nível acompanha a
      leitura (volta ao verde assim que ela estiver normal).
    A primeira leitura vale de imediato (início do painel)."""

    def __init__(self, seg=2.0, manter=300.0):
        self.seg, self.manter = float(seg), float(manter)
        self.nivel, self.cand, self.desde, self.acendeu = None, None, None, 0.0

    def _fixa(self, lv, now):
        if lv != self.nivel and lv in (WARN, CRIT):
            self.acendeu = now                       # cada mudança para âmbar ou vermelho reinicia a permanência
        self.nivel, self.cand = lv, None

    def update(self, lv, now):
        if lv not in (OK, WARN, CRIT):
            self.nivel = self.cand = None
            return lv
        if self.nivel is None:
            self._fixa(lv, now)
            return lv
        if lv > self.nivel:                          # subida: confirma por 'seg' segundos
            if self.cand != lv:
                self.cand, self.desde = lv, now
            if now - self.desde >= self.seg:
                self._fixa(lv, now)
        elif lv < self.nivel:                        # descida: só depois da permanência mínima
            self.cand = None
            if now - self.acendeu >= self.manter:
                self._fixa(lv, now)
        else:
            self.cand = None
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
