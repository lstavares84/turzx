<!-- docs/estilos.md | versão 1.3.0 | 07/11/2026 19:40 (-03) | criação original (Claude, para Lucas Tavares). Fonte: código v1.6.0 e histórico do projeto. -->
<!-- histórico: 1.3.0 07/11/2026 19:40 gráficos de 24 h do GAMMA DELTA; 1.2.0 07/11/2026 19:00 GAMMA DELTA; 1.1.0 07/11/2026 18:45 variante de estudo GAMMA GAMMA COLUNA -->

# Estilos

O GAMMA tem quatro estilos de entrega. Todos usam os mesmos dados, as mesmas regras de saúde e a mesma coleta: muda só o desenho. Todos mostram, no canto superior direito, o selo do estilo e da versão (por exemplo `GAMMA v1.6.0`), com o nome em verde-claro e a versão em cinza.

[Voltar ao README](../README.md)

## Identidade visual

| Elemento | Valor |
|---|---|
| Tela | 320x480 pixels, retrato |
| Fundo | quase preto, RGB (3, 10, 4) |
| Destaque | verde fluorescente, RGB (120, 255, 90) |
| Atenção | âmbar, RGB (255, 190, 0) |
| Crítico | vermelho, RGB (255, 60, 50) |
| Apoio | cinza-esverdeado, RGB (110, 170, 110) |
| Fontes | JetBrains Mono (números e dados) e Roboto (títulos), ambas OFL |
| Acabamento | brilho (bloom) aplicado ao quadro inteiro no final |

## Cores e estados

| Cor | Estado | Significado |
|---|---|---|
| Verde | `OK` | dentro do limite |
| Âmbar | `WARN` | atenção (N1) |
| Vermelho | `CRIT` | crítico (N2), pisca 1 s aceso e 1 s apagado |
| Cinza | `NA` | o sensor não existe nesta máquina (N/D), não alerta |
| Amarelo | `LOST` | o sensor existia e sumiu |
| Branco | `NEUTRAL` | número sem significado de saúde (por exemplo, tráfego de rede) |

No cabeçalho, a **escala N0 NORMAL, N1 AVISO, N2 ALERTA** mostra o pior nível do sistema. O nível ativo brilha e os outros ficam esmaecidos.

## GAMMA ALPHA (`gamma-alpha`)

Nome antigo: GAMMA SENTINELA (apelidos aceitos: `gamma-sentinela`, `gamma-n3-esq`).

- **Cabeçalho:** título GAMMA, aviso DEMO (só no modo demonstração), escala N0/N1/N2 à esquerda, sem tarja, e selo à direita.
- **Favo de 19 hexágonos** em linhas de 3, 4, 5, 4 e 3: CPU, CPU°, GPU, BOMBA, LOAD ou PLACA, GPU°, G.FAN, RAM, VRAM, CORE (saúde geral), FPS, GPU W, os três discos (M.2, 2T, 4T), PING, REDE, RAM° e SSD°.
- **Linhas de texto abaixo:** CPU; GPU (VRAM, W, LIM, FPS e FAN %); RAM; refrigeração (BOMBA, RAD, INF, LAT e TRA em RPM); discos com uso, percentual e livre; rede (↓ ↑, RX, TX, ETH, WIFI); relógio grande, data, uptime e sistema; ping, internet e clima; rodapé com TOTAL W e COLETA.

## GAMMA BETA (`gamma-beta`)

Nome antigo: GAMMA DOSÍMETRO (apelidos aceitos: `gamma-dosimetro`, `gamma-n3-compacto`).

Igual ao ALPHA, com duas diferenças de texto e uma de conteúdo:

- Percentuais **entre parênteses** e na cor do nível: `VRAM 10.9/12.0GB (91%)`, `RAM 12.4/31.3GB (40%)`.
- Informações secundárias (DISP da RAM, LIVRE dos discos, LIM da GPU) **coladas logo depois do uso**, em vez de alinhadas à direita.
- **Baias do TerraMaster:** quando o gabinete é detectado, as 4 baias aparecem em 2x2 no rodapé, no lugar de TOTAL W e COLETA. Sem gabinete, o rodapé volta ao normal.

