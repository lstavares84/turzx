#!/usr/bin/env bash
# GAMMA | construir/aplicar-na-tela.sh | versão 1.1.0 | 07/11/2026 19:42 (-03) | criação original (Claude, para Lucas Tavares)
# Aplica o código atual do repositório na tela do PC: monta o ZIP do estilo, extrai com unzip e roda o instalador
# sem mexer em pacotes do sistema. O instalador faz backup do tema anterior e reinicia o serviço da tela.
# Uso, na raiz do repositório e com o usuário comum (sem sudo):
#   construir/aplicar-na-tela.sh [alpha|beta|gamma|delta]     (padrão: gamma)
set -euo pipefail
export TZ=America/Sao_Paulo
log(){ printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*"; }
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; cd "$RAIZ"
case "${1:-gamma}" in alpha) NOME=Alpha ;; beta) NOME=Beta ;; gamma) NOME=Gamma ;; delta) NOME=Delta ;; *) log "ERRO estilo aceito: alpha, beta, gamma ou delta"; exit 1 ;; esac
VER="$(tr -d '[:space:]' < VERSION)"
SAIDA="$RAIZ/saida"
rm -rf "$SAIDA/Gamma-$NOME-v$VER" "$SAIDA/aplicar"
python3 -I construir/construir_zips.py "$SAIDA" "$VER:$NOME"
mkdir -p "$SAIDA/aplicar"
unzip -q -o "$SAIDA/Gamma-$NOME-v$VER.zip" -d "$SAIDA/aplicar"      # unzip preserva o bit de execução
log "instalando GAMMA $NOME v$VER na tela"
cd "$SAIDA/aplicar/Gamma-$NOME-v$VER"
./instalar-gamma.sh --versao "${1:-gamma}" --sem-apt
log "pronto: GAMMA $NOME v$VER aplicado"
