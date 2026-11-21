# GAMMA GAMMA | versão 1.4.0 | 02/11/2026 22:45 (-03) | criação original (Claude, para Lucas Tavares)
# Base GAMMA BETA. Sete colmeias: CORE no centro e, ao redor, o resumo de CPU, GPU, RAM, DISCOS, REFR. e REDE
# (só OK, ATEN, CRIT). Os números ficam no painel abaixo, separados por grupo.
from .reator_gamma import GAMMA
from .reator_grupos import render_grupos

P = dict(GAMMA, selo="GAMMA", alert="n3_esq", pct="paren", flow=True, cool=True, temps=True)


def draw_frame(vm_dict):
    return render_grupos(vm_dict, P, "resumo")
