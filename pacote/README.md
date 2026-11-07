<!-- versão 1.3.0 | 02/11/2026 21:50 (-03) | temperaturas de placa, RAM e SSD -->
# VERSÃO 1.3.0: temperaturas de placa, RAM e SSD

Nos dois estilos (GAMMA SENTINELA e GAMMA DOSÍMETRO), que agora também trazem a bomba e as ventoinhas:

- Três células hexagonais novas: `PLACA`, `RAM°` e `SSD°`. Elas ocupam o lugar de LOAD, TOT W e COLETA, que continuam nas linhas de texto.
- `PLACA` vem do canal SYSTIN do chip da placa e é só informativa (não conheço o ponto físico nem o limite).
- `RAM°` é o maior valor entre os pentes (sensores spd5118): aviso em 50 °C e crítico em 55 °C.
- `SSD°` é a temperatura composta do NVMe: aviso em 70 °C e crítico em 80 °C.
- Mapa e limites em `cpu.temps` e `cpu.temps_limites` do `config.yaml`. Entradas sem sensor (como AUXTIN5, que lê 105 °C solto) são ignoradas.
- A GPU não informa temperatura de memória nem de ponto quente nesse driver (`N/A`), então esses valores não aparecem.

<!-- versão 1.2.1 | 02/11/2026 21:38 (-03) | remove o RPM da GPU -->
# VERSÃO 1.2.1: sem o RPM da GPU

O driver da NVIDIA informa só o percentual da ventoinha da GPU (o comando da curva), nunca o RPM. O campo `RPM -` foi removido e a linha mostra `FAN 0%` com o nível de alerta (parada com a GPU quente = aviso ou crítico).

<!-- versão 1.2.0 | 02/11/2026 21:45 (-03) | GAMMA v1.2.0: BOMBA e ventoinhas (RPM) no Dosímetro -->
# VERSÃO 1.2.0: bomba e ventoinhas

Baseada no GAMMA DOSÍMETRO (1.1.0). Novidades (SemVer MINOR, compatível):

- Célula **BOMBA** no lugar de C.FAN e uma linha de RPM: `BOMBA`, `RAD` (radiador), `INF`, `LAT` e `TRA` (Squama inferior, lateral e traseira).
- **Alerta da bomba:** se a bomba já girou e passa a 0 RPM, é CRÍTICO (conta no N2). Ventoinha do gabinete ou do radiador a 0 RPM só alerta com a CPU quente (abaixo de 60 °C é modo semipassivo).
- Entrada que nunca girou (conector vazio) aparece como `0` neutro, sem alarme.
- Divisores de ventoinha entregam **uma leitura por conector**: as 3 do radiador e as 3 de baixo aparecem como uma leitura cada.
- Leitura direta do sysfs (`/sys/class/hwmon`), com o mapa em `cpu.fans` (padrão: bomba=fan1, radiador=fan2, sq_inf=fan3, sq_lat=fan4, sq_tras=fan5).
- Ferramenta `tools/mgp_mapear_fans.py`: descobre sozinha qual entrada é cada ventoinha (você desconecta um cabo por vez) e grava `~/.config/matrixgreenpro/fans.yaml`. A bomba nunca é desconectada.
- O instalador carrega o driver `nct6775` automaticamente quando o kernel não expõe ventoinhas (placas com NCT6796D/NCT6799D, como a ASRock B850M Pro-A).

<!-- versão 1.0.0 | 02/11/2026 19:15 (-03) | renomeação: N3 Esquerda vira GAMMA SENTINELA e N3 Compacto vira GAMMA DOSÍMETRO; versionamento SemVer -->
# VERSÃO 1.0.0: GAMMA SENTINELA e GAMMA DOSÍMETRO

A numeração passou a seguir SemVer (MAJOR.MINOR.PATCH). Os estilos finais ganharam nomes definitivos:

