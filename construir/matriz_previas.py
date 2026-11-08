# GAMMA | construir/matriz_previas.py | versão 1.6.0 | 08/11/2026 13:22 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.6.0 08/11/2026 13:22 opção --tela 3.5 ou 5.2 (a 5,2" aparece reduzida à metade)
# histórico: 1.5.0 07/11/2026 22:20 o DELTA entra nas colunas padrão (4 x 3); sai o --extra delta
# histórico: 1.4.0 07/11/2026 20:35 opção --delta5: o DELTA 5 e as variantes 5A, 5B e 5C
# histórico: 1.3.0 07/11/2026 20:25 opção --deltas: as 6 variantes do GAMMA DELTA
# histórico: 1.2.0 07/11/2026 20:00 opção --v2: as 12 propostas da v2.0.0 no lugar das colunas normais
# histórico: 1.1.0 07/11/2026 18:40 opção --extra para variantes de estudo em colunas a mais
# Matriz de prévias: as 4 versões (ALPHA, BETA, GAMMA, DELTA) nos 3 estados (normal, atenção, crítico), num único PNG.
# Desenha com o código ATUAL de pacote/ (não com o que está instalado) e os dados de demonstração do painel.
# Uso, na raiz do repositório:
#   python3 -I construir/matriz_previas.py SAIDA.png [pasta_do_turing] [--extra coluna] [--tela 3.5|5.2]
# --tela: qual tela desenhar (padrão 3.5). A 5,2" (720x1280) entra na matriz reduzida à metade (360x640).
# --extra NOME (repetível): acrescenta uma variante de estudo como coluna a mais (veja EXTRAS).
# pasta_do_turing: cópia do turing-smart-screen, só para as fontes em res/fonts (padrão: ~/turing-smart-screen-linux).
# Requer Pillow e psutil. Também confere limites, sobreposições, glifos e cobertura de métricas de cada quadro.
import copy, importlib, itertools, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
os.environ.setdefault("TZ", "America/Sao_Paulo")     # horário de Brasília nos logs, no título e no relógio dos quadros
time.tzset()
COLUNAS = [("gamma-alpha", "reator_gamma_alpha", "ALPHA", "escala N0/N1/N2, percentuais"),
           ("gamma-beta", "reator_gamma_beta", "BETA", "percentuais entre parênteses, baias"),
           ("gamma-gamma", "reator_gamma_gamma", "GAMMA", "7 colmeias e painel por grupo"),
           ("gamma-delta", "reator_gamma_delta", "DELTA", "gráficos de 24 h, alertas e LOG")]
EXTRAS = {"epsilon": ("gamma-epsilon", "reator_gamma_epsilon", "EPSILON", "protótipo: colmeias por grupo"),
                    "coluna": ("gamma-gamma-coluna", "reator_gamma_gamma_coluna", "COLUNA", "estudo: hexágonos em coluna")}
DELTAS = [("gamma-delta-1", "reator_gamma_delta_v1", "DELTA 1", "variante 1"), ("gamma-delta-2", "reator_gamma_delta_v2", "DELTA 2", "variante 2"), ("gamma-delta-3", "reator_gamma_delta_v3", "DELTA 3", "variante 3"), ("gamma-delta-4", "reator_gamma_delta_v4", "DELTA 4", "variante 4"), ("gamma-delta-5", "reator_gamma_delta_v5", "DELTA 5", "variante 5"), ("gamma-delta-6", "reator_gamma_delta_v6", "DELTA 6", "variante 6")]
DELTA5 = [("gamma-delta-5", "reator_gamma_delta_v5", "DELTA 5", "base"), ("gamma-delta-5a", "reator_gamma_delta_v5a", "DELTA 5A", "barra por disco"), ("gamma-delta", "reator_gamma_delta", "DELTA", "o oficial (ex 5B)"), ("gamma-delta-5c", "reator_gamma_delta_v5c", "DELTA 5C", "mapa de capacidade")]
V2 = [("v2-concreto", "v2_brutal", "BRUTALISTA", "concreto"),
      ("v2-silencio", "v2_minimal", "MINIMALISTA", "silêncio"),
      ("v2-hud", "v2_scifi", "SCI-FI", "hud orbital"),
      ("v2-root", "v2_hacking", "HACKING", "root"),
      ("v2-dossie", "v2_espiao", "ESPIONAGEM", "dossiê"),
      ("v2-vital", "v2_uti", "UTI", "monitor vital"),
      ("v2-cockpit", "v2_cockpit", "COCKPIT", "painel de voo"),
      ("v2-metro", "v2_metro", "METRÔ", "linha gamma"),
      ("v2-anunciador", "v2_anunciador", "SALA DE CONTROLE", "anunciador"),
      ("v2-8bits", "v2_arcade", "ARCADE", "8 bits"),
      ("v2-osciloscopio", "v2_osciloscopio", "LABORATÓRIO", "osciloscópio"),
      ("v2-grade", "v2_suico", "SUÍÇO", "grade")]
