<!-- docs/desenvolvimento.md | versão 2.3.0 | 21/11/2026 18:40 (-03) | criação original (Claude, para Lucas Tavares). Fonte: tools/, tela-3.5-gamma/construir/ e regras do projeto na v1.8.3. -->
<!-- histórico: 2.3.0 21/11/2026 18:40 repositório organizado por tela (tela-3.5-gamma/, tela-5.2-nobreak/, legado/) -->
<!-- histórico: 2.2.0 15/11/2026 15:50 matriz --epsilon; pasta do Turing do PC em ~/Documentos/Projetos -->
<!-- histórico: 2.1.0 08/11/2026 13:30 duas telas: pastas por tela, MGP_TELA, matriz --tela, ZIPs por tela -->
<!-- histórico: 2.0.0 07/11/2026 22:24 revisão para a v1.8.2: quatro ZIPs, contagens, matriz 4 x 3, aplicar delta, Releases -->

# Desenvolvimento

[Voltar ao README](../README.md)

## Estrutura do repositório

```
.
├── README.md                     mapa do repositório (o que é cada pasta e o que roda em cada tela)
├── CHANGELOG.md                  histórico de versões
├── LICENSE                       GPL-3.0
├── CLAUDE.md                     regras para agentes de IA que trabalham no projeto
├── tela-3.5-gamma/               tema GAMMA: em uso na tela de 3,5" (suporte pronto para a de 5,2")
│   ├── README.md                 estilos, telas do EPSILON e instalação rápida
│   ├── VERSION                   versão atual do GAMMA (SemVer)
│   ├── instalar-gamma.sh         instalador de ponta a ponta
│   ├── construir/
│   │   ├── construir_zips.py     gera os ZIPs enxutos (5 estilos x 2 telas)
│   │   ├── matriz_previas.py     matrizes de prévias (estilos, telas do EPSILON, estudos), da 3,5" ou da 5,2"
│   │   └── aplicar-na-tela.sh    aplica um estilo na tela do PC a partir do ZIP
│   └── pacote/                   o que vai para o ZIP
│       ├── sensors/matrixgreenpro/   extensão Python: coleta, saúde, histórico e desenho
│       │   └── estilos/              estilos entregues (ALPHA, BETA, GAMMA, DELTA, EPSILON e as telas do EPSILON)
│       │       └── estudos/          estilos de estudo e legados (não entram nos ZIPs)
│       ├── scripts/              instalar, diagnosticar e restaurar
│       ├── tools/                autoteste, prévias, detector, mapeadores
│       ├── extras/               config.exemplo.yaml e MangoHud
│       └── telas/
│           ├── 3.5/MatrixGreenPro/   tema da tela de 3,5" (320x480)
│           └── 5.2/MatrixGreenPro/   tema da tela de 5,2" (720x1280)
├── tela-5.2-nobreak/             tela do nobreak Ragtech na 5,2" em paisagem (programa próprio, serviço nobreak-tela)
├── docs/                         documentação (img/ com capturas, brainstorm/ com estudos e mockups)
└── legado/                       scripts substituídos (construir-zips.sh, publicar-no-github.sh) e o espelho do GitHub antigo
```

## Ambiente de testes

Os testes importam o pacote `library` do Turing Smart Screen, então o tema precisa estar dentro de uma cópia dele.

No PC já instalado (no PC do Lucas, a pasta do Turing é `~/Documentos/Projetos/turing-smart-screen-linux` desde 14/11/2026; troque o caminho abaixo):

```bash
cd ~/turing-smart-screen-linux
.venv/bin/python3 tools/mgp_selftest.py
.venv/bin/python3 tools/mgp_preview.py /tmp/previas
```

Numa cópia de desenvolvimento do Turing:

```bash
cp -r tela-3.5-gamma/pacote/sensors/matrixgreenpro <turing>/library/sensors/
cp tela-3.5-gamma/pacote/tools/*.py <turing>/tools/
cd <turing> && .venv/bin/python3 tools/mgp_selftest.py
```

## Ferramentas

