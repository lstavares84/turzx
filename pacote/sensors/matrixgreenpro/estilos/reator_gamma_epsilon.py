# GAMMA EPSILON | versão 1.0.0 | 15/11/2026 09:40 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.0.0 15/11/2026 09:40 criação: GAMMA DELTA com rotação de telas e tela de andamento do backup
# GAMMA EPSILON: o GAMMA DELTA como tela principal e mais duas telas que se alternam (rotacao.periodo_s, padrão
# 60 s): gráficos de 24 h e status das rotinas de backup. Enquanto um backup roda, a tela mostra o andamento e
# volta à rotação quando ele termina. Alerta vermelho fixa a principal (passa na frente do backup); alerta âmbar
# fixa a principal quando não há backup rodando. Telas em epsilon_telas.py; a principal em reator_delta2.py.
from . import epsilon_telas as T
from .reator_delta2 import render
from .reator_gamma_delta import P as P_DELTA

P = dict(P_DELTA, selo="EPSILON")


def draw_frame(vm_dict, agora=None):
    tela, telas = T.escolher(vm_dict, agora)
    if tela == "principal":
        c, v = render(vm_dict, P)
    else:
        c, v = getattr(T, tela)(vm_dict, P)[:2]
    from .reator_grupos import _base  # noqa: F401  (mesmas fontes do cabeçalho)
    from .base import font, JB
    T.indicador(c, P, {"xs": font(JB, 11, "Regular")}, tela, telas)
    if tela != "principal":
        T._topo(c, v, P, {"xs": font(JB, 11, "Regular")}, tela, telas)
    return c, v
