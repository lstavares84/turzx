#!/usr/bin/env bash
# GAMMA | construir/aplicar-na-tela.sh | versão 1.2.0 | 08/11/2026 13:24 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.2.0 08/11/2026 13:24 segundo argumento: a tela (3.5, padrão, ou 5.2)
# Aplica o código atual do repositório na tela do PC: monta o ZIP do estilo, extrai com unzip e roda o instalador
# sem mexer em pacotes do sistema. O instalador faz backup do tema anterior e reinicia o serviço da tela.
# Uso, na raiz do repositório e com o usuário comum (sem sudo):
#   construir/aplicar-na-tela.sh [alpha|beta|gamma|delta] [3.5|5.2]     (padrão: gamma na 3.5)
set -euo pipefail
export TZ=America/Sao_Paulo
log(){ printf '[%s] %s\n' "$(date '+%d/%m/%Y %H:%M:%S')" "$*"; }
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"; cd "$RAIZ"
case "${1:-gamma}" in alpha) NOME=Alpha ;; beta) NOME=Beta ;; gamma) NOME=Gamma ;; delta) NOME=Delta ;; *) log "ERRO estilo aceito: alpha, beta, gamma ou delta"; exit 1 ;; esac
TELA="${2:-3.5}"; [[ "$TELA" == "3.5" || "$TELA" == "5.2" ]] || { log "ERRO tela aceita: 3.5 ou 5.2"; exit 1; }
VER="$(tr -d '[:space:]' < VERSION)"
SAIDA="$RAIZ/saida"
rm -rf "$SAIDA/Gamma-$NOME-$TELA-v$VER" "$SAIDA/aplicar"
python3 -I construir/construir_zips.py "$SAIDA" "$VER:$NOME:$TELA"
mkdir -p "$SAIDA/aplicar"
unzip -q -o "$SAIDA/Gamma-$NOME-$TELA-v$VER.zip" -d "$SAIDA/aplicar"      # unzip preserva o bit de execução
log "instalando GAMMA $NOME v$VER na tela de $TELA\""
cd "$SAIDA/aplicar/Gamma-$NOME-$TELA-v$VER"
./instalar-gamma.sh --versao "${1:-gamma}" --tela "$TELA" --sem-apt
log "pronto: GAMMA $NOME v$VER aplicado"
