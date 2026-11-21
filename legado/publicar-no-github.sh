#!/usr/bin/env bash
# GAMMA TUS-35 | publicação no GitHub com SemVer | versão 1.0.0 | 02/11/2026 19:25 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.0.0 02/11/2026 19:25 versionamento SemVer automático por commit, CHANGELOG, ZIPs e tag vX.Y.Z
#
# Publica a pasta gamma-tus35 em https://github.com/lstavares84/debian (clona, copia, versiona, commit, tag e push).
# Rode na pasta onde estão este script e a pasta gamma-tus35, com a SUA conta do GitHub:
#   ./publicar-no-github.sh                              primeira vez: publica a versão do arquivo VERSION (1.0.0)
#   ./publicar-no-github.sh --mensagem "o que mudou"     depois: sobe PATCH (1.0.0 para 1.0.1)
#   ./publicar-no-github.sh --nivel minor --mensagem "..."   sobe MINOR (1.0.1 para 1.1.0)
#   ./publicar-no-github.sh --nivel major --mensagem "..."   sobe MAJOR (1.1.0 para 2.0.0)
# Regras: MAJOR = mudança incompatível (remove estilo, muda formato da config); MINOR = novidade compatível
#         (novo estilo ou recurso); PATCH = correção ou ajuste. A versão muda a cada commit publicado.
# Opções: --sem-gh (usa só git/SSH)   --ajuda
# Variável opcional: GAMMA_REPO_URL (outro repositório de destino).
set -uo pipefail

REPO_URL="${GAMMA_REPO_URL:-https://github.com/lstavares84/debian.git}"
REPO_SSH="git@github.com:lstavares84/debian.git"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGEM="$AQUI/gamma-tus35"
USAR_GH=1; NIVEL="patch"; MENSAGEM=""
log() { printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*"; }
die() { log "ERRO: $*"; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sem-gh) USAR_GH=0 ;;
    --nivel) NIVEL="${2:-}"; shift ;;
    --mensagem) MENSAGEM="${2:-}"; shift ;;
    -h|--ajuda|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) die "opção desconhecida: $1" ;;
  esac
  shift
done
case "$NIVEL" in major|minor|patch) ;; *) die "--nivel aceita: major, minor ou patch" ;; esac

