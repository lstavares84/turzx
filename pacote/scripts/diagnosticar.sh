#!/usr/bin/env bash
# MATRIX GREEN PRO | versão 3.1.0 | 01/11/2026 11:15 (-03) | mostra o estilo ativo
# histórico: 2.1.0 01/11/2026 00:15 diagnóstico (somente leitura)
# histórico: 2.0.0 01/11/2026 00:00 mgp-diagnostico.sh
#
# Verifica USB, porta serial efetiva, permissões, serviços, erros recentes, sensores,
# discos, estado da coleta e tema ativo. Não altera nada.
# Uso:
#   ./scripts/diagnosticar.sh                 relatório completo (salvo em ~/.local/state/matrixgreenpro/)
#   ./scripts/diagnosticar.sh --resumo        só o essencial (usado no fim do instalador)
#   ./scripts/diagnosticar.sh --dir CAMINHO   pasta do programa
set -uo pipefail
DIR="${HOME}/turing-smart-screen-linux"; RESUMO=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="${2%/}"; shift ;;
    --resumo) RESUMO=1 ;;
    *) echo "opção desconhecida: $1"; exit 1 ;;
  esac; shift
done
OUT="${HOME}/.local/state/matrixgreenpro/diagnostico-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p "$(dirname "$OUT")"
log() { printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*" | tee -a "$OUT"; }
run() { log "\$ $*"; ( "$@" 2>&1 || true ) | while IFS= read -r l; do log "  $l"; done; }
sec() { log "== $*"; }
PY="$DIR/.venv/bin/python3"
OKC=0; BADC=0
ok()  { log "  [OK]    $*"; OKC=$((OKC + 1)); }
bad() { log "  [FALHA] $*"; BADC=$((BADC + 1)); }

sec "MATRIX GREEN PRO | diagnóstico | $DIR"

sec "Tela USB e porta serial"
lsusb 2>/dev/null | grep -qi '1a86:5722' && ok "USB 1a86:5722 conectado" || bad "USB 1a86:5722 não encontrado"
BYID="$(ls /dev/serial/by-id/ 2>/dev/null | grep -i 'USB35INCHIPSV2\|UsbMonitor' | head -1 || true)"
REAL=""; [[ -n "$BYID" ]] && REAL="$(readlink -f "/dev/serial/by-id/$BYID")"
[[ -n "$REAL" ]] && ok "porta efetiva: $REAL (via /dev/serial/by-id/$BYID)" || bad "nenhuma porta by-id do TUS-35"
CFGPORT="$(grep -E '^  COM_PORT:' "$DIR/config.yaml" 2>/dev/null | sed 's/.*: *//; s/"//g')"
log "  COM_PORT no config.yaml: ${CFGPORT:-?} (o start-at-boot.sh do projeto atualiza este valor a cada início)"
[[ -n "$REAL" && "$CFGPORT" != "AUTO" && "$CFGPORT" != "$REAL" ]] && log "  aviso: COM_PORT difere da porta atual; será corrigido no próximo início do serviço"

sec "Permissões"
id -nG "$USER" | grep -qw dialout && ok "usuário $USER no grupo dialout" || bad "usuário $USER fora do grupo dialout"
[[ -n "$REAL" ]] && { [[ -r "$REAL" && -w "$REAL" ]] && ok "leitura/escrita em $REAL" || bad "sem acesso a $REAL"; }

sec "Serviços"
for s in turing-smart-screen.service turing-fps.service; do
  st="$(systemctl --user is-active "$s" 2>/dev/null)"; en="$(systemctl --user is-enabled "$s" 2>/dev/null)"
  [[ "$st" == "active" ]] && ok "$s: ativo, $en" || bad "$s: ${st:-desconhecido}, ${en:-?}"
done
N="$(pgrep -fc '(^|/)python3 main\.py$' 2>/dev/null)"; N="${N:-0}"
[[ "$N" -le 1 ]] && ok "instâncias do programa: $N" || bad "instâncias do programa: $N (mais de uma disputa a porta USB)"

sec "Tema ativo"
THEME="$(grep -E '^  THEME:' "$DIR/config.yaml" 2>/dev/null | sed 's/.*: *//')"
[[ "$THEME" == "MatrixGreenPro" ]] && ok "THEME: MatrixGreenPro" || log "  THEME: $THEME"
[[ -f "$DIR/res/themes/MatrixGreenPro/theme.yaml" ]] && ok "pasta res/themes/MatrixGreenPro presente" || bad "pasta do tema ausente"
grep -q "MATRIXGREENPRO >>>" "$DIR/library/sensors/sensors_custom.py" 2>/dev/null && ok "sensor registrado em sensors_custom.py" || bad "sensor não registrado"
log "  ESTILO=$(grep -E '^  estilo:' "${HOME}/.config/matrixgreenpro/config.yaml" 2>/dev/null | awk '{print $2}' || true) (matrix | pcb | gamma | gamma-NOME)"
log "  REVISION=$(grep -E '^  REVISION:' "$DIR/config.yaml" | awk '{print $2}') DISPLAY_REVERSE=$(grep -E '^  DISPLAY_REVERSE:' "$DIR/config.yaml" | awk '{print $2}') BRIGHTNESS=$(grep -E '^  BRIGHTNESS:' "$DIR/config.yaml" | awk '{print $2}')"

sec "Sensores, discos e estado da coleta (leitura real, mesmas rotinas do painel)"
if [[ -x "$PY" && -d "$DIR/library/sensors/matrixgreenpro" ]]; then
  (cd "$DIR" && timeout 40 "$PY" - 2>/dev/null <<'PYEOF') | while IFS= read -r l; do log "  $l"; done
import time
from library.sensors.matrixgreenpro import panel
e = panel.Engine()
time.sleep(6)                      # dá tempo às threads de GPU, discos e ping
s = e.snapshot(); vm = e.vm.build(s)
c, g = s["cpu"], s["gpu"]
print(f"CPU: {e.cpu.model} | temp={c.get('temp')} °C | fan={c.get('fan')} RPM | limites {e.cpu.thresholds()}")
print(f"GPU: backend={e.gpu.backend} | temp={g.get('temp')} | fan={g.get('fan_pct')}% / {g.get('fan_rpm')} RPM | W={g.get('power')}")
print(f"FPS (MangoHud): {s['fps']}")
for d in s["disks"]:
    print(f"DISCO {d.get('nome')}: {d.get('state')} " + (f"{d['pct']:.1f}% usado" if d.get('pct') is not None else ""))
n = s["net"]
print(f"REDE: eth={n['eth'].get('name')} up={n['eth'].get('up')} | wifi={n['wifi'].get('name')} up={n['wifi'].get('up')} | rota padrão={n.get('default')}")
print(f"PING: {s['ping']} | CLIMA: {s['weather'].get('state')} | ENERGIA: {s['power']}")
print(f"SAÚDE: {vm['hdr_status'][0]} | detalhes: {vm['health']}")
print(f"COLETA: {vm['coleta'][0]} | fontes esperadas: {s['coleta']['esperados']} | falhas: {s['coleta']['falhas'] or 'nenhuma'}")
PYEOF
else
  bad "extensão do painel não instalada"
fi

if [[ $RESUMO -eq 0 ]]; then
  sec "Detalhes de hardware"
  run grep -E '^(PRETTY_NAME|VERSION_ID)=' /etc/os-release
  run sh -c "command -v sensors >/dev/null && sensors || echo 'lm-sensors não instalado'"
  run nvidia-smi --query-gpu=name,driver_version,utilization.gpu,temperature.gpu,clocks.gr,memory.used,memory.total,fan.speed,power.draw,power.limit --format=csv
  run lsblk -o NAME,SIZE,TYPE,FSTYPE,UUID,LABEL,MOUNTPOINTS,MODEL
  run ip -br addr
  run ip route show default
  run sh -c "command -v mangohud; grep -A4 MATRIXGREENPRO ~/.config/MangoHud/MangoHud.conf 2>/dev/null; ls -lt /tmp/mgp-mangohud 2>/dev/null | head -4"
  run cat "${HOME}/.config/matrixgreenpro/config.yaml"
fi

sec "Erros recentes"
if [[ -f /tmp/turing-screen.log ]]; then
  E="$(grep -cE '\[ERROR\]|Traceback' /tmp/turing-screen.log)"
  [[ "$E" -eq 0 ]] && ok "nenhum erro em /tmp/turing-screen.log" || bad "$E linha(s) de erro em /tmp/turing-screen.log"
  grep -E '\[ERROR\]|Traceback|MatrixGreenPro' /tmp/turing-screen.log | tail -n 8 | while IFS= read -r l; do log "  $l"; done
else
  log "  /tmp/turing-screen.log ainda não existe"
fi
run sh -c "journalctl --user -u turing-smart-screen -n 8 --no-pager 2>/dev/null || true"

sec "Resultado: $OKC verificação(ões) OK, $BADC falha(s). Relatório: $OUT"
exit 0
