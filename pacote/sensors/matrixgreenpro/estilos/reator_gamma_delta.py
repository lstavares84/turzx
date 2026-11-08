# GAMMA DELTA | versão 2.0.0 | 07/11/2026 21:14 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 2.0.0 07/11/2026 21:14 o desenho estudado como DELTA 5B vira o GAMMA DELTA (lançamento 1.8.0)
# histórico: 1.1.0 07/11/2026 19:40 3 gráficos de 24 h com o pico marcado por um ponto (graficos.py)
# histórico: 1.0.0 07/11/2026 19:00 criação
# GAMMA DELTA: derivado do GAMMA GAMMA, com a colmeia à direita e, no espaço livre do alto, 3 gráficos de 24 h
# (temperatura de CPU e GPU; VRAM com RAM; rede com download e upload), nomes girados 90° e o pico de cada série
# marcado por um ponto. Valor em alerta aparece com fundo âmbar ou vermelho. RAM com barra de uso no título,
# total de todos os HDs num hexágono que se enche com o uso, baias do TerraMaster com uso, refrigeração numa
# linha (SQUAMA INF e LAT em série), INTERNET ON/OFF e LOG dos alertas (mudanças de cor) no rodapé.
# Motor em reator_delta2.py. P_BASE guarda os parâmetros comuns, usados também pelas variantes de estudo.
import math

from . import graficos
from .reator_gamma import GAMMA
from .reator_delta2 import render

R, GAP = 21, 2
COLMEIA_X = 314 - (math.sqrt(3) * R + GAP) - math.sqrt(3) * R / 2      # centro da colmeia com a borda direita em 314
P_BASE = dict(GAMMA, selo="DELTA", alert="n3_esq", pct="paren", flow=True, cool=True, temps=True,
              colmeia_x=COLMEIA_X, texto_y=137 + 14, baias_uso=True, rodape_enxuto=True,
              extra=graficos.desenhar, pico="marcador")
P = dict(P_BASE, total="rosca", rosca_hex=True, ram_barra=True, registro="barras", nome_log="LOG", marca="nenhuma",
         alerta_inverso=True, inet_onoff=True, rotulos_rot=True)


def draw_frame(vm_dict):
    return render(vm_dict, P)