| Nome | Estilo (`--estilo`) | Nome antigo (ainda aceito) |
|---|---|---|
| GAMMA SENTINELA | `gamma-sentinela` | `gamma-n3-esq` |
| GAMMA DOSÍMETRO | `gamma-dosimetro` | `gamma-n3-compacto` |

Histórico anterior (numeração interna 3.x, antes do SemVer):

<!-- versão 3.6.0 | 02/11/2026 19:50 (-03) | gamma-n3-compacto: percentuais entre parênteses e informações à esquerda -->
# NOVO NA 3.6.0: `gamma-dosimetro` (ex gamma-n3-compacto)

Nova variante, a partir do `gamma-sentinela` (ex gamma-n3-esq) (escala N0/N1/N2 sem tarja e sem LIVE):

* **Percentuais entre parênteses**, na cor do nível de saúde: `VRAM 10.9/12.0GB (91%)`, `RAM 12.4/31.3GB (40%)` e `(42%)` em cada disco.
* **Informações à esquerda:** DISP (RAM), LIVRE (discos) e LIM (potência da GPU) ficam coladas logo depois do uso, em vez de alinhadas na borda direita. CPU, GPU e VRAM mantêm LOAD, FPS e FAN à direita.

Uso: `./scripts/instalar.sh --estilo gamma-n3-compacto`. O `gamma-sentinela` (ex gamma-n3-esq) da 3.5.0 continua como estava.

<!-- versão 3.5.0 | 02/11/2026 19:15 (-03) | gamma-n3-esq: sem tarja, sem LIVE, com percentuais -->
# NOVO NA 3.5.0: ajustes no `gamma-sentinela` (ex gamma-n3-esq)

* **Sem tarja:** a escala N0, N1 e N2 usa só a barra à esquerda e o nome com brilho (halo suave). Os níveis inativos ficam esmaecidos. Em N2 a barra e o nome piscam (1 s aceso, 1 s apagado).
* **Sem o "LIVE"** no canto superior direito.
* **Percentuais no registro:** VRAM, RAM e cada disco mostram o percentual de uso (por exemplo `VRAM 6.4/12.0GB 53%`, `RAM 12.4/31.3GB 40%` e `42%` antes do espaço livre de cada disco), na cor do nível de saúde.

Os outros estilos continuam como na 3.4.0.

<!-- versão 3.4.0 | 02/11/2026 18:55 (-03) | cinco variantes com escala de terminal N0 NORMAL, N1 AVISO, N2 ALERTA -->
# NOVO NA 3.4.0: escala de terminal N0, N1 e N2

Cinco estilos a partir do GAMMA original, com o aviso em escala de três níveis como num terminal de eventos: **N0 NORMAL**, **N1 AVISO** e **N2 ALERTA**. O nível ativo recebe barra, fundo e borda; os outros ficam esmaecidos. Em N2 o vermelho pisca (1 s aceso, 1 s apagado), junto com o ponto do "LIVE".

| `--estilo` | Onde e como |
|---|---|
| `gamma-n3` | escala de 3 linhas no canto superior direito, "LIVE" com ponto no cabeçalho |
| `gamma-sentinela` (ex gamma-n3-esq) | a mesma escala no canto superior esquerdo |
| `gamma-n3-abas` | três abas N0, N1 e N2 no cabeçalho; a ativa se expande com o nome e a contagem |
| `gamma-n3-linha` | uma linha no cabeçalho: `> [N1] AVISO // OBSERVAR` |
| `gamma-n3-eventos` | escala à esquerda e, à direita, a lista dos itens em alerta (por exemplo `CPU° 96°C`, `4T 99%`) |

Os textos de apoio ficam em português: PRONTO, OBSERVAR e INTERVIR. Se a coleta falhar por completo, o nível N2 mostra "SEM DADOS". Os estilos da 3.3.0 (`gamma-escala`, `gamma-barra`, `gamma-banner`, `gamma-faixa`) e da 3.2.0 (`gamma-sonar`, `gamma-raiox`, `gamma-uv`) continuam no pacote.

