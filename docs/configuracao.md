<!-- docs/configuracao.md | versão 1.0.0 | 07/11/2026 15:20 (-03) | criação original (Claude, para Lucas Tavares). Fonte: pacote/sensors/matrixgreenpro/settings.py e pacote/extras/config.exemplo.yaml da v1.6.0. -->

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

| Indicador | Atenção | Crítico | Chaves |
|---|---|---|---|
| CPU °C | automático pelo modelo (Ryzen 7000/8000/9000: 88) | automático (Ryzen 7000/8000/9000: 94) | `cpu.temp_warn`, `cpu.temp_crit` |
| GPU °C | limite de desaceleração da NVML menos 10 | NVML menos 3 (sem NVML: 80/87) | `gpu.temp_warn`, `gpu.temp_crit` |
| VRAM | 90% | 97% | `gpu.vram_warn`, `gpu.vram_crit` |
| RAM | 85% | 95% | `ram.warn`, `ram.crit` |
| RAM °C | 50 | 55 | `cpu.temps_limites.ram` |
| SSD °C (NVMe) | 70 | 80 | `cpu.temps_limites.ssd` |
| Disco (uso) | 85% ou menos de 50 GB livres | 95% ou menos de 10 GB livres | `disco_warn`, `disco_crit`, `disco_livre_warn_gb`, `disco_livre_crit_gb` |
| Disco °C | HDD 50, SSD 70 | HDD 55, SSD 80 | `disco_temp_limites` |
| Ping | 80 ms ou 1ª falha | 200 ms ou 3 falhas seguidas | `ping.warn_ms`, `ping.crit_ms` |
| Bomba | | 0 RPM depois de já ter girado | |
| Ventoinha parada | componente a 60 °C ou mais | componente na faixa de atenção | `cpu.fan_stop_ok_below_c` |

Abaixo de `fan_stop_ok_below_c` (60 °C), ventoinha parada é modo semipassivo e não alerta. Uma entrada que nunca girou (conector vazio) aparece como `0` neutro.

A **histerese** evita que a cor pisque entre dois níveis: `histerese: {temperatura: 3, percentual: 2, ping_ms: 15}`.

## Ventoinhas e temperaturas da placa

```yaml
cpu:
  fans: {bomba: fan1, radiador: fan2, sq_inf: fan3, sq_lat: fan4, sq_tras: fan5}
  temps: {placa: nct6799/SYSTIN, ram: spd5118/*, ssd: nvme/Composite}
```

As ventoinhas são lidas direto de `/sys/class/hwmon/*/fanN_input`. As temperaturas usam `chip/rótulo`, e `*` significa o maior valor do chip. Leituras 0 e 105 °C são entradas sem sensor e são descartadas.

O mapa padrão é um palpite. Para descobrir qual entrada é cada ventoinha, use o mapeador guiado. Ele pede que você desconecte um cabo por vez e grava `~/.config/matrixgreenpro/fans.yaml`, que substitui `cpu.fans`. A bomba nunca é desconectada.

⚠️ Rode o mapeador com o PC ligado e acompanhe as instruções na tela:

```bash
cd ~/turing-smart-screen-linux && .venv/bin/python3 tools/mgp_mapear_fans.py
```

## Discos

```yaml
discos:
  - {nome: "M.2", uuid: "", montagem: "/"}
  - {nome: "2T",  uuid: "", montagem: ""}
  - {nome: "4T",  uuid: "", montagem: ""}
```

Os discos são identificados por UUID (persistente), nunca por `/dev/sdX`. Disco desmontado aparece como OFF. ⚠️ Preencha os UUIDs com a saída de `lsblk -f`. A ferramenta `tools/mgp_detect.py` cria uma configuração inicial com o que encontrar.

## Gabinete TerraMaster (baias)

```yaml
terramaster: {ativo: auto, hub: "0bda:0423", ponte: "174c:235c", baias: 4, inverter: false, mapa: {}}
```

O gabinete aparece como um hub USB (`hub`) com uma ponte USB-SATA (`ponte`) por baia. A porta do hub é o número da baia. Se a baia 1 da tela não for a baia 1 do gabinete, use `inverter: true` ou um `mapa` de porta para baia. O recurso é só informativo: não entra na saúde nem na contagem de alertas. Com `ativo: nao`, ele fica desligado.

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

Sem nenhum enlace (nem Ethernet nem Wi-Fi) é sempre crítico. A internet é avaliada à parte, pelo ping: `INTERNET OK`, `INSTÁVEL`, `SEM INTERNET` ou `SEM REDE`.

## Energia e FPS

- `energia.fonte`: `auto`, `none`, `hwmon` (fonte digital com driver), `arquivo`, `tasmota` ou `shelly_gen2`. Sem medidor, TOTAL W aparece como N/D. `psu_watts` define a capacidade da fonte para os alertas (0 desliga).
- `fps.mangohud_dir`: pasta dos registros do MangoHud (padrão `/tmp/mgp-mangohud`). O FPS só aparece com jogos rodando sob o MangoHud.
