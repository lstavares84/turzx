# GAMMA | estilos selecionáveis | versão 1.7.0 | 07/11/2026 18:40 (-03) | variante de estudo GAMMA GAMMA COLUNA
# histórico: 1.5.0 02/11/2026 22:45 GAMMA GAMMA definitivo (7 colmeias de resumo)
# histórico: 1.4.0 02/11/2026 22:00 GAMMA ALPHA, BETA e GAMMA (3 variantes)
# histórico: 1.0.0 02/11/2026 20:10 GAMMA SENTINELA e GAMMA DOSÍMETRO
# histórico: 3.6.0 02/11/2026 19:40 gamma-n3-compacto
# histórico: 3.4.0 02/11/2026 18:40 escalas N0/N1/N2
# histórico: 3.3.0 02/11/2026 18:05 GAMMA, variantes e indicadores de alerta
# histórico: 3.2.0 02/11/2026 17:40 GAMMA e três variantes
# histórico: 3.1.0 01/11/2026 10:45 finalistas 06-A e 13-C | 3.1.0-alfa 09:30 famílias 06 e 13 | 3.0.0-alfa catálogo
# O estilo é escolhido em ~/.config/matrixgreenpro/config.yaml (painel.estilo).
# Todos usam o mesmo modelo de visão (métricas, saúde e coleta idênticas).
ESTILOS = {
    "matrix": ("MATRIX GREEN PRO", None),                         # desenho da versão 2.1.0 (render.py)
    "gamma": ("GAMMA", "reator_gamma"),
    "gamma-sonar": ("GAMMA SONAR", "reator_gamma_sonar"),
    "gamma-raiox": ("GAMMA RAIO-X", "reator_gamma_raiox"),
    "gamma-uv": ("GAMMA ULTRAVIOLETA", "reator_gamma_uv"),
    "gamma-escala": ("GAMMA ESCALA", "reator_gamma_escala"),
    "gamma-barra": ("GAMMA BARRA", "reator_gamma_barra"),
    "gamma-banner": ("GAMMA BANNER", "reator_gamma_banner"),
    "gamma-faixa": ("GAMMA FAIXA (proposta)", "reator_gamma_faixa"),
    "gamma-n3": ("GAMMA N3 DIREITA", "reator_gamma_n3"),
    "gamma-n3-abas": ("GAMMA N3 ABAS", "reator_gamma_n3_abas"),
    "gamma-n3-linha": ("GAMMA N3 LINHA", "reator_gamma_n3_linha"),
    "gamma-alpha": ("GAMMA ALPHA", "reator_gamma_alpha"),                 # ex GAMMA SENTINELA
    "gamma-beta": ("GAMMA BETA", "reator_gamma_beta"),                    # ex GAMMA DOSÍMETRO
    "gamma-gamma-colmeia": ("GAMMA GAMMA COLMEIA", "reator_gamma_gamma_colmeia"),
    "gamma-gamma-mini": ("GAMMA GAMMA MINI", "reator_gamma_gamma_mini"),
    "gamma-gamma-painel": ("GAMMA GAMMA PAINEL", "reator_gamma_gamma_painel"),
    "gamma-gamma-coluna": ("GAMMA GAMMA COLUNA", "reator_gamma_gamma_coluna"),   # hexágonos em coluna, ao lado de cada grupo
    "gamma-gamma": ("GAMMA GAMMA", "reator_gamma_gamma"),                  # 7 colmeias de resumo, CORE no centro
    "gamma-n3-eventos": ("GAMMA N3 EVENTOS", "reator_gamma_n3_eventos"),
    "pcb": ("13-C PLACA DE CIRCUITO", "blueprint_pcb"),
}
ALIASES = {"uranio": "gamma", "urânio": "gamma",                  # nomes antigos continuam valendo
           "gamma-n3-esq": "gamma-alpha", "gamma-n3-compacto": "gamma-beta",
           "gamma-sentinela": "gamma-alpha", "gamma-dosimetro": "gamma-beta",
           "gamma-gamma-fronteira": "gamma-gamma"}


def renderer(nome):
    """Retorna função vm -> PIL.Image para o estilo pedido (padrão: matrix)."""
    import importlib
    nome = str(nome or "matrix").lower()
    nome = ALIASES.get(nome, nome)
    if nome not in ESTILOS:
        nome = "matrix"
    mod = ESTILOS[nome][1]
    if mod is None:
        from ..render import draw_frame
        return nome, lambda vm: draw_frame(vm)[0]
    fn = importlib.import_module(f"{__name__}.{mod}").draw_frame
    return nome, lambda vm: fn(vm)[0].img
