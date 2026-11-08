#!/usr/bin/env bash
# MATRIX GREEN PRO | versão 3.7.0 | 07/11/2026 20:40 (-03) | estilo conferido pelo registro ESTILOS (aceita gamma-delta-5b e v2-*)
# histórico: 3.6.1 02/11/2026 19:25 ESTILO_PADRAO do pacote
# histórico: 3.2.0 02/11/2026 17:45 edição GAMMA: estilo padrão gamma e 3 variantes
# histórico: 3.1.1 02/11/2026 15:50 edição URÂNIO, estilo padrão uranio
# histórico: 3.1.0 01/11/2026 11:10 opção --estilo (matrix, uranio, pcb)
# histórico: 2.1.0 01/11/2026 00:10 instalador do pacote TUS35-Debian13
# histórico: 2.0.0 31/10/2026 23:55 instalador idempotente | 1.0.0 31/10/2026 criação
#
# Instala o tema vertical MatrixGreenPro (320x480, retrato) no turing-smart-screen-linux
# JÁ instalado. Faz backup, preserva os temas existentes, não roda como root e pode ser
# executado quantas vezes for preciso (idempotente).
#
# Uso (a partir da pasta do pacote):
#   ./scripts/instalar.sh                     instala/atualiza, seleciona o tema e reinicia o serviço
#   ./scripts/instalar.sh --dir CAMINHO       pasta do programa (padrão ~/turing-smart-screen-linux)
#   ./scripts/instalar.sh --invertido         gira 180° (DISPLAY_REVERSE: true), se a imagem ficar de ponta-cabeça
#   ./scripts/instalar.sh --normal            DISPLAY_REVERSE: false
#   ./scripts/instalar.sh --teste-orientacao  para o serviço, exibe uma seta TOPO por 15 s e religa
#   ./scripts/instalar.sh --mangohud          configura o MangoHud para gravar o FPS real
#   ./scripts/instalar.sh --corrigir-servico  reescreve a unit systemd de usuário para apontar para --dir
#   ./scripts/instalar.sh --sem-reiniciar     instala sem reiniciar o serviço
#   ./scripts/instalar.sh --forcar            continua mesmo fora do Debian 13
#   ./scripts/instalar.sh --estilo NOME       gamma (padrão) | gamma-sonar | gamma-raiox | gamma-uv | matrix | pcb (13-C PLACA DE CIRCUITO). 'uranio' = gamma
set -uo pipefail

VERSION="$(cat "$(dirname "$0")/../VERSION" 2>/dev/null || echo 2.1.0)"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="${HOME}/turing-smart-screen-linux"
REVERSE=""; TEST_ORIENT=0; MANGO=0; FIX_UNIT=0; RESTART=1; FORCE=0; ESTILO=""
STATE="${HOME}/.local/state/matrixgreenpro"
DATA="${HOME}/.local/share/matrixgreenpro"
CONF="${HOME}/.config/matrixgreenpro"
mkdir -p "$STATE" "$DATA" "$CONF"
LOG="$STATE/instalar-$(date +%Y%m%d-%H%M%S).log"
ERRORS=0; WARNS=0

log()  { printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*" | tee -a "$LOG"; }
warn() { log "AVISO: $*"; WARNS=$((WARNS + 1)); }
err()  { log "ERRO: $*"; ERRORS=$((ERRORS + 1)); }
die()  { log "ERRO: $*"; log "instalação interrompida sem alterar o tema ativo. Log: $LOG"; exit 1; }
acao() { log "⚠️ AÇÃO MANUAL: $*"; }
step() { log "---- etapa $1"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="${2%/}"; shift ;;
    --invertido) REVERSE="true" ;;
    --normal) REVERSE="false" ;;
    --teste-orientacao) TEST_ORIENT=1 ;;
    --mangohud) MANGO=1 ;;
    --corrigir-servico) FIX_UNIT=1 ;;
    --sem-reiniciar) RESTART=0 ;;
    --forcar) FORCE=1 ;;
    --estilo) ESTILO="${2,,}"; shift ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) die "opção desconhecida: $1 (use --help)" ;;
  esac
  shift