<!-- versão 3.3.0 | 02/11/2026 18:20 (-03) | indicadores de alerta modernos (escala, barra, banner) e proposta em faixa -->
# NOVO NA 3.3.0: aviso e alerta em escala, com o crítico piscando

Quatro estilos novos a partir do GAMMA, trocando só o indicador do canto superior direito (antes "SISTEMA OK" ou "+ 4 AVISOS"). Em CRÍTICO o vermelho pisca: 1 s aceso e 1 s apagado. Aviso (âmbar) fica fixo.

| `--estilo` | Indicador |
|---|---|
| `gamma-escala` | medidor de 15 marcas (5 verdes, 5 âmbar, 5 vermelhas); a marca ativa fica mais alta e a contagem de alertas avança a marca |
| `gamma-barra` | barra em degradê verde, âmbar e vermelho com ponteiro triangular |
| `gamma-banner` | caixa com ícone; no crítico vira caixa vermelha cheia "ALERTA n CRÍTICOS" e uma linha vermelha pisca sob o cabeçalho (inspirado num banner de terminal) |
| `gamma-faixa` | proposta com a escala em outro lugar: 31 marcas na largura toda, no lugar da divisória do cabeçalho |

Prévias em `previews/`: `MatrixGreenPro-GammaEscala-Critico.png` (aceso) e `...-CriticoApagado.png` (apagado), e o mesmo para `GammaBarra`, `GammaBanner` e `GammaFaixa`. O piscar depende do painel redesenhar a cada ciclo (cerca de 1 s); como só as regiões alteradas vão para a tela, o custo de USB é pequeno.

<!-- versão 3.2.0 | 02/11/2026 17:50 (-03) | edição GAMMA: URÂNIO renomeado para GAMMA, sem subtítulo, e 3 variantes novas -->
# EDIÇÃO GAMMA (3.2.0)

O tema URÂNIO passou a se chamar **GAMMA**. Na tela aparece só a palavra "GAMMA" (o subtítulo "NÚCLEO U-235" foi removido). Este pacote instala o GAMMA por padrão e traz três variantes novas, todas com as mesmas métricas, regras de saúde e coleta. O nome antigo `uranio` continua funcionando como apelido de `gamma`, então uma configuração existente não quebra.

| `--estilo` | Nome | Aparência |
|---|---|---|
| `gamma` (padrão) | GAMMA | favo de 19 hexágonos em verde fluorescente, brilho suave, malha hexagonal |
| `gamma-sonar` | GAMMA SONAR | verde-água sobre azul-petróleo, 14 células em losango sobre um radar (anéis, mira e graus) |
| `gamma-raiox` | GAMMA RAIO-X | chapa de raio-X em aço e branco sobre grafite, linhas de varredura, cantoneiras e células grandes; verde só como sinal de saúde |
| `gamma-uv` | GAMMA ULTRAVIOLETA | violeta de luz negra, 12 células em anel ao redor do núcleo e raios irradiando do centro |
| `matrix` | MATRIX GREEN PRO | minimalista preto, branco e verde (o da 2.1.0) |
| `pcb` | 13-C PLACA DE CIRCUITO | placa verde com trilhas de cobre, ilhas douradas e serigrafia branca |

```bash
# GAMMA 3.2.0 | trocar o estilo (grava em ~/.config/matrixgreenpro/config.yaml e reinicia o serviço)
./scripts/instalar.sh --estilo gamma
./scripts/instalar.sh --estilo gamma-sonar
./scripts/instalar.sh --estilo gamma-raiox
./scripts/instalar.sh --estilo gamma-uv
```

Sem `--estilo`, o instalador mantém o estilo já gravado (e usa `gamma` numa instalação nova). Prévias: `previews/MatrixGreenPro-{Gamma,GammaSonar,GammaRaioX,GammaUV,PCB}-{Normal,Atencao,Critico}.png` e a montagem `previews/MatrixGreenPro-Comparativo-Estilos.png`. A pasta do tema continua `MatrixGreenPro` (nome interno do projeto).

# MATRIX GREEN PRO para TURZX TUS-35 (Debian 13)

