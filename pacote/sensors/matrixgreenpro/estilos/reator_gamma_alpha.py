# GAMMA ALPHA | versão 1.4.0 | 02/11/2026 22:00 (-03) | novo nome (ex GAMMA SENTINELA)
# histórico: 1.3.0 02/11/2026 21:50 bomba, ventoinhas e temperaturas
# histórico: 1.0.0 02/11/2026 20:10 | criação original
# histórico: 3.5.0 02/11/2026 19:05 gamma-n3-esq | 3.4.0 02/11/2026 18:40 criação
# A sentinela do sistema: escala de estado N0 NORMAL, N1 AVISO e N2 ALERTA no canto superior esquerdo,
# sem tarja (só a barra e o nome brilhando) e sem LIVE; em N2 a barra e o nome piscam (1 s aceso, 1 s apagado).
# Mostra o percentual de uso de RAM, VRAM e discos no registro.
from .reator import render
from .reator_gamma import GAMMA

P = dict(GAMMA, selo="ALPHA", alert="n3_esq", pct=True, cool=True, temps=True)    # cool: bomba e ventoinhas; temps: PLACA, RAM, SSD


def draw_frame(vm_dict):
    return render(vm_dict, P, "favo19")
