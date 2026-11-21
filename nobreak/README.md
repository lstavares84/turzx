<!-- nobreak/README.md | versão 1.3.0 | 21/11/2026 17:44 (-03) | criação original (Claude, para Lucas Tavares) -->
<!-- histórico: 1.3.0 21/11/2026 17:44 dinheiro acumulado (gasto, gerado, saldo), cotação automática do dólar, MINERANDO piscando -->
<!-- histórico: 1.2.0 21/11/2026 10:48 histórico retomado ao reiniciar, gráficos por tempo, faixas da ANEEL e do fabricante -->
<!-- histórico: 1.1.0 21/11/2026 10:33 tag MINERANDO e médias separadas por minerando ou não -->

# Tela do nobreak (TURZX de 5,2", paisagem)

A tela de 5,2" mostra só o nobreak Ragtech New Easy Pro NEP 1200 (modelo 4162), em paisagem (1280x720), atualizada a cada 1 segundo. Cada leitura também entra num log em CSV.

![Tela do nobreak com dados de demonstração](../docs/img/nobreak-5.2.png)

<sub>Dados de demonstração: um período minerando (faixa mais clara nos gráficos), uma queda de energia e 1 minuto desligado (trecho em branco).</sub>

## O que aparece

- Estado em destaque: REDE ADEQUADA (verde), REDE PRECÁRIA (âmbar), REDE CRÍTICA (vermelho), NA BATERIA (âmbar) ou SEM LEITURA (vermelho).
- Tag da mineração: MINERANDO (piscando, 1 s aceso e 1 s apagado) ou SEM MINERAÇÃO, ao lado do estado.
- Dinheiro acumulado desde a primeira execução: gasto com a energia enquanto minera, valor gerado pela mineração (estimado) e saldo, em reais e em dólares, mais o tempo total minerando e a energia total que passou pelo nobreak. Ao reiniciar, continua de onde parou.
- Cotação do dólar, automática, com a fonte e a hora da cotação.
- Médias de hoje separadas em minerando e sem mineração: tempo, potência média, pico, carga e temperatura, para comparar o comportamento.
- Entrada, saída, frequência, corrente, potência (V x A), carga (com a carga informada pelo firmware), bateria (% e V) e temperatura, cada um com o valor atual, o mínimo, a média e o máximo do dia e a faixa de operação, com a situação (ADEQUADA, PRECÁRIA, CRÍTICA, NORMAL, FORA ou OK).
- Rede hoje: a parte do dia com a tensão de entrada adequada, precária e crítica, as quedas de energia e o tempo na bateria; durante uma queda, há quanto tempo está na bateria.
- Os alarmes do próprio nobreak (bateria fraca, sobrecarga, superaquecimento e outros). Só eles decidem âmbar e vermelho; nenhum limite foi inventado aqui.
- Gráficos dos últimos 15 minutos: tensão de entrada e de saída, potência e tensão da bateria, com o tempo minerando marcado por uma faixa mais clara.

## Faixas de operação

| Variável | Faixa | Fonte |
|---|---|---|
| Tensão de entrada (rede de 220 V) | adequada 202 a 231 V; precária 191 a 202 V ou 231 a 233 V; crítica abaixo de 191 V ou acima de 233 V | ANEEL, PRODIST Módulo 8 (Anexo VIII da REN 956/2021), Anexo 8.A, tabelas 4 e 5 |
| Tensão de entrada (rede de 127 V, `--rede 127`) | adequada 117 a 133 V; precária 110 a 117 V ou 133 a 135 V; crítica fora disso | idem |
| Frequência | normal 59,9 a 60,1 Hz; fora da faixa até 59,5 a 60,5 Hz; crítica fora disso | ANEEL, PRODIST Módulo 8, itens 65 e 66 |
| Tensão de saída | 115 V com regulação de mais ou menos 2 % (112,7 a 117,3 V) | ficha do fabricante (anúncios do NEP 1200, modelo 4162) |
| Potência e carga | até 840 W (1200 VA), 100 % | ficha do fabricante |
| Corrente, bateria e temperatura | sem faixa publicada; só os alarmes do próprio nobreak | |