LINHAS = [("normal", "NORMAL", (110, 255, 110)), ("atencao", "ATENÇÃO", (255, 190, 40)), ("critico", "CRÍTICO", (255, 80, 70))]


def ts():
    return time.strftime("%d/%m/%Y %H:%M:%S")


def log(msg):
    print(f"[{ts()}] {msg}")


def montar_arvore(turing, versao):
    """Árvore mínima library/sensors/matrixgreenpro + res/ (fontes do Turing), numa pasta temporária."""
    tmp = Path(tempfile.mkdtemp(prefix="gamma-matriz-"))
    sens = tmp / "library" / "sensors"
    sens.mkdir(parents=True)
    (tmp / "library" / "__init__.py").write_text("")
    (sens / "__init__.py").write_text("")
    shutil.copytree(RAIZ / "pacote" / "sensors" / "matrixgreenpro", sens / "matrixgreenpro",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (sens / "matrixgreenpro" / "versao.py").write_text(f'VERSAO = "{versao}"\n', encoding="utf-8")
    os.symlink(Path(turing).resolve() / "res", tmp / "res")
    return tmp


def conferir(c, v, nome, required):
    from library.sensors.matrixgreenpro.estilos.base import W, HL
    erros = []
    for n, (x0, y0, x1, y1) in c.texts:
        if x0 < 0 or y0 < 0 or x1 > W or y1 > HL + 0.5:
            erros.append(f"{n} fora da tela")
    textos = [(n, b) for n, b in c.texts if not n.endswith(("bar", "band")) and not n.startswith("sep")]
    for (na, a), (nb, b) in itertools.combinations(textos, 2):
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            erros.append(f"sobreposição: {na} x {nb}")
    erros += [f"glifo ausente em {n}: {m!r}" for n, m, _ in c.glyph_issues]
    falta = required - v.used
    if falta:
        erros.append(f"métricas omitidas: {sorted(falta)}")
    for e in erros:
        log(f"[{nome}] ERRO {e}")
    return len(erros)


def main():
    if len(sys.argv) < 2:
        sys.exit(f"[{ts()}] uso: python3 -I construir/matriz_previas.py SAIDA.png [pasta_do_turing]")
    args, extras = [], []
    it = iter(sys.argv[1:])
    for a in it:
        if a == "--delta5":
            COLUNAS[:] = []
            extras.extend(DELTA5)
        elif a == "--deltas":
            COLUNAS[:] = []
            extras.extend(DELTAS)
        elif a == "--v2":
            COLUNAS[:] = []
            extras.extend(V2)
        elif a == "--tela":
            tela = next(it, "")
            if tela not in ("3.5", "5.2"):
                sys.exit(f"[{ts()}] ERRO --tela aceita: 3.5 ou 5.2")
            os.environ["MGP_TELA"] = tela
        elif a == "--extra":
            nome = next(it, "")
            if nome not in EXTRAS:
                sys.exit(f"[{ts()}] ERRO --extra aceita: {', '.join(EXTRAS)}")
            extras.append(EXTRAS[nome])
        else:
            args.append(a)
    COLUNAS[:] = COLUNAS + extras
    saida = Path(args[0]).resolve()
    turing = Path(args[1] if len(args) > 1 else Path.home() / "turing-smart-screen-linux")
    if not (turing / "res" / "fonts").is_dir():
        sys.exit(f"[{ts()}] ERRO fontes não encontradas em {turing}/res/fonts")
    versao = (RAIZ / "VERSION").read_text().strip()
    try:
        commit = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
        sujo = subprocess.run(["git", "-C", str(RAIZ), "status", "--porcelain", "pacote"], capture_output=True, text=True).stdout.strip()
    except OSError:
        commit, sujo = "", ""
    ref = (commit or "sem git") + (" + alterações locais" if sujo else "")

    tmp = montar_arvore(turing, versao)
    sys.path.insert(0, str(tmp))
    try:
        from PIL import Image, ImageDraw, ImageFont
        from library.sensors.matrixgreenpro import panel
        from library.sensors.matrixgreenpro.viewmodel import ViewModel
        from library.sensors.matrixgreenpro.settings import DEFAULTS
        from library.sensors.matrixgreenpro.estilos.base import REQUIRED
        from library.sensors.matrixgreenpro.tela import TELA, LARGURA, ALTURA
        red = 2 if TELA == "5.2" else 1                       # a 5,2" entra reduzida à metade
        FW, FH = LARGURA // red, ALTURA // red

        quadros, erros = {}, 0
        for chave, mod, rotulo, _ in COLUNAS:
            m_est = importlib.import_module(f"library.sensors.matrixgreenpro.estilos.{mod}")
            for cen, _, _ in LINHAS:
                vm = ViewModel(copy.deepcopy(DEFAULTS), (80, 90), (80, 87)).build(panel.demo_snapshot(cen))
                vm["blink"] = True
                c, v = m_est.draw_frame(vm)                   # o mesmo desenho nas duas telas
                assert c.img.size == (LARGURA, ALTURA)
                quadros[(chave, cen)] = c.img if red == 1 else c.img.resize((FW, FH), Image.LANCZOS)
                n = conferir(c, v, f"{rotulo}-{cen}", REQUIRED)
                erros += n
                log(f"{rotulo:<5} {cen:<8} {len(c.texts)} elementos, {n} problema(s)")

        fr = Path(tmp) / "res" / "fonts" / "jetbrains-mono"
        f = lambda t, w: ImageFont.truetype(str(fr / f"JetBrainsMonoNL-{w}.ttf"), t)
        esq, topo, gx, gy, cab = 132, 96, 24, 24, 26
        nc = len(COLUNAS)
        L = esq + nc * (FW + 2) + (nc - 1) * gx + 22
        A = topo + 3 * (cab + FH + 2) + 2 * gy + 60
        m = Image.new("RGB", (L, A), (10, 16, 12))
        d = ImageDraw.Draw(m)
        d.text((24, 14), f"GAMMA | tela de {TELA.replace('.', ',')}\" ({LARGURA}x{ALTURA}) | v{versao} | todas as versões nos 3 estados"
               + (" + estudo" if extras else ""), font=f(26, "Bold"), fill=(110, 255, 110))
        d.text((24, 50), f"{ts()} | código {ref} | dados de demonstração do painel", font=f(14, "Regular"), fill=(150, 170, 150))
        for k, (chave, _, rotulo, desc) in enumerate(COLUNAS):
            x = esq + k * (FW + 2 + gx)
            d.text((x, topo - 26), rotulo, font=f(18, "Bold"), fill=(235, 245, 235))
            d.text((x, topo - 4), desc, font=f(12, "Regular"), fill=(130, 150, 130))
            for r, (cen, lab, cor) in enumerate(LINHAS):
                y = topo + cab + r * (cab + FH + 2 + gy)
                d.rectangle((x, y, x + FW + 1, y + FH + 1), outline=(40, 70, 45))
                m.paste(quadros[(chave, cen)], (x + 1, y + 1))
                if k == 0:
                    d.text((24, y + FH // 2 - 10), lab, font=f(18, "Bold"), fill=cor)
        d.text((24, A - 44), f"Problemas de layout (limites, sobreposição, glifos, métricas): {erros}.", font=f(13, "Bold"),
               fill=(110, 255, 110) if not erros else (255, 80, 70))
        d.text((24, A - 24), f"Criação original (Claude, para Lucas Tavares). Quadros {LARGURA}x{ALTURA} desenhados pelos próprios estilos"
               + (", reduzidos à metade" if red > 1 else "") + "; não são fotos da tela física.", font=f(12, "Regular"), fill=(130, 150, 130))
        saida.parent.mkdir(parents=True, exist_ok=True)
        m.save(saida)
        log(f"matriz gravada: {saida} ({L}x{A}), {erros} problema(s) de layout")
        return 1 if erros else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