| Ferramenta | Para quê |
|---|---|
| `mgp_selftest.py` | autoteste: estados de saúde e limites, filtros de 2 s e 5 min, LOG, histórico de 24 h, total dos HDs, VeraCrypt, rede e internet, coleta parcial, histerese, discos, baias, ventoinhas, apelidos de estilos, selo de versão e o motor real |
| `mgp_preview.py` | gera PNGs nos estados Normal, Atenção, Crítico e Crítico Apagado e verifica limites, sobreposição de textos, glifos ausentes e cobertura de métricas (`REQUIRED`) |
| `mgp_mapear_fans.py` | mapeador guiado de ventoinhas (grava `fans.yaml`) |
| `mgp_baias.py` | confere a numeração das baias do TerraMaster |
| `mgp_detect.py` | detecta discos e rede e cria a configuração inicial |
| `mgp_orientation_test.py` | mostra uma seta TOPO na tela física |

Resultados de referência da v1.8.3 com as duas telas: autoteste 232 de 232 no repositório inteiro, tanto com `MGP_TELA=3.5` quanto com `MGP_TELA=5.2`; 110 de 110 nos ZIPs Alpha, Beta e Gamma e 109 de 109 no Delta, nas duas telas. Para testar a outra tela sem reinstalar, defina `MGP_TELA=5.2` (ou `3.5`) antes do autoteste ou das prévias. No repositório inteiro, o estilo experimental `pcb` acusa "métricas omitidas" (ele não é entregue).

Para testar sem mexer na instalação do PC, monte uma cópia de desenvolvimento do Turing (pastas `library`, `tools`, `main.py`, `config.yaml` e um link para `res`), copie o `matrixgreenpro` e as ferramentas para ela e defina `MGP_HISTORICO` para um arquivo temporário, para o autoteste não gravar no histórico real:

```bash
MGP_HISTORICO=/tmp/hist-teste.json ~/turing-smart-screen-linux/.venv/bin/python3 tools/mgp_selftest.py
```

⚠️ A conferência de glifos ausentes usa o `fontTools`; sem ele (como hoje no PC), ela é pulada em silêncio. Confira acentos e setas nas imagens.

## Matriz de prévias

Toda modificação é mostrada ao Lucas como uma matriz em PNG: as 4 versões (ALPHA, BETA, GAMMA, DELTA) nas colunas e os 3 estados (normal, atenção, crítico) nas linhas, desenhadas com o código atual de `tela-3.5-gamma/pacote/`. A ferramenta também confere limites, sobreposição de textos, glifos e cobertura de métricas de cada quadro e sai com código 1 se houver problema.

```bash
python3 -I tela-3.5-gamma/construir/matriz_previas.py previas/matriz.png ~/turing-smart-screen-linux
python3 -I tela-3.5-gamma/construir/matriz_previas.py previas/matriz-5.2.png ~/turing-smart-screen-linux --tela 5.2
python3 -I tela-3.5-gamma/construir/matriz_previas.py previas/matriz-epsilon.png --epsilon     # as 4 telas do GAMMA EPSILON
```

Sem a pasta do Turing no comando, a matriz procura as fontes em `~/turing-smart-screen-linux` e em `~/Documentos/Projetos/turing-smart-screen-linux`.

Opções: `--extra coluna` acrescenta a variante GAMMA GAMMA COLUNA; `--deltas` troca as colunas pelas 6 variantes de estudo do DELTA; `--delta5` mostra o DELTA e as variantes 5A e 5C; `--v2` mostra as 12 propostas da v2.0.0. O segundo argumento é uma cópia do Turing Smart Screen, usada só pelas fontes de `res/fonts`. Requer Pillow e psutil. A pasta `previas/` fica fora do Git.

## Aplicar na tela do PC

