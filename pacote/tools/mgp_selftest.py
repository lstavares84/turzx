#!/usr/bin/env python3
# MATRIX GREEN PRO | versão 3.2.0 | 07/11/2026 18:40 (-03) | testes dos estilos selecionáveis (Claude, para Lucas Tavares)
# histórico: 3.2.0 07/11/2026 18:40 estilo de estudo gamma-gamma-coluna na lista de estilos
# histórico: 3.1.1 07/11/2026 18:15 teste de baias invertidas isolado das montagens reais do PC; 2.1.0 31/10/2026 23:55 testes de rede x internet e do estado da coleta
# histórico: 2.0.0 31/10/2026 23:45 criação: testes de cenários e de coletores
# Testes automáticos SEM hardware (rodam em qualquer Debian e no instalador).
# Uso: .venv/bin/python3 tools/mgp_selftest.py
import copy
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from library.sensors.matrixgreenpro import panel, render, collectors as col  # noqa: E402
from library.sensors.matrixgreenpro.alerts import OK, WARN, CRIT, NA, LOST, NEUTRAL, Hyst  # noqa: E402
from library.sensors.matrixgreenpro.settings import DEFAULTS  # noqa: E402
from library.sensors.matrixgreenpro.viewmodel import ViewModel  # noqa: E402

RESULTS = []


def ts():
    return time.strftime("[%d/%m/%Y %H:%M:%S]")


def check(name, cond, detail=""):
    RESULTS.append(cond)
    print(f"{ts()} {'OK   ' if cond else 'FALHA'} {name}{(' :: ' + detail) if detail and not cond else ''}")


def vm_of(snap, cfg=None):
    v = ViewModel(cfg or copy.deepcopy(DEFAULTS), (80, 90), (80, 87)).build(snap)
    img, el = render.draw_frame(v)
    assert img.size == (320, 480)
    return v


def base():
    return panel.demo_snapshot("normal")


