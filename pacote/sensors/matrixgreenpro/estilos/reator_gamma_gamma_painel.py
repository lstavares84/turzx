# GAMMA GAMMA PAINEL | versão 1.4.0 | 02/11/2026 22:10 (-03) | criação original (Claude, para Lucas Tavares)
# Base GAMMA BETA, reorganizada por grupos (CPU, GPU, RAM, DISCOS, REFRIGERAÇÃO, REDE, SISTEMA): colmeia de 24 células; o texto traz só o que não cabe nela.
from .reator_gamma import GAMMA
from .reator_grupos import render_grupos

P = dict(GAMMA, alert="n3_esq", pct="paren", flow=True, cool=True, temps=True)


def draw_frame(vm_dict):
    return render_grupos(vm_dict, P, "painel")