Numa sessão que roda no próprio PC, `tela-3.5-gamma/construir/aplicar-na-tela.sh delta 3.5` (ou `alpha`, `beta`, `gamma`; e `5.2` para a tela de 5,2") monta o ZIP do estilo a partir do código atual, extrai com `unzip` e roda o instalador com `--sem-apt`. O instalador guarda o tema anterior (volta com `--restaurar`) e reinicia o serviço da tela. Rodar com o usuário comum, sem sudo. Instalado assim, o selo mostra a versão; instalado direto do repositório (`./instalar-gamma.sh --estilo NOME`), mostra `dev`. ⚠️ Só com autorização explícita do Lucas, a cada envio, e antes do commit.

## Gerar os ZIPs

```bash
python3 -I tela-3.5-gamma/construir/construir_zips.py SAIDA 1.8.3:Alpha:3.5 1.8.3:Beta:3.5 1.8.3:Gamma:3.5 1.8.3:Delta:3.5 \
    1.8.3:Alpha:5.2 1.8.3:Beta:5.2 1.8.3:Gamma:5.2 1.8.3:Delta:5.2
```

Para cada estilo e tela, o construtor cria `SAIDA/Gamma-<Nome>-<tela>-v<versão>/` e o ZIP correspondente (sem a tela no pedido, vale 3.5). Cada pacote leva só a pasta do tema da sua tela, `TELA_PADRAO` e o `tela.py` já gravado. A versão é a mesma nas duas telas: criar o pacote da 5,2" não muda a versão do estilo, só o nome do pacote. Ele copia `tela-3.5-gamma/pacote/`, remove os estilos não usados, reescreve `ESTILOS` e `ALIASES`, ajusta o autoteste e a prévia ao estilo, grava `versao.py`, `VERSION`, `ESTILO_PADRAO`, `LEIA-ME.md` e `CHANGELOG.md`, copia o instalador e preserva as permissões. O Delta leva também `reator_grupos.py`, `reator_delta2.py` e `graficos.py`. Contagem com as duas telas: na 3,5", Alpha e Beta com 40 arquivos, Gamma com 41 e Delta com 43; na 5,2", os mesmos números.

Para uma nova versão, troque o número nas linhas de `V`, acrescente a entrada em `ENT` dentro de `construir_zips.py` e rode de novo. O construtor reescreve a lista de estilos do autoteste procurando o trecho que termina em `"pcb"`: estilos novos entram antes dele.

⚠️ Para testar o instalador de um ZIP, extraia com `unzip`. A extração pelo Python perde o bit de execução.

## Versionamento

[SemVer](https://semver.org/lang/pt-BR/): MAJOR.MINOR.PATCH. A versão só muda a cada commit publicado.

- **MAJOR:** mudança incompatível (remover um estilo, mudar o formato da configuração).
- **MINOR:** recurso novo compatível.
- **PATCH:** correção ou ajuste.

Os quatro estilos saem juntos, na mesma versão.

## Publicação

Os ZIPs são artefatos de lançamento: não vão para o Git (veja o `.gitignore`). Cada versão tem uma [Release no GitHub](https://github.com/lstavares84/turzx/releases) com a tag `vX.Y.Z` no commit da versão, os ZIPs gerados a partir desse commit e as notas do CHANGELOG. Publicação só com autorização do Lucas:

```bash
gh release create vX.Y.Z saida/*.zip --target COMMIT --title "GAMMA TUS-35 vX.Y.Z" --notes-file NOTAS.md
```

## Critérios de pronto

Toda mudança só está pronta quando:

1. o autoteste está verde;
2. `mgp_preview.py` mostra 0 problema de layout nos estados Normal, Atenção e Crítico;
3. as imagens de prévia foram conferidas visualmente;
4. a instalação do zero foi testada com usuário comum (não root) usando o ZIP gerado;
5. a versão subiu no nível SemVer correto e o `CHANGELOG.md` foi atualizado;
6. não há travessão longo em nenhum texto, os acentos estão corretos e toda linha de log tem data e hora (`dd/mm/aaaa HH:MM:SS`).

## Convenções

- Todo texto em português do Brasil, com acentuação correta, inclusive comentários e mensagens de log.
- Cada arquivo começa com um comentário de controle de versão: nome, versão, data e hora, autoria. Revisões acrescentam uma linha `histórico:`.
- Logs e saídas na tela com data e hora em cada linha.
- Antes de qualquer ação manual do usuário, o emoji ⚠️.
- Mexa nos espaçamentos aos poucos: linhas novas causaram sobreposição muitas vezes. Use sempre `mgp_preview.py`.
