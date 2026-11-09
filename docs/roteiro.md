<!-- docs/roteiro.md | versão 2.4.0 | 08/11/2026 20:57 (-03) | criação original (Claude, para Lucas Tavares). Fonte: pendências do projeto em 07/11/2026, depois da v1.8.2. -->
<!-- histórico: 2.4.0 08/11/2026 20:57 sinalização de internet via VPN -->
<!-- histórico: 2.3.0 08/11/2026 13:38 portas USB em uso e velocidade de leitura e escrita dos discos -->
<!-- histórico: 2.2.0 08/11/2026 13:30 validação da tela de 5,2" -->
<!-- histórico: 2.1.0 08/11/2026 12:35 protótipo GAMMA EPSILON nos estudos -->
<!-- histórico: 2.0.0 07/11/2026 22:24 validações feitas na tela física, drivetemp, LOG em disco, estudos e Releases -->

# Roteiro

[Voltar ao README](../README.md)

Pendências em ordem de prioridade. Os itens marcados com ⚠️ exigem ação do Lucas na máquina real.

## Validação em hardware

Já validados na tela física (07/11/2026): imagem, selo de versão, sensores de CPU, GPU, RAM, NVMe e placa, ping, gráficos de 24 h, LOG e as 4 baias do TerraMaster, inclusive um disco com VeraCrypt.

0. ⚠️ **Tela de 5,2" (quando chegar):** conferir o `lsusb` (`1cbe:0050`), instalar com `--tela 5.2`, ver se o serviço abre a tela (permissão USB, `pyusb`), conferir a orientação, a nitidez e o tempo de atualização (720x1280 é quase 6 vezes mais pixels que a 3,5") e se as duas telas funcionam juntas (o programa do Turing controla uma tela por instância).
1. ⚠️ **Bomba e ventoinhas:** rodar `tools/mgp_mapear_fans.py` para gerar o `fans.yaml`. O mapa padrão é um palpite: `fan3` (mapeado como SQUAMA INF) lê 0 e o DELTA mostra a LAT no lugar.
2. ⚠️ **Temperatura dos HDs SATA:** o módulo `drivetemp` não está carregado no PC (não aparece no `lsmod` nem em `/etc/modules-load.d/`), por isso os HDs mostram N/D. Conferir por que o instalador não o carregou.
3. ⚠️ **Baias:** rodar `tools/mgp_baias.py` e conferir se a baia 1 do tema é a baia 1 do gabinete; corrigir com `terramaster.inverter` ou `terramaster.mapa`.
4. **Discos em repouso:** depois do `drivetemp`, confirmar se a leitura acorda discos em standby. Se acordar, ler a temperatura só com o disco ativo ou aumentar o intervalo.

## Recursos opcionais

5. Temperatura dos discos do TerraMaster pela ponte USB com `smartctl -d sat` (exige root ou regra de permissão; avaliar custo e utilidade antes).
6. Alerta para baia que tinha disco e ficou livre (precisa de confirmação: retirar um disco de propósito também alertaria).
7. Guardar o LOG em disco, para sobreviver a reinícios do serviço (hoje fica na memória).
8. **Portas USB em uso e livres:** o kernel mostra cada porta lógica de cada controlador (`/sys/bus/usb/devices/usbN-portM`), se há algo ligado e a velocidade negociada. Em 08/11/2026 o PC tinha teclado, mouse, câmera, controlador de LED, a própria tela ("UsbMonitor") e um hub USB 3.2 a 10 Gb/s (provavelmente o TerraMaster) em uso, e vários ports livres. As portas lógicas não dizem qual é o conector físico: cada porta USB 3 aparece duas vezes (barramentos USB 2 e USB 3) e algumas são conectores internos da placa. Para nomear as portas ("traseira 3"), fazer um mapeador guiado como o das ventoinhas (ligar um pendrive em cada porta física); sem ele, mostrar só um resumo (quantas em uso, a mais rápida).
9. **Leitura e escrita de cada disco (MB/s):** diferença por segundo dos setores lidos e gravados em `/proc/diskstats`, para o NVMe, os HDs e as baias do TerraMaster (os contadores já existem para nvme0n1 e sda a sdf). Custa quase nada e não acorda disco em repouso. Mede o quanto o disco está trabalhando agora, não a velocidade máxima; um teste de desempenho (`fio` ou `dd`) ocuparia o disco e só serviria como ferramenta avulsa, rodada quando o Lucas quiser.
10. **Internet via VPN:** mostrar no grupo REDE se a internet está saindo por uma VPN (`VPN ON` ou `VPN OFF`). Como detectar: a interface da rota até a internet (`ip route get 1.1.1.1`, que respeita as regras de roteamento da VPN) e o tipo dela (`ip -d link`: WireGuard ou tun). Só informação, sem alerta; opcional um âmbar quando uma VPN esperada cair. Em 08/11/2026 o PC tinha o ProtonVPN e o `wg` instalados e nenhuma VPN ligada. ⚠️ Antes de implementar, rodar `ip -br link; ip route get 1.1.1.1` com a VPN ligada, para saber o nome da interface que o ProtonVPN cria.

## Organização do repositório

11. Remover `construir-zips.sh` e `publicar-no-github.sh`, substituídos por `construir/construir_zips.py` e `gh release create` (veja o [desenvolvimento](desenvolvimento.md)).
12. Decidir o destino dos estilos de estudo e legados (propostas v2, variantes do DELTA e do GAMMA GAMMA, protótipo EPSILON, sonar, raio-x, uv, n3, faixa, `pcb`): arquivar, remover ou levar adiante na v2.0.0.
13. Revisar redundâncias: taxas de ETH repetidas, SSD° no favo do BETA e na linha do disco, e o CORE duplicando a escala N0/N1/N2.

## Qualidade

14. Testes automáticos no CI do GitHub (autoteste e prévias), checagem de lint e um modo de simulação que dispense a árvore do Turing.
15. Instalar o `fontTools` no ambiente de testes para a conferência de glifos voltar a valer.
16. Automatizar a publicação das Releases (notas a partir do CHANGELOG e ZIPs do commit da versão).