done

log "GAMMA TUS-35 $VERSION (MatrixGreenPro) | instalador | log: $LOG"
[[ "$ESTILO" == "uranio" || "$ESTILO" == "urânio" ]] && ESTILO="gamma"   # nome antigo
if [[ -z "$ESTILO" && -s "$ROOT/ESTILO_PADRAO" ]]; then   # pacote com versão própria (ZIP N3 Esquerda ou N3 Compacto)
  ESTILO="$(head -1 "$ROOT/ESTILO_PADRAO" | tr -d '[:space:]')"
fi
if [[ -z "$ESTILO" ]]; then   # sem --estilo: mantém a escolha já gravada; instalação nova usa gamma
  ESTILO="$(grep -E '^  estilo:' "$CONF/config.yaml" 2>/dev/null | awk '{print $2}' | head -1)"
  [[ "$ESTILO" == "uranio" || -z "$ESTILO" || "$ESTILO" == "matrix" ]] && ESTILO="gamma"
fi
case "$ESTILO" in gamma-n3-esq|gamma-sentinela) ESTILO="gamma-alpha" ;; gamma-n3-compacto|gamma-dosimetro) ESTILO="gamma-beta" ;; gamma-gamma-fronteira) ESTILO="gamma-gamma" ;; esac   # nomes antigos
case "$ESTILO" in matrix|pcb|gamma|gamma-*|v2-*) ;; *) die "estilo inválido: $ESTILO (use matrix, pcb, gamma, gamma-NOME ou v2-NOME; veja o README)" ;; esac
# o estilo precisa estar registrado em ESTILOS (o nome do arquivo nem sempre segue o nome do estilo)
[[ "$ESTILO" != matrix ]] && ! grep -q "^ *\"$ESTILO\": (" "$ROOT/sensors/matrixgreenpro/estilos/__init__.py" && die "estilo desconhecido: $ESTILO (veja a lista no README)"
[[ $EUID -eq 0 ]] && die "não execute como root. Use seu usuário: o programa roda como serviço systemd --user"
for f in MatrixGreenPro/theme.yaml MatrixGreenPro/background.png sensors/matrixgreenpro/panel.py \
         sensors/sensors_custom_hook.txt tools/mgp_selftest.py; do
  [[ -f "$ROOT/$f" ]] || die "pacote incompleto: falta $f"
done

# ------------------------------------------------------------------ 1. sistema
step "1/15 sistema operacional"
OS_ID="$(. /etc/os-release 2>/dev/null; echo "${ID:-?}")"
OS_VER="$(. /etc/os-release 2>/dev/null; echo "${VERSION_ID:-?} ${VERSION_CODENAME:-}")"
log "sistema: $OS_ID $OS_VER"
if [[ "$OS_ID" != "debian" ]]; then
  [[ $FORCE -eq 1 ]] && warn "sistema não Debian; continuando por --forcar" || die "sistema não é Debian (use --forcar por sua conta)"
elif [[ "$OS_VER" != 13* ]]; then
  warn "Debian $OS_VER: o pacote foi preparado para o Debian 13 Trixie"
fi

# ------------------------------------------------------------------ 2. instalação existente
step "2/15 instalação existente do Turing Smart Screen"
[[ -f "$DIR/main.py" && -f "$DIR/config.yaml" && -f "$DIR/library/sensors/sensors_custom.py" ]] \
  || die "turing-smart-screen não encontrado em $DIR (use --dir CAMINHO)"
PY="$DIR/.venv/bin/python3"
[[ -x "$PY" ]] || die "ambiente $DIR/.venv ausente. O programa precisa estar instalado (scripts/install-ubuntu.sh do projeto)"
log "programa: $DIR | $(cat "$DIR/VERSION" 2>/dev/null || echo 'versão ?') | $("$PY" --version 2>&1)"
[[ -f "$DIR/res/themes/Cyberdeck/theme.yaml" ]] && log "tema Cyberdeck presente (não será alterado)" \
  || warn "tema Cyberdeck não encontrado em res/themes"