<!-- versão 3.1.0 | 01/11/2026 11:20 (-03) | estilos finalistas selecionáveis: 06-A NÚCLEO URÂNIO e 13-C PLACA DE CIRCUITO -->
<!-- histórico: 2.1.0 01/11/2026 00:30 pacote final instalável (continua disponível, congelado) -->

Tema vertical nativo (320 × 480, retrato) para a tela TURZX/Turing TUS-35 de 3,5" (USB `1a86:5722`, série `USB35INCHIPSV2`, revisão A), instalado como extensão do `turing-smart-screen-linux` que já está no seu computador. O design, o código e os scripts são criação original (Claude, para Lucas Tavares). A extensão usa a licença GPL-3.0-or-later, a mesma do projeto em que ela se integra.

## Estilos

Veja a tabela no topo deste arquivo.

## 1. Conteúdo do pacote

```
MatrixGreenPro-TUS35-Debian13/
├── MatrixGreenPro/              pasta do tema (vai para res/themes/MatrixGreenPro)
│   ├── theme.yaml               display 3.5" portrait, fundo estático, sensor CUSTOM
│   ├── background.png           320x480: faixa do cabeçalho, título e divisórias
│   └── preview.png              miniatura usada pela galeria e pelo Centro Turing
├── sensors/
│   ├── matrixgreenpro/          extensão Python (vai para library/sensors/matrixgreenpro)
│   │   ├── panel.py             sensor MatrixGreenProPanel + motor (diferença de quadros)
│   │   ├── collectors.py        CPU, GPU (NVML/nvidia-smi), FPS (MangoHud), discos por UUID,
│   │   │                        rede por interface, ping, clima (Open-Meteo), energia
│   │   ├── viewmodel.py         formatação, saúde, contagem de alertas, estado da coleta
│   │   ├── render.py            layout 320x480 do estilo matrix
│   │   ├── estilos/             estilos gamma (reator_gamma*.py) e pcb (blueprint*.py) + base.py e kit.py
│   │   ├── alerts.py            paleta e histerese
│   │   └── settings.py          padrões + ~/.config/matrixgreenpro/config.yaml
│   └── sensors_custom_hook.txt  bloco de 7 linhas acrescentado ao sensors_custom.py
├── tools/                       vão para tools/ do programa
│   ├── mgp_preview.py           gera as prévias e confere limites e sobreposição
│   ├── mgp_selftest.py          53 testes automáticos
│   ├── mgp_detect.py            detecta discos (UUID) e rede, cria a configuração
│   └── mgp_orientation_test.py  seta TOPO na tela física
├── scripts/
│   ├── instalar.sh              instalação em 15 etapas, idempotente
│   ├── diagnosticar.sh          diagnóstico somente leitura
│   └── restaurar.sh             volta ao Cyberdeck, restaura backups, desinstala
├── extras/
│   ├── MangoHud-mgp.conf        bloco de log do MangoHud (FPS real)
│   └── config.exemplo.yaml      exemplo comentado da configuração do painel
├── previews/                    três PNG nativos, montagem 2x, testes, captura do programa real
├── README.md
└── VERSION
```

Nenhuma imagem de ícone ou barra foi incluída: barras, marcadores e textos são desenhados pelo Pillow em tempo real, o que permite mudar a cor conforme a saúde. A única fonte usada (JetBrains Mono NL, licença OFL) já vem com o projeto em `res/fonts/jetbrains-mono/`, por isso não foi redistribuída.

## 2. Análise técnica dos quatro temas de referência

Os quatro temas enviados são idênticos aos do repositório `pilahito/turing-smart-screen-linux` (comparação arquivo por arquivo). Foram estudados só como implementação; nenhuma cor, fundo ou disposição foi aproveitada.

