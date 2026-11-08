<!-- docs/instalacao.md | versão 2.1.0 | 08/11/2026 13:30 (-03) | criação original (Claude, para Lucas Tavares). Fonte: instalar-gamma.sh e pacote/scripts/ da v1.8.3. -->
<!-- histórico: 2.1.0 08/11/2026 13:30 tela de 5,2": --tela, TELA_PADRAO, REVISION TUR_USB e pacotes por tela -->
<!-- histórico: 2.0.0 07/11/2026 22:24 Releases, GAMMA DELTA, apelidos, selo dev e histórico de 24 h -->

# Instalação

[Voltar ao README](../README.md)

## Requisitos

- Debian 13 (testado como alvo) ou distribuição parecida com `apt` e `systemd`.
- Uma das telas: TURZX / Turing Smart Screen de 3,5" (TUS-35, USB `1a86:5722`, revisão `A`, porta serial) ou TURZX / Turing de 5,2" (720x1280, USB `1cbe:0050`, revisão `TUR_USB`, USB direto). A de 5,2" ainda não foi testada no aparelho.
- Usuário comum com `sudo` (o instalador pede a senha só quando precisa e **se recusa a rodar como root**).
- Opcional: GPU NVIDIA (dados de GPU), MangoHud (FPS dos jogos), gabinete TerraMaster (baias).

## Instalar por ZIP (recomendado)

Baixe o ZIP do estilo na [página de Releases](https://github.com/lstavares84/turzx/releases/latest). Cada versão tem oito pacotes, quatro por tela: `Gamma-Alpha`, `Gamma-Beta`, `Gamma-Gamma` e `Gamma-Delta` (o recomendado), com `3.5` ou `5.2` no nome.

⚠️ Use `unzip`, que preserva a permissão de execução do instalador:

```bash
unzip Gamma-Delta-3.5-v1.8.3.zip && cd Gamma-Delta-3.5-v1.8.3 && ./instalar-gamma.sh
```

Para a tela de 5,2", troque `3.5` por `5.2` nos dois nomes. Cada ZIP já sabe qual é o seu estilo (arquivo `ESTILO_PADRAO`) e a sua tela (arquivo `TELA_PADRAO`) e grava a versão no selo da tela.

## Instalar pelo repositório

```bash
./instalar-gamma.sh --versao delta --tela 3.5     # ou --tela 5.2
```

Sem `--versao`, o instalador pergunta qual estilo usar; sem `--tela`, usa a 3,5". Instalado direto do repositório, o selo da tela mostra `dev` em vez da versão.

## O que o instalador faz

Tudo é registrado com data e hora em `~/.local/state/matrixgreenpro/instalar-gamma-AAAAMMDD-HHMMSS.log`.

1. Confere o sistema e instala as dependências com `apt` (git, python3-venv, python3-tk, usbutils e outras).
2. Na tela de 3,5", adiciona o usuário ao grupo `dialout`, que dá acesso à porta serial. A de 5,2" fala USB direto (biblioteca `pyusb` do Turing) e não usa porta serial.
3. Baixa o Turing Smart Screen em `~/turing-smart-screen-linux` (clone, ambiente virtual e dependências), se ainda não existir.
4. Carrega os drivers de sensores `nct6775` (ventoinhas e temperaturas da placa) e `drivetemp` (temperatura dos HDDs) e grava em `/etc/modules-load.d/` para valerem após reiniciar.
5. Cria e habilita o serviço systemd de usuário `turing-smart-screen.service`.
6. Instala o tema da tela escolhida (pasta `res/themes/MatrixGreenPro` e extensão `library/sensors/matrixgreenpro`, com a tela gravada em `tela.py`), ajusta `REVISION` no `config.yaml` do Turing (`A` ou `TUR_USB`), faz backup do estado anterior e reinicia o serviço.

## Opções

| Opção | Efeito |
|---|---|
| `--versao alpha\|beta\|gamma\|delta` | escolhe o estilo (aceita também `sentinela`, `dosimetro`, `esquerda`, `compacto`) |
| `--tela 3.5\|5.2` | escolhe a tela (padrão: a do pacote; no repositório, 3.5) |
| `--invertido` / `--normal` | gira a imagem 180 graus, ou desfaz |
| `--mangohud` | configura o MangoHud para o FPS real dos jogos |
| `--sem-apt` | não instala pacotes do sistema |
| `--sem-servico` | não cria o serviço systemd |
| `--restaurar` | volta ao tema anterior usando o backup do instalador |
| `--dir CAMINHO` | pasta do Turing (padrão `~/turing-smart-screen-linux`) |
| `--estilo NOME` | avançado: qualquer estilo ou apelido registrado no pacote, inclusive os de estudo (só no repositório) |
| `--ajuda` | mostra a ajuda |

## Depois de instalar

⚠️ Se o instalador disser que você entrou no grupo `dialout`, saia da sessão e entre de novo (ou reinicie), depois rode:

```bash
systemctl --user restart turing-smart-screen
```

⚠️ Para o FPS aparecer nos jogos da Steam, use a opção de inicialização `mangohud %command%`.

⚠️ Confira a orientação da tela. Se a imagem estiver de ponta-cabeça, rode `./instalar-gamma.sh --invertido`. Para ver uma seta de teste na tela física, use `pacote/scripts/instalar.sh --teste-orientacao`.

⚠️ Confira o mapa das ventoinhas e a numeração das baias com as ferramentas descritas em [configuração](configuracao.md).

### Tela de 5,2" (ainda não testada no aparelho)

O suporte vem do próprio Turing Smart Screen ([PR 892](https://github.com/mathoudebine/turing-smart-screen-python/pull/892), incorporado em 12/04/2026): instalações dele a partir dessa data já trazem o driver `lcd_comm_turing_usb.py`. Antes de instalar, ⚠️ confira se a tela é o modelo suportado (comando somente leitura; deve aparecer `1cbe:0050`):

```bash
lsusb | grep -i 1cbe
```

O instalador avisa se faltar o módulo `pyusb` no ambiente do Turing. Se o serviço não conseguir abrir a tela, o motivo provável é permissão de acesso ao dispositivo USB; nesse caso, mande o log (`journalctl --user -u turing-smart-screen -n 50`) antes de mudar qualquer coisa no sistema.

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
| `~/.local/state/matrixgreenpro/` | logs com data e hora e o histórico de 24 h dos gráficos (`historico.json`) |
| `~/.local/share/matrixgreenpro/backups/` | backups do instalador |
| `~/.config/systemd/user/turing-smart-screen.service` | serviço de usuário |