# ------------------------------------------------------------------ 3. dispositivo
step "3/15 tela TURZX TUS-35"
if lsusb 2>/dev/null | grep -qi '1a86:5722'; then
  log "USB: $(lsusb | grep -i '1a86:5722' | head -1)"
else
  warn "1a86:5722 não aparece no lsusb agora (cabo, porta ou tela desligada). A instalação continua"
fi
BYID="$(ls /dev/serial/by-id/ 2>/dev/null | grep -i 'USB35INCHIPSV2\|UsbMonitor' | head -1 || true)"
[[ -n "$BYID" ]] && log "porta persistente: /dev/serial/by-id/$BYID -> $(readlink -f "/dev/serial/by-id/$BYID")" \
  || warn "nenhuma porta /dev/serial/by-id com USB35INCHIPSV2"
if id -nG "$USER" | grep -qw dialout; then
  log "usuário $USER pertence ao grupo dialout"
else
  warn "usuário $USER fora do grupo dialout (sem acesso à porta serial)"
  if [[ -t 0 ]]; then
    read -r -p "Adicionar $USER ao grupo dialout agora com sudo? [s/N] " ans
    if [[ "$ans" =~ ^[sS]$ ]]; then
      sudo usermod -aG dialout "$USER" && acao "encerre a sessão e entre novamente para valer o grupo dialout"
    fi
  else
    acao "sudo usermod -aG dialout $USER  (depois encerre a sessão e entre novamente)"
  fi
fi

# ------------------------------------------------------------------ 4. serviços
step "4/15 serviços systemd de usuário"
UNIT="${HOME}/.config/systemd/user/turing-smart-screen.service"
FPSUNIT="${HOME}/.config/systemd/user/turing-fps.service"
HAS_SYSTEMD=0
systemctl --user show-environment >/dev/null 2>&1 && HAS_SYSTEMD=1
if [[ -f "$UNIT" ]]; then
  EXEC="$(grep -E '^ExecStart=' "$UNIT" | head -1 | cut -d= -f2-)"
  log "turing-smart-screen.service ExecStart=$EXEC"
  if [[ "$EXEC" != "$DIR/"* || ! -x "${EXEC%% *}" ]]; then
    if [[ $FIX_UNIT -eq 1 ]]; then
      FIX_PENDING=1
    else
      warn "a unit não aponta para $DIR"
      acao "se o serviço não subir, rode novamente com --corrigir-servico"
    fi
  fi
else
  warn "unit $UNIT inexistente"
  acao "habilite o início automático: cd $DIR && ./scripts/install-autostart.sh"
fi
[[ -f "$FPSUNIT" ]] && log "turing-fps.service presente (não será modificado; grava Hz do monitor, que o painel ignora)"

# ------------------------------------------------------------------ 5. dependências
step "5/15 dependências"
for mod in psutil PIL yaml serial; do
  "$PY" -c "import $mod" 2>/dev/null && log "python ok: $mod" || die "módulo Python ausente no venv do programa: $mod"
done
for f in roboto/Roboto-Bold.ttf generale-mono/GeneraleMonoA.ttf; do   # usadas pelos estilos gamma e pcb
  [[ -f "$DIR/res/fonts/$f" ]] && log "fonte ok: $f" || warn "fonte ausente: res/fonts/$f (estilos gamma/pcb podem falhar)"
done
for f in JetBrainsMonoNL-Regular.ttf JetBrainsMonoNL-Bold.ttf; do
  [[ -f "$DIR/res/fonts/jetbrains-mono/$f" ]] && log "fonte ok: jetbrains-mono/$f (já distribuída pelo projeto, licença OFL)" \
    || die "fonte ausente: res/fonts/jetbrains-mono/$f"
done
for cmd in lsblk ping; do command -v "$cmd" >/dev/null && log "comando ok: $cmd" || warn "comando ausente: $cmd"; done
if command -v nvidia-smi >/dev/null; then
  log "GPU: $(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -1)"
  if ! "$PY" -c "import pynvml" 2>/dev/null; then
    "$DIR/.venv/bin/pip" install -q nvidia-ml-py >>"$LOG" 2>&1 && log "nvidia-ml-py instalado no venv (NVML: limite térmico e RPM, se a placa expuser)" \
      || warn "nvidia-ml-py não instalado; o painel usará o nvidia-smi"
  else
    log "python ok: pynvml"
  fi