| Aspecto | Cyberdeck | MatrixES_H | Cyberpunk | 3.5inchTheme2 |
|---|---|---|---|---|
| Tamanho/orientação | 3.5", landscape | 3.5", landscape | 3.5", portrait | 3.5", portrait |
| Fundo (`static_images`) | 480×320 | 480×320, gerado por script | 320×480 + `background_text.png` | 320×480 |
| Textos fixos (`static_text`) | não | não | sim (com `BACKGROUND_IMAGE`) | sim (com `BACKGROUND_COLOR`) |
| Indicadores | RADIAL, TEXT, GRAPH, LINE_GRAPH, FPS | TEXT, GRAPH, LINE_GRAPH | TEXT, GRAPH, DATE | TEXT, GRAPH, DATE |
| Posicionamento | X/Y + ANCHOR padrão | X/Y + WIDTH/HEIGHT + ALIGN/ANCHOR | X/Y | X/Y, ANCHOR `lm` |
| Fontes | roboto, jetbrains-mono | jetbrains-mono | generale-mono | jetbrains-mono |

Como o sistema de temas funciona (conferido no código, não só nos exemplos):

* `display.DISPLAY_SIZE: 3.5"` vira 320×480 (`library/display.py`). `DISPLAY_ORIENTATION: portrait` envia `SET_ORIENTATION` 100 à revisão A. O giro de 180° fica no `config.yaml` do programa (`DISPLAY_REVERSE`).
* Coordenadas em pixels a partir do canto superior esquerdo. `FONT` é relativo a `res/fonts/`; `PATH` e `BACKGROUND_IMAGE` são relativos à pasta do tema.
* Cores no formato `"r, g, b"` (`library/lcd/color.py`). **São fixas no YAML.**
* Cada grupo de `STATS` tem um `INTERVAL`; blocos sem `SHOW: True` não são desenhados; grupos ausentes herdam `INTERVAL: 0` do `res/themes/default.yaml` (ficam desligados).
* `STATS.CUSTOM` chama, a cada intervalo, classes de `library/sensors/sensors_custom.py` que herdam `CustomDataSource` (mecanismo oficial, exemplo `CustomDataExample`).

O que o sistema nativo não cobre e exigiu a extensão Python:

| Requisito | Limitação nativa |
|---|---|
| Cores de saúde dinâmicas (verde, amarelo, vermelho) | `FONT_COLOR`/`BAR_COLOR` fixos |
| Três discos | `DISK` lê apenas `/` (`psutil.disk_usage("/")`) |
| Ventoinha da GPU em % e RPM | não existe |
| Rede por interface, rota padrão, internet à parte | só ETH e WLO, sem estado |
| Ping, clima Open-Meteo, energia legítima, estado da coleta | ping e clima nativos (OpenWeatherMap) sem os demais |

Por isso o tema declara um único sensor `MatrixGreenProPanel` em `STATS.CUSTOM`. Ele desenha o quadro inteiro e envia à tela só as regiões alteradas, pelo mesmo método que o programa usa (`lcd.DisplayPILImage`, com a fila e a trava USB do próprio programa). A ferramenta do projeto `tools/audit-theme-resolution.py` aprova o tema: `OK MatrixGreenPro fondo=320x480 size=3.5" orient=portrait`.

## 3. Ajustes da versão 2.1.0 (mantidos)

* **Rede x internet.** Ethernet desconectada com Wi-Fi funcionando não gera alerta (exceto com `ethernet_obrigatoria: true`). Wi-Fi inexistente aparece como `N/D`. A internet é avaliada à parte, pelo ping: `INTERNET OK`, `INSTÁVEL`, `SEM INTERNET` ou `SEM REDE`. Sem nenhum enlace conta um único crítico; a falha do ping, nesse caso, não é contada de novo.
* **Estado da coleta** no rodapé, independente da saúde: `COLETA OK`, `COLETA PARCIAL <fontes>` ou `COLETA FALHOU`. Sensor que sumiu, API do clima vencida ou coletor com erro entram aqui, não nos avisos. Se tudo falhar, o cabeçalho mostra `■ SEM DADOS` em vez de `SISTEMA OK`.
* **Ventoinha da GPU:** `FAN 72% | 1800RPM` ou `FAN 72% | RPM -`. Nada é estimado.
* **Energia:** `GPU W 212` (com `LIM` da placa) separado de `TOTAL W N/D`.
* **Contagem:** avisos (▲) e críticos (●) separados; cada indicador conta uma vez; utilização de CPU/GPU nunca conta.

