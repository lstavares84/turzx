<!-- docs/roteiro.md | versão 1.0.0 | 07/11/2026 15:45 (-03) | criação original (Claude, para Lucas Tavares). Fonte: pendências registradas na transferência do projeto em 07/11/2026. -->

# Roteiro

[Voltar ao README](../README.md)

Pendências em ordem de prioridade. Os itens marcados com ⚠️ exigem ação do Lucas na máquina real.

## Validação em hardware

1. ⚠️ **Tela física:** orientação, brilho, bloom e o piscar do crítico; reinício e início automático do serviço; leitura do relatório do instalador.
2. ⚠️ **Bomba e ventoinhas:** rodar `tools/mgp_mapear_fans.py` para gerar o `fans.yaml`. Hoje o mapa padrão é um palpite e `fan3` lê 0, apesar de haver 5 conectores em uso.
3. ⚠️ **Baias:** rodar `tools/mgp_baias.py` e conferir se a baia 1 do tema é a baia 1 do gabinete; corrigir com `terramaster.inverter` ou `terramaster.mapa`.
4. **Discos em repouso:** confirmar se a leitura do `drivetemp` acorda discos em standby. Se acordar, ler a temperatura só com o disco ativo ou aumentar o intervalo.

## Recursos opcionais

5. Temperatura dos discos do TerraMaster pela ponte USB com `smartctl -d sat` (exige root ou regra de permissão; avaliar custo e utilidade antes).
6. Alerta para baia que tinha disco e ficou livre (precisa de confirmação: retirar um disco de propósito também alertaria).

## Organização do repositório

7. Reescrever ou remover `construir-zips.sh` (substituído por `construir/construir_zips.py`) e adaptar `publicar-no-github.sh` à estrutura atual: uma pasta de projeto, SemVer e ZIPs como artefatos de Release. Atualizar o `pacote/README.md`, que ainda descreve as versões 1.3.0 e anteriores.
8. Decidir se os estilos experimentais (sonar, raio-x, uv, n3, faixa e outros), as variantes antigas do GAMMA GAMMA (colmeia, mini, painel), se a variante coluna substitui o GAMMA GAMMA atual e o `pcb` (que tem erros de cobertura de métricas) serão arquivados ou removidos.
9. Revisar redundâncias: taxas de ETH repetidas, SSD° no favo do BETA e na linha do disco, e o CORE duplicando a escala N0/N1/N2.
10. Os ZIPs 1.6.0 já entregues têm um travessão residual e invisível (texto interno do campo `gpu_fan_rpm`, que não aparece na tela) em `viewmodel.py` e `mgp_selftest.py`. Já está corrigido neste fonte; sai na próxima versão PATCH.

## Qualidade

11. Testes automáticos no CI do GitHub (autoteste e prévias), checagem de lint e um modo de simulação que dispense a árvore do Turing.
12. Publicar capturas reais dos três estilos (geradas com `mgp_preview.py`) no lugar do esquema ilustrativo do README.