def main():
    # ---- estado normal
    v = vm_of(base())
    check("normal: cabeçalho SISTEMA OK", v["hdr_status"][0] == "● SISTEMA OK", v["hdr_status"][0])

    # ---- CPU e GPU a 100% não são alerta
    s = base(); s["cpu"]["util"] = 100; s["gpu"]["util"] = 100
    check("utilização 100% não gera alerta", vm_of(s)["hdr_status"][1] == OK)

    # ---- GPU sem dados de ventoinha / só percentual
    s = base(); s["gpu"]["fan_rpm"] = None; s["gpu"]["fan_pct"] = None
    v = vm_of(s)
    check("GPU sem ventoinha: N/D neutro", v["gpu_fan_pct"] == ("N/D", NA) and v["gpu_fan_rpm"][1] == NA)
    s = base(); s["gpu"]["fan_rpm"] = None
    v = vm_of(s)
    check("GPU só percentual: 'RPM -' sem estimativa", v["gpu_fan_rpm"][0] == "RPM -" and v["gpu_fan_pct"][0] == "68%")

    # ---- ventoinha parada
    s = base(); s["cpu"].pop("cool", None); s["cpu"]["fan"] = 0; s["cpu"]["temp"] = 45
    check("CPU 0 RPM fria = semipassivo (OK)", vm_of(s)["cpu_fan"][1] == OK)
    s = base(); s["cpu"].pop("cool", None); s["cpu"]["fan"] = 0; s["cpu"]["temp"] = 85
    check("CPU 0 RPM quente = CRÍTICO", vm_of(s)["cpu_fan"][1] == CRIT)

    # ---- bomba e ventoinhas por papel (water cooler)
    s = base(); v = vm_of(s)
    check("bomba girando = OK e radiador vira o cpu_fan", v["pump"] == ("5600RPM", OK) and v["cpu_fan"][0] == "1240RPM")
    s = base(); s["cpu"]["cool"]["bomba"] = {"rpm": 0, "visto": True}
    v = vm_of(s)
    check("bomba que girava e parou = CRÍTICO (conta no cabeçalho)", v["pump"][1] == CRIT and "CRÍTIC" in v["hdr_status"][0])
    s = base(); s["cpu"]["cool"]["sq_inf"] = {"rpm": 0, "visto": False}
    v = vm_of(s)
    check("entrada que nunca girou = 0RPM neutro, sem alarme", v["fan_sqi"] == ("0RPM", NA) and v["hdr_status"][1] == OK)
    s = base(); s["cpu"]["cool"]["sq_lat"] = {"rpm": None, "visto": True}
    check("entrada que sumiu = perdida (LOST), não é saúde", vm_of(s)["fan_sql"][1] == LOST)
    s = base(); s["cpu"]["cool"]["sq_tras"] = {"rpm": 0, "visto": True}; s["cpu"]["temp"] = 45
    check("ventoinha do gabinete a 0 RPM fria = semipassivo (OK)", vm_of(s)["fan_sqt"][1] == OK)
    s = base(); s["cpu"]["cool"]["sq_tras"] = {"rpm": 0, "visto": True}; s["cpu"]["temp"] = 85
    check("ventoinha do gabinete a 0 RPM quente = CRÍTICO", vm_of(s)["fan_sqt"][1] == CRIT)
    # ---- temperaturas de placa, RAM e SSD
    v = vm_of(base())
    check("temperaturas: placa informativa e RAM e SSD normais", v["t_placa"] == ("34°C", NEUTRAL) and v["t_ram"][1] == OK and v["t_ssd"][1] == OK)
    s = base(); s["cpu"]["temps"]["ram"]["c"] = 56
    check("RAM a 56 °C = CRÍTICO (conta no cabeçalho)", vm_of(s)["t_ram"][1] == CRIT and "CRÍTIC" in vm_of(s)["hdr_status"][0])
    s = base(); s["cpu"]["temps"]["ssd"]["c"] = 72
    check("SSD a 72 °C = AVISO", vm_of(s)["t_ssd"][1] == WARN)
    s = base(); s["cpu"]["temps"]["placa"]["c"] = 90
    check("placa quente não gera alerta (sem limite conhecido)", vm_of(s)["t_placa"][1] == NEUTRAL and vm_of(s)["hdr_status"][1] == OK)
    s = base(); s["cpu"]["temps"]["ssd"] = {"c": None, "visto": True}
    check("SSD que sumiu = perdido (LOST), não é saúde", vm_of(s)["t_ssd"][1] == LOST and vm_of(s)["hdr_status"][1] == OK)
    s = base(); s["cpu"].pop("temps")
    check("sem mapa de temperaturas: N/D", vm_of(s)["t_ram"] == ("N/D", NA))

    s = base(); s["cpu"].pop("cool")
    v = vm_of(s)
    check("sem mapa de ventoinhas: bomba N/D e cpu_fan antigo", v["pump"] == ("N/D", NA) and v["cpu_fan"][0] == "1240RPM")

    # ---- FPS indisponível
    s = base(); s["fps"] = None
    check("FPS indisponível = N/D e não conta", vm_of(s)["fps"] == ("N/D", NA) and vm_of(s)["hdr_status"][1] == OK)

    # ---- RAM elevada
    s = base(); s["ram"] = {"used": 29.9, "avail": 1.4, "total": 31.3, "pct": 95.5}
    check("RAM 95,5% = CRÍTICO", vm_of(s)["ram_used"][1] == CRIT)

    # ---- disco cheio / pouco espaço absoluto / desmontado
    s = base(); s["disks"][2].update(used=3990e9, free=10e9, pct=99.7)
    check("disco cheio = CRÍTICO", vm_of(s)["disks"][2]["lvl"] == CRIT)
    s = base(); s["disks"][0].update(used=960e9, free=40e9, pct=96.0 - 20)
    check("disco com < 50 GB livres = ATENÇÃO", vm_of(s)["disks"][0]["lvl"] == WARN)
    s = base(); s["disks"][1] = {"nome": "2T", "state": "OFF"}
    v = vm_of(s)
    check("disco desmontado = OFF amarelo, sem valores antigos",
          v["disks"][1]["use"] == "DESMONTADO" and v["disks"][1]["pct"] is None and v["disks"][1]["lvl"] == WARN)

    # ---- temperatura por disco (HDD tem limites próprios; sem leitura não alerta)
    s = base(); s["disks"][2].update(temp=57.0, hdd=True)
    check("HDD a 57 °C = CRÍTICO", vm_of(s)["disks"][2]["temp_lvl"] == CRIT)
    s = base(); s["disks"][1].update(temp=52.0, hdd=True)
    check("HDD a 52 °C = ATENÇÃO", vm_of(s)["disks"][1]["temp_lvl"] == WARN)
    s = base(); s["disks"][0].update(temp=57.0, hdd=False)
    check("SSD a 57 °C = OK (limites de SSD)", vm_of(s)["disks"][0]["temp_lvl"] == OK)
    s = base(); s["disks"][1].pop("temp", None)
    v = vm_of(s)
    check("disco sem leitura de temperatura = N/D e não alerta",
          v["disks"][1]["temp_txt"] == "N/D" and v["hdr_status"][1] == OK)
    C = col
    with tempfile.TemporaryDirectory() as td:        # sysfs falso: disco sdb com sensor drivetemp
        os.makedirs(f"{td}/class/block/sdb/device/hwmon/hwmon7")
        os.makedirs(f"{td}/class/block/sdb1")
        os.makedirs(f"{td}/devices/pci/sdb/sdb1", exist_ok=True)
        open(f"{td}/class/block/sdb/device/hwmon/hwmon7/temp1_input", "w").write("33000\n")
        open(f"{td}/class/block/sdb1/partition", "w").write("1\n")
        check("sysfs falso: temperatura do disco lida do drivetemp", C._temp_bloco("sdb", td) == 33.0)
        check("sysfs falso: disco sem sensor devolve None", C._temp_bloco("sdc", td) is None)

    # ---- baias do gabinete USB (TerraMaster): sysfs falso com hub 4-2 e 4 pontes ASMedia
    with tempfile.TemporaryDirectory() as td:
        def w(rel, txt):
            os.makedirs(os.path.dirname(f"{td}/{rel}"), exist_ok=True)
            open(f"{td}/{rel}", "w").write(txt)
        w("bus/usb/devices/4-2/idVendor", "0bda\n"); w("bus/usb/devices/4-2/idProduct", "0423\n")
        for n in (1, 2, 3, 4):
            d = f"bus/usb/devices/4-2.{n}"
            w(f"{d}/idVendor", "174c\n"); w(f"{d}/idProduct", "235c\n")
        for n, bloco, setores, mod in ((1, "sdc", 23437770752, "WD120EFGX-68CPHN0"), (2, "sdd", 976773168, "MK5076GSX"),
                                      (3, "sde", 15628053168, "ST8000DM004-2U9188")):
            w(f"bus/usb/devices/4-2.{n}/4-2.{n}:1.0/host6/target6:0:0/6:0:0:0/block/{bloco}/x", "")
            w(f"block/{bloco}/size", f"{setores}\n"); w(f"block/{bloco}/device/model", mod + "\n")
        import types
        ant = col.psutil.disk_partitions
        col.psutil.disk_partitions = lambda all=False: [types.SimpleNamespace(device="/dev/sdc1", mountpoint="/mnt/12TB")]
        try:
            bs = col.Baias({"terramaster": {"ativo": "auto"}}, td).leitura()
            bi = col.Baias({"terramaster": {"ativo": "auto", "inverter": True}}, td).leitura()
        finally:
            col.psutil.disk_partitions = ant
        check("baias: 4 baias lidas do hub", bs is not None and [b["n"] for b in bs] == [1, 2, 3, 4], str(bs))
        check("baias: montada, desmontada, desmontada e livre",
              [b["estado"] for b in bs] == ["MONT", "DESM", "DESM", "LIVRE"], str([b["estado"] for b in bs]))
        check("baias: capacidade lida (12 TB na baia 1)", abs(bs[0]["bytes"] - 12e12) < 0.01e12, str(bs[0]["bytes"]))
        check("baias: inverter troca a numeração", bi[3]["estado"] == "MONT" and bi[0]["estado"] == "LIVRE",
              str([b["estado"] for b in bi]))
        check("baias: sem gabinete devolve None", col.Baias({}, td + "/nada").leitura() is None)
    vb = vm_of(base())["baias"]
    check("baias: viewmodel com 4 baias, sem alerta",
          len(vb) == 4 and vb[0]["cap"] == "12TB" and vb[3]["palavra"] == "LIVRE" and vm_of(base())["hdr_status"][1] == OK, str(vb[:1]))
    s2 = base(); s2["baias"] = None
    check("baias: recurso ausente = lista vazia", vm_of(s2)["baias"] == [])

    # ---- selo de estilo e versão no canto superior direito (ALPHA, BETA, GAMMA)
    from library.sensors.matrixgreenpro.estilos import renderer as _rend, ALIASES as _al
    from library.sensors.matrixgreenpro import versao as _ver
    for _est, _nome in (("gamma-alpha", "ALPHA"), ("gamma-beta", "BETA"), ("gamma-gamma", "GAMMA")):
        try:
            _mod = __import__(f"library.sensors.matrixgreenpro.estilos.reator_{_est.replace('-', '_')}", fromlist=["draw_frame"])
        except ImportError:
            continue                                    # pacote enxuto: só o estilo do ZIP
        _c, _v = _mod.draw_frame(vm_of(base()))
        _t = {n for n, _ in _c.texts}
        check(f"{_nome}: selo de estilo e versão no canto superior direito", "hdr.ver" in _t and "hdr.estilo" in _t)

    # ---- Ethernet desconectada / Wi-Fi inexistente
    s = base(); s["net"]["eth"]["up"] = False; s["net"]["wifi"] = {"exists": False}
    s["ping"] = {"ok": False, "ms": None}
    v = vm_of(s)
    check("sem nenhum enlace = 1 CRÍTICO (ping não conta de novo)",
          v["eth"]["state"][1] == CRIT and v["hdr_status"][0] == "● 1 CRÍTICO" and v["inet"][0] == "SEM REDE",
          v["hdr_status"][0])
    s = base(); s["net"]["eth"]["up"] = False
    v = vm_of(s)
    check("Ethernet caída com Wi-Fi ativo = sem alerta (padrão)",
          v["eth"]["state"][1] == NA and v["hdr_status"][0] == "● SISTEMA OK", v["hdr_status"][0])
    cfg = copy.deepcopy(DEFAULTS); cfg["rede"]["ethernet_obrigatoria"] = True
    check("Ethernet obrigatória caída com Wi-Fi ativo = ATENÇÃO", vm_of(s, cfg)["eth"]["state"][1] == WARN)
    s = base(); s["ping"] = {"ok": False, "ms": None}
    v = vm_of(s)
    check("enlace OK e ping falhando = internet avaliada à parte", v["inet"][0] == "INSTÁVEL" and v["ping"][1] == WARN)
    s = base(); s["net"]["wifi"] = {"exists": False}
    v = vm_of(s)
    check("Wi-Fi inexistente = N/D, não conta", v["wifi"]["state"] == ("N/D", NA) and v["hdr_status"][1] == OK)

    # ---- ping
    s = base(); s["ping"] = {"ok": None, "ms": None}
    check("ping indisponível = N/D", vm_of(s)["ping"] == ("N/D", NA))
    vmod = ViewModel(copy.deepcopy(DEFAULTS), (80, 90), (80, 87))
    lv = [vmod.build({**base(), "ping": {"ok": False, "ms": None}})["ping"][1] for _ in range(3)]
    check("ping falhando: amarelo e vermelho após 3 falhas", lv == [WARN, WARN, CRIT], str(lv))

    # ---- clima
    s = base(); s["weather"] = {"state": "ND"}
    check("API de clima indisponível = N/D", vm_of(s)["wtemp"] == ("N/D", NA))
    s = base(); s["weather"] = {"state": "STALE", "temp": 20.0, "desc": "NUBLADO", "ts": time.time() - 4000}
    check("clima desatualizado = aviso", vm_of(s)["wage"][1] == WARN)

    # ---- energia
    check("sem medidor de energia = TOTAL W N/D", vm_of(base())["power"] == ("N/D", NA))
    s = base(); s["power"] = {"state": "OK", "w": 245, "tag": "TOMADA"}
    v = vm_of(s)
    check("medidor na tomada: valor e origem", v["power"][0] == "245" and v["power_tag"][0] == "MEDIDOR TOMADA")
    check("GPU W separado do TOTAL W", v["gpu_w"][0] == "212")

    # ---- estado da coleta (independente da saúde)
    s = base(); s["cpu"]["temp"] = None; s["cpu"]["temp_lost"] = True
    s["coleta"] = {"esperados": 8, "falhas": ["CPU°C"]}
    v = vm_of(s)
    check("sensor perdido = COLETA PARCIAL, saúde não muda",
          v["cpu_temp"][1] == LOST and v["hdr_status"][0] == "● SISTEMA OK" and v["coleta"][0].startswith("COLETA PARCIAL"),
          f'{v["hdr_status"][0]} | {v["coleta"][0]}')
    check("COLETA OK no cenário normal", vm_of(base())["coleta"] == ("COLETA OK", OK))
    s = base(); s["coleta"] = {"esperados": 3, "falhas": ["CPU", "REDE", "PING"]}
    v = vm_of(s)
    check("todas as fontes falharam = COLETA FALHOU e cabeçalho SEM DADOS",
          v["coleta"][0] == "COLETA FALHOU" and v["hdr_status"][0] == "■ SEM DADOS")
    s = base(); s["weather"] = {"state": "STALE", "temp": 20.0, "desc": "NUBLADO", "ts": time.time() - 4000}
    check("clima vencido não é problema de saúde", vm_of(s)["hdr_status"][0] == "● SISTEMA OK")

    # ---- histerese sem oscilação
    h = Hyst(80, 90, 3)
    seq = [h.update(x) for x in (79, 80, 79.5, 78, 77.5, 76.9, 90, 88, 86.9)]
    check("histerese evita piscar", seq == [OK, WARN, WARN, WARN, WARN, OK, CRIT, CRIT, WARN], str(seq))

    # ---- contagem dos cenários demo
    for sc, exp in (("normal", "● SISTEMA OK"), ("atencao", "▲ 5 AVISOS"), ("critico", "● 3 CRÍTICOS ▲1")):
        got = vm_of(panel.demo_snapshot(sc))["hdr_status"][0]
        check(f"cenário {sc}: '{exp}'", got == exp, got)

    # ---- coletores com arquivos simulados
    with tempfile.TemporaryDirectory() as d:
        cfg = copy.deepcopy(DEFAULTS); cfg["fps"]["mangohud_dir"] = d
        f = col.Fps(cfg)
        check("MangoHud ausente = None", f.read() is None)
        p = Path(d) / "jogo_2026-10-31_23-00-00.csv"
        p.write_text("os,cpu,gpu,ram,kernel,driver,cpuscheduler\nDebian,x,y,z,k,d,s\n"
                     "fps,frametime,cpu_load,cpu_power,gpu_load,cpu_temp,gpu_temp,gpu_core_clock,gpu_mem_clock,"
                     "gpu_vram_used,gpu_power,ram_used,swap_used,process_rss,cpu_mhz,elapsed\n"
                     "141.7,7.05,30,60,98,60,66,2655,10501,6.4,212,12.4,0,2.1,4850,1000000000\n")
        check("MangoHud CSV recente = FPS real", abs((f.read() or 0) - 141.7) < 0.01)
        os.utime(p, (time.time() - 30, time.time() - 30))
        check("MangoHud CSV parado (jogo fechado) = None", f.read() is None)
        cfg["discos"] = [{"nome": "X", "uuid": "00000000-dead-beef-0000-000000000000", "montagem": ""},
                         {"nome": "Y", "uuid": "", "montagem": "/caminho/inexistente"},
                         {"nome": "R", "uuid": "", "montagem": "/"}]
        r = col.Disks._read(type("T", (), {"items": cfg["discos"], "_mount_for": staticmethod(col.Disks._mount_for)})())
        check("UUID inexistente = OFF", r[0]["state"] == "OFF")
        check("montagem inexistente = OFF", r[1]["state"] == "OFF")
        check("raiz montada = leitura válida", r[2]["state"] == "OK" and r[2]["total"] > 0)
        pf = Path(d) / "watts"
        pf.write_text("245.5\n")
        cfg["energia"].update(fonte="arquivo", arquivo=str(pf), tipo_arquivo="tomada")
        pw = col.Power(cfg)
        time.sleep(0.3)
        check("energia por arquivo recente", pw._read() == {"w": 245.5, "tag": "TOMADA"})
        os.utime(pf, (time.time() - 60, time.time() - 60))
        check("energia por arquivo antigo = sem valor", pw._read() is None)

    # ---- coletor de rede real: estado do enlace não pode ser sobrescrito pela taxa
    n = col.Net(copy.deepcopy(DEFAULTS)); n.read(); time.sleep(0.5); r = n.read()
    okb = all(isinstance(r[k].get("up"), bool) for k in ("eth", "wifi") if r[k].get("exists"))
    check("rede: estado ON/OFF é booleano e taxas ficam separadas", okb, str(r.get("eth")))

    # ---- motor real (coletores deste computador) sem exceções
    eng = panel.Engine()
    snap = eng.snapshot()
    check("motor real: snapshot com estado da coleta", isinstance(snap.get("coleta", {}).get("falhas"), list),
          str(snap.get("coleta")))
    img = eng.frame()
    check("motor real: quadro 320x480", img.size == (320, 480))

    # ---- estilos selecionáveis (matrix, gamma, gamma-sonar, gamma-raiox, gamma-uv, pcb)
    from library.sensors.matrixgreenpro.estilos import renderer
    for nome in ("matrix", "gamma", "gamma-sonar", "gamma-raiox", "gamma-uv", "gamma-escala", "gamma-barra",
                 "gamma-banner", "gamma-faixa", "gamma-n3", "gamma-alpha", "gamma-n3-abas", "gamma-n3-linha",
                 "gamma-n3-eventos", "gamma-beta", "gamma-gamma-colmeia", "gamma-gamma-mini", "gamma-gamma-painel", "gamma-gamma-coluna", "gamma-gamma", "pcb"):
        for sc in ("normal", "atencao", "critico"):
            key, draw = renderer(nome)
            img = draw(ViewModel(copy.deepcopy(DEFAULTS), (80, 90), (80, 87)).build(panel.demo_snapshot(sc)))
            check(f"estilo {nome}/{sc}: quadro 320x480", key == nome and img.size == (320, 480))
    key, _ = renderer("uranio")
    check("apelido antigo 'uranio' abre o estilo gamma", key == "gamma")
    check("apelidos antigos abrem os novos estilos", renderer("gamma-n3-esq")[0] == "gamma-alpha"
          and renderer("gamma-n3-compacto")[0] == "gamma-beta" and renderer("gamma-sentinela")[0] == "gamma-alpha"
          and renderer("gamma-dosimetro")[0] == "gamma-beta" and renderer("gamma-gamma-fronteira")[0] == "gamma-gamma")
    key, _ = renderer("inexistente")
    check("estilo desconhecido volta para matrix", key == "matrix")
    os.environ["MGP_ESTILO"] = "pcb"
    eng2 = panel.Engine()
    check("motor real com estilo pcb", eng2.estilo == "pcb" and eng2.frame().size == (320, 480))
    os.environ.pop("MGP_ESTILO", None)

    ok = sum(RESULTS)
    print(f"{ts()} RESULTADO: {ok}/{len(RESULTS)} testes aprovados")
    sys.exit(0 if ok == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
