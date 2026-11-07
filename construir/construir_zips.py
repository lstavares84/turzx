# GAMMA | construir/construir_zips.py | versão 1.0.0 | 07/11/2026 14:30 (-03) | criação original (Claude, para Lucas Tavares)
# Monta os ZIPs enxutos (um por estilo) a partir de pacote/. Uso, na raiz do repositório:
#   python3 -I construir/construir_zips.py SAIDA 1.6.0:Alpha 1.6.0:Beta 1.6.0:Gamma
# Gera SAIDA/Gamma-<Nome>-v<versão>/ e o ZIP correspondente (permissões preservadas, instalador executável).
# Para uma nova versão, adicione uma linha em V (e uma entrada em ENT, o histórico de versões).
import os, re, shutil, stat, sys, time, zipfile
from pathlib import Path
SRC=str(Path(__file__).resolve().parent.parent); OUT=sys.argv[1]
V={"1.6.0:Alpha":("gamma-alpha","GAMMA ALPHA","Alpha",["gamma-n3-esq","gamma-sentinela"],"escala N0/N1/N2 sem tarja, percentuais, bomba, ventoinhas, temperaturas e selo de versão na tela (ex GAMMA SENTINELA)"),
   "1.6.0:Beta":("gamma-beta","GAMMA BETA","Beta",["gamma-n3-compacto","gamma-dosimetro"],"percentuais entre parênteses, bomba, ventoinhas, temperaturas, 4 baias do TerraMaster e selo de versão na tela (ex GAMMA DOSÍMETRO)"),
   "1.6.0:Gamma":("gamma-gamma","GAMMA GAMMA","Gamma",["gamma-gamma-fronteira"],"7 colmeias de resumo e painel numérico por grupo, com temperatura dos discos, 4 baias do TerraMaster e selo de versão na tela")}
KEEP={"__init__.py","base.py","reator.py","alerta.py","reator_gamma.py","reator_grupos.py"}
def sub(p,a,b):
    s=open(p,encoding="utf-8").read(); assert a in s,(p,a[:40]); open(p,"w",encoding="utf-8").write(s.replace(a,b,1))