## 4. Regras de saúde (configuráveis em `~/.config/matrixgreenpro/config.yaml`)

| Indicador | Atenção | Crítico |
|---|---|---|
| CPU °C | auto pelo modelo (Ryzen 7000/8000/9000: 88; 3000/5000: 80; outros: 80) | 94 / 88 / 90 |
| GPU °C | limite de desaceleração NVML - 10 | NVML - 3 (sem NVML: 80/87) |
| Ventoinhas a 0 RPM | componente ≥ 60 °C | componente na faixa de atenção (frio = modo semipassivo, normal) |
| RAM (pela memória disponível) | 85% | 95% |
| VRAM | 90% | 97% |
| Cada disco | 85% ou < 50 GB livres; desmontado | 95% ou < 10 GB livres |
| Ping | 80 ms ou 1ª falha | 200 ms ou 3 falhas seguidas |
| Conexão | Ethernet obrigatória caída com Wi-Fi ativo | nenhum enlace |
| TOTAL W | 80% de `psu_watts` | 90% (só com medidor e `psu_watts`) |

Histerese de 3 °C, 2 pontos percentuais e 15 ms evita piscar entre cores.

## 5. Instalação

⚠️ Copie o ZIP para o Debian e rode como seu usuário (não use sudo nos scripts):

```bash
# MATRIX GREEN PRO 3.1.0 | instalação
cd ~/Downloads
unzip -o MatrixGreenPro-TUS35-Debian13-3.1.0.zip
cd MatrixGreenPro-TUS35-Debian13
chmod +x scripts/*.sh
./scripts/diagnosticar.sh                  # opcional: verificação antes de instalar
./scripts/instalar.sh --mangohud --estilo gamma   # instala, FPS real, estilo e reinicia (ou --estilo pcb / matrix)
```

O instalador verifica o sistema, a pasta `/home/lstavares84/turing-smart-screen-linux`, a tela USB, as units do systemd, as dependências e as fontes; faz backup; instala tema e extensão; valida YAML, recursos e importação **antes** de trocar o tema; seleciona `MatrixGreenPro`; reinicia só o `turing-smart-screen.service` (o `turing-fps.service` não é tocado); confere o log e mostra o diagnóstico. Só pede sudo, com confirmação, para incluir seu usuário no grupo `dialout`, se faltar.

Ativação e ajustes:

```bash
# MATRIX GREEN PRO 3.1.0 | orientação física
./scripts/instalar.sh --teste-orientacao   # seta TOPO por 15 s na tela
./scripts/instalar.sh --invertido          # se a seta apontou para baixo (desfazer: --normal)
```

⚠️ Confira os UUIDs dos três discos em `~/.config/matrixgreenpro/config.yaml` (comando `lsblk -f`). A detecção usa UUID, nunca `/dev/sdX`; NVMe vira M.2, ~2 TB vira 2T e ~4 TB vira 4T.

⚠️ Na Steam, use a opção de inicialização `mangohud %command%` para o FPS aparecer.

⚠️ Se o instalador avisar que a unit aponta para outra pasta (o modelo do projeto usa `turing-smart-screen-python`), rode `./scripts/instalar.sh --corrigir-servico`.

Executar de novo é seguro: cada execução gera um backup em `~/.local/share/matrixgreenpro/backups/`, mantém sua configuração e só altera `THEME` (e `DISPLAY_REVERSE`, se pedido) no `config.yaml`.

## 6. Diagnóstico

```bash
# MATRIX GREEN PRO 3.1.0 | diagnóstico
./scripts/diagnosticar.sh            # completo, salvo em ~/.local/state/matrixgreenpro/
./scripts/diagnosticar.sh --resumo   # essencial
```

