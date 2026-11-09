<!-- docs/configuracao.md | versão 2.1.0 | 08/11/2026 21:03 (-03) | criação original (Claude, para Lucas Tavares). Fonte: pacote/sensors/matrixgreenpro/settings.py e pacote/extras/config.exemplo.yaml da v1.8.2. -->
<!-- histórico: 2.1.0 08/11/2026 21:03 discos pelo número de série -->
<!-- histórico: 2.0.0 07/11/2026 22:24 limites com fontes, alertas 2 s e 5 min, discos via VeraCrypt, INTERNET ON/OFF, histórico de 24 h -->

# Configuração

[Voltar ao README](../README.md)

A configuração fica em `~/.config/matrixgreenpro/config.yaml` (ou no caminho da variável `MGP_CONFIG`). Todo valor tem padrão embutido em `settings.py`, então o arquivo só precisa ter o que você quer mudar. Se o arquivo tiver erro, o painel segue com os padrões e registra o problema. Exemplo comentado: [pacote/extras/config.exemplo.yaml](../pacote/extras/config.exemplo.yaml).

Depois de editar, reinicie o serviço:

```bash
systemctl --user restart turing-smart-screen
```

## Painel

| Chave | Padrão | Função |
|---|---|---|
| `painel.estilo` | `matrix` | estilo ativo (o instalador grava `gamma-alpha`, `gamma-beta` ou `gamma-gamma`); a variável `MGP_ESTILO` tem prioridade |
| `painel.demo` | `false` | dados de demonstração (o cabeçalho mostra DEMO); também com `MGP_DEMO=1` |
| `painel.refresh_full_s` | `300` | redesenho completo periódico, corrige ruído de USB |

## Limites de alerta

Os limites vêm dos manuais, dos valores gravados no próprio hardware e das boas práticas de monitoramento (modelo Linux do Zabbix). Fontes ao lado de cada linha.

