# GAMMA DELTA variante 5 | versão 0.1.0 | 07/11/2026 20:25 (-03) | criação original (Claude, para Lucas Tavares)
# total no título DISCOS, registro com barras, marca invertida. Motor em reator_delta2.py.
from .reator_delta2 import render
from .reator_gamma_delta import P as P_DELTA

P = dict(P_DELTA, selo="DELTA 5", total="titulo", registro="barras", marca="inverso", total_grande=False)


def draw_frame(vm_dict):
    return render(vm_dict, P)