Mostra: USB, porta serial efetiva (by-id), grupo `dialout` e acesso à porta, estado dos dois serviços, instâncias duplicadas, tema ativo, leitura real de cada sensor e dos três discos, saúde, estado da coleta e erros recentes.

## 7. Restauração

```bash
# MATRIX GREEN PRO 3.1.0 | reversão
./scripts/restaurar.sh                          # volta ao tema anterior (Cyberdeck)
./scripts/restaurar.sh --listar                 # lista os backups
./scripts/restaurar.sh --backup 20261101-001500 # devolve config.yaml, sensors_custom.py, unit e MangoHud.conf
./scripts/restaurar.sh --remover-tudo           # desinstala tema e extensão (pede confirmação)
```

Para voltar ao estado anterior à primeira instalação, use o backup cuja linha mostra "tema ativo antes: Cyberdeck". A configuração em `~/.config/matrixgreenpro` e os backups nunca são apagados.

## 8. Layout (linhas de base em y, px)

| Seção | Faixa | Conteúdo |
|---|---|---|
| Cabeçalho | 0 a 19 | título, DEMO (só no modo demonstrativo), estado geral (14) |
| CPU | 22 a 77 | uso, GHz, °C (46); barra 51 a 55; FAN e LOAD (70) |
| GPU | 79 a 166 | uso, MHz, °C (101); barra; VRAM (125); FAN % \| RPM e FPS (142); GPU W e LIM (159) |
| RAM | 168 a 203 | usada/total e disponível (186); barra |
| Discos | 205 a 282 | M.2 (221), 2T (246), 4T (271), barra de 3 px cada |
| Rede | 284 a 360 | ↓ ↑ (302); RX/TX desde o boot (319); ETH (336); WIFI (353) |
| Sistema | 362 a 409 | hora e data (385); Debian e uptime (402) |
| Ping e clima | 411 a 453 | ping, internet, cidade, °C (429); condição e origem (446) |
| Energia e coleta | 455 a 479 | TOTAL W e estado da coleta (472) |

Os 103 elementos com caixa exata estão em `previews/layout_coordenadas.tsv`. Margens: x 7 a 314; trilho de saúde em x 0 a 2. Fonte de 22, 15, 12 e 11 px.

## 9. Testes realizados e limites do que foi testado

Executado neste ambiente de desenvolvimento (Linux, Python 3.13, cópia do repositório com os quatro temas enviados):

* 53/53 testes automáticos aprovados (inclui os três estilos e o motor real com `pcb`) (`tools/mgp_selftest.py`): estados de saúde, rede x internet, coleta OK/PARCIAL/FALHOU, GPU sem ventoinha, FPS ausente, RAM alta, disco cheio e desmontado, Wi-Fi inexistente, ping, clima, energia, histerese, leitura de CSV real do MangoHud, UUID inexistente e o motor com os coletores reais.
* Limites e sobreposição dos 103 elementos nos três estados, no pior caso (105 °C, 9999 RPM, 999 MB/s, 99,99 TB, 99 dias, nomes de interface longos) e com coleta falha: 0 problemas.
* YAML do tema e do `config.yaml`, existência e tamanho de `background.png` (320×480), fontes, importação do sensor e herança de `CustomDataSource`.
* Programa real (`main.py`) com o tema e `REVISION: SIMU` nos estilos `gamma` e `pcb`: tema carregado, estilo informado no log, quadro de 320×480 (validação da 3.1.0; capturas antigas não incluídas nesta edição).
* Estilos `gamma` e `pcb`: 2 × 5 cenários sem texto fora da tela, sem sobreposição, sem glifo ausente e sem métrica omitida. Custo medido por ciclo de 1 s: matrix 38 ms e ~29 KiB; gamma 54 ms e ~56 KiB (medido na 3.1.0); pcb 33 ms e ~36 KiB enviados à tela.
* Instalação com `--estilo uranio` (hoje `gamma`), troca para `--estilo pcb`, reinstalação (sem alterar o `config.yaml` de novo, bloco único), restauração por backup e remoção: `config.yaml` e `sensors_custom.py` voltam idênticos aos originais (md5).
* `bash -n` e `py_compile` em todos os scripts; integridade do ZIP (`unzip -t`).

