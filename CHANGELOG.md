<!-- CHANGELOG | GAMMA TUS-35 | versão 2.0.0 | 07/11/2026 15:50 (-03) | criação original (Claude, para Lucas Tavares) -->
<!-- histórico: 1.0.0 02/11/2026 19:15 primeira versão do histórico -->

# Histórico de versões

Segue [SemVer](https://semver.org/lang/pt-BR/) (MAJOR.MINOR.PATCH). Os estilos (ALPHA, BETA, GAMMA e DELTA) saem juntos, na mesma versão.

## [Não lançado]

## [1.8.0] - 07/11/2026 21:14 (-03)

- GAMMA DELTA passa a ser o desenho estudado como DELTA 5B (o nome `gamma-delta-5b` continua aceito): valor em alerta com fundo âmbar ou vermelho e texto escuro, como na 1.7.0 de estudo; selo `DELTA` com a versão.
- Alertas por limites absolutos de manuais, do hardware e do Zabbix (tabela com fontes em `docs/configuracao.md`): RAM 90/95 %, discos 80/90 %, NVMe 80/90 °C, RAM DDR5 55/85 °C, HDD 50/60 °C, placa-mãe 70/80 °C (antes só informativa), CPU uso 90 % e carga 1,5 por núcleo sustentados por 5 min, bomba e ventoinhas abaixo de 600 RPM, redução de clock da GPU (NVML) e Ethernet abaixo da velocidade de sempre.
- Contra ruído de leitura: as leituras contínuas só sobem de cor depois de 2 s (`Confirma` em `alerts.py`); ping, discos e baias valem pela última leitura.
- LOG de alertas (`alertas.py`): registra cada mudança de cor com hora, leitura e nova cor. No DELTA 5B, o LOG mostra esses alertas e a marca de variação brusca saiu; o hexágono do total fica centrado entre a linha do título RAM e a do título seguinte.
- ⚠️ Quem já tem `config.yaml` mantém os valores antigos gravados nele (por exemplo RAM 85/95, discos 85/95, ping 80/200).
- Instalador (`scripts/instalar.sh`): o estilo pedido com `--estilo` é conferido no registro ESTILOS, e não mais pelo nome do arquivo; passa a aceitar `gamma-delta-5b` e os estilos `v2-*`.
- DELTA 5B: total dos discos num hexágono cujo contorno se enche com o uso, centrado no canto direito do grupo DISCOS (sem o texto de espaço livre ao lado); barra de uso da RAM segmentada logo depois da palavra RAM, na mesma distância da barra do título DISCOS do DELTA 6. Rótulos girados dos gráficos recortados, centrados na altura de cada gráfico e com a fonte reduzida até caber.
- Variantes `gamma-delta-5a`, `5b` e `5c` (base DELTA 5): LOG no lugar de REGISTRO, INTERNET ON/OFF, rótulos dos gráficos girados 90° e gráficos mais largos. Espaço dos discos: barra no título e barrinha por disco (5A), rosca do total (5B), mapa de capacidade proporcional ao tamanho de cada HD (5C). `construir/matriz_previas.py --delta5` desenha as quatro.
- Seis variantes do GAMMA DELTA (`gamma-delta-1` a `gamma-delta-6`, motor `reator_delta2.py`) com: total de TB de todos os HDs (discos + baias montadas, cada dispositivo contado uma vez); marca das mudanças bruscas em uso, temperatura, frequência, carga, potência, ventoinhas, FPS, rede e ping, visível por até 10 min depois de normalizar (`brusco.py`, só visual, não altera N0/N1/N2); refrigeração numa linha (SQUAMA INF e LAT são a mesma leitura); sistema compacto e registro das últimas mudanças bruscas. As variantes diferem no lugar do total, no formato do registro e na forma da marca. `construir/matriz_previas.py --deltas` desenha as seis.
- Ping: verde até 20 ms, âmbar até 100 ms, vermelho acima (padrão, `config.exemplo.yaml` e `mgp_detect.py`; histerese de 5 ms). Na demonstração Crítico, o ping de 34 ms passa a contar como aviso.
- Discos: o coletor guarda o dispositivo de cada disco, para o total não contar duas vezes um disco que também está numa baia.
- Autoteste: a lista de estilos mantém `"pcb"` por último, como o construtor dos ZIPs espera.
- `docs/brainstorm/`: as 12 propostas da v2.0.0 e as 6 variantes do DELTA guardadas como brainstorm, com imagens.
- 12 propostas de desenho para a v2.0.0 (mesma paleta, mesmos dados): `v2-concreto` (brutalista), `v2-silencio` (minimalista), `v2-hud` (sci-fi), `v2-root` (hacking), `v2-dossie` (espionagem), `v2-vital` (UTI), `v2-cockpit` (cockpit), `v2-metro` (metrô), `v2-anunciador` (sala de controle), `v2-8bits` (arcade), `v2-osciloscopio` (laboratório) e `v2-grade` (suíço). Base comum em `estilos/v2_base.py`. Não entram nos ZIPs. `construir/matriz_previas.py --v2` desenha as 12.
## [1.7.0] - 07/11/2026 19:42 (-03)

- Quarto pacote, `Gamma-Delta-v1.7.0.zip`, e `./instalar-gamma.sh --versao delta` (também no menu do instalador e em `construir/aplicar-na-tela.sh delta`).
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
