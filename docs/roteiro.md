<!-- docs/roteiro.md | versão 2.0.0 | 07/11/2026 22:30 (-03) | criação original (Claude, para Lucas Tavares). Fonte: pendências do projeto em 07/11/2026, depois da v1.8.2. -->
<!-- histórico: 2.0.0 07/11/2026 22:30 validações feitas na tela física, drivetemp, LOG em disco, estudos e Releases -->

# Roteiro

[Voltar ao README](../README.md)

Pendências em ordem de prioridade. Os itens marcados com ⚠️ exigem ação do Lucas na máquina real.

## Validação em hardware

Já validados na tela física (07/11/2026): imagem, selo de versão, sensores de CPU, GPU, RAM, NVMe e placa, ping, gráficos de 24 h, LOG e as 4 baias do TerraMaster, inclusive um disco com VeraCrypt.

1. ⚠️ **Bomba e ventoinhas:** rodar `tools/mgp_mapear_fans.py` para gerar o `fans.yaml`. O mapa padrão é um palpite: `fan3` (mapeado como SQUAMA INF) lê 0 e o DELTA mostra a LAT no lugar.
2. ⚠️ **Temperatura dos HDs SATA:** o módulo `drivetemp` não está carregado no PC (não aparece no `lsmod` nem em `/etc/modules-load.d/`), por isso os HDs mostram N/D. Conferir por que o instalador não o carregou.
3. ⚠️ **Baias:** rodar `tools/mgp_baias.py` e conferir se a baia 1 do tema é a baia 1 do gabinete; corrigir com `terramaster.inverter` ou `terramaster.mapa`.
4. **Discos em repouso:** depois do `drivetemp`, confirmar se a leitura acorda discos em standby. Se acordar, ler a temperatura só com o disco ativo ou aumentar o intervalo.

## Recursos opcionais

5. Temperatura dos discos do TerraMaster pela ponte USB com `smartctl -d sat` (exige root ou regra de permissão; avaliar custo e utilidade antes).
6. Alerta para baia que tinha disco e ficou livre (precisa de confirmação: retirar um disco de propósito também alertaria).
7. Guardar o LOG em disco, para sobreviver a reinícios do serviço (hoje fica na memória).

## Organização do repositório

8. Remover `construir-zips.sh` e `publicar-no-github.sh`, substituídos por `construir/construir_zips.py` e `gh release create` (veja o [desenvolvimento](desenvolvimento.md)).
9. Decidir o destino dos estilos de estudo e legados (propostas v2, variantes do DELTA e do GAMMA GAMMA, sonar, raio-x, uv, n3, faixa, `pcb`): arquivar, remover ou levar adiante na v2.0.0.
10. Revisar redundâncias: taxas de ETH repetidas, SSD° no favo do BETA e na linha do disco, e o CORE duplicando a escala N0/N1/N2.

## Qualidade

11. Testes automáticos no CI do GitHub (autoteste e prévias), checagem de lint e um modo de simulação que dispense a árvore do Turing.
12. Instalar o `fontTools` no ambiente de testes para a conferência de glifos voltar a valer.
13. Automatizar a publicação das Releases (notas a partir do CHANGELOG e ZIPs do commit da versão).
