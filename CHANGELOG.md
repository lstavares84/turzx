<!-- CHANGELOG | GAMMA TUS-35 | versão 2.0.0 | 07/11/2026 15:50 (-03) | criação original (Claude, para Lucas Tavares) -->
<!-- histórico: 1.0.0 02/11/2026 19:15 primeira versão do histórico -->

# Histórico de versões

Segue [SemVer](https://semver.org/lang/pt-BR/) (MAJOR.MINOR.PATCH). Os três estilos (ALPHA, BETA e GAMMA) saem juntos, na mesma versão.

## [Não lançado]

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