else
  warn "nvidia-smi não encontrado: GPU aparecerá como N/D"
fi
command -v sensors >/dev/null || acao "para temperaturas e ventoinhas: sudo apt install lm-sensors && sudo sensors-detect"

# ------------------------------------------------------------------ 6. backup
step "6/15 backup"
BK="$DATA/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BK"
{
  echo "dir=$DIR"
  cp -a "$DIR/config.yaml" "$BK/config.yaml" && echo "config.yaml=$DIR/config.yaml"
  cp -a "$DIR/library/sensors/sensors_custom.py" "$BK/sensors_custom.py" && echo "sensors_custom.py=$DIR/library/sensors/sensors_custom.py"
  [[ -f "$UNIT" ]] && cp -a "$UNIT" "$BK/turing-smart-screen.service" && echo "turing-smart-screen.service=$UNIT"
  [[ -f "${HOME}/.config/MangoHud/MangoHud.conf" ]] && cp -a "${HOME}/.config/MangoHud/MangoHud.conf" "$BK/MangoHud.conf" \
    && echo "MangoHud.conf=${HOME}/.config/MangoHud/MangoHud.conf"
  [[ -d "$DIR/res/themes/MatrixGreenPro" ]] && cp -a "$DIR/res/themes/MatrixGreenPro" "$BK/tema_MatrixGreenPro" && echo "tema_MatrixGreenPro=$DIR/res/themes/MatrixGreenPro"
  [[ -d "$DIR/library/sensors/matrixgreenpro" ]] && cp -a "$DIR/library/sensors/matrixgreenpro" "$BK/modulo_matrixgreenpro" && echo "modulo_matrixgreenpro=$DIR/library/sensors/matrixgreenpro"
} > "$BK/manifesto.txt"
CUR_THEME="$("$PY" -c "import yaml,sys; print(yaml.safe_load(open(sys.argv[1]))['config'].get('THEME',''))" "$DIR/config.yaml" 2>/dev/null)"
if [[ -n "$CUR_THEME" && "$CUR_THEME" != "MatrixGreenPro" ]]; then
  echo "$CUR_THEME" > "$CONF/tema_anterior"
fi
[[ -f "$CONF/tema_anterior" ]] || echo "Cyberdeck" > "$CONF/tema_anterior"
echo "$CUR_THEME" > "$BK/tema_ativo_antes.txt"
ln -sfn "$BK" "$DATA/backups/ultimo"
log "backup: $BK | tema ativo antes: ${CUR_THEME:-?} | tema a restaurar: $(cat "$CONF/tema_anterior")"

# ------------------------------------------------------------------ 7. tema
step "7/15 pasta do tema MatrixGreenPro"
mkdir -p "$DIR/res/themes/MatrixGreenPro"
cp -a "$ROOT/MatrixGreenPro/." "$DIR/res/themes/MatrixGreenPro/" || die "falha ao copiar o tema"
log "instalado em res/themes/MatrixGreenPro: $(ls "$DIR/res/themes/MatrixGreenPro" | tr '\n' ' ')"

# ------------------------------------------------------------------ 8. extensão de sensores
step "8/15 extensão de sensores personalizados"
rm -rf "$DIR/library/sensors/matrixgreenpro.novo"
cp -a "$ROOT/sensors/matrixgreenpro" "$DIR/library/sensors/matrixgreenpro.novo" || die "falha ao copiar a extensão"
rm -rf "$DIR/library/sensors/matrixgreenpro" && mv "$DIR/library/sensors/matrixgreenpro.novo" "$DIR/library/sensors/matrixgreenpro"
mkdir -p "$DIR/tools" && cp -a "$ROOT/tools/"mgp_*.py "$DIR/tools/" || die "falha ao copiar ferramentas"
"$PY" - "$DIR/library/sensors/sensors_custom.py" "$ROOT/sensors/sensors_custom_hook.txt" <<'PYEOF' || die "falha ao registrar o sensor"
import re, sys
sc, hook = sys.argv[1], open(sys.argv[2], encoding="utf-8").read()
t = open(sc, encoding="utf-8").read()
new = re.sub(r"\n# >>> MATRIXGREENPRO >>>.*?# <<< MATRIXGREENPRO <<<\n?", "\n", t, flags=re.S).rstrip("\n") + "\n" + hook
if new != t:
    open(sc, "w", encoding="utf-8").write(new)
