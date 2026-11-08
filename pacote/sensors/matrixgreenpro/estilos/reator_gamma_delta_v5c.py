# GAMMA DELTA 5C | versão 0.1.0 | 07/11/2026 20:35 (-03) | criação original (Claude, para Lucas Tavares)
# Base: GAMMA DELTA 5 (registro com barras, marca invertida). Com LOG no lugar de REGISTRO, INTERNET ON/OFF e os
# rótulos dos gráficos girados 90° (gráficos mais largos). Espaço dos discos: mapa de capacidade no título: cada HD é um trecho proporcional ao tamanho, preenchido pelo uso.
from .reator_delta2 import render
from .reator_gamma_delta import P as P_DELTA

P = dict(P_DELTA, selo="DELTA 5C", total="mapa", registro="barras", marca="inverso", nome_log="LOG",
         inet_onoff=True, rotulos_rot=True)


def draw_frame(vm_dict):
    return render(vm_dict, P)
