<!-- docs/desenvolvimento.md | versão 2.0.0 | 07/11/2026 22:28 (-03) | criação original (Claude, para Lucas Tavares). Fonte: tools/, construir/ e regras do projeto na v1.8.2. -->
<!-- histórico: 2.0.0 07/11/2026 22:28 revisão para a v1.8.2: quatro ZIPs, contagens, matriz 4 x 3, aplicar delta, Releases -->

# Desenvolvimento

[Voltar ao README](../README.md)

## Estrutura do repositório

```
.
├── README.md                 página de entrada
├── CHANGELOG.md              histórico de versões
├── VERSION                   versão atual (SemVer)
├── LICENSE                   GPL-3.0
├── CLAUDE.md                 regras para agentes de IA que trabalham no projeto
├── instalar-gamma.sh         instalador de ponta a ponta
├── construir/
│   ├── construir_zips.py     gera os quatro ZIPs enxutos
│   ├── matriz_previas.py     matriz de prévias (4 estilos x 3 estados)
│   └── aplicar-na-tela.sh    aplica um estilo na tela do PC a partir do ZIP
├── construir-zips.sh         OBSOLETO (modelo antigo, veja o roteiro)
├── publicar-no-github.sh     OBSOLETO para a estrutura atual (veja o roteiro)
├── pacote/                   tema, extensão Python, scripts e ferramentas
├── pc/espelho-github/        utilitário do PC: espelho local dos repositórios (não entra nos ZIPs)
└── docs/                     documentação (img/ com capturas, brainstorm/ com estudos)
```

## Ambiente de testes

Os testes importam o pacote `library` do Turing Smart Screen, então o tema precisa estar dentro de uma cópia dele.

No PC já instalado:

```bash
cd ~/turing-smart-screen-linux
.venv/bin/python3 tools/mgp_selftest.py
.venv/bin/python3 tools/mgp_preview.py /tmp/previas
```

Numa cópia de desenvolvimento do Turing:

```bash
cp -r pacote/sensors/matrixgreenpro <turing>/library/sensors/
cp pacote/tools/*.py <turing>/tools/
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

Resultados de referência da v1.8.2: autoteste 229 de 229 no repositório inteiro; 110 de 110 nos ZIPs Alpha, Beta e Gamma e 109 de 109 no Delta. No repositório inteiro, o estilo experimental `pcb` acusa "métricas omitidas" (ele não é entregue).

Para testar sem mexer na instalação do PC, monte uma cópia de desenvolvimento do Turing (pastas `library`, `tools`, `main.py`, `config.yaml` e um link para `res`), copie o `matrixgreenpro` e as ferramentas para ela e defina `MGP_HISTORICO` para um arquivo temporário, para o autoteste não gravar no histórico real:

```bash
MGP_HISTORICO=/tmp/hist-teste.json ~/turing-smart-screen-linux/.venv/bin/python3 tools/mgp_selftest.py
```

⚠️ A conferência de glifos ausentes usa o `fontTools`; sem ele (como hoje no PC), ela é pulada em silêncio. Confira acentos e setas nas imagens.

## Matriz de prévias

Toda modificação é mostrada ao Lucas como uma matriz em PNG: as 4 versões (ALPHA, BETA, GAMMA, DELTA) nas colunas e os 3 estados (normal, atenção, crítico) nas linhas, desenhadas com o código atual de `pacote/`. A ferramenta também confere limites, sobreposição de textos, glifos e cobertura de métricas de cada quadro e sai com código 1 se houver problema.

```bash
python3 -I construir/matriz_previas.py previas/matriz.png ~/turing-smart-screen-linux
```

Opções: `--extra coluna` acrescenta a variante GAMMA GAMMA COLUNA; `--deltas` troca as colunas pelas 6 variantes de estudo do DELTA; `--delta5` mostra o DELTA e as variantes 5A e 5C; `--v2` mostra as 12 propostas da v2.0.0. O segundo argumento é uma cópia do Turing Smart Screen, usada só pelas fontes de `res/fonts`. Requer Pillow e psutil. A pasta `previas/` fica fora do Git.

## Aplicar na tela do PC

Numa sessão que roda no próprio PC, `construir/aplicar-na-tela.sh delta` (ou `alpha`, `beta`, `gamma`) monta o ZIP do estilo a partir do código atual, extrai com `unzip` e roda o instalador com `--sem-apt`. O instalador guarda o tema anterior (volta com `--restaurar`) e reinicia o serviço da tela. Rodar com o usuário comum, sem sudo. Instalado assim, o selo mostra a versão; instalado direto do repositório (`./instalar-gamma.sh --estilo NOME`), mostra `dev`. ⚠️ Só com autorização explícita do Lucas, a cada envio, e antes do commit.

## Gerar os ZIPs

```bash
python3 -I construir/construir_zips.py SAIDA 1.8.2:Alpha 1.8.2:Beta 1.8.2:Gamma 1.8.2:Delta
```

Para cada estilo, o construtor cria `SAIDA/Gamma-<Nome>-v<versão>/` e o ZIP correspondente. Ele copia `pacote/`, remove os estilos não usados, reescreve `ESTILOS` e `ALIASES`, ajusta o autoteste e a prévia ao estilo, grava `versao.py`, `VERSION`, `ESTILO_PADRAO`, `LEIA-ME.md` e `CHANGELOG.md`, copia o instalador e preserva as permissões. O Delta leva também `reator_grupos.py`, `reator_delta2.py` e `graficos.py`. Contagem na v1.8.2: Alpha e Beta com 38 arquivos, Gamma com 39 e Delta com 41.

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
