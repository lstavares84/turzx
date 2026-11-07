# GAMMA DELTA | versão 1.1.0 | 07/11/2026 19:40 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.1.0 07/11/2026 19:40 3 gráficos de 24 h com o pico marcado por um ponto (graficos.py)
# histórico: 1.0.0 07/11/2026 19:00 criação
# Derivado do GAMMA GAMMA (mesmo motor, reator_grupos.py), com quatro mudanças pedidas pelo Lucas:
#   TERRAMASTER com ocupado/total e percentual nas baias montadas, como na seção DISCOS;
#   sem a linha do sistema operacional e sem a idade do clima (OPEN-METEO HH:MM);
#   painel de texto 14 px mais baixo, ocupando o espaço que essas linhas deixaram;
#   colmeia alinhada à direita (a borda do último hexágono em x = 314).
# No espaço livre do alto, 3 gráficos de 24 h: temperatura de CPU e GPU; VRAM com RAM; rede (download e upload).
# O pico de 24 h de cada série é um ponto no gráfico, com o valor ao lado (VRAM e RAM em GB).
import math

from . import graficos
from .reator_gamma import GAMMA
from .reator_grupos import render_grupos

R, GAP = 21, 2
COLMEIA_X = 314 - (math.sqrt(3) * R + GAP) - math.sqrt(3) * R / 2      # centro da colmeia com a borda direita em 314
P = dict(GAMMA, selo="DELTA", alert="n3_esq", pct="paren", flow=True, cool=True, temps=True,
         colmeia_x=COLMEIA_X, texto_y=137 + 14, baias_uso=True, rodape_enxuto=True,
         extra=graficos.desenhar, pico="marcador")


def draw_frame(vm_dict):
    return render_grupos(vm_dict, P, "resumo")
