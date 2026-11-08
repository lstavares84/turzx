<!-- docs/decisoes-e-licoes.md | versão 2.0.0 | 07/11/2026 22:24 (-03) | criação original (Claude, para Lucas Tavares). Fonte: histórico do projeto de 31/10/2026 a 07/11/2026. -->
<!-- histórico: 2.0.0 07/11/2026 22:24 decisões e lições das versões 1.7.0 a 1.8.2 -->

# Decisões e lições

[Voltar ao README](../README.md)

Este documento explica por que o GAMMA é como é. Antes de propor uma mudança, confira se ela não desfaz uma decisão abaixo.

## Linha do tempo

| Data | Marco |
|---|---|
| 31/10/2026 | MATRIX GREEN PRO: primeiro tema, minimalista em preto, branco e verde (numeração interna 1.x e 2.x) |
| 01/11/2026 | catálogo de estilos e finalistas: NÚCLEO URÂNIO e PLACA DE CIRCUITO (3.0 e 3.1) |
| 02/11/2026 | URÂNIO vira GAMMA; variantes de alerta e a escala N0/N1/N2 (3.2 a 3.6) |
| 02/11/2026 | adoção do SemVer: 1.0.0 SENTINELA, 1.1.0 DOSÍMETRO, 1.2 bomba e ventoinhas, 1.3 temperaturas, 1.4 ALPHA, BETA e GAMMA |
| 07/11/2026 | 1.5.0 baias do TerraMaster, 1.6.0 selo de estilo e versão |
| 07/11/2026 | 1.7.0 quarto pacote, GAMMA DELTA (colmeia à direita, gráficos de 24 h, baias com uso) |
| 07/11/2026 | 12 propostas da v2.0.0 e variantes de estudo guardadas como brainstorm |
| 07/11/2026 | 1.8.0 alertas por limites de manuais e do Zabbix, LOG, o DELTA 5B vira o GAMMA DELTA |
| 07/11/2026 | 1.8.1 ping de 20 ms verde e alerta mantido 5 min; 1.8.2 LOG só com alertas, ping com decimal, HDs via VeraCrypt |
| 07/11/2026 | releases v1.6.0 a v1.8.2 publicadas no GitHub com os ZIPs |

## Decisões de produto

- **Pacotes enxutos.** Cada estilo é um ZIP separado, só com os arquivos necessários e o seu instalador. Um pacote com 53 arquivos foi recusado.
- **"O mais automático possível".** O instalador faz tudo de ponta a ponta e só pede a senha do `sudo` quando precisa.
- **Estilos na mesma versão.** No início a numeração seguia a ordem de lançamento; hoje os quatro (ALPHA, BETA, GAMMA e DELTA) saem juntos.
- **Sem RPM da GPU.** O driver NVIDIA só informa o percentual; um campo sempre vazio não serve para nada.
- **Temperaturas sem linhas novas.** Placa, RAM e SSD entraram no favo no lugar de LOAD, TOTAL W e COLETA, que já estavam nas linhas de texto.
- **GAMMA GAMMA.** Passou por quatro variantes (COLMEIA, MINI, PAINEL e FRONTEIRA). A FRONTEIRA, com linhas brancas, foi rejeitada. A direção final: CORE no centro, 7 hexágonos de resumo com 3 estados, números só no painel de texto e nenhum rótulo ao redor.
- **CORE redundante com a escala.** O hexágono CORE mostra a mesma informação da escala N0/N1/N2. A redundância foi assumida e aceita.
- **Layout do rodapé.** Clima separado no canto inferior direito, data acima da hora. TOTAL W e COLETA saíram do GAMMA GAMMA; no BETA só somem quando as baias aparecem.
- **Selo de estilo e versão** no canto superior direito de todas as telas.
- **Desmontado não é alerta.** Nem as baias nem os discos configurados: desmontar ou retirar um disco de propósito não deve gerar alarme (desde a 1.8.3, os discos seguem a regra das baias).
- **Tela física só com autorização.** Nenhuma versão vai para a tela sem um sim explícito do Lucas, a cada envio, e a mudança é vista na tela antes do commit.
- **GAMMA DELTA.** Escolhido entre seis variantes e três subvariantes: valores em alerta com fundo âmbar ou vermelho (preferido à marca só de cor), gráficos com os nomes girados para ganhar largura, VRAM e RAM no mesmo gráfico, pico de 24 h como ponto, total dos HDs num hexágono e barra de uso da RAM junto da palavra RAM.
- **Alertas por limites absolutos, não por variação.** A marca de "mudança brusca" foi testada e abandonada: o ruído natural dos sensores (o Tctl da CPU salta 2 °C em 1 s parado; a GPU troca de clock em até 1500 MHz por segundo) gerava alarme falso, e nenhum manual define limite de variação. Os limites vêm dos manuais, do próprio hardware e do Zabbix, com as fontes em [configuração](configuracao.md).
- **2 s para subir, 5 min para descer.** Uma leitura contínua só muda de cor depois de 2 s (ruído não vira alerta); âmbar e vermelho ficam no mínimo 5 min para dar tempo de ver. Ping, discos e baias valem pela última leitura.
- **Ping verde até 20 ms**, com uma casa decimal, classificado pelo número exibido. Mais rígido que a ITU-T G.114, por escolha do Lucas.
- **LOG só com âmbar e vermelho.** A volta ao verde não entra; o LOG acumula até 20 alertas.
- **Limite de potência da GPU não é alerta.** Bater os 300 W em jogo é o controle normal da placa.
- **Uso da GPU é informativo;** o da CPU só alerta depois de 5 min acima de 90 %.

