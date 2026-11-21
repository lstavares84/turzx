#!/usr/bin/env bash
# GAMMA TUS-35 | construtor dos ZIPs | versão 1.0.0 | 02/11/2026 19:20 (-03) | criação original (Claude, para Lucas Tavares)
# Gera zips/Gamma-Sentinela-<VERSION>.zip e zips/Gamma-Dosimetro-<VERSION>.zip a partir de pacote/.
# Usa python3 (zipfile) porque o comando zip pode não existir no Debian. Preserva permissões de execução.
# Uso: ./construir-zips.sh
set -euo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VER="$(head -1 "$AQUI/VERSION" | tr -d '[:space:]')"
[[ "$VER" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "[$(date '+%d/%m/%Y %H:%M:%S')] ERRO: VERSION inválido: $VER"; exit 1; }
echo "[$(date '+%d/%m/%Y %H:%M:%S')] construindo ZIPs da versão $VER"
mkdir -p "$AQUI/zips"; rm -f "$AQUI"/zips/Gamma-*.zip
python3 -I - "$AQUI" "$VER" <<'PY'
import os, sys, time, zipfile
aqui, ver = sys.argv[1], sys.argv[2]
ts = lambda: time.strftime("[%d/%m/%Y %H:%M:%S]")
VARIANTES = {
    "Sentinela": ("gamma-sentinela", "GAMMA SENTINELA", "escala N0/N1/N2 sem tarja (barra lateral e nome brilhante), sem LIVE, com percentuais de RAM, VRAM e discos"),
    "Dosimetro": ("gamma-dosimetro", "GAMMA DOSÍMETRO", "percentuais entre parênteses e informações de limite, disponível e livre junto do uso"),
}
def add(z, src, dst):
    zi = zipfile.ZipInfo.from_file(src, dst)
    zi.compress_type = zipfile.ZIP_DEFLATED
    with open(src, "rb") as f: z.writestr(zi, f.read())
for chave, (estilo, titulo, desc) in VARIANTES.items():
    raiz = f"Gamma-{chave}"
    destino = os.path.join(aqui, "zips", f"{raiz}-{ver}.zip")
    leia = f"""<!-- LEIA-ME | {titulo} {ver} | gerado em {time.strftime('%d/%m/%Y %H:%M')} (-03) | criação original (Claude, para Lucas Tavares) -->
# {titulo} {ver}

Tema para a tela TURZX/Turing TUS-35 de 3,5" no Debian 13: {desc}.

## Instalar (um comando)

```bash
unzip {raiz}-{ver}.zip && cd {raiz} && ./instalar-gamma.sh
```

O script instala as dependências, configura o grupo dialout, baixa o turing-smart-screen, cria o serviço systemd e instala o tema.
Se a imagem estiver de ponta-cabeça: `./instalar-gamma.sh --invertido`. Para voltar ao tema anterior: `./instalar-gamma.sh --restaurar`.

Detalhes técnicos: `README-pacote.md`. Histórico: `CHANGELOG.md`. Prévias: pasta `previews/`.
"""
    with zipfile.ZipFile(destino, "w") as z:
        pac = os.path.join(aqui, "pacote")
        for d, ds, fs in os.walk(pac):
            ds[:] = sorted(x for x in ds if x not in ("__pycache__", ".git"))
            for f in sorted(fs):
                if f.endswith(".pyc") or f in ("VERSION", "README.md"): continue
                src = os.path.join(d, f); rel = os.path.relpath(src, pac)
                add(z, src, f"{raiz}/{rel}")
        add(z, os.path.join(pac, "README.md"), f"{raiz}/README-pacote.md")
        add(z, os.path.join(aqui, "instalar-gamma.sh"), f"{raiz}/instalar-gamma.sh")
        add(z, os.path.join(aqui, "VERSION"), f"{raiz}/VERSION")
        add(z, os.path.join(aqui, "CHANGELOG.md"), f"{raiz}/CHANGELOG.md")
        for nome, conteudo in (("ESTILO_PADRAO", estilo + "\n"), ("LEIA-ME.md", leia)):
            zi = zipfile.ZipInfo(f"{raiz}/{nome}", time.localtime()[:6]); zi.external_attr = 0o644 << 16
            zi.compress_type = zipfile.ZIP_DEFLATED; z.writestr(zi, conteudo)
        nome_ps = chave
        pv = os.path.join(aqui, "previews")
        for f in sorted(os.listdir(pv)):
            if f.startswith("Comparativo") or f"Gamma{nome_ps}" in f or f.startswith(f"gamma-{estilo.split('-')[1]}-"):
                add(z, os.path.join(pv, f), f"{raiz}/previews/{f}")
    print(ts(), "gerado", os.path.relpath(destino, aqui), os.path.getsize(destino) // 1024, "KB")
PY
