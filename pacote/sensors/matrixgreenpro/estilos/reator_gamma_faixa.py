# MATRIX GREEN PRO | estilo GAMMA FAIXA (variante de alerta) | versão 3.3.0 | 02/11/2026 18:05 (-03) | criação original
# GAMMA com o indicador de aviso e alerta redesenhado: proposta: escala de 31 marcas na largura toda, sob o cabeçalho.
# Em CRÍTICO o vermelho pisca (1 s aceso, 1 s apagado).
from .reator import render
from .reator_gamma import GAMMA

P = dict(GAMMA, alert="faixa")


def draw_frame(vm_dict):
    return render(vm_dict, P, "favo19")
