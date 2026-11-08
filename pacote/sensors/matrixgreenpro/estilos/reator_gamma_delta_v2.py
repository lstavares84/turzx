# GAMMA DELTA variante 2 | versão 0.1.0 | 07/11/2026 20:25 (-03) | criação original (Claude, para Lucas Tavares)
# total no título DISCOS, registro na largura toda, marca sublinhada. Motor em reator_delta2.py.
from .reator_delta2 import render
from .reator_gamma_delta import P_BASE as P_DELTA

P = dict(P_DELTA, selo="DELTA 2", total="titulo", registro="faixa", marca="sublinhado", total_grande=False)


def draw_frame(vm_dict):
    return render(vm_dict, P)
