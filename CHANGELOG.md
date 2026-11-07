<!-- CHANGELOG | GAMMA TUS-35 | versão 2.0.0 | 07/11/2026 15:50 (-03) | criação original (Claude, para Lucas Tavares) -->
<!-- histórico: 1.0.0 02/11/2026 19:15 primeira versão do histórico -->

# Histórico de versões

Segue [SemVer](https://semver.org/lang/pt-BR/) (MAJOR.MINOR.PATCH). Os três estilos (ALPHA, BETA e GAMMA) saem juntos, na mesma versão.

## [Não lançado]

- Gráficos de 24 h no GAMMA DELTA: temperatura de CPU e GPU no alto; VRAM com RAM e rede (download e upload) abaixo da escala. O pico de 24 h de cada série aparece como um ponto no gráfico, com o valor ao lado; VRAM e RAM em GB. Histórico com média e máximo por intervalo em `historico.py`, gravado em `~/.local/state/matrixgreenpro/historico.json`.
- Novo estilo GAMMA DELTA (`gamma-delta`), derivado do GAMMA GAMMA: o TERRAMASTER mostra ocupado, total e percentual das baias montadas (como em DISCOS); somem a linha do sistema operacional e a idade do clima; o painel de texto desce 14 px e a colmeia fica alinhada à direita. Ainda não entra nos ZIPs.
- Baias do TerraMaster: o coletor passa a ler o uso das partições montadas (ocupado e total), e o modelo de visão gera o texto e o percentual. A cor do percentual segue os limites dos discos, mas não entra na saúde nem nos alertas.
- Nova variante de estudo GAMMA GAMMA COLUNA (`gamma-gamma-coluna`): os hexágonos de resumo viram uma coluna à esquerda, cada um ao lado dos números do seu grupo, e a faixa do grupo fica âmbar ou vermelha quando ele sai do verde. Relógio no alto à direita, ao lado da escala. Não entra nos ZIPs.
- `construir/matriz_previas.py --extra delta` e `--extra coluna` acrescentam esses estilos como colunas a mais na matriz.
- Autoteste: o caso "baias: inverter troca a numeração" lia as montagens reais do PC e falhava quando `/dev/sdc1` estava montado; agora usa a mesma simulação de partições da leitura normal.
- Utilitário do PC `pc/espelho-github/`: espelho local de todos os repositórios do GitHub no HDD de 12TB, sincronizado por timer do systemd. Não entra nos ZIPs.
- Script de desenvolvimento `construir/aplicar-na-tela.sh`: aplica o código atual na tela do PC (monta o ZIP do estilo e roda o instalador). Não entra nos ZIPs.
- Ferramenta de desenvolvimento `construir/matriz_previas.py`: um PNG com as 3 versões nos 3 estados, desenhado com o código atual, com conferência de layout. Não entra nos ZIPs.
- Documentação completa do repositório: nova página de entrada e a pasta `docs/` (estilos, instalação, configuração, hardware, arquitetura, desenvolvimento, decisões e roteiro).
- Removido do fonte o travessão residual do texto interno do campo `gpu_fan_rpm` em `viewmodel.py` e `mgp_selftest.py` (não aparecia na tela). Os ZIPs 1.6.0 ainda o contêm.

## [1.6.0] - 07/11/2026 14:20 (-03)

- Selo no canto superior direito de todas as telas com o estilo e a versão do pacote, por exemplo `BETA v1.6.0`. A versão vem de `versao.py`, gravado pelo construtor dos ZIPs (no repositório aparece `dev`).

## [1.5.0] - 07/11/2026 14:30 (-03)

- Leitura das 4 baias do gabinete TerraMaster (DAS USB): por baia, capacidade e estado (montado, desmontado ou livre).
- GAMMA BETA mostra as baias em 2x2 no rodapé quando o gabinete é detectado.
- GAMMA GAMMA ganha o grupo TERRAMASTER, e os títulos de grupo passam a levar dados-chave (LOAD, FPS e FAN, TEMP da RAM, PING).
- Ferramenta `tools/mgp_baias.py` para conferir a numeração das baias.

## [1.4.0] - 02/11/2026 22:50 (-03)

- Novos nomes: GAMMA ALPHA (ex SENTINELA) e GAMMA BETA (ex DOSÍMETRO). Os nomes antigos continuam aceitos.
- Novo estilo GAMMA GAMMA: 7 hexágonos de resumo com CORE no centro e painel numérico por grupo.
- Temperatura de cada disco (HDD pelo módulo `drivetemp`, NVMe direto), com limites e alerta. O instalador carrega o `drivetemp`.
- Instalador com `--versao alpha`, `beta` ou `gamma`.

## [1.3.0] - 02/11/2026 21:50 (-03)

- Temperaturas de PLACA, RAM e SSD nas células do favo, no lugar de LOAD, TOT W e COLETA (que continuam nas linhas). RAM e SSD com limites e alerta.
- GAMMA SENTINELA ganha a bomba e as ventoinhas.

## [1.2.1] - 02/11/2026 21:38 (-03)

- Removido o RPM da ventoinha da GPU (o driver NVIDIA só informa o percentual).

## [1.2.0] - 02/11/2026 21:30 (-03)

- Bomba e ventoinhas em RPM: célula BOMBA, linha RAD, INF, LAT e TRA, alerta de bomba parada.
- Mapeador guiado de ventoinhas (`tools/mgp_mapear_fans.py`) e driver `nct6775` carregado automaticamente.

## [1.1.0] - 02/11/2026 19:20 (-03)

- GAMMA DOSÍMETRO: percentuais entre parênteses e LIM, DISP e LIVRE junto do uso.

## [1.0.0] - 02/11/2026 19:15 (-03)

- Primeira versão publicada: GAMMA SENTINELA e o instalador automático `instalar-gamma.sh`.

## Antes do SemVer

A numeração interna 1.x a 3.x (31/10 a 02/11/2026) cobriu o MATRIX GREEN PRO original, o catálogo de estilos, o NÚCLEO URÂNIO (depois GAMMA) e as variantes de alerta. O detalhe está em [pacote/README.md](pacote/README.md).
