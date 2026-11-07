# GAMMA BETA | versão 1.5.0 | 07/11/2026 14:10 (-03) | baias do TerraMaster no rodapé (quando o gabinete existe)
# histórico: 1.4.0 02/11/2026 22:00 novo nome (ex GAMMA DOSÍMETRO)
# histórico: 1.3.0 02/11/2026 21:50 temperaturas de placa, RAM e SSD nas células
# histórico: 1.2.0 02/11/2026 21:30 BOMBA e ventoinhas (RPM)
# histórico: 1.0.0 02/11/2026 20:10 criação original
# histórico: 3.6.0 02/11/2026 19:40 gamma-n3-compacto
# Leituras como num dosímetro: a mesma sentinela N0/N1/N2 do GAMMA SENTINELA, com os percentuais entre
# parênteses, por exemplo "RAM 12.4/31.3GB (40%)", e as informações secundárias (DISP, LIVRE, LIM)
# coladas à esquerda, logo depois do uso, em vez de alinhadas na borda direita.
from .reator import render
from .reator_gamma import GAMMA

P = dict(GAMMA, selo="BETA", alert="n3_esq", pct="paren", flow=True, cool=True, temps=True, baias=True)    # cool: BOMBA e RPM; baias: 2x2 baias do gabinete no rodapé


def draw_frame(vm_dict):
    return render(vm_dict, P, "favo19")
