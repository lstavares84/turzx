#!/usr/bin/env bash
# GAMMA TUS-35 | instalador automático | versão 1.0.0 | 02/11/2026 19:15 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.7.0 07/11/2026 19:42 versão delta (GAMMA DELTA)
# histórico: 1.5.0 07/11/2026 14:25 dica para conferir a numeração das baias do TerraMaster
# histórico: 1.4.0 02/11/2026 22:46 versões alpha, beta e gamma (nomes antigos continuam valendo)
# histórico: 1.3.0 02/11/2026 22:40 módulo drivetemp automático (temperatura dos HDDs)
# histórico: 1.2.0 02/11/2026 21:40 driver nct6775 automático e dica do mapeador de ventoinhas
# histórico: 1.0.0 02/11/2026 19:15 nomes GAMMA SENTINELA e GAMMA DOSÍMETRO; versão lida do arquivo VERSION
#
# Faz tudo em sequência, sem perguntas (exceto a senha do sudo, se faltar algo):
#   1. confere o sistema e instala as dependências com apt (git, python3-venv, python3-tk, usbutils...)
#   2. adiciona o usuário ao grupo dialout (acesso à porta serial da tela)
#   3. instala o turing-smart-screen-linux (clone, venv e requirements) se ainda não existir
#   4. cria e habilita o serviço systemd de usuário se ele ainda não existir
#   5. instala o tema GAMMA na versão escolhida e reinicia o serviço
#
# Uso:
#   ./instalar-gamma.sh                         usa a versão do pacote (ZIP) ou pergunta (repositório)
#   ./instalar-gamma.sh --versao alpha          GAMMA ALPHA (ex SENTINELA: escala N0/N1/N2 sem tarja, percentuais)
#   ./instalar-gamma.sh --versao beta           GAMMA BETA (ex DOSÍMETRO: percentuais entre parênteses, infos à esquerda)
#   ./instalar-gamma.sh --versao gamma          GAMMA GAMMA (7 colmeias de resumo e painel numérico por grupo)
#   ./instalar-gamma.sh --versao delta          GAMMA DELTA (GAMMA GAMMA com gráficos de 24 h)
#   ./instalar-gamma.sh --mangohud              também configura o FPS real (MangoHud)
#   ./instalar-gamma.sh --invertido | --normal  gira a imagem 180 graus (ou não)
#   ./instalar-gamma.sh --dir CAMINHO           pasta do Turing (padrão ~/turing-smart-screen-linux)
#   ./instalar-gamma.sh --estilo NOME           avançado: qualquer estilo do pacote (ex.: gamma-n3, gamma-sonar)
#   ./instalar-gamma.sh --sem-apt               não instala pacotes do sistema
#   ./instalar-gamma.sh --sem-servico           não cria o serviço systemd
#   ./instalar-gamma.sh --restaurar             volta ao tema anterior (usa o backup do instalador)
#   ./instalar-gamma.sh --ajuda
set -uo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSAO="$(head -1 "$AQUI/VERSION" 2>/dev/null | tr -d '[:space:]')"; VERSAO="${VERSAO:-1.0.0}"
if [[ -f "$AQUI/scripts/instalar.sh" ]]; then PKG="$AQUI"                    # layout do ZIP
elif [[ -f "$AQUI/pacote/scripts/instalar.sh" ]]; then PKG="$AQUI/pacote"    # layout do repositório
else echo "[$(date '+%d/%m/%Y %H:%M:%S')] ERRO: pacote do GAMMA não encontrado ao lado deste script"; exit 1; fi

DIR="${HOME}/turing-smart-screen-linux"
ESTILO=""; SEM_APT=0; SEM_SERVICO=0; RESTAURAR=0; RELOGIN=0
REPASSE=()
STATE="${HOME}/.local/state/matrixgreenpro"; mkdir -p "$STATE"
LOG="$STATE/instalar-gamma-$(date +%Y%m%d-%H%M%S).log"

log()  { printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*" | tee -a "$LOG"; }
die()  { log "ERRO: $*"; log "instalação interrompida. Log: $LOG"; exit 1; }
acao() { log "⚠️ AÇÃO MANUAL: $*"; }
etapa(){ log "---- etapa $1"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --versao) case "${2:-}" in
                alpha|sentinela|esquerda) ESTILO="gamma-alpha" ;;
                beta|dosimetro|dosímetro|compacto) ESTILO="gamma-beta" ;;
                gamma) ESTILO="gamma-gamma" ;;
                delta) ESTILO="gamma-delta" ;;
                *) die "--versao aceita: alpha, beta, gamma ou delta (sentinela, dosimetro, esquerda e compacto ainda funcionam)" ;;
              esac; shift ;;
    --estilo) ESTILO="${2:-}"; shift ;;
    --dir) DIR="${2%/}"; shift ;;
    --mangohud|--invertido|--normal|--teste-orientacao|--corrigir-servico|--sem-reiniciar|--forcar) REPASSE+=("$1") ;;
    --sem-apt) SEM_APT=1 ;;
    --sem-servico) SEM_SERVICO=1 ;;
    --restaurar) RESTAURAR=1 ;;
    -h|--ajuda|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) die "opção desconhecida: $1 (use --ajuda)" ;;
  esac
  shift
