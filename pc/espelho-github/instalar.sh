#!/usr/bin/env bash
# GAMMA | pc/espelho-github/instalar.sh | versão 1.0.0 | 07/11/2026 15:40 (-03) | criação original (Claude, para Lucas Tavares)
# Instala o espelho do GitHub para o usuário atual (sem sudo, exceto para criar a pasta no HDD se faltar permissão).
set -euo pipefail
export TZ=America/Sao_Paulo
log(){ printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*"; }
[[ $EUID -eq 0 ]] && { log "ERRO: rode com o seu usuário, sem sudo"; exit 1; }
AQUI="$(cd "$(dirname "$0")" && pwd)"
command -v gh >/dev/null || { log "ERRO: instale o gh (sudo apt install gh) e rode gh auth login"; exit 1; }
gh auth status >/dev/null 2>&1 || { log "ERRO: gh sem login. Rode gh auth login e depois gh auth setup-git"; exit 1; }
gh auth setup-git >/dev/null 2>&1 && log "git passa a usar o login do gh para push e pull"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}/espelho-github.conf"
[[ -f "$CONF" ]] || { install -D -m 644 "$AQUI/espelho-github.conf" "$CONF"; log "configuração criada: $CONF"; }
. "$CONF"
if ! mkdir -p "$ESPELHO_BASE" 2>/dev/null; then
  log "a pasta $ESPELHO_BASE precisa de sudo uma única vez (dono: $USER)"
  sudo install -d -o "$USER" -g "$(id -gn)" "$ESPELHO_BASE"
fi
install -D -m 755 "$AQUI/sincronizar-github.sh" "$HOME/.local/bin/sincronizar-github.sh"
install -D -m 644 "$AQUI/espelho-github.service" "$HOME/.config/systemd/user/espelho-github.service"
install -D -m 644 "$AQUI/espelho-github.timer" "$HOME/.config/systemd/user/espelho-github.timer"
systemctl --user daemon-reload
systemctl --user enable --now espelho-github.timer
log "timer ativo; primeira sincronização agora (pode demorar na primeira vez)"
systemctl --user start espelho-github.service || true
log "log: ${XDG_STATE_HOME:-$HOME/.local/state}/espelho-github/sincronizar.log"
