<!-- docs/instalacao.md | versão 1.0.0 | 07/11/2026 15:15 (-03) | criação original (Claude, para Lucas Tavares). Fonte: instalar-gamma.sh e pacote/scripts/ da v1.6.0. -->

# Instalação

[Voltar ao README](../README.md)

## Requisitos

- Debian 13 (testado como alvo) ou distribuição parecida com `apt` e `systemd`.
- Tela TURZX / Turing Smart Screen de 3,5" (TUS-35, USB `1a86:5722`).
- Usuário comum com `sudo` (o instalador pede a senha só quando precisa e **se recusa a rodar como root**).
- Opcional: GPU NVIDIA (dados de GPU), MangoHud (FPS dos jogos), gabinete TerraMaster (baias).

## Instalar por ZIP (recomendado)

⚠️ Use `unzip`, que preserva a permissão de execução do instalador:

```bash
unzip Gamma-Gamma-v1.6.0.zip && cd Gamma-Gamma-v1.6.0 && ./instalar-gamma.sh
```

Troque `Gamma` por `Alpha` ou `Beta` para os outros estilos. Cada ZIP já sabe qual é o seu estilo (arquivo `ESTILO_PADRAO`).

## Instalar pelo repositório

```bash
./instalar-gamma.sh --versao gamma
```

Sem `--versao`, o instalador pergunta qual estilo usar.

## O que o instalador faz

Tudo é registrado com data e hora em `~/.local/state/matrixgreenpro/instalar-gamma-AAAAMMDD-HHMMSS.log`.

1. Confere o sistema e instala as dependências com `apt` (git, python3-venv, python3-tk, usbutils e outras).
2. Adiciona o usuário ao grupo `dialout`, que dá acesso à porta serial da tela.
3. Baixa o Turing Smart Screen em `~/turing-smart-screen-linux` (clone, ambiente virtual e dependências), se ainda não existir.
4. Carrega os drivers de sensores `nct6775` (ventoinhas e temperaturas da placa) e `drivetemp` (temperatura dos HDDs) e grava em `/etc/modules-load.d/` para valerem após reiniciar.
5. Cria e habilita o serviço systemd de usuário `turing-smart-screen.service`.
6. Instala o tema (pasta `res/themes/MatrixGreenPro` e extensão `library/sensors/matrixgreenpro`), faz backup do estado anterior e reinicia o serviço.

## Opções

| Opção | Efeito |
|---|---|
| `--versao alpha\|beta\|gamma` | escolhe o estilo (aceita também `sentinela`, `dosimetro`, `esquerda`, `compacto`) |
| `--invertido` / `--normal` | gira a imagem 180 graus, ou desfaz |
| `--mangohud` | configura o MangoHud para o FPS real dos jogos |
| `--sem-apt` | não instala pacotes do sistema |
| `--sem-servico` | não cria o serviço systemd |
| `--restaurar` | volta ao tema anterior usando o backup do instalador |
| `--dir CAMINHO` | pasta do Turing (padrão `~/turing-smart-screen-linux`) |
| `--estilo NOME` | avançado: qualquer estilo do pacote, inclusive os experimentais |
| `--ajuda` | mostra a ajuda |

## Depois de instalar

⚠️ Se o instalador disser que você entrou no grupo `dialout`, saia da sessão e entre de novo (ou reinicie), depois rode:

```bash
systemctl --user restart turing-smart-screen
```

⚠️ Para o FPS aparecer nos jogos da Steam, use a opção de inicialização `mangohud %command%`.

⚠️ Confira a orientação da tela. Se a imagem estiver de ponta-cabeça, rode `./instalar-gamma.sh --invertido`. Para ver uma seta de teste na tela física, use `pacote/scripts/instalar.sh --teste-orientacao`.

⚠️ Confira o mapa das ventoinhas e a numeração das baias com as ferramentas descritas em [configuração](configuracao.md).

## Diagnóstico

Somente leitura, mostra USB, porta serial, grupo `dialout`, serviços, tema ativo, leitura real de cada sensor, saúde e erros recentes:

```bash
pacote/scripts/diagnosticar.sh            # completo, salvo em ~/.local/state/matrixgreenpro/
pacote/scripts/diagnosticar.sh --resumo   # essencial
```

No ZIP, os scripts ficam em `scripts/` (sem o prefixo `pacote/`).

## Restauração e remoção

```bash
pacote/scripts/restaurar.sh                          # volta ao tema anterior
pacote/scripts/restaurar.sh --listar                 # lista os backups
pacote/scripts/restaurar.sh --backup 20261101-001500 # restaura um backup específico
pacote/scripts/restaurar.sh --remover-tudo           # desinstala tema e extensão (pede confirmação)
```

Cada execução do instalador gera um backup em `~/.local/share/matrixgreenpro/backups/`. A configuração em `~/.config/matrixgreenpro/` e os backups nunca são apagados.

## Arquivos no seu sistema

| Caminho | Conteúdo |
|---|---|
| `~/turing-smart-screen-linux/` | programa da tela, com `.venv` |
| `~/.config/matrixgreenpro/config.yaml` | configuração do painel (o instalador nunca sobrescreve) |
| `~/.config/matrixgreenpro/fans.yaml` | mapa das ventoinhas, gerado pelo mapeador |
| `~/.local/state/matrixgreenpro/` | logs com data e hora |
| `~/.local/share/matrixgreenpro/backups/` | backups do instalador |
| `~/.config/systemd/user/turing-smart-screen.service` | serviço de usuário |