PYEOF
log "MatrixGreenProPanel registrado (bloco único em library/sensors/sensors_custom.py)"
"$PY" "$DIR/tools/mgp_detect.py" 2>&1 | tee -a "$LOG"
grep -q 'NÃO DETECTADO' "$CONF/config.yaml" 2>/dev/null && acao "confira os UUIDs dos discos em $CONF/config.yaml (comando: lsblk -f)"
if [[ -n "$ESTILO" ]]; then
  "$PY" - "$CONF/config.yaml" "$ESTILO" <<'PYEOF' 2>&1 | tee -a "$LOG" || die "falha ao gravar o estilo"
import re, sys, yaml
p, est = sys.argv[1], sys.argv[2]
t0 = open(p, encoding="utf-8").read()
t = t0
if re.search(r"(?m)^  estilo:", t):
    t = re.sub(r"(?m)^  estilo:.*$", f"  estilo: {est}           # matrix | pcb | gamma | gamma-NOME (veja o README)", t)
elif re.search(r"(?m)^painel:\s*$", t):
    t = re.sub(r"(?m)^painel:\s*$", f"painel:\n  estilo: {est}           # matrix | pcb | gamma | gamma-NOME (veja o README)", t, count=1)
else:
    t = t.rstrip("\n") + f"\npainel:\n  estilo: {est}\n"
yaml.safe_load(t)
if t != t0:
    open(p, "w", encoding="utf-8").write(t)
print(f"  estilo do painel: {est}" + ("" if t != t0 else " (já estava definido)"))
PYEOF
fi
log "estilo ativo: $(grep -E '^  estilo:' "$CONF/config.yaml" 2>/dev/null | awk '{print $2}' || echo matrix)"

# ------------------------------------------------------------------ 9. validação
step "9/15 validação do YAML, recursos e importação"
(cd "$DIR" && "$PY" - <<'PYEOF') 2>&1 | tee -a "$LOG"
import sys, yaml
from pathlib import Path
from PIL import Image
ok = True
t = yaml.safe_load(open("res/themes/MatrixGreenPro/theme.yaml", encoding="utf-8"))
def need(cond, msg):
    global ok
    print(("  ok    " if cond else "  ERRO  ") + msg)
    ok &= bool(cond)
need(t["display"]["DISPLAY_SIZE"] == '3.5"', 'display.DISPLAY_SIZE = 3.5" (320x480)')
need(t["display"]["DISPLAY_ORIENTATION"] == "portrait", "display.DISPLAY_ORIENTATION = portrait")
for k, v in t.get("static_images", {}).items():
    p = Path("res/themes/MatrixGreenPro") / v["PATH"]
    need(p.is_file(), f"static_images.{k}: {v['PATH']} existe")
    if p.is_file():
        need(Image.open(p).size == (320, 480), f"{v['PATH']} tem 320x480")
need(set(t["STATS"].keys()) == {"CUSTOM"}, "STATS contém só CUSTOM (sensores nativos ficam desligados)")
from library.sensors import sensors_custom as sc
need(hasattr(sc, "MatrixGreenProPanel"), "sensors_custom.MatrixGreenProPanel importável")
need(issubclass(sc.MatrixGreenProPanel, sc.CustomDataSource), "MatrixGreenProPanel herda CustomDataSource")
for k in t["STATS"]["CUSTOM"]:
    if k != "INTERVAL":
        need(hasattr(sc, k), f"STATS.CUSTOM.{k} existe em sensors_custom.py")