## Lições aprendidas (não repetir)

- ZIP extraído pelo Python perde o bit de execução: teste o instalador com `unzip`.
- A mensagem de commit do script de publicação saía como "patch1.1.0" (corrigido com `NIVEL_TXT`).
- `nct6683` com `force=1` falha; o chip é NCT6799D e o driver certo é `nct6775`.
- A numeração posicional de ventoinhas do `psutil` não coincide com `fanN`: leia o sysfs.
- Linhas novas de texto causaram sobreposição muitas vezes: confira com `mgp_preview.py` e mexa em espaçamentos aos poucos.
- No autoteste, uma variável local chamada `base` colidiu com a função `base()`. Cuidado com nomes.
- Alertas novos mudam as contagens esperadas no autoteste (por exemplo, a demonstração Atenção passou a 5 avisos e a Crítico a 3 críticos depois da temperatura dos discos).
- O desenvolvimento aconteceu num ambiente sem a tela, sem a GPU e sem os sensores. Tudo que depende de hardware precisa ser validado na máquina real.
- O selo mostra `dev` quando o tema é instalado direto do repositório: para ver a versão na tela, instale pelo ZIP (`construir/aplicar-na-tela.sh`).
- O instalador procurava o arquivo do estilo pelo nome (`reator_<estilo>.py`) e recusava estilos com outro nome de arquivo e apelidos: hoje ele confere o registro `ESTILOS`/`ALIASES`.
- O construtor dos ZIPs reescreve a lista de estilos do autoteste até `"pcb"`: estilo novo depois dele deixa o ZIP testando estilos que não existem.
- Ping classificado pelo valor real e exibido arredondado acendia o âmbar com "20ms" na tela, e uma histerese de 5 ms prendia o âmbar até 15 ms: classifique pelo número exibido e mantenha a histerese pequena.
- Disco montado por VeraCrypt ou LUKS aparece como `/dev/dm-N`, não como a partição: siga `/sys/block/dm-N/slaves` até o disco físico.
- Variável local com o mesmo nome de uma função do módulo (`total`, `base`) já quebrou o modelo de visão e o autoteste.
- A conferência de glifos depende do `fontTools`; sem ele, passa em silêncio. A Generale Mono, por exemplo, não desenha bem Ç e Õ.
- Horários nos cabeçalhos dos arquivos: use a hora real (`date`), não uma estimativa.
