# GAMMA DELTA variante 1 | versão 0.1.0 | 07/11/2026 20:25 (-03) | criação original (Claude, para Lucas Tavares)
# total à direita dos discos, registro à esquerda, marca em âmbar. Motor em reator_delta2.py.
from .reator_delta2 import render
from .reator_gamma_delta import P_BASE as P_DELTA

P = dict(P_DELTA, selo="DELTA 1", total="coluna", registro="esq", marca="cor", total_grande=False)


def draw_frame(vm_dict):
    return render(vm_dict, P)
