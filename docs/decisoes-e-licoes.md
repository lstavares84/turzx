<!-- docs/decisoes-e-licoes.md | versão 1.0.0 | 07/11/2026 15:40 (-03) | criação original (Claude, para Lucas Tavares). Fonte: histórico do projeto de 31/10/2026 a 07/11/2026. -->

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

## Decisões de produto

- **Pacotes enxutos.** Cada estilo é um ZIP separado, só com os arquivos necessários e o seu instalador. Um pacote com 53 arquivos foi recusado.
- **"O mais automático possível".** O instalador faz tudo de ponta a ponta e só pede a senha do `sudo` quando precisa.
- **Três estilos na mesma versão.** No início a numeração seguia a ordem de lançamento; hoje os três saem juntos.
- **Sem RPM da GPU.** O driver NVIDIA só informa o percentual; um campo sempre vazio não serve para nada.
- **Temperaturas sem linhas novas.** Placa, RAM e SSD entraram no favo no lugar de LOAD, TOTAL W e COLETA, que já estavam nas linhas de texto.
- **GAMMA GAMMA.** Passou por quatro variantes (COLMEIA, MINI, PAINEL e FRONTEIRA). A FRONTEIRA, com linhas brancas, foi rejeitada. A direção final: CORE no centro, 7 hexágonos de resumo com 3 estados, números só no painel de texto e nenhum rótulo ao redor.
- **CORE redundante com a escala.** O hexágono CORE mostra a mesma informação da escala N0/N1/N2. A redundância foi assumida e aceita.
- **Layout do rodapé.** Clima separado no canto inferior direito, data acima da hora. TOTAL W e COLETA saíram do GAMMA GAMMA; no BETA só somem quando as baias aparecem.
- **Selo de estilo e versão** no canto superior direito de todas as telas.
- **Baias informativas.** O estado das baias não entra na saúde: retirar um disco de propósito não deve gerar alarme.

## Lições aprendidas (não repetir)

- ZIP extraído pelo Python perde o bit de execução: teste o instalador com `unzip`.
- A mensagem de commit do script de publicação saía como "patch1.1.0" (corrigido com `NIVEL_TXT`).
- `nct6683` com `force=1` falha; o chip é NCT6799D e o driver certo é `nct6775`.
- A numeração posicional de ventoinhas do `psutil` não coincide com `fanN`: leia o sysfs.
- Linhas novas de texto causaram sobreposição muitas vezes: confira com `mgp_preview.py` e mexa em espaçamentos aos poucos.
- No autoteste, uma variável local chamada `base` colidiu com a função `base()`. Cuidado com nomes.
- Alertas novos mudam as contagens esperadas no autoteste (por exemplo, a demonstração Atenção passou a 5 avisos e a Crítico a 3 críticos depois da temperatura dos discos).
- O desenvolvimento aconteceu num ambiente sem a tela, sem a GPU e sem os sensores. Tudo que depende de hardware precisa ser validado na máquina real.