yaml.safe_load(open("config.yaml", encoding="utf-8"))
sys.exit(0 if ok else 1)
PYEOF
[[ ${PIPESTATUS[0]} -eq 0 ]] || die "validação falhou; o tema ativo NÃO foi alterado (restaure com scripts/restaurar.sh se quiser)"
(cd "$DIR" && "$PY" tools/mgp_selftest.py) >>"$LOG" 2>&1 && log "testes automáticos aprovados" \
  || err "testes automáticos falharam (detalhes em $LOG)"
(cd "$DIR" && "$PY" tools/mgp_preview.py "$DATA/previews") >>"$LOG" 2>&1 && log "prévias regeneradas em $DATA/previews" \
  || err "falha ao gerar prévias"

# ------------------------------------------------------------------ 10. temas antigos
step "10/15 preservação dos temas"
log "temas instalados: $(ls -d "$DIR"/res/themes/*/ 2>/dev/null | wc -l) pastas; nenhum tema existente foi modificado"

# ------------------------------------------------------------------ 11 e 12. orientação e seleção do tema
step "11/15 orientação retrato | 12/15 seleção do tema"
"$PY" - "$DIR/config.yaml" "$REVERSE" <<'PYEOF' 2>&1 | tee -a "$LOG" || die "falha ao ajustar config.yaml"
import re, sys, yaml
p, rev = sys.argv[1], sys.argv[2]
t0 = open(p, encoding="utf-8").read()
t = t0
t, n = re.subn(r"(?m)^  THEME:.*$", "  THEME: MatrixGreenPro", t)
if n == 0:
    t = t.replace("config:\n", "config:\n  THEME: MatrixGreenPro\n", 1)
if rev in ("true", "false"):
    t, n = re.subn(r"(?m)^  DISPLAY_REVERSE:.*$", f"  DISPLAY_REVERSE: {rev}", t)
    if n == 0:
        t = t.replace("display:\n", f"display:\n  DISPLAY_REVERSE: {rev}\n", 1)
yaml.safe_load(t)  # nunca grava um config.yaml inválido
if t != t0:
    open(p, "w", encoding="utf-8").write(t)
    print("  config.yaml atualizado (somente THEME e, se pedido, DISPLAY_REVERSE)")
else:
    print("  config.yaml já estava correto; nada alterado")
PYEOF
HWREV="$(grep -E '^  REVISION:' "$DIR/config.yaml" | awk '{print $2}')"
REV_NOW="$(grep -E '^  DISPLAY_REVERSE:' "$DIR/config.yaml" | awk '{print $2}')"
log "THEME=MatrixGreenPro | DISPLAY_ORIENTATION=portrait (no tema) | DISPLAY_REVERSE=${REV_NOW:-false} | REVISION=${HWREV:-?}"
[[ "$HWREV" == "A" ]] || warn "REVISION=$HWREV; o TUS-35 (USB35INCHIPSV2) usa a revisão A"

if [[ $MANGO -eq 1 ]]; then
  MH="${HOME}/.config/MangoHud/MangoHud.conf"
  mkdir -p "$(dirname "$MH")"; touch "$MH"
  "$PY" - "$MH" "$ROOT/extras/MangoHud-mgp.conf" <<'PYEOF'
import re, sys
p, blk = sys.argv[1], open(sys.argv[2], encoding="utf-8").read()
t = open(p, encoding="utf-8").read()
new = re.sub(r"\n?# >>> MATRIXGREENPRO >>>.*?# <<< MATRIXGREENPRO <<<\n?", "\n", t, flags=re.S).rstrip("\n") + "\n" + blk
if new != t:
    open(p, "w", encoding="utf-8").write(new)
PYEOF
  log "MangoHud: log de FPS em /tmp/mgp-mangohud (bloco único em $MH)"
  command -v mangohud >/dev/null || acao "instale o MangoHud: sudo apt install mangohud ; na Steam use: mangohud %command%"
fi

