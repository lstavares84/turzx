# GAMMA DELTA variante 4 | versão 0.1.0 | 07/11/2026 20:25 (-03) | criação original (Claude, para Lucas Tavares)
# total grande à direita dos discos, registro à direita, marca com ponto. Motor em reator_delta2.py.
from .reator_delta2 import render
from .reator_gamma_delta import P_BASE as P_DELTA

P = dict(P_DELTA, selo="DELTA 4", total="coluna", registro="dir", marca="ponto", total_grande=True)


def draw_frame(vm_dict):
    return render(vm_dict, P)
