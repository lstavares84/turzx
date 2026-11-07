#!/usr/bin/env bash
# GAMMA | pc/espelho-github/sincronizar-github.sh | versão 1.0.0 | 07/11/2026 15:40 (-03) | criação original (Claude, para Lucas Tavares)
# Espelho local de todos os repositórios do GitHub no HDD de 12TB. Para cada repositório:
#   - não existe no disco: clona;
#   - só atrás do GitHub: avança (git merge --ff-only);
#   - só à frente (commits locais não enviados): envia (git push);
#   - mudanças sem commit, divergência ou sem upstream: não mexe e registra AVISO no log.
# Nunca faz merge com conflito, rebase, reset ou push forçado. Requer git e gh (gh auth login feito pelo usuário).
# Configuração por variáveis (veja espelho-github.conf): ESPELHO_BASE, ESPELHO_AFILIACAO.
set -uo pipefail
export TZ=America/Sao_Paulo
CONF="${XDG_CONFIG_HOME:-$HOME/.config}/espelho-github.conf"
[[ -f "$CONF" ]] && . "$CONF"
BASE="${ESPELHO_BASE:-/mnt/12TB_3.5/github}"
DISCO="${ESPELHO_DISCO-/mnt/12TB_3.5}"          # vazio: não confere a montagem
AFILIACAO="${ESPELHO_AFILIACAO:-owner}"          # owner | owner,collaborator | owner,collaborator,organization_member
ESTADO="${XDG_STATE_HOME:-$HOME/.local/state}/espelho-github"
mkdir -p "$ESTADO"
LOG="$ESTADO/sincronizar.log"
log(){ printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*" | tee -a "$LOG"; }

exec 9>"$ESTADO/trava"
flock -n 9 || { log "outra sincronização ainda está rodando; saindo"; exit 0; }

if [[ -n "$DISCO" ]] && ! mountpoint -q "$DISCO"; then
  log "AVISO: $DISCO não está montado (TerraMaster desligado?); nada a fazer"; exit 0
fi
mkdir -p "$BASE" 2>/dev/null || { log "ERRO: sem permissão para criar $BASE"; exit 1; }
command -v gh >/dev/null || { log "ERRO: gh não instalado"; exit 1; }
if ! LISTA="$(gh api --paginate "user/repos?affiliation=$AFILIACAO&per_page=100" -q '.[].full_name' 2>&1)"; then
  log "ERRO: não consegui listar os repositórios (internet ou gh auth login?): $LISTA"; exit 1
fi

n=0; avisos=0
while IFS= read -r REPO; do
  [[ -z "$REPO" ]] && continue
  n=$((n+1)); DIR="$BASE/$REPO"
  if [[ ! -d "$DIR/.git" ]]; then
    mkdir -p "$(dirname "$DIR")"
    if gh repo clone "$REPO" "$DIR" -- --quiet >>"$LOG" 2>&1; then log "$REPO: clonado"; else log "AVISO $REPO: falha ao clonar"; avisos=$((avisos+1)); fi
    continue
  fi
  cd "$DIR" || continue
  if ! git fetch --all --prune --quiet >>"$LOG" 2>&1; then log "AVISO $REPO: falha no fetch"; avisos=$((avisos+1)); continue; fi
  if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    log "AVISO $REPO: mudanças sem commit; não sincronizado (faça o commit)"; avisos=$((avisos+1)); continue
  fi
  RAMO="$(git symbolic-ref --short -q HEAD)" || { log "AVISO $REPO: HEAD solto; não sincronizado"; avisos=$((avisos+1)); continue; }
  if ! git rev-parse -q --verify '@{u}' >/dev/null; then
    log "AVISO $REPO: ramo $RAMO sem upstream; não sincronizado"; avisos=$((avisos+1)); continue
  fi
  read -r FRENTE ATRAS < <(git rev-list --left-right --count 'HEAD...@{u}')
  if (( FRENTE == 0 && ATRAS == 0 )); then
    :
  elif (( FRENTE == 0 )); then
    git merge --ff-only --quiet '@{u}' >>"$LOG" 2>&1 && log "$REPO ($RAMO): atualizado, $ATRAS commit(s) do GitHub" \
      || { log "AVISO $REPO: falha no avanço rápido"; avisos=$((avisos+1)); }
  elif (( ATRAS == 0 )); then
    git push --quiet >>"$LOG" 2>&1 && log "$REPO ($RAMO): enviado, $FRENTE commit(s) locais" \
      || { log "AVISO $REPO: falha no push"; avisos=$((avisos+1)); }
  else
    log "AVISO $REPO ($RAMO): divergiu ($FRENTE local, $ATRAS no GitHub); resolva à mão ou peça ao Claude"; avisos=$((avisos+1))
  fi
done <<< "$LISTA"
log "fim: $n repositório(s), $avisos aviso(s)"