# ------------------------------------------------------------------ 13. serviço
step "13/15 reinício somente do turing-smart-screen.service"
kill_dupes() {   # instâncias manuais DESTE programa disputando a porta USB
  local pid
  for pid in $(pgrep -f '(^|/)python3 main\.py$' 2>/dev/null); do
    [[ "$(readlink -f "/proc/$pid/cwd" 2>/dev/null)" == "$(readlink -f "$DIR")" ]] || continue
    systemctl --user show -p MainPID --value turing-smart-screen.service 2>/dev/null | grep -qx "$pid" && continue
    kill "$pid" 2>/dev/null && log "instância manual encerrada (PID $pid)"
  done
}
if [[ "${FIX_PENDING:-0}" -eq 1 ]]; then
  sed "s|%h/turing-smart-screen-python|$DIR|g; s|%h|$HOME|g" "$DIR/scripts/turing-smart-screen.user.service" > "$UNIT"
  log "unit reescrita para $DIR (original no backup)"
fi
if [[ $HAS_SYSTEMD -eq 1 && -f "$UNIT" ]]; then
  systemctl --user daemon-reload
  systemctl --user is-enabled turing-smart-screen.service >/dev/null 2>&1 || {
    systemctl --user enable turing-smart-screen.service >>"$LOG" 2>&1 && log "serviço habilitado no login" || err "falha ao habilitar o serviço"; }
fi
if [[ $TEST_ORIENT -eq 1 ]]; then
  [[ $HAS_SYSTEMD -eq 1 ]] && systemctl --user stop turing-smart-screen.service 2>/dev/null
  kill_dupes; sleep 2
  INV=""; [[ "${REV_NOW:-false}" == "true" ]] && INV="--invertido"
  log "teste de orientação: observe a tela por 15 s"
  (cd "$DIR" && "$PY" tools/mgp_orientation_test.py $INV --segundos 15) 2>&1 | tee -a "$LOG"
  acao "se a seta NÃO apontou para cima: ./scripts/instalar.sh --invertido   (desfazer: --normal)"
fi
if [[ $RESTART -eq 1 ]]; then
  if [[ $HAS_SYSTEMD -eq 1 && -f "$UNIT" ]]; then
    kill_dupes
    rm -f /tmp/turing-smart-screen.lock /tmp/turing-smart-screen.pid
    systemctl --user restart turing-smart-screen.service >>"$LOG" 2>&1 && log "turing-smart-screen.service reiniciado (turing-fps.service intocado)" \
      || err "falha ao reiniciar o serviço"
  else
    warn "systemd --user indisponível ou sem unit: inicie manualmente com $DIR/scripts/start-screen.sh"
  fi
fi

# ------------------------------------------------------------------ 14. erros de inicialização
step "14/15 verificação da inicialização"
if [[ $RESTART -eq 1 && $HAS_SYSTEMD -eq 1 && -f "$UNIT" ]]; then
  log "aguardando 20 s"
  sleep 20
  systemctl --user is-active turing-smart-screen.service >/dev/null && log "serviço ativo" \
    || err "serviço inativo: journalctl --user -u turing-smart-screen -n 50"
  if [[ -f /tmp/turing-screen.log ]]; then
    grep -q "Loading theme MatrixGreenPro" /tmp/turing-screen.log && log "programa carregou o tema MatrixGreenPro" || err "o log não mostra o carregamento do tema"
    grep -q "\[MatrixGreenPro\] CPU" /tmp/turing-screen.log && log "painel iniciado: $(grep '\[MatrixGreenPro\] CPU' /tmp/turing-screen.log | tail -1 | cut -c1-170)"
    grep -E "\[ERROR\]|Traceback" /tmp/turing-screen.log | tail -5 | while read -r l; do warn "log: $l"; done
  fi
else
  log "verificação pulada (serviço não reiniciado)"
fi

# ------------------------------------------------------------------ 15. diagnóstico final
step "15/15 diagnóstico final"
bash "$ROOT/scripts/diagnosticar.sh" --dir "$DIR" --resumo 2>&1 | tee -a "$LOG"
log "concluído: $ERRORS erro(s), $WARNS aviso(s). Reverter: ./scripts/restaurar.sh | Log: $LOG"
exit $(( ERRORS > 0 ? 1 : 0 ))