done

log "GAMMA TUS-35 v$VERSAO | instalador automático | pacote: $PKG | log: $LOG"
[[ $EUID -eq 0 ]] && die "não execute como root nem com sudo. Use o seu usuário; o script pede a senha só quando precisar"

if [[ $RESTAURAR -eq 1 ]]; then
  etapa "restaurar tema anterior"
  bash "$PKG/scripts/restaurar.sh" 2>&1 | while IFS= read -r l; do log "$l"; done
  exit "${PIPESTATUS[0]}"
fi

# ---------------------------------------------------------------- versão (estilo)
if [[ -z "$ESTILO" ]]; then
  if [[ -s "$PKG/ESTILO_PADRAO" ]]; then
    ESTILO="$(head -1 "$PKG/ESTILO_PADRAO" | tr -d '[:space:]')"
  elif [[ -t 0 ]]; then
    echo "Escolha a versão do GAMMA:"
    echo "  1) ALPHA  escala N0/N1/N2 sem tarja, com brilho no nome"
    echo "  2) BETA   percentuais entre parênteses e informações à esquerda"
    echo "  3) GAMMA  7 colmeias de resumo (CORE no centro) e painel numérico por grupo"
    echo "  4) DELTA  o GAMMA com gráficos de 24 h (temperatura, VRAM e RAM, rede)"
    read -r -p "Número (Enter = 3): " n
    case "$n" in 1) ESTILO="gamma-alpha" ;; 2) ESTILO="gamma-beta" ;; 4) ESTILO="gamma-delta" ;; *) ESTILO="gamma-gamma" ;; esac
  else
    ESTILO="gamma-gamma"
  fi
fi
log "versão escolhida: estilo $ESTILO"

# ---------------------------------------------------------------- 1. sistema e dependências
etapa "1/5 sistema e dependências"
OS_ID="$(. /etc/os-release 2>/dev/null; echo "${ID:-?}")"
OS_VER="$(. /etc/os-release 2>/dev/null; echo "${VERSION_ID:-?}")"
log "sistema: $OS_ID $OS_VER"
[[ "$OS_ID" == "debian" ]] || { REPASSE+=("--forcar"); log "AVISO: sistema não é Debian; seguindo por conta própria"; }
[[ "$OS_VER" == 13* ]] || log "AVISO: o pacote foi preparado para o Debian 13 (Trixie)"