A classificação na tela é da leitura instantânea e serve como indicação: a apuração oficial da ANEEL usa médias de 10 minutos. O manual oficial da Ragtech não estava acessível; os dados do fabricante vêm de fichas de lojas.

## Como funciona

- Leitura: `ragtech_read.py`, do repositório `ragtech_4162` (só leitura, protocolo do driver `ragtech` do NUT). Este programa usa só a função `poll()` e nunca envia comando de escrita ao nobreak. A calibração dos valores é do leitor.
- Tela: biblioteca do turing-smart-screen-python (`LcdCommTuringUSB`), sem uma segunda instância do programa. A tela de 3,5" continua com o serviço do Turing.
- Mineração: o computador conta como minerando quando um processo de mineração conhecido está rodando (Kryptex, XMRig, lolMiner, GMiner, T-Rex, NBMiner, TeamRedMiner, SRBMiner, BzMiner, Rigel, OneZeroMiner, NanoMiner, Excavator, Ethminer, WildRig). Para trocar a lista: `--mineradores nome1,nome2` ou a variável `NOBREAK_MINERADORES`. Começar e parar de minerar entram no log de eventos.
- Dinheiro: o acumulado fica em `~/.local/state/nobreak/acumulado.json`, gravado a cada 30 s e ao parar o serviço; ao iniciar, a tela continua dele. Gasto = energia medida na saída do nobreak enquanto minera x tarifa. Gerado = receita estimada pelo hashrate do SRBMiner (lido do log em `~/mineracao/logs`), pela receita de referência por dia a um hashrate de referência, o mesmo modelo do painel do chat da mineração. A tarifa (R$ 0,869/kWh, Celesc), a receita de referência (US$ 3,05/dia a 190 TH/s) e o câmbio de reserva vêm de `~/mineracao/painel.conf`, relido a cada minuto: mudou lá, muda aqui. Saldo = gerado - gasto; os valores em outra moeda usam a cotação do momento.
- Cotação: dólar comercial (venda) da AwesomeAPI (`economia.awesomeapi.com.br`, gratuita, sem chave, com atraso de alguns minutos e só em dia útil), consultada a cada 10 min em segundo plano e guardada em `cotacao.json`. Sem internet, vale a última guardada; sem nenhuma, o câmbio do `painel.conf`.
- Log: `~/.local/state/nobreak/nobreak-AAAA-MM-DD.csv`, uma linha por leitura, com a coluna `minerando` (sim ou não), separada por ponto e vírgula, com data e hora `dd/mm/aaaa HH:MM:SS`; eventos (quedas, volta da rede, alarmes, mineração, falhas de leitura) em `nobreak-eventos.log`.

## Instalar

⚠️ Uma vez só, libere a tela de 5,2" para o seu usuário (a regra que já existe no PC cobre só o produto `0028`):

```bash
sudo cp 99-turzx-52.rules /etc/udev/rules.d/ && sudo udevadm control --reload && sudo udevadm trigger
```

Depois, com o usuário comum:

```bash
./instalar.sh
```

Para parar: `./instalar.sh --parar`. Depois de reiniciar, o dia inteiro (mínimos, médias, máximos, tempos por faixa, mineração e quedas) e os últimos 15 minutos dos gráficos voltam do CSV e do log de eventos; o período desligado ou sem leitura fica em branco nos gráficos. Respostas embaralhadas do nobreak (modelo desconhecido) são descartadas e contadas como falha. A prévia (`--previa`) desenha a partir do log, sem abrir a porta do nobreak. Para ver um quadro sem usar a tela: `python3 nobreak_tela.py --previa quadro.png` (ou `--demo`).

Só um programa por vez pode ler a porta serial do nobreak. Com o serviço ligado, use o CSV do log em vez de rodar o `ragtech_read.py` em paralelo.
