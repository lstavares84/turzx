<!-- docs/hardware-de-referencia.md | versão 2.1.0 | 08/11/2026 21:03 (-03) | criação original (Claude, para Lucas Tavares). Fonte: leituras de hardware no PC do Lucas entre 31/10/2026 e 07/11/2026 (hwmon, nvidia-smi, lsblk). -->
<!-- histórico: 2.1.0 08/11/2026 21:03 disco pelo número de série -->
<!-- histórico: 2.0.0 07/11/2026 22:24 limites lidos do hardware, discos e baias atuais, VeraCrypt, drivetemp -->

# Hardware de referência e coleta

[Voltar ao README](../README.md)

O GAMMA foi feito para um PC específico. Os padrões de configuração refletem essa máquina, mas tudo pode ser ajustado no [config.yaml](configuracao.md).

## A máquina

| Componente | Modelo | Observação |
|---|---|---|
| Sistema | Debian 13 (trixie), kernel 6.12 | |
| Placa-mãe | ASRock B850M Pro-A | chip de sensores Nuvoton NCT6799D-R, driver `nct6775` |
| CPU | AMD Ryzen 9 9900X (12 núcleos, 24 threads) | Tjmax 95 °C; temperatura pelo `k10temp` (Tctl) |
| RAM | DDR5, cerca de 30 GB visíveis | temperatura pelo `spd5118` (dois módulos) |
| GPU | MSI GeForce RTX 5070 Ti 16 GB Shadow 3X OC | informa só o percentual da ventoinha, sem RPM; sem temperatura de memória e hotspot; limite de potência 300 W |
| Refrigeração | water cooler Eskimo 36 (3 ventoinhas no radiador e bomba) e 5 ventoinhas Squama no gabinete | 4 reversas (3 na base, 1 na lateral) e 1 normal na traseira; não há ventoinha sobre a CPU |
| SSD | SanDisk Optimus GX Pro 8100 2 TB, NVMe (raiz em LUKS) | temperatura pelo hwmon do NVMe |
| HDDs internos | Seagate ST4000DM004 (4 TB) e ST2000DM006 (2 TB), SATA | temperatura pelo módulo `drivetemp` (hoje não carregado: N/D) |
| Gabinete externo | TerraMaster DAS USB de 4 baias | hub Realtek `0bda:0423` com 4 pontes ASMedia `174c:235c` |
| Discos nas baias | WD WD120EFGX (12 TB), Toshiba MK5076GSX (500 GB), Seagate ST8000DM004 (8 TB, VeraCrypt) e SanDisk SSD PLUS (480 GB) | lidos em 07/11/2026; a ordem das baias ainda não foi conferida com o `mgp_baias.py` |
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

Leituras observadas em 07/11/2026: `fan1` 5601 RPM (provavelmente a bomba), `fan2` 1473, `fan4` 1315 e `fan5` 1401 RPM, `fan3` e `fan7` em 0. Como INF e LAT estão em série, o GAMMA DELTA mostra em SQUAMA a entrada que tem leitura. O mapa padrão do tema é um palpite até ser confirmado com o mapeador (veja o [roteiro](roteiro.md)). Com divisor, cada conector entrega uma única leitura.

## Limites gravados no próprio hardware

Lidos do sysfs e do driver em 07/11/2026; são a base dos limites de alerta (veja [configuração](configuracao.md#limites-de-alerta)).

| Componente | Fonte | Valores |
|---|---|---|
| NVMe | hwmon `nvme`, `temp1_max` e `temp1_crit` | aviso 89,85 °C, crítico 93,85 °C |
| RAM DDR5 | hwmon `spd5118`, `temp1_max` e `temp1_crit` | alto 55 °C, crítico 85 °C |
| Chip de sensores | hwmon `nct6799`, `temp*_max` | 80 °C na maioria das entradas |
| GPU | `nvidia-smi -q` (T.Limit) | operação máxima ≈ 88 °C, redução de clock ≈ 90 °C, desligamento ≈ 93 °C |
| CPU | especificação da AMD | Tjmax 95 °C |

## Decisões de coleta

- **Ventoinhas e temperaturas direto do sysfs** (`/sys/class/hwmon/*`), não pelo `psutil`: a numeração posicional do psutil não bate com `fanN`.
- **Driver certo:** o chip NCT6799D funciona com `nct6775`. O `nct6683` (mesmo com `force=1`) falha com "No such device". O instalador carrega `nct6775` e `drivetemp` e grava em `/etc/modules-load.d/`.
- **Temperatura por disco:** o coletor acha o bloco do disco pelo número de série, pelo UUID ou pelo ponto de montagem, mesmo desmontado, e lê `device/hwmon*/temp1_input`. Sem leitura, mostra N/D e não alerta. Discos atrás de ponte USB (como os do TerraMaster) não têm temperatura pelo `drivetemp`.
- **GPU:** NVML, com `nvidia-smi` como reserva. O RPM da ventoinha foi removido da tela porque o driver nunca o informa.
- **Baias:** a porta do hub é o número da baia. Baia com ponte e sem disco é LIVRE; montado significa que alguma partição do disco está montada, inclusive através de VeraCrypt, LUKS ou LVM (o coletor segue `/sys/block/dm-N/slaves` até o disco físico). Não há SES (`/sys/class/enclosure` não existe), então não dá para ler LEDs nem slots pelo gabinete.
- **FPS:** lido dos registros CSV do MangoHud. O `turing-fps.service`, se existir, grava a taxa do monitor (Hz) e é ignorado de propósito.
- **Clima:** Open-Meteo, sem chave de API.
