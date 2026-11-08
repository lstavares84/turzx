<!-- README do pacote | GAMMA TUS-35 | versão 2.0.0 | 07/11/2026 22:24 (-03) | criação original (Claude, para Lucas Tavares) -->
<!-- histórico: 2.0.0 07/11/2026 22:24 reescrito para a v1.8.2 (antes descrevia as versões 1.3.0 e anteriores; o histórico completo está no CHANGELOG) -->

# GAMMA TUS-35: conteúdo do pacote

Tema de monitoramento para a tela TURZX / Turing TUS-35 de 3,5" (320x480, retrato, USB `1a86:5722`), instalado como extensão do [turing-smart-screen-python](https://github.com/mathoudebine/turing-smart-screen-python). Cada ZIP traz um estilo (ALPHA, BETA, GAMMA ou DELTA), o instalador e as ferramentas. O design, o código e os scripts são criação original (Claude, para Lucas Tavares), sob a licença GPL-3.0-or-later.

Documentação completa, com imagens: <https://github.com/lstavares84/turzx>.

## Instalar

⚠️ Como usuário comum (nunca com `sudo`), na pasta extraída com `unzip`:

```bash
./instalar-gamma.sh
```

Opções úteis: `--invertido` (imagem de ponta-cabeça), `--restaurar` (volta ao tema anterior), `--sem-apt` (não instala pacotes do sistema), `--ajuda`.

## Conteúdo

```
Gamma-<Estilo>-vX.Y.Z/
├── instalar-gamma.sh            instalador de ponta a ponta
├── VERSION, ESTILO_PADRAO       versão do pacote e estilo que ele instala
├── LEIA-ME.md, CHANGELOG.md     resumo e histórico de versões
├── README-pacote.md             este arquivo
├── MatrixGreenPro/              pasta do tema (vai para res/themes/MatrixGreenPro)
├── sensors/
│   ├── sensors_custom_hook.txt  bloco acrescentado ao sensors_custom.py do Turing
│   └── matrixgreenpro/          extensão: coletores, modelo de visão, alertas, histórico e o estilo
├── scripts/                     instalar.sh, restaurar.sh, diagnosticar.sh
├── tools/                       autoteste, prévias, mapeador de ventoinhas, baias, detecção e orientação
└── extras/                      config.exemplo.yaml e MangoHud-mgp.conf
```

## Ferramentas

Rodar a partir de `~/turing-smart-screen-linux`, com `.venv/bin/python3 tools/NOME`:

| Ferramenta | Para quê |
|---|---|
| `mgp_selftest.py` | autoteste do pacote (limites, alertas, discos, baias, rede, estilo e motor real) |
| `mgp_preview.py PASTA` | prévias em PNG nos estados normal, atenção e crítico, com conferência de layout |
| `mgp_mapear_fans.py` | mapeador guiado das ventoinhas (grava `~/.config/matrixgreenpro/fans.yaml`) |
| `mgp_baias.py` | confere a numeração das baias do TerraMaster |
| `mgp_detect.py` | detecta discos e rede e cria a configuração inicial |
| `mgp_orientation_test.py` | mostra uma seta TOPO na tela física |

Diagnóstico somente leitura: `scripts/diagnosticar.sh` (ou `--resumo`).

## Configuração

`~/.config/matrixgreenpro/config.yaml` (o instalador nunca sobrescreve). Modelo comentado em `extras/config.exemplo.yaml`. Os limites de alerta vêm dos manuais, do próprio hardware e do Zabbix; a tabela com as fontes está em `docs/configuracao.md`, no repositório.

## Arquivos no sistema

| Caminho | Conteúdo |
|---|---|
| `~/turing-smart-screen-linux/` | programa da tela, com `.venv` |
| `~/.config/matrixgreenpro/` | `config.yaml` e `fans.yaml` |
| `~/.local/state/matrixgreenpro/` | logs com data e hora e o histórico de 24 h (`historico.json`) |
| `~/.local/share/matrixgreenpro/backups/` | backups do instalador |
| `~/.config/systemd/user/turing-smart-screen.service` | serviço de usuário |

## Créditos

- Base: turing-smart-screen-python, de Matthieu Houdebine e colaboradores (GPL-3.0).
- Fontes JetBrains Mono e Roboto (SIL OFL), usadas a partir do próprio Turing Smart Screen, sem redistribuição.
- Clima: Open-Meteo. FPS: MangoHud.
