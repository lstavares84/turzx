# GAMMA GAMMA COLMEIA | versão 1.4.0 | 02/11/2026 22:10 (-03) | criação original (Claude, para Lucas Tavares)
# Base GAMMA BETA, reorganizada por grupos (CPU, GPU, RAM, DISCOS, REFRIGERAÇÃO, REDE, SISTEMA): uma colmeia de 19 células, cada grupo numa região contígua.
from .reator_gamma import GAMMA
from .reator_grupos import render_grupos

P = dict(GAMMA, alert="n3_esq", pct="paren", flow=True, cool=True, temps=True)


def draw_frame(vm_dict):
    return render_grupos(vm_dict, P, "colmeia")