| Indicador | Atenção (âmbar) | Crítico (vermelho) | Chaves | Fonte |
|---|---|---|---|---|
| CPU °C | automático pelo modelo (Ryzen 9000: 88) | automático (Ryzen 9000: 94) | `cpu.temp_warn`, `cpu.temp_crit` | Tjmax 95 °C do Ryzen 9 9900X ([AMD](https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-9-9900x.html)) |
| CPU uso | 90 % por 5 min seguidos | | `cpu.uso_warn`, `cpu.uso_janela_s` | gatilho "High CPU utilization" do [Zabbix](https://www.zabbix.com/br/integrations/debian) |
| Carga (1 min) | 1,5 por núcleo lógico por 5 min (24 threads: 36) | | `cpu.carga_por_nucleo` | Zabbix |
| GPU °C | limite de desaceleração da NVML menos 10 | NVML menos 3 (sem NVML: 80/87) | `gpu.temp_warn`, `gpu.temp_crit` | operação máxima ≈ 88 °C informada pelo driver (`nvidia-smi -q`) |
| GPU clock | redução térmica por software | redução por hardware (térmica, slowdown ou power brake) | | motivos de redução de clock da NVML, como no [NVIDIA NVSentinel](https://docs.nvidia.com/nvsentinel/runbooks/gpu-thermal-margin); o limite de potência (300 W) não alerta |
| VRAM | 90 % | 97 % | `gpu.vram_warn`, `gpu.vram_crit` | sem norma de fabricante |
| RAM | 90 % | 95 % | `ram.warn`, `ram.crit` | Zabbix: 90 % |
| RAM °C (DDR5) | 55 | 85 | `cpu.temps_limites.ram` | limites alto e crítico do próprio módulo (SPD5118, lidos do hwmon) |
| SSD °C (NVMe) | 80 | 90 | `cpu.temps_limites.ssd` | aviso de 89,85 °C e crítico de 93,85 °C gravados no SSD |
| Placa-mãe °C | 70 | 80 | `cpu.temps_limites.placa` | limite de 80 °C do chip NCT6799D (hwmon) |
| Disco (uso) | 80 % ou menos de 50 GB livres | 90 % ou menos de 10 GB livres | `disco_warn`, `disco_crit`, `disco_livre_warn_gb`, `disco_livre_crit_gb` | Zabbix: 80 e 90 % |
| Disco °C | HDD 50, SSD 80 | HDD 60, SSD 90 | `disco_temp_limites` | Seagate BarraCuda: operação até 60 °C ([manual](https://www.manualowl.com/m/Seagate/Barracuda/Manual/273400?page=21)) |
| Ping | acima de 20 ms ou 1ª falha | acima de 100 ms ou 3 falhas seguidas | `ping.warn_ms`, `ping.crit_ms` | escolha do Lucas, mais rígida que a [ITU-T G.114](https://www.cs.columbia.edu/%7Eandreaf/new/documents/other/T-REC-G.114-200305.pdf) |
| Bomba e ventoinhas | girando abaixo de 600 RPM | bomba parada depois de já ter girado | `cpu.fan_min_rpm` | alarme típico de BIOS |
| Ventoinha parada | componente a 60 °C ou mais | componente na faixa de atenção | `cpu.fan_stop_ok_below_c` | |
| Ethernet | link abaixo da maior velocidade já vista | sem nenhum link | | boa prática de monitoramento de interface |

Informativos, sem cor de alerta: uso da GPU (100 % em jogo é o esperado), potência da GPU, frequência da CPU, FPS e velocidade de download e upload.

**Contra ruído de leitura:** as leituras contínuas (temperaturas, VRAM, RAM, ventoinhas, clock da GPU) só sobem de cor depois de ficar 2 s no novo nível. O ping vale pela última leitura (é lido a cada 5 s), assim como discos e baias.

**Tempo mínimo na tela:** âmbar e vermelho ficam pelo menos 5 minutos, para dar tempo de ver; depois a cor acompanha a leitura e volta ao verde quando ela normaliza. Chave: `alertas: {confirmar_s: 2, manter_s: 300}`.

**Ping:** aparece com uma casa decimal e o limite é "acima de" sobre o número exibido: `20.0ms` ainda é verde, `20.1ms` já é âmbar.

Abaixo de `fan_stop_ok_below_c` (60 °C), ventoinha parada é modo semipassivo e não alerta. Uma entrada que nunca girou (conector vazio) aparece como `0` neutro.

A **histerese** evita que a cor pisque entre dois níveis: `histerese: {temperatura: 3, percentual: 2, ping_ms: 0}` (no ping, a permanência de 5 minutos já evita piscar).

**LOG de alertas (GAMMA DELTA):** cada vez que um indicador entra em âmbar ou vermelho, o LOG registra a hora, a leitura e a cor (a volta ao verde não entra). Alertas com mais de 1 hora aparecem esmaecidos.

## Ventoinhas e temperaturas da placa

```yaml
cpu:
  fans: {bomba: fan1, radiador: fan2, sq_inf: fan3, sq_lat: fan4, sq_tras: fan5}
  temps: {placa: nct6799/SYSTIN, ram: spd5118/*, ssd: nvme/Composite}
```

As ventoinhas são lidas direto de `/sys/class/hwmon/*/fanN_input`. As temperaturas usam `chip/rótulo`, e `*` significa o maior valor do chip. Leituras 0 e 105 °C são entradas sem sensor e são descartadas.

O mapa padrão é um palpite (no PC de referência, `fan3` lê 0; como INF e LAT estão em série, o GAMMA DELTA mostra em SQUAMA a entrada que tem leitura). Para descobrir qual entrada é cada ventoinha, use o mapeador guiado. Ele pede que você desconecte um cabo por vez e grava `~/.config/matrixgreenpro/fans.yaml`, que substitui `cpu.fans`. A bomba nunca é desconectada.

⚠️ Rode o mapeador com o PC ligado e acompanhe as instruções na tela:

```bash
cd ~/turing-smart-screen-linux && .venv/bin/python3 tools/mgp_mapear_fans.py
```

## Discos

```yaml
discos:
  - {nome: "M.2", serie: "", uuid: "", montagem: "/"}
  - {nome: "2T",  serie: "", uuid: "", montagem: ""}
  - {nome: "4T",  serie: "", uuid: "", montagem: ""}
```

Os discos são identificados, nesta ordem, pelo número de série (`serie`), pelo UUID do sistema de arquivos e pelo ponto de montagem, nunca por `/dev/sdX`. A série é o nome do disco em `/dev/disk/by-id` (por exemplo `ata-ST2000DM006-2DM164_Z4Z95AL7`) ou só o número de série (`Z4Z95AL7`); ela não muda quando o disco é formatado, ao contrário do UUID. Se o UUID configurado sumir e houver montagem configurada, vale a montagem. Com a série, o painel mostra o ponto de montagem configurado, a raiz `/` ou a maior partição do disco. Disco desmontado aparece como DESMONTADO, em branco e sem alerta (como as baias). Discos montados através de VeraCrypt, LUKS ou LVM são reconhecidos: o coletor segue o dispositivo `dm-N` até a partição física. O GAMMA DELTA soma todos os discos e baias montados (cada dispositivo uma vez) no hexágono do total. ⚠️ Preencha a série com a saída de `ls -l /dev/disk/by-id` (ou o UUID com `lsblk -f`). A ferramenta `tools/mgp_detect.py` cria uma configuração inicial com o que encontrar.

## Gabinete TerraMaster (baias)

```yaml
terramaster: {ativo: auto, hub: "0bda:0423", ponte: "174c:235c", baias: 4, inverter: false, mapa: {}}
```

O gabinete aparece como um hub USB (`hub`) com uma ponte USB-SATA (`ponte`) por baia. A porta do hub é o número da baia. Se a baia 1 da tela não for a baia 1 do gabinete, use `inverter: true` ou um `mapa` de porta para baia. As baias montadas mostram uso e percentual (também via VeraCrypt ou LUKS), e o percentual usa a cor dos limites dos discos. O recurso é só informativo: não entra na saúde nem na contagem de alertas. Com `ativo: nao`, ele fica desligado.

⚠️ Para conferir a numeração, rode e compare com o gabinete:

```bash
cd ~/turing-smart-screen-linux && .venv/bin/python3 tools/mgp_baias.py
```

## Rede, ping e clima

| Chave | Padrão | Função |
|---|---|---|
| `rede.ethernet`, `rede.wifi` | `auto` | interfaces mostradas |
| `rede.ethernet_obrigatoria` | `false` | `true` faz Ethernet caída gerar aviso mesmo com Wi-Fi ativo |
| `ping.host` | `8.8.8.8` | destino do ping (intervalo de 5 s) |
| `clima.cidade`, `latitude`, `longitude` | Rio do Sul (-27.2139, -49.6428) | local do clima no Open-Meteo |
| `clima.intervalo_min` / `desatualizado_min` | 15 / 45 | frequência e idade máxima do dado |

Sem nenhum enlace (nem Ethernet nem Wi-Fi) é sempre crítico. A internet é avaliada à parte, pelo ping: `INTERNET OK`, `INSTÁVEL`, `SEM INTERNET` ou `SEM REDE` (no GAMMA DELTA, `INTERNET ON` ou `INTERNET OFF`). O ping aparece com uma casa decimal.

## Energia e FPS

- `energia.fonte`: `auto`, `none`, `hwmon` (fonte digital com driver), `arquivo`, `tasmota` ou `shelly_gen2`. Sem medidor, TOTAL W aparece como N/D. `psu_watts` define a capacidade da fonte para os alertas (0 desliga).
- `fps.mangohud_dir`: pasta dos registros do MangoHud (padrão `/tmp/mgp-mangohud`). O FPS só aparece com jogos rodando sob o MangoHud.

## Histórico dos gráficos (GAMMA DELTA)

O histórico de 24 h fica em `~/.local/state/matrixgreenpro/historico.json`, com média e máximo de cada intervalo de cerca de 10 minutos, e é gravado a cada intervalo fechado. Para recomeçar os gráficos do zero, pare o serviço e apague esse arquivo.
