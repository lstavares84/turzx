# GAMMA | construir/matriz_previas.py | versão 1.1.0 | 07/11/2026 18:40 (-03) | criação original (Claude, para Lucas Tavares)
# histórico: 1.3.0 07/11/2026 20:25 opção --deltas: as 6 variantes do GAMMA DELTA
# histórico: 1.2.0 07/11/2026 20:00 opção --v2: as 12 propostas da v2.0.0 no lugar das colunas normais
# histórico: 1.1.0 07/11/2026 18:40 opção --extra para variantes de estudo em colunas a mais
# Matriz de prévias: as 3 versões (ALPHA, BETA, GAMMA) nos 3 estados (normal, atenção, crítico), num único PNG.
# Desenha com o código ATUAL de pacote/ (não com o que está instalado) e os dados de demonstração do painel.
# Uso, na raiz do repositório:
#   python3 -I construir/matriz_previas.py SAIDA.png [pasta_do_turing] [--extra delta] [--extra coluna]
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
           ("gamma-gamma", "reator_gamma_gamma", "GAMMA", "7 colmeias e painel por grupo")]
EXTRAS = {"delta": ("gamma-delta", "reator_gamma_delta", "DELTA", "gráficos de 24 h, baias com uso"),
          "coluna": ("gamma-gamma-coluna", "reator_gamma_gamma_coluna", "COLUNA", "estudo: hexágonos em coluna")}
DELTAS = [("gamma-delta-1", "reator_gamma_delta_v1", "DELTA 1", "variante 1"), ("gamma-delta-2", "reator_gamma_delta_v2", "DELTA 2", "variante 2"), ("gamma-delta-3", "reator_gamma_delta_v3", "DELTA 3", "variante 3"), ("gamma-delta-4", "reator_gamma_delta_v4", "DELTA 4", "variante 4"), ("gamma-delta-5", "reator_gamma_delta_v5", "DELTA 5", "variante 5"), ("gamma-delta-6", "reator_gamma_delta_v6", "DELTA 6", "variante 6")]
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
    from library.sensors.matrixgreenpro.estilos.base import W, H
    erros = []
    for n, (x0, y0, x1, y1) in c.texts:
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
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
        if a == "--deltas":
            COLUNAS[:] = []
            extras.extend(DELTAS)
        elif a == "--v2":
            COLUNAS[:] = []
            extras.extend(V2)
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

        quadros, erros = {}, 0
        for chave, mod, rotulo, _ in COLUNAS:
            draw = importlib.import_module(f"library.sensors.matrixgreenpro.estilos.{mod}").draw_frame
            for cen, _, _ in LINHAS:
                vm = ViewModel(copy.deepcopy(DEFAULTS), (80, 90), (80, 87)).build(panel.demo_snapshot(cen))
                vm["blink"] = True
                c, v = draw(vm)
                assert c.img.size == (320, 480)
                quadros[(chave, cen)] = c.img
                n = conferir(c, v, f"{rotulo}-{cen}", REQUIRED)
                erros += n
                log(f"{rotulo:<5} {cen:<8} {len(c.texts)} elementos, {n} problema(s)")

        fr = Path(tmp) / "res" / "fonts" / "jetbrains-mono"
        f = lambda t, w: ImageFont.truetype(str(fr / f"JetBrainsMonoNL-{w}.ttf"), t)
        esq, topo, gx, gy, cab = 132, 96, 24, 24, 26
        nc = len(COLUNAS)
        L = esq + nc * 322 + (nc - 1) * gx + 22
        A = topo + 3 * (cab + 482) + 2 * gy + 60
        m = Image.new("RGB", (L, A), (10, 16, 12))
        d = ImageDraw.Draw(m)
        d.text((24, 14), f"GAMMA TUS-35 | v{versao} | todas as versões nos 3 estados" + (" + estudo" if extras else ""), font=f(26, "Bold"), fill=(110, 255, 110))
        d.text((24, 50), f"{ts()} | código {ref} | dados de demonstração do painel", font=f(14, "Regular"), fill=(150, 170, 150))
        for k, (chave, _, rotulo, desc) in enumerate(COLUNAS):
            x = esq + k * (322 + gx)
            d.text((x, topo - 26), rotulo, font=f(18, "Bold"), fill=(235, 245, 235))
            d.text((x, topo - 4), desc, font=f(12, "Regular"), fill=(130, 150, 130))
            for r, (cen, lab, cor) in enumerate(LINHAS):
                y = topo + cab + r * (cab + 482 + gy)
                d.rectangle((x, y, x + 321, y + 481), outline=(40, 70, 45))
                m.paste(quadros[(chave, cen)], (x + 1, y + 1))
                if k == 0:
                    d.text((24, y + 230), lab, font=f(18, "Bold"), fill=cor)
        d.text((24, A - 44), f"Problemas de layout (limites, sobreposição, glifos, métricas): {erros}.", font=f(13, "Bold"),
               fill=(110, 255, 110) if not erros else (255, 80, 70))
        d.text((24, A - 24), "Criação original (Claude, para Lucas Tavares). Quadros 320x480 desenhados pelos próprios estilos; "
               "não são fotos da tela física.", font=f(12, "Regular"), fill=(130, 150, 130))
        saida.parent.mkdir(parents=True, exist_ok=True)
        m.save(saida)
        log(f"matriz gravada: {saida} ({L}x{A}), {erros} problema(s) de layout")
        return 1 if erros else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