for chave,(est,tit,nome,antigo,desc) in V.items():
    if chave not in sys.argv[2:]: continue
    ver=chave.split(":")[0]; raiz_nome=f"Gamma-{nome}-v{ver}" if ":" in chave else f"Gamma-v{ver}"
    R=f"{OUT}/{raiz_nome}"; shutil.rmtree(R,ignore_errors=True)
    shutil.copytree(f"{SRC}/pacote",R,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    os.rename(f"{R}/README.md",f"{R}/README-pacote.md")
    open(f"{R}/sensors/matrixgreenpro/versao.py","w",encoding="utf-8").write(f'# MATRIX GREEN PRO | versao.py | versão {ver} | {time.strftime("%d/%m/%Y %H:%M")} (-03) | gerado pelo construtor dos ZIPs\nVERSAO = "{ver}"\n')
    E=f"{R}/sensors/matrixgreenpro/estilos"; mod=est.replace("-","_")
    for f in os.listdir(E):
        if f.endswith(".py") and f not in KEEP and f!=f"reator_{mod}.py": os.remove(f"{E}/{f}")
    if est!="gamma-gamma": os.remove(f"{E}/reator_grupos.py")
    s=open(f"{E}/__init__.py",encoding="utf-8").read()
    i=s.index("ESTILOS = {"); j=s.index("def renderer")
    s=s[:i]+f'''ESTILOS = {{
    "matrix": ("MATRIX GREEN PRO", None),                         # desenho básico (render.py), usado como reserva
    "gamma": ("GAMMA", "reator_gamma"),                           # estilo base GAMMA
    "{est}": ("{tit}", "reator_{mod}"),
}}
ALIASES = {{"uranio": "gamma", "urânio": "gamma"{"".join(f", {chr(34)}{a}{chr(34)}: {chr(34)}{est}{chr(34)}" for a in antigo)}}}   # nomes antigos continuam valendo


'''+s[j:]
    s=re.sub(r"# histórico: 3\..*\n","",s); s=s.replace("GAMMA SENTINELA e GAMMA DOSÍMETRO",tit).replace("versão 1.0.0",f"versão {ver}")
    open(f"{E}/__init__.py","w",encoding="utf-8").write(s)
    T=f"{R}/tools"
    p=f"{T}/mgp_selftest.py"; s=open(p,encoding="utf-8").read()
    s=re.sub(r'for nome in \("matrix", "gamma".*?"pcb"\):',f'for nome in ("matrix", "gamma", "{est}"):',s,flags=re.S)
    cond=" and ".join(f'renderer("{a}")[0] == "{est}"' for a in antigo)
    s=re.sub(r'    check\("apelidos antigos abrem os novos estilos".*?(?=\n    key, _ = renderer)',f'    check("apelidos antigos abrem o estilo atual", {cond})',s,flags=re.S)
    s=s.replace('os.environ["MGP_ESTILO"] = "pcb"',f'os.environ["MGP_ESTILO"] = "{est}"').replace('eng2.estilo == "pcb"',f'eng2.estilo == "{est}"').replace("motor real com estilo pcb",f"motor real com estilo {est}")
    open(p,"w",encoding="utf-8").write(s)
    sub(f"{T}/mgp_preview.py",'}[key]\n','}.get(key, key)\n')
    p=f"{T}/mgp_preview.py"; s=open(p,encoding="utf-8").read()
    s=re.sub(r'    rows = \[\("MatrixGreenPro", "MATRIX GREEN PRO"\).*?"13-C PLACA DE CIRCUITO"\)\]\n',
             f'    rows = [("MatrixGreenPro", "MATRIX GREEN PRO"), ("MatrixGreenPro-Gamma", "GAMMA"), ("MatrixGreenPro-Gamma{nome}", "{tit}")]\n',s,flags=re.S)
    s=s.replace("6 estilos x 3 estados","estilos x 3 estados"); open(p,"w",encoding="utf-8").write(s)
    # raiz
    shutil.copy(f"{SRC}/instalar-gamma.sh",R); os.chmod(f"{R}/instalar-gamma.sh",0o755)
    open(f"{R}/VERSION","w").write(ver+"\n"); open(f"{R}/ESTILO_PADRAO","w").write(est+"\n")
    open(f"{R}/LEIA-ME.md","w",encoding="utf-8").write(f"""<!-- LEIA-ME | GAMMA v{ver} | {time.strftime('%d/%m/%Y %H:%M')} (-03) | criação original (Claude, para Lucas Tavares) -->
# GAMMA v{ver}

Tema para a tela TURZX/Turing TUS-35 de 3,5" no Debian 13 ({tit}): {desc}.

## Instalar (um comando)

```bash
unzip {raiz_nome}.zip && cd {raiz_nome} && ./instalar-gamma.sh
```

O script instala as dependências, configura o grupo dialout, baixa o turing-smart-screen, cria o serviço systemd e instala o tema.
Se a imagem estiver de ponta-cabeça: `./instalar-gamma.sh --invertido`. Para voltar ao tema anterior: `./instalar-gamma.sh --restaurar`.

Detalhes técnicos: `README-pacote.md`.

Autoria: criação original de Claude para Lucas Tavares. Fontes JetBrains Mono e Roboto (OFL). Base: turing-smart-screen-python (GPL-3.0).
""")
    ENT=[("1.6.0","07/11/2026 14:20","Selo no canto superior direito da tela com o estilo (ALPHA, BETA ou GAMMA) e a versão do pacote, por exemplo BETA v1.6.0. A versão vem do arquivo VERSION do lançamento."),
         ("1.5.0","07/11/2026 14:30","Leitura das 4 baias do TerraMaster (DAS USB): por baia, capacidade e estado (montado, desmontado ou livre); GAMMA BETA mostra 2x2 no rodapé e GAMMA GAMMA ganha o grupo TERRAMASTER. Títulos de grupo do GAMMA GAMMA passam a levar dados-chave (LOAD, FPS e FAN, TEMP da RAM, PING). Ferramenta tools/mgp_baias.py para conferir a numeração."),
         ("1.4.0","02/11/2026 22:50","Nomes ALPHA (ex SENTINELA), BETA (ex DOSÍMETRO) e GAMMA (novo: 7 colmeias de resumo com CORE no centro e painel numérico por grupo). Temperatura de cada disco (HDD pelo módulo drivetemp, NVMe direto) com limites e alerta; o instalador carrega o drivetemp. Instalador com --versao alpha, beta ou gamma (nomes antigos continuam valendo)."),
         ("1.3.0","02/11/2026 21:50","Temperaturas de PLACA, RAM e SSD nas células (no lugar de LOAD, TOT W e COLETA, que já aparecem nas linhas); RAM e SSD com limites e alerta. GAMMA SENTINELA ganha a bomba e as ventoinhas."),
         ("1.2.1","02/11/2026 21:38","Removido o RPM da GPU (o driver NVIDIA só informa o percentual); a linha mostra FAN com o percentual."),
         ("1.2.0","02/11/2026 21:30","BOMBA e ventoinhas (RPM): célula BOMBA, linha RAD/INF/LAT/TRA, alerta de bomba parada, mapeador de ventoinhas e driver nct6775 automático (GAMMA DOSÍMETRO)."),
         ("1.1.0","02/11/2026 19:20","GAMMA DOSÍMETRO: percentuais entre parênteses e LIM, DISP e LIVRE junto do uso."),
         ("1.0.0","02/11/2026 19:15","Primeira versão: GAMMA SENTINELA e instalador automático.")]
    vt=lambda x: tuple(int(n) for n in x.split("."))
    cl="# Histórico de versões (SemVer: MAJOR.MINOR.PATCH)\n\n"+"".join(f"## [{v}] - {d} (-03)\n\n- {t}\n\n" for v,d,t in ENT if vt(v)<=vt(ver))
    open(f"{R}/CHANGELOG.md","w",encoding="utf-8").write(cl)

    zp=f"{OUT}/{raiz_nome}.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        for root,_,fs in os.walk(R):
            for f in sorted(fs):
                p=os.path.join(root,f); zi=zipfile.ZipInfo.from_file(p, os.path.relpath(p,OUT))
                zi.compress_type=zipfile.ZIP_DEFLATED
                zi.external_attr=((0o755 if os.access(p,os.X_OK) else 0o644)|stat.S_IFREG)<<16
                z.writestr(zi, open(p,"rb").read())
    print(time.strftime("[%d/%m/%Y %H:%M:%S]"), "ZIP gerado:", zp)