## GAMMA GAMMA (`gamma-gamma`), o mais recente

Apelido aceito: `gamma-gamma-fronteira`. Veja o [esquema ilustrativo](img/gamma-gamma-esquema.svg).

**Colmeia de resumo.** Exatamente 7 hexágonos (raio 21, vão 2). CORE no centro; CPU e GPU em cima; REFR. e RAM nas laterais do CORE; REDE e DISCOS embaixo. Cada hexágono mostra só o nome e o estado `OK`, `ATEN` ou `CRIT` (`N/D` quando o grupo não tem nenhum dado). O estado do grupo é o pior nível entre os seus indicadores, e um sensor perdido (`LOST`) conta como atenção. O CORE é o pior estado geral, a mesma informação da escala N0/N1/N2. Não há rótulos ao redor nem linhas de fronteira.

**Painel numérico**, por grupo, com título e linha divisória. Para economizar espaço, um dado-chave vai no próprio título:

| Grupo | No título | Linhas |
|---|---|---|
| CPU | LOAD | USO, TEMP, FREQ |
| GPU | FPS e FAN | USO, TEMP, FREQ; VRAM com percentual, W e LIM |
| RAM | TEMP | USO com total e percentual, DISP |
| DISCOS | | nome, uso, percentual, livre e temperatura à direita |
| TERRAMASTER | | 4 baias em 2x2: número, capacidade e MONTADO, DESMONT. ou LIVRE (só com o gabinete conectado) |
| REFRIGERAÇÃO | | BOMBA, RAD, PLACA; SQUAMA INF, LAT, TRA |
| REDE | PING e internet | ↓ ↑, TX, RX; ETH e WIFI |

**Rodapé.** Sistema à esquerda (data acima da hora, uptime, sistema operacional) e clima isolado no canto inferior direito, sem moldura (cidade, temperatura grande, condição do tempo e idade do dado). TOTAL W, "sem medidor" e COLETA foram removidos de propósito.

A folga vertical é praticamente zero: qualquer linha nova exige reorganizar o layout.

Cores das baias: montado em verde, desmontado em branco, livre em cinza.

## GAMMA DELTA (`gamma-delta`), o mais novo

O GAMMA GAMMA com a colmeia à direita, três gráficos de 24 h e um LOG de alertas. Pacote `Gamma-Delta-v1.8.2.zip`, instalado com `--versao delta`. Na 1.8.0 ele passou a ser o desenho estudado como DELTA 5B (o nome `gamma-delta-5b` continua aceito).

- **Valor em alerta em destaque.** Qualquer leitura em atenção ou crítico aparece com fundo âmbar ou vermelho e texto escuro (por exemplo `FPS 96`, `TEMP 84°C`). Os limites estão em [configuração](configuracao.md).
- **Nomes dos gráficos girados 90°**, centrados na altura de cada gráfico; os gráficos ficam mais largos.
- **RAM** com barra de uso segmentada logo depois da palavra RAM.
- **Total dos HDs** (discos e baias montadas, cada dispositivo uma vez) num hexágono que se enche com o uso, centrado entre os títulos RAM e TERRAMASTER.
- **Refrigeração numa linha**: BOMBA, RAD, SQUAMA (INF e LAT estão em série, uma leitura só) e TRA, com a PLACA no título.
- **INTERNET ON / OFF** no título REDE.
- **LOG** no rodapé: cada alerta âmbar ou vermelho, com hora, leitura e cor (a volta ao verde não entra); relógio, data, tempo ligado e clima à direita.