if [[ $SEM_APT -eq 0 ]]; then
  FALTAM=()
  for p in git python3 python3-venv python3-pip python3-tk python3-pil.imagetk usbutils lm-sensors curl; do
    dpkg -s "$p" >/dev/null 2>&1 || FALTAM+=("$p")
  done
  if ((${#FALTAM[@]})); then
    log "pacotes a instalar: ${FALTAM[*]}"
    acao "se o terminal pedir a senha do sudo, digite a sua senha (é só para instalar os pacotes acima)"
    if sudo apt-get update -qq && sudo apt-get install -y "${FALTAM[@]}"; then
      log "pacotes instalados"
    else
      die "falha no apt. Rode manualmente: sudo apt-get install -y ${FALTAM[*]}"
    fi
  else
    log "dependências do sistema: todas presentes"
  fi
else
  log "pacotes do sistema: pulado por --sem-apt"
fi

# ---------------------------------------------------------------- 2. grupo dialout
etapa "2/5 acesso à porta serial (grupo dialout)"
if id -nG "$USER" | grep -qw dialout; then
  log "usuário $USER já está no grupo dialout"
else
  if sudo usermod -aG dialout "$USER"; then
    log "usuário $USER adicionado ao grupo dialout"; RELOGIN=1
  else
    acao "rode: sudo usermod -aG dialout $USER  (depois saia e entre na sessão)"
  fi
fi

# ---------------------------------------------------------------- 3. Turing Smart Screen
etapa "3/5 turing-smart-screen-linux"
if [[ ! -f "$DIR/main.py" ]]; then
  log "programa não encontrado em $DIR; baixando do projeto oficial"
  git clone --depth 1 https://github.com/mathoudebine/turing-smart-screen-python.git "$DIR" 2>&1 | while IFS= read -r l; do log "$l"; done
  [[ -f "$DIR/main.py" ]] || die "falha ao baixar o turing-smart-screen (internet ou git)"
else
  log "programa já instalado em $DIR"
fi
if [[ ! -x "$DIR/.venv/bin/python3" ]]; then
  log "criando o ambiente virtual e instalando as dependências Python (pode levar alguns minutos)"
  python3 -m venv "$DIR/.venv" || die "falha ao criar o venv"
  "$DIR/.venv/bin/python3" -m pip install --upgrade pip -q 2>&1 | while IFS= read -r l; do log "$l"; done
  "$DIR/.venv/bin/python3" -m pip install -r "$DIR/requirements.txt" 2>&1 | tail -n 5 | while IFS= read -r l; do log "$l"; done
  "$DIR/.venv/bin/python3" -c "import serial, PIL, psutil, yaml" 2>/dev/null || die "dependências Python incompletas em $DIR/.venv"
  log "ambiente Python pronto"
else
  log "ambiente Python já existe"
fi

# ---------------------------------------------------------------- 3b. driver do chip de ventoinhas
if [[ $SEM_APT -eq 0 ]]; then
  if ls /sys/class/hwmon/hwmon*/fan*_input >/dev/null 2>&1; then
    log "ventoinhas: o kernel já expõe leituras de RPM"
  elif sudo modprobe nct6775 2>/dev/null && ls /sys/class/hwmon/hwmon*/fan*_input >/dev/null 2>&1; then
    echo nct6775 | sudo tee /etc/modules-load.d/nct6775.conf >/dev/null && log "ventoinhas: driver nct6775 carregado e gravado para o boot"
  else
    log "AVISO: nenhuma leitura de ventoinha disponível (chip sem driver no kernel). A bomba e as ventoinhas aparecerão como N/D"
  fi
fi

# ---------------------------------------------------------------- 3c. temperatura dos HDDs (módulo drivetemp)
if [[ $SEM_APT -eq 0 ]]; then
  if ls /sys/class/hwmon/hwmon*/name >/dev/null 2>&1 && grep -qx drivetemp /sys/class/hwmon/hwmon*/name 2>/dev/null; then
    log "discos: o kernel já expõe a temperatura dos HDDs (drivetemp)"
  elif sudo modprobe drivetemp 2>/dev/null && grep -qx drivetemp /sys/class/hwmon/hwmon*/name 2>/dev/null; then
    echo drivetemp | sudo tee /etc/modules-load.d/drivetemp.conf >/dev/null && log "discos: módulo drivetemp carregado e gravado para o boot"
  else
    log "AVISO: temperatura dos HDDs indisponível (módulo drivetemp sem efeito). A temperatura dos discos aparecerá como N/D"
  fi
fi

# ---------------------------------------------------------------- 4. serviço systemd de usuário
etapa "4/5 serviço systemd de usuário"
UNIT="$HOME/.config/systemd/user/turing-smart-screen.service"
if [[ $SEM_SERVICO -eq 1 ]]; then
  log "serviço: pulado por --sem-servico"
elif [[ -f "$UNIT" ]]; then
  log "serviço já existe: $UNIT (não será alterado)"
else
  mkdir -p "$(dirname "$UNIT")"
  cat > "$UNIT" <<UNITEOF
[Unit]
Description=Turing Smart Screen (monitor USB)
After=default.target

[Service]
Type=simple
WorkingDirectory=$DIR
ExecStart=$DIR/.venv/bin/python3 main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
UNITEOF
  log "serviço criado: $UNIT"
  if systemctl --user daemon-reload 2>/dev/null && systemctl --user enable turing-smart-screen.service 2>&1 | while IFS= read -r l; do log "$l"; done; then
    log "serviço habilitado para iniciar com a sessão"
  else
    acao "não consegui habilitar o serviço agora. Depois de entrar na sessão: systemctl --user enable --now turing-smart-screen.service"
  fi
  loginctl enable-linger "$USER" 2>/dev/null && log "início no boot habilitado (linger)" \
    || log "AVISO: início antes do login não habilitado (opcional): sudo loginctl enable-linger $USER"
fi

# ---------------------------------------------------------------- 5. tema GAMMA
etapa "5/5 instalação do tema GAMMA ($ESTILO)"
bash "$PKG/scripts/instalar.sh" --dir "$DIR" --estilo "$ESTILO" "${REPASSE[@]}" 2>&1 | tee -a "$LOG"
RC="${PIPESTATUS[0]}"
[[ $RC -eq 0 ]] || die "o instalador do tema terminou com código $RC (veja o log acima)"

log "concluído: GAMMA v$VERSAO ($ESTILO) instalado. Log completo: $LOG"
[[ $RELOGIN -eq 1 ]] && acao "saia da sessão e entre de novo (ou reinicie) para valer o grupo dialout; depois rode: systemctl --user restart turing-smart-screen"
[[ -f "$PKG/tools/mgp_mapear_fans.py" ]] && acao "para identificar a bomba e as ventoinhas: $DIR/.venv/bin/python3 $DIR/tools/mgp_mapear_fans.py (leva 2 minutos)"
if [[ -f "$PKG/tools/mgp_baias.py" ]] && grep -qs "174c" /sys/bus/usb/devices/*/idVendor 2>/dev/null; then
  acao "se usa o gabinete TerraMaster, confira se a numeração das baias bate com a do gabinete: $DIR/.venv/bin/python3 $DIR/tools/mgp_baias.py"
fi
acao "olhe a tela de 3,5\". Se estiver de ponta-cabeça: ./instalar-gamma.sh --invertido"
log "para voltar ao tema anterior: ./instalar-gamma.sh --restaurar"
