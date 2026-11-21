#!/usr/bin/env bash
# GAMMA NOBREAK | nobreak/instalar.sh | versão 1.0.0 | 21/11/2026 10:20 (-03) | criação original (Claude, para Lucas Tavares)
# Instala a tela do nobreak como serviço systemd de usuário (nobreak-tela.service): lê o nobreak a cada 1 s,
# grava o log em ~/.local/state/nobreak e mostra na tela de 5,2" em paisagem. Rodar com o usuário comum.
#   ./instalar.sh            instala, habilita e inicia
#   ./instalar.sh --parar    para e desabilita o serviço
set -uo pipefail
export TZ=America/Sao_Paulo
log(){ printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*"; }
AQUI="$(cd "$(dirname "$0")" && pwd)"
TURING="$(sed -n 's/^WorkingDirectory=//p' "$HOME/.config/systemd/user/turing-smart-screen.service" 2>/dev/null | head -1)"
[[ -f "$TURING/main.py" ]] || TURING="$HOME/Documentos/Projetos/turing-smart-screen-linux"
PY="$TURING/.venv/bin/python3"
UNIT="$HOME/.config/systemd/user/nobreak-tela.service"
[[ $EUID -eq 0 ]] && { log "ERRO: não rode como root"; exit 1; }
if [[ "${1:-}" == "--parar" ]]; then
  systemctl --user disable --now nobreak-tela.service && log "serviço parado e desabilitado"; exit 0
fi
[[ -x "$PY" ]] || { log "ERRO: ambiente do Turing não encontrado em $TURING"; exit 1; }
"$PY" -c "import usb.core, PIL" || { log "ERRO: pyusb ou Pillow ausente em $PY"; exit 1; }
lsusb | grep -qi 1cbe:0050 && log "tela de 5,2\" conectada (1cbe:0050)" || log "AVISO: tela de 5,2\" (1cbe:0050) não aparece no lsusb"
ls /dev/serial/by-id/ 2>/dev/null | grep -qi ragtech && log "nobreak Ragtech conectado" || log "AVISO: nobreak Ragtech não aparece em /dev/serial/by-id"
if ! grep -qs '1cbe.*0050' /etc/udev/rules.d/*.rules; then
  log "⚠️ AÇÃO MANUAL: libere a tela de 5,2\" para o grupo plugdev (uma vez só) e rode este script de novo:"
  log "  sudo cp $AQUI/99-turzx-52.rules /etc/udev/rules.d/ && sudo udevadm control --reload && sudo udevadm trigger"
  exit 1
fi
mkdir -p "$(dirname "$UNIT")" "$HOME/.local/state/nobreak"
cat > "$UNIT" <<UNITEOF
[Unit]
Description=Tela do nobreak Ragtech na TURZX de 5,2" (paisagem) e log
After=default.target

[Service]
Type=simple
Environment=TZ=America/Sao_Paulo
ExecStart=$PY $AQUI/nobreak_tela.py --turing $TURING --intervalo 1
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
UNITEOF
log "serviço gravado: $UNIT"
systemctl --user daemon-reload
systemctl --user enable --now nobreak-tela.service && log "serviço habilitado e iniciado"
sleep 8
systemctl --user is-active nobreak-tela.service && log "serviço ativo" || log "ERRO: serviço inativo: journalctl --user -u nobreak-tela -n 30"
journalctl --user -u nobreak-tela -n 5 --no-pager | tail -5
