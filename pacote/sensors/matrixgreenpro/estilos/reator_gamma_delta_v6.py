# GAMMA DELTA variante 6 | versão 0.1.0 | 07/11/2026 20:25 (-03) | criação original (Claude, para Lucas Tavares)
# total com barra, registro em tabela, marca em âmbar. Motor em reator_delta2.py.
from .reator_delta2 import render
from .reator_gamma_delta import P as P_DELTA

P = dict(P_DELTA, selo="DELTA 6", total="barra", registro="tabela", marca="cor", total_grande=False)


def draw_frame(vm_dict):
    return render(vm_dict, P)
