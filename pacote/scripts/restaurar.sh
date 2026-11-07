#!/usr/bin/env bash
# MATRIX GREEN PRO | versão 3.1.0 | 01/11/2026 11:15 (-03) | sem mudanças funcionais (versão alinhada)
# histórico: 2.1.0 01/11/2026 00:20 restauração do tema e dos arquivos anteriores
# histórico: 2.0.0 31/10/2026 23:58 mgp-restaurar.sh
#
# Uso:
#   ./scripts/restaurar.sh                     volta ao tema anterior (Cyberdeck por padrão) e reinicia o serviço
#   ./scripts/restaurar.sh --tema NOME         volta a um tema específico
#   ./scripts/restaurar.sh --listar            lista os backups feitos pelo instalador
#   ./scripts/restaurar.sh --backup ultimo     devolve config.yaml, sensors_custom.py, unit e MangoHud.conf do backup
#   ./scripts/restaurar.sh --backup DATA       idem, de um backup específico (ex.: 20261101-001500)
#   ./scripts/restaurar.sh --remover-tudo      remove tema, extensão e ganchos (pede confirmação)
#   ./scripts/restaurar.sh --sim               responde "sim" às confirmações
#   ./scripts/restaurar.sh --dir CAMINHO       pasta do programa
# Nunca apaga ~/.config/matrixgreenpro nem os backups.
set -uo pipefail
DIR="${HOME}/turing-smart-screen-linux"; THEME=""; PURGE=0; BACKUP=""; LIST=0; YES=0
BKROOT="${HOME}/.local/share/matrixgreenpro/backups"
log() { printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*"; }
confirm() {
  [[ $YES -eq 1 ]] && return 0
  [[ -t 0 ]] || { log "confirmação necessária: rode de novo com --sim"; return 1; }
  read -r -p "$1 [s/N] " a; [[ "$a" =~ ^[sS]$ ]]
}
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="${2%/}"; shift ;;
    --tema) THEME="$2"; shift ;;
    --backup) BACKUP="$2"; shift ;;
    --listar) LIST=1 ;;
    --remover-tudo) PURGE=1 ;;
    --sim) YES=1 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) log "opção desconhecida: $1"; exit 1 ;;
  esac; shift
done
[[ $EUID -eq 0 ]] && { log "não execute como root"; exit 1; }
[[ -f "$DIR/config.yaml" ]] || { log "config.yaml não encontrado em $DIR"; exit 1; }
PY="$DIR/.venv/bin/python3"; [[ -x "$PY" ]] || PY=python3

if [[ $LIST -eq 1 ]]; then
  log "backups em $BKROOT:"
  for b in "$BKROOT"/2*; do [[ -d "$b" ]] && log "  $(basename "$b")  tema ativo antes: $(cat "$b/tema_ativo_antes.txt" 2>/dev/null)"; done
  exit 0
fi

if [[ -n "$BACKUP" ]]; then
  B="$BKROOT/$BACKUP"; [[ "$BACKUP" == "ultimo" ]] && B="$(readlink -f "$BKROOT/ultimo")"
  [[ -f "$B/manifesto.txt" ]] || { log "backup inválido: $B"; exit 1; }
  log "restaurando arquivos de $B:"
  grep -v '^dir=' "$B/manifesto.txt" | grep -vE '^(tema_|modulo_)' | while IFS='=' read -r name dest; do log "  $name -> $dest"; done
  confirm "Substituir esses arquivos pelas cópias do backup?" || { log "cancelado"; exit 1; }
  while IFS='=' read -r name dest; do
    case "$name" in
      dir|tema_MatrixGreenPro|modulo_matrixgreenpro) continue ;;
    esac
    [[ -e "$B/$name" ]] || continue
    cp -a "$dest" "$dest.antes-restaurar-$(date +%Y%m%d-%H%M%S)" 2>/dev/null
    cp -a "$B/$name" "$dest" && log "  restaurado: $dest (versão atual guardada ao lado)"
  done < "$B/manifesto.txt"
  systemctl --user daemon-reload 2>/dev/null
else
  [[ -z "$THEME" ]] && THEME="$(cat "${HOME}/.config/matrixgreenpro/tema_anterior" 2>/dev/null || echo Cyberdeck)"
  [[ -f "$DIR/res/themes/$THEME/theme.yaml" ]] || { log "tema '$THEME' não existe em res/themes"; exit 1; }
  cp -a "$DIR/config.yaml" "$DIR/config.yaml.bak-mgp-$(date +%Y%m%d-%H%M%S)"
  sed -i "s|^  THEME:.*|  THEME: $THEME|" "$DIR/config.yaml"
  log "tema selecionado: $THEME (cópia do config.yaml anterior guardada ao lado)"
fi

if [[ $PURGE -eq 1 ]]; then
  log "serão removidos: res/themes/MatrixGreenPro, library/sensors/matrixgreenpro, tools/mgp_*.py,"
  log "o bloco MATRIXGREENPRO de sensors_custom.py e do MangoHud.conf. Configuração e backups ficam."
  if confirm "Confirmar a remoção?"; then
    if grep -q "^  THEME: MatrixGreenPro" "$DIR/config.yaml"; then
      sed -i "s|^  THEME:.*|  THEME: Cyberdeck|" "$DIR/config.yaml"; log "tema ativo trocado para Cyberdeck antes da remoção"
    fi
    for f in "$DIR/library/sensors/sensors_custom.py" "${HOME}/.config/MangoHud/MangoHud.conf"; do
      [[ -f "$f" ]] || continue
      "$PY" - "$f" <<'PYEOF'
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
n = re.sub(r"\n?# >>> MATRIXGREENPRO >>>.*?# <<< MATRIXGREENPRO <<<\n?", "\n", t, flags=re.S).rstrip("\n") + "\n"
if n != t:
    open(p, "w", encoding="utf-8").write(n)
PYEOF
    done
    rm -rf "$DIR/res/themes/MatrixGreenPro" "$DIR/library/sensors/matrixgreenpro" "$DIR"/tools/mgp_*.py
    log "remoção concluída"
  else
    log "remoção cancelada"
  fi
fi

if systemctl --user is-enabled turing-smart-screen.service >/dev/null 2>&1; then
  systemctl --user restart turing-smart-screen.service && log "turing-smart-screen.service reiniciado"
else
  log "serviço não habilitado; inicie com: $DIR/scripts/start-screen.sh"
fi
log "tema ativo agora: $(grep -E '^  THEME:' "$DIR/config.yaml" | sed 's/.*: *//')"