- **TERRAMASTER com uso.** Baia montada mostra ocupado/total e percentual, como na seção DISCOS: `1 6.24/11.99TB (52%)`. A cor do percentual segue os limites dos discos (85% e 95%, 50 GB e 10 GB livres), mas só como informação: não entra na saúde. Por falta de largura, a palavra MONTADO sai da baia que mostra o uso. Baia desmontada ou livre continua como antes.
- **Rodapé mais curto.** Sem a linha do sistema operacional (`DEBIAN 13 TRIXIE`) e sem a idade do clima (`OPEN-METEO HH:MM`).
- **Texto 14 px mais baixo.** Do CPU ao SISTEMA, tudo desce para ocupar o espaço dessas linhas, e a sobra fica no alto.
- **Colmeia à direita.** Os 7 hexágonos ficam alinhados à direita, com a borda em x = 314, deixando livre a área abaixo da escala N0/N1/N2.
- **Gráficos de 24 h** no espaço livre do alto. A primeira série de cada gráfico é uma área verde, e a segunda é uma linha branca:
  - à direita da escala: temperatura da CPU (área) e da GPU (linha), de 20 a 100 °C, um pixel a cada ~19 min;
  - abaixo da escala: VRAM (área) e RAM (linha), cada uma em percentual da própria capacidade, um pixel a cada ~10 min;
  - rede: download (área) e upload (linha), com a escala ajustada ao pico do dia.
  A linha é a média de cada intervalo. O **pico de 24 h** de cada série é um ponto no gráfico, no momento e na altura em que aconteceu, com o valor ao lado (VRAM e RAM em GB, temperatura em °C, rede em MB/s). Marcas pontilhadas a cada 6 h; a borda direita é agora. Falha na linha = sem dado (PC desligado ou sensor ausente).
  O histórico (`historico.py`) guarda média e máximo por intervalo em `~/.local/state/matrixgreenpro/historico.json`, gravado a cada ~10 min, e sobrevive a reinícios. Logo depois da instalação os gráficos começam vazios e enchem ao longo do dia.
- Selo `DELTA` com a versão no canto superior direito.

## GAMMA GAMMA COLUNA (`gamma-gamma-coluna`), variante de estudo

Quarta variante do GAMMA GAMMA, ainda não entregue nos ZIPs. Mesmos dados, mesmas cores e mesmos 7 hexágonos, em outra disposição:

- **Coluna à esquerda.** Os hexágonos (raio 21) ficam empilhados numa linha vertical. O CORE é o do topo, ao lado da escala N0/N1/N2; abaixo dele vêm CPU, GPU, RAM, DISCOS, REFR. e REDE, cada um centralizado na faixa dos seus números. Assim o estado de cada grupo fica encostado nos dados que o explicam.
- **Faixa colorida.** Grupo em atenção ganha fundo âmbar na faixa inteira; grupo crítico ganha fundo vermelho, que pisca junto com a escala.
- **TERRAMASTER** aparece com um hexágono pequeno e vazio na coluna: as baias são informativas e não têm estado.
- **Sem títulos de grupo.** O nome está no hexágono; LOAD, FPS, FAN, TEMP da RAM e PING voltaram para as linhas.
- **Relógio e data** no alto à direita. Rodapé com UP, sistema e idade do clima à esquerda e o clima à direita.
- Selo `COLUNA` no canto superior direito.

## Estilos legados e experimentais

O código ainda contém estilos de fases anteriores que **não são entregues nos ZIPs**: `matrix` (minimalista, usado como reserva), `gamma` (o favo original), `gamma-sonar`, `gamma-raiox`, `gamma-uv`, `gamma-escala`, `gamma-barra`, `gamma-banner`, `gamma-faixa`, `gamma-n3`, `gamma-n3-abas`, `gamma-n3-linha`, `gamma-n3-eventos`, as variantes de estudo do GAMMA GAMMA (`gamma-gamma-colmeia`, `gamma-gamma-mini`, `gamma-gamma-painel`, `gamma-gamma-coluna`) e `pcb` (placa de circuito). Eles podem ser usados com `--estilo NOME`, mas não recebem manutenção. A decisão de arquivar ou remover está no [roteiro](roteiro.md).
