# GAMMA | estilos selecionáveis | versão 1.15.0 | 07/11/2026 21:14 (-03) | o DELTA 5B vira o gamma-delta (apelido gamma-delta-5b)
# histórico: 1.14.0 07/11/2026 20:35 variantes 5A, 5B e 5C do GAMMA DELTA
# histórico: 1.13.0 07/11/2026 20:25 6 variantes do GAMMA DELTA (gamma-delta-1 a 6)
# histórico: 1.12.0 07/11/2026 20:00 12 propostas da v2.0.0 (v2-*)
# histórico: 1.11.0 07/11/2026 19:40 GAMMA DELTA com 3 gráficos de 24 h e pico marcado
# histórico: 1.10.0 07/11/2026 19:30 opções de pico p1, p2, p3
# histórico: 1.9.0 07/11/2026 19:15 propostas de gráficos do GAMMA DELTA (3g e 2g)
# histórico: 1.8.0 07/11/2026 19:00 GAMMA DELTA (derivado do GAMMA GAMMA) e GAMMA GAMMA COLUNA
# histórico: 1.7.0 07/11/2026 18:40 variante de estudo GAMMA GAMMA COLUNA
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
    "gamma-gamma-coluna": ("GAMMA GAMMA COLUNA", "reator_gamma_gamma_coluna"),   # estudo: hexágonos em coluna
    "gamma-delta": ("GAMMA DELTA", "reator_gamma_delta"),                  # o antigo estudo DELTA 5B (apelido gamma-delta-5b)
    # variantes do DELTA: total de TB, mudanças bruscas, refrigeração numa linha e registro (reator_delta2.py)
    "gamma-delta-1": ("GAMMA DELTA 1", "reator_gamma_delta_v1"),
    "gamma-delta-2": ("GAMMA DELTA 2", "reator_gamma_delta_v2"),
    "gamma-delta-3": ("GAMMA DELTA 3", "reator_gamma_delta_v3"),
    "gamma-delta-4": ("GAMMA DELTA 4", "reator_gamma_delta_v4"),
    "gamma-delta-5": ("GAMMA DELTA 5", "reator_gamma_delta_v5"),
    "gamma-delta-6": ("GAMMA DELTA 6", "reator_gamma_delta_v6"),
    "gamma-delta-5a": ("GAMMA DELTA 5A", "reator_gamma_delta_v5a"),
    "gamma-delta-5c": ("GAMMA DELTA 5C", "reator_gamma_delta_v5c"),
    "gamma-gamma": ("GAMMA GAMMA", "reator_gamma_gamma"),                  # 7 colmeias de resumo, CORE no centro
    "gamma-n3-eventos": ("GAMMA N3 EVENTOS", "reator_gamma_n3_eventos"),
    "pcb": ("13-C PLACA DE CIRCUITO", "blueprint_pcb"),
    # propostas da v2.0.0 (mesma paleta, desenho novo); não entram nos ZIPs
    "v2-concreto": ("v2 BRUTALISTA: CONCRETO", "v2_brutal"),
    "v2-silencio": ("v2 MINIMALISTA: SILÊNCIO", "v2_minimal"),
    "v2-hud": ("v2 SCI-FI: HUD ORBITAL", "v2_scifi"),
    "v2-root": ("v2 HACKING: ROOT", "v2_hacking"),
    "v2-dossie": ("v2 ESPIONAGEM: DOSSIÊ", "v2_espiao"),
    "v2-vital": ("v2 UTI: MONITOR VITAL", "v2_uti"),
    "v2-cockpit": ("v2 COCKPIT: PAINEL DE VOO", "v2_cockpit"),
    "v2-metro": ("v2 METRÔ: LINHA GAMMA", "v2_metro"),
    "v2-anunciador": ("v2 SALA DE CONTROLE: ANUNCIADOR", "v2_anunciador"),
    "v2-8bits": ("v2 ARCADE: 8 BITS", "v2_arcade"),
    "v2-osciloscopio": ("v2 LABORATÓRIO: OSCILOSCÓPIO", "v2_osciloscopio"),
    "v2-grade": ("v2 SUÍÇO: GRADE", "v2_suico"),
}
ALIASES = {"uranio": "gamma", "urânio": "gamma",                  # nomes antigos continuam valendo
           "gamma-n3-esq": "gamma-alpha", "gamma-n3-compacto": "gamma-beta",
           "gamma-sentinela": "gamma-alpha", "gamma-dosimetro": "gamma-beta",
           "gamma-gamma-fronteira": "gamma-gamma",
           "gamma-delta-5b": "gamma-delta"}


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
