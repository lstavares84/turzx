<!-- tela-3.5-gamma/README.md | versão 1.0.0 | 21/11/2026 18:45 (-03) | criação original (Claude, para Lucas Tavares) -->
# GAMMA (tela de 3,5")

Tema de monitoramento GAMMA para a tela TURZX / Turing de 3,5" (320x480, retrato), em uso no PC de referência com o GAMMA EPSILON. O mesmo código também gera os pacotes para a tela de 5,2" (720x1280), ainda não usada com o GAMMA.

| Pasta ou arquivo | O que é |
|---|---|
| `instalar-gamma.sh` | instalador de ponta a ponta (dependências, Turing, serviço e tema) |
| `VERSION` | versão do GAMMA (SemVer) |
| `pacote/sensors/matrixgreenpro/` | extensão Python: coleta, saúde, histórico e desenho |
| `pacote/sensors/matrixgreenpro/estilos/` | estilos entregues: ALPHA, BETA, GAMMA, DELTA e EPSILON (com as telas de gráficos, backups, andamento e mineração em `epsilon_telas.py`) |
| `pacote/sensors/matrixgreenpro/estilos/estudos/` | estilos de estudo e mockups, que não entram nos ZIPs |
| `pacote/scripts/` | instalar, diagnosticar e restaurar |
| `pacote/tools/` | autoteste, prévias, detector do hardware e mapeadores |
| `pacote/telas/3.5/` e `pacote/telas/5.2/` | o tema de cada tela |
| `construir/` | construtor dos ZIPs, matrizes de prévias e envio à tela do PC |

Visão geral, imagens e documentação: [README principal](../README.md) e [docs/](../docs/). Para mexer no código: [desenvolvimento](../docs/desenvolvimento.md).