**Não testado:** comunicação real com o TUS-35. Este ambiente não tem a tela, a GPU NVIDIA, os sensores da placa-mãe, o systemd de usuário nem acesso à API do Open-Meteo (bloqueada pela rede do ambiente). A orientação física, os sensores reais e o início automático após reiniciar o Debian precisam ser conferidos no seu computador com `./scripts/instalar.sh --teste-orientacao` e `./scripts/diagnosticar.sh`.

## 10. Limitações conhecidas

* **RPM da GPU:** o `nvidia-smi` só informa %. O RPM depende de a NVML expor `nvmlDeviceGetFanSpeedRPM` para a sua placa e driver; senão aparece `RPM -`.
* **TOTAL W:** `N/D` sem medidor. Suportados: fonte digital com driver hwmon (ex.: `corsairpsu`), tomada Tasmota ou Shelly Gen2, ou arquivo atualizado por outro programa.
* **FPS:** só com jogos rodando sob MangoHud. O `turing-fps.service` existente grava a taxa do monitor (Hz) em `/tmp/turing-fps`; o painel ignora esse arquivo de propósito.
* **Ventoinha da CPU** em placas Gigabyte pode exigir o módulo `it87` (`scripts/install-fan-modules.sh` do projeto).
* **Densidade:** corpo mínimo de 11 px (~1,7 mm a 165 ppi).
* **`git pull` no repositório** pode reclamar do `sensors_custom.py` alterado: rode `./scripts/restaurar.sh --remover-tudo`, atualize e reinstale.

## 11. Fontes

* turing-smart-screen-linux (código inspecionado: `library/stats.py`, `library/display.py`, `library/config.py`, `library/lcd/color.py`, `library/lcd/lcd_comm_rev_a.py`, `library/sensors/sensors_custom.py`, `res/themes/default.yaml`, `res/themes/CustomDataExample`, `scripts/`, `tools/audit-theme-resolution.py`): https://github.com/pilahito/turing-smart-screen-linux
* turing-smart-screen-python: https://github.com/mathoudebine/turing-smart-screen-python
* MangoHud, gravação incremental do CSV (`src/logging.cpp`, `writeToFile` com `flush`): https://github.com/flightlessmango/MangoHud
* Open-Meteo: https://open-meteo.com
* Coordenadas de Rio do Sul (-27,2139; -49,6428): https://www.cidade-brasil.com.br/municipio-rio-do-sul.html

## Validação da 3.2.0 (02/11/2026)

* 90/90 testes automáticos aprovados (3.4.0; eram 75/75 na 3.3.0 e 63/63 na 3.2.0) (`tools/mgp_selftest.py`), incluindo os seis estilos e o apelido antigo `uranio` abrindo o `gamma`.
* Seis estilos × cinco cenários (normal, atenção, crítico, pior caso, coleta falhou): 0 texto fora da tela, 0 sobreposição, 0 glifo ausente e 0 métrica omitida (`tools/mgp_preview.py`).
* Ainda pendente de conferência na tela real: o brilho (bloom) e as cores das três variantes novas, a orientação física e o início automático.
* 3.3.0: 10 estilos × 6 cenários (inclui o crítico aceso e apagado): 0 problema de limites, sobreposição, glifo ou métrica omitida.
* 3.4.0: 15 estilos × 6 cenários (inclui o crítico aceso e apagado): 0 problema de limites, sobreposição, glifo ou métrica omitida.
* 3.5.0: 90/90 testes automáticos aprovados; 15 estilos × 6 cenários sem problema de limites, sobreposição, glifo ou métrica omitida.
* 3.6.0: 93/93 testes automáticos aprovados; 16 estilos × 6 cenários sem problema de limites, sobreposição, glifo ou métrica omitida.
