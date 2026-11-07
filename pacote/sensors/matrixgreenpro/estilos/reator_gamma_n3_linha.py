# MATRIX GREEN PRO | estilo GAMMA N3 LINHA (variante de alerta) | versão 3.4.0 | 02/11/2026 18:40 (-03) | criação original
# GAMMA com o aviso em escala de terminal de eventos: uma linha de terminal no cabeçalho: > [N1] AVISO // OBSERVAR.
# Em CRÍTICO (N2) o vermelho pisca: 1 s aceso, 1 s apagado.
from .reator import render
from .reator_gamma import GAMMA

P = dict(GAMMA, alert="n3_linha")


def draw_frame(vm_dict):
    return render(vm_dict, P, "favo19")
