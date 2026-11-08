# GAMMA DELTA 5B | versão 0.4.0 | 07/11/2026 21:00 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 0.4.0 07/11/2026 21:00 sem marca de variação (alertas só por limites absolutos); LOG de alertas; hexágono centrado entre as linhas RAM e TERRAMASTER
# histórico: 0.3.0 07/11/2026 20:50 hexágono sem o texto ao lado; barra da RAM segmentada; 0.2.0 07/11/2026 20:45 hexágono e barra da RAM
# Base: GAMMA DELTA 5 (registro com barras, marca invertida). Com LOG no lugar de REGISTRO, INTERNET ON/OFF e os
# rótulos dos gráficos girados 90° (gráficos mais largos). Espaço dos discos: rosca do total à direita das linhas dos discos.
from .reator_delta2 import render
from .reator_gamma_delta import P as P_DELTA

P = dict(P_DELTA, selo="DELTA 5B", total="rosca", registro="barras", marca="nenhuma", nome_log="LOG", rosca_hex=True, ram_barra=True,
         inet_onoff=True, rotulos_rot=True)


def draw_frame(vm_dict):
    return render(vm_dict, P)