command -v git >/dev/null || die "git não instalado (sudo apt install git)"
command -v python3 >/dev/null || die "python3 não instalado (sudo apt install python3)"
[[ -f "$ORIGEM/instalar-gamma.sh" ]] || die "pasta gamma-tus35 não encontrada ao lado deste script ($ORIGEM)"
LOCAL_VER="$(head -1 "$ORIGEM/VERSION" 2>/dev/null | tr -d '[:space:]')"
[[ "$LOCAL_VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "VERSION inválido em $ORIGEM/VERSION: '$LOCAL_VER'"

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
DEST="$TMP/debian"

if [[ $USAR_GH -eq 1 && -n "$(command -v gh)" && "$REPO_URL" == https://github.com/* ]]; then
  if ! gh auth status >/dev/null 2>&1; then
    log "⚠️ AÇÃO MANUAL: entre na sua conta do GitHub (abrirá o navegador ou mostrará um código)"
    gh auth login --hostname github.com --git-protocol https --web || die "login no GitHub não concluído"
  fi
  gh auth setup-git >/dev/null 2>&1 || true
  log "clonando lstavares84/debian com o gh"
  gh repo clone lstavares84/debian "$DEST" || die "não consegui clonar (o repositório existe e a sua conta tem acesso?)"
else
  log "clonando $REPO_URL"
  if ! git clone "$REPO_URL" "$DEST" 2>&1; then
    log "https falhou; tentando SSH ($REPO_SSH)"
    git clone "$REPO_SSH" "$DEST" 2>&1 || die "não consegui clonar. Crie o repositório lstavares84/debian no GitHub e confira o acesso (gh auth login ou chave SSH)"
  fi
fi

cd "$DEST" || die "pasta clonada ausente"
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git pull --ff-only -q 2>&1 || log "AVISO: não consegui atualizar o clone (seguindo com a versão clonada)"
else
  git checkout -q -B main
  log "repositório vazio: criando a branch main"
fi

# versão já publicada (se houver)
REMOTE_VER=""
if [[ -f gamma-tus35/VERSION ]]; then
  REMOTE_VER="$(head -1 gamma-tus35/VERSION | tr -d '[:space:]')"
  [[ "$REMOTE_VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "VERSION publicado é inválido: '$REMOTE_VER'"
  cp gamma-tus35/CHANGELOG.md "$TMP/CHANGELOG.remoto" 2>/dev/null || true
fi

log "copiando gamma-tus35 para o repositório"
rm -rf gamma-tus35
cp -a "$ORIGEM" gamma-tus35
find gamma-tus35 -name __pycache__ -prune -exec rm -rf {} \; 2>/dev/null || true
if [[ -n "$REMOTE_VER" ]]; then          # a versão e o histórico publicados valem até o bump
  echo "$REMOTE_VER" > gamma-tus35/VERSION; echo "$REMOTE_VER" > gamma-tus35/pacote/VERSION
  [[ -f "$TMP/CHANGELOG.remoto" ]] && cp "$TMP/CHANGELOG.remoto" gamma-tus35/CHANGELOG.md
fi

# houve mudança real? (ignora VERSION, CHANGELOG e zips, que o próprio script gera)
git add -A gamma-tus35
if git diff --cached --quiet -- . ':(exclude)gamma-tus35/VERSION' ':(exclude)gamma-tus35/pacote/VERSION' ':(exclude)gamma-tus35/CHANGELOG.md' ':(exclude)gamma-tus35/zips'; then
  if [[ -n "$REMOTE_VER" ]]; then
    log "nada a publicar: o repositório já está igual à pasta gamma-tus35 (versão $REMOTE_VER)"
    exit 0
  fi
fi

# nova versão
if [[ -z "$REMOTE_VER" ]]; then
  NOVA="$LOCAL_VER"; [[ -n "$MENSAGEM" ]] || MENSAGEM="primeira versão publicada"
  log "primeira publicação: versão $NOVA (sem incremento)"
else
  IFS=. read -r MA MI PA <<<"$REMOTE_VER"
  case "$NIVEL" in major) MA=$((MA+1)); MI=0; PA=0 ;; minor) MI=$((MI+1)); PA=0 ;; patch) PA=$((PA+1)) ;; esac
  NOVA="$MA.$MI.$PA"; [[ -n "$MENSAGEM" ]] || MENSAGEM="atualização"
  log "versão publicada $REMOTE_VER, nível $NIVEL: nova versão $NOVA"
fi
git rev-parse -q --verify "refs/tags/v$NOVA" >/dev/null && die "a tag v$NOVA já existe no repositório"
echo "$NOVA" > gamma-tus35/VERSION; echo "$NOVA" > gamma-tus35/pacote/VERSION

# CHANGELOG (entrada nova logo abaixo do marcador; no primeiro envio o 1.0.0 já está escrito)
if [[ -n "$REMOTE_VER" ]]; then
  python3 -I - "$DEST/gamma-tus35/CHANGELOG.md" "$NOVA" "$NIVEL" "$MENSAGEM" <<'PY'
import sys, time
p, ver, nivel, msg = sys.argv[1:5]
entrada = f"\n## [{ver}] - {time.strftime('%d/%m/%Y %H:%M')} (-03)\n\nNível: {nivel}.\n\n- {msg}\n"
s = open(p, encoding="utf-8").read()
m = "<!-- NOVAS-VERSOES -->"
s = s.replace(m, m + "\n" + entrada, 1) if m in s else s + entrada
open(p, "w", encoding="utf-8").write(s)
PY
fi

log "reconstruindo os ZIPs da versão $NOVA"
rm -f gamma-tus35/zips/Gamma-*.zip
bash gamma-tus35/construir-zips.sh || die "falha ao construir os ZIPs"
git add -A gamma-tus35

NIVEL_TXT="$NIVEL"; [[ -n "$REMOTE_VER" ]] || NIVEL_TXT="inicial"
git commit -q -F - <<MSG || die "falha no commit (configure git config --global user.name e user.email)"
v$NOVA: $MENSAGEM

GAMMA TUS-35 (GAMMA SENTINELA e GAMMA DOSÍMETRO). Nível de versão: $NIVEL_TXT.

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MrFCPAFHPZSYBa53jzMDj4
MSG
git tag -a "v$NOVA" -m "GAMMA TUS-35 v$NOVA: $MENSAGEM" || die "falha ao criar a tag v$NOVA"
log "enviando (push) com a tag v$NOVA"
git push -u origin HEAD --follow-tags 2>&1 || die "push recusado. Confira o acesso de escrita ao repositório"
BR="$(git rev-parse --abbrev-ref HEAD)"
log "publicado v$NOVA: https://github.com/lstavares84/debian/tree/$BR/gamma-tus35"
