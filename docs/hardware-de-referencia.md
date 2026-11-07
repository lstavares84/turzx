<!-- docs/hardware-de-referencia.md | versão 1.0.0 | 07/11/2026 15:30 (-03) | criação original (Claude, para Lucas Tavares). Fonte: leituras de hardware enviadas pelo Lucas entre 31/10/2026 e 07/11/2026. -->

# Hardware de referência e coleta

[Voltar ao README](../README.md)

O GAMMA foi feito para um PC específico. Os padrões de configuração refletem essa máquina, mas tudo pode ser ajustado no [config.yaml](configuracao.md).

## A máquina

| Componente | Modelo | Observação |
|---|---|---|
| Sistema | Debian 13 (trixie), kernel 6.12 | |
| Placa-mãe | ASRock B850M Pro-A | chip de sensores Nuvoton NCT6799D-R, driver `nct6775` |
| GPU | MSI GeForce RTX 5070 Ti 16 GB Shadow 3X OC | informa só o percentual da ventoinha, sem RPM; sem temperatura de memória e hotspot |
| Refrigeração | water cooler Eskimo 36 (3 ventoinhas no radiador e bomba) e 5 ventoinhas Squama no gabinete | 4 reversas (3 na base, 1 na lateral) e 1 normal na traseira; não há ventoinha sobre a CPU |
| SSD | NVMe de 2 TB (raiz em LUKS) | temperatura pelo hwmon do NVMe |
| HDDs internos | 4 TB e 2 TB SATA | temperatura pelo módulo `drivetemp` |
| Gabinete externo | TerraMaster DAS USB de 4 baias | hub Realtek `0bda:0423` com 4 pontes ASMedia `174c:235c` |
| Tela | TURZX / Turing TUS-35 de 3,5" | USB `1a86:5722` |

A `amdgpu` que aparece no hwmon é a GPU integrada do processador Ryzen, não a placa de vídeo.

### Ligação das ventoinhas (informada pelo Lucas)

| Conector | Ligado a | Papel no tema |
|---|---|---|
| CPU_FAN1 | radiador (com divisor) | `radiador` (RAD) |
| CPU_FAN2 | bomba | `bomba` |
| CHA_FAN1 | 3 ventoinhas da base (com divisor) | `sq_inf` (INF) |
| CHA_FAN2 | lateral | `sq_lat` (LAT) |
| CHA_FAN3 | traseira | `sq_tras` (TRA) |

Leituras observadas: `fan1` perto de 5600 RPM estável (provavelmente a bomba), `fan2`, `fan4` e `fan5` em torno de 1400 RPM, `fan3` e `fan7` em 0. O mapa padrão do tema é um palpite até ser confirmado com o mapeador (veja o [roteiro](roteiro.md)). Com divisor, cada conector entrega uma única leitura.

## Decisões de coleta

- **Ventoinhas e temperaturas direto do sysfs** (`/sys/class/hwmon/*`), não pelo `psutil`: a numeração posicional do psutil não bate com `fanN`.
- **Driver certo:** o chip NCT6799D funciona com `nct6775`. O `nct6683` (mesmo com `force=1`) falha com "No such device". O instalador carrega `nct6775` e `drivetemp` e grava em `/etc/modules-load.d/`.
- **Temperatura por disco:** o coletor acha o bloco do disco pelo UUID ou ponto de montagem, mesmo desmontado, e lê `device/hwmon*/temp1_input`. Sem leitura, mostra N/D e não alerta. Discos atrás de ponte USB (como os do TerraMaster) não têm temperatura pelo `drivetemp`.
- **GPU:** NVML, com `nvidia-smi` como reserva. O RPM da ventoinha foi removido da tela porque o driver nunca o informa.
- **Baias:** a porta do hub é o número da baia. Baia com ponte e sem disco é LIVRE; montado significa que alguma partição do disco está montada. Não há SES (`/sys/class/enclosure` não existe), então não dá para ler LEDs nem slots pelo gabinete.
- **FPS:** lido dos registros CSV do MangoHud. O `turing-fps.service`, se existir, grava a taxa do monitor (Hz) e é ignorado de propósito.
- **Clima:** Open-Meteo, sem chave de API.
