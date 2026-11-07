<!-- docs/desenvolvimento.md | versão 1.1.0 | 07/11/2026 18:45 (-03) | criação original (Claude, para Lucas Tavares). Fonte: tools/, construir/construir_zips.py e regras do projeto na v1.6.0. -->

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
│   └── construir_zips.py     gera os três ZIPs enxutos
├── construir-zips.sh         OBSOLETO (modelo antigo, veja o roteiro)
├── publicar-no-github.sh     OBSOLETO para a estrutura atual (veja o roteiro)
├── pacote/                   tema, extensão Python, scripts e ferramentas
└── docs/                     documentação
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
| `mgp_selftest.py` | autoteste: estados de saúde, rede e internet, coleta parcial, histerese, discos, baias, ventoinhas, apelidos de estilos, selo de versão e o motor real |
| `mgp_preview.py` | gera PNGs nos estados Normal, Atenção, Crítico e Crítico Apagado e verifica limites, sobreposição de textos, glifos ausentes e cobertura de métricas (`REQUIRED`) |
| `mgp_mapear_fans.py` | mapeador guiado de ventoinhas (grava `fans.yaml`) |
| `mgp_baias.py` | confere a numeração das baias do TerraMaster |
| `mgp_detect.py` | detecta discos e rede e cria a configuração inicial |
| `mgp_orientation_test.py` | mostra uma seta TOPO na tela física |

Resultados de referência da v1.6.0: autoteste 135 de 135 no repositório inteiro e 82 de 82 em cada ZIP. No repositório inteiro, o estilo experimental `pcb` acusa "métricas omitidas" (ele não é entregue).

## Matriz de prévias

Toda modificação é mostrada ao Lucas como uma matriz em PNG: as 3 versões (ALPHA, BETA, GAMMA) nas colunas e os 3 estados (normal, atenção, crítico) nas linhas, desenhadas com o código atual de `pacote/`. A ferramenta também confere limites, sobreposição de textos, glifos e cobertura de métricas de cada quadro e sai com código 1 se houver problema.

```bash
python3 -I construir/matriz_previas.py previas/matriz.png ~/turing-smart-screen-linux
```

Com `--extra delta` (GAMMA DELTA, com gráficos de demonstração) ou `--extra coluna` (GAMMA GAMMA COLUNA), o estilo entra como coluna a mais. O segundo argumento é uma cópia do Turing Smart Screen, usada só pelas fontes de `res/fonts`. Requer Pillow e psutil. A pasta `previas/` fica fora do Git.

## Aplicar na tela do PC

Numa sessão que roda no próprio PC, `construir/aplicar-na-tela.sh gamma` monta o ZIP do estilo a partir do código atual, extrai com `unzip` e roda o instalador com `--sem-apt`. O instalador guarda o tema anterior (volta com `--restaurar`) e reinicia o serviço da tela. Rodar com o usuário comum, sem sudo. ⚠️ Só com autorização explícita do Lucas, a cada envio.

## Gerar os ZIPs

```bash
python3 -I construir/construir_zips.py SAIDA 1.6.0:Alpha 1.6.0:Beta 1.6.0:Gamma
```

Para cada estilo, o construtor cria `SAIDA/Gamma-<Nome>-v<versão>/` e o ZIP correspondente. Ele copia `pacote/`, remove os estilos não usados, reescreve `ESTILOS` e `ALIASES`, ajusta o autoteste e a prévia ao estilo, grava `versao.py`, `VERSION`, `ESTILO_PADRAO`, `LEIA-ME.md` e `CHANGELOG.md`, copia o instalador e preserva as permissões. Contagem atual: Alpha e Beta com 35 arquivos, Gamma com 36.

Para uma nova versão, adicione a linha em `V` e a entrada em `ENT` dentro de `construir_zips.py` e rode de novo.

⚠️ Para testar o instalador de um ZIP, extraia com `unzip`. A extração pelo Python perde o bit de execução.

## Versionamento

[SemVer](https://semver.org/lang/pt-BR/): MAJOR.MINOR.PATCH. A versão só muda a cada commit publicado.

- **MAJOR:** mudança incompatível (remover um estilo, mudar o formato da configuração).
- **MINOR:** recurso novo compatível.
- **PATCH:** correção ou ajuste.

Os três estilos saem juntos, na mesma versão.

## Publicação

Os ZIPs são artefatos de lançamento: não vão para o Git (veja o `.gitignore`). A proposta é anexá-los a uma Release do GitHub com a tag `vX.Y.Z`. ⚠️ A publicação é feita pelo Lucas, com o login dele.

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
