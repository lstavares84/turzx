# MATRIX GREEN PRO | versão 2.6.1 | 07/11/2026 21:58 (-03) | ping com uma casa decimal
# histórico: 2.6.0 07/11/2026 21:46 alerta mantido 5 min; ping classificado pelo número exibido
# histórico: 2.5.0 07/11/2026 21:00 alertas confirmados em 2 s, limites sustentados, clock da GPU, link e LOG de alertas
# histórico: 2.4.0 07/11/2026 20:15 total de TB dos discos, mudanças bruscas e registro
# histórico: 2.3.0 07/11/2026 19:10 séries de 24 h repassadas aos estilos (vm['hist'])
# histórico: 2.2.0 07/11/2026 19:00 baias com uso, total e percentual (cor só informativa)
# histórico: 2.1.0 31/10/2026 23:40 ajustes finais: rede x internet, estado da coleta
#   (OK/PARCIAL/FALHOU) separado da saúde, ventoinha GPU 'FAN 72% | 1800RPM'
# histórico: 2.0.0 31/10/2026 23:15 saúde por indicador | 1.0.0 31/10/2026 22:40 criação inicial
#
# Converte leituras brutas em textos formatados + nível. Convenções de unidade:
#   RAM e VRAM em GB binários (1 GB = 1024^3 bytes, como free e nvidia-smi);
#   discos em GB/TB decimais (1 TB = 10^12 bytes, como o rótulo do fabricante);
#   rede em B/s, KB/s e MB/s decimais (1 MB = 10^6 bytes).
#
# Regras de contagem do cabeçalho (vm["health"]):
#   * cada INDICADOR conta uma única vez (ex.: RAM = texto + disponível + barra = 1);
#   * só entram níveis WARN/LOST (aviso) e CRIT (crítico);
#   * utilização de CPU/GPU, FPS, frequência, carga e tráfego nunca entram;
#   * N/D de hardware inexistente (ex.: Wi-Fi ausente, sem medidor de energia) nunca entra;
#   * sensor que existia e sumiu (LOST) NÃO é saúde do computador: vai para o
#     estado da coleta (COLETA OK / COLETA PARCIAL / COLETA FALHOU), no rodapé;
#   * sem nenhum enlace de rede conta 1 crítico ("conexao"); nesse caso a falha
#     do ping é consequência e não é contada de novo.
import time

from .alerts import Hyst, Streak, Confirma, Sustentado, OK, WARN, CRIT, NA, LOST, NEUTRAL

DIAS = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
ND = ("N/D", NA)


def _ld(v):
    return f"{v:.2f}" if v < 10 else (f"{v:.1f}" if v < 100 else f"{v:.0f}")


def rate(bps, short=False):
    """short=True: formato compacto por interface (12.4M = 12,4 MB/s)."""
    if bps is None:
        return "N/D" if not short else "--"
    if bps < 1000:
        return f"{bps:.0f}B/s" if not short else f"{bps:.0f}B"
    if bps < 1e6:
        v = bps / 1e3
        t = f"{v:.1f}" if v < 100 else f"{v:.0f}"
        return t + ("KB/s" if not short else "K")
    if bps < 1e9:
        v = bps / 1e6
        t = f"{v:.1f}" if v < 100 else f"{v:.0f}"
        return t + ("MB/s" if not short else "M")
    return f"{bps / 1e9:.2f}" + ("GB/s" if not short else "G")


def total(b):
    if b is None:
        return "N/D"
    if b >= 1e12:
        return f"{b / 1e12:.2f}TB"
    if b >= 1e9:
        return f"{b / 1e9:.1f}GB"
    return f"{b / 1e6:.0f}MB"


def disk_use(used, tot):
    if tot >= 1e12:
        return f"{used / 1e12:.2f}/{tot / 1e12:.2f}TB"
    return f"{used / 1e9:.0f}/{tot / 1e9:.0f}GB"


def cap_txt(b):
    """Capacidade em unidades decimais, como o fabricante anuncia (12TB, 500GB)."""
    if b >= 1e13:
        return f"{b / 1e12:.0f}TB"
    if b >= 1e12:
        return f"{b / 1e12:.1f}TB"
    return f"{b / 1e9:.0f}GB"


def disk_free(b):
    if b >= 1e12:
        return f"{b / 1e12:.2f}TB"
    if b >= 10e9:
        return f"{b / 1e9:.0f}GB"
    return f"{b / 1e9:.1f}GB"


def speed_txt(mbps):
    if not mbps:
        return ""
    return f"{mbps // 1000}Gb/s" if mbps >= 1000 and mbps % 1000 == 0 else f"{mbps}Mb/s"


class ViewModel:
    def __init__(self, cfg, cpu_limits, gpu_limits):
        hy = cfg["histerese"]
        self.cfg = cfg
        self.h_cpu_t = Hyst(*cpu_limits, hy["temperatura"])
        self.h_gpu_t = Hyst(*gpu_limits, hy["temperatura"])
        self.h_vram = Hyst(cfg["gpu"]["vram_warn"], cfg["gpu"]["vram_crit"], hy["percentual"])
        self.h_ram = Hyst(cfg["ram"]["warn"], cfg["ram"]["crit"], hy["percentual"])
        self.h_disk = [Hyst(cfg["disco_warn"], cfg["disco_crit"], 1) for _ in range(3)]
        dl = cfg.get("disco_temp_limites") or {"hdd": [50, 55], "ssd": [70, 80]}
        self.h_dt = [{k: Hyst(dl[k][0], dl[k][1], hy["temperatura"]) for k in ("hdd", "ssd")} for _ in range(3)]
        self.h_ping = Hyst(cfg["ping"]["warn_ms"], cfg["ping"]["crit_ms"], hy["ping_ms"], estrito=True)   # "acima de"
        self.s_ping = Streak(1, 3)
        psu = float(cfg["energia"].get("psu_watts") or 0)
        self.h_pwr = Hyst(psu * 0.8 if psu else None, psu * 0.9 if psu else None, 10)
        self.cpu_limits, self.gpu_limits = cpu_limits, gpu_limits
        from .brusco import Brusco
        self.brusco = Brusco()
        tl = cfg["cpu"].get("temps_limites") or {}
        self.h_t = {k: Hyst(tl[k][0], tl[k][1], hy["temperatura"]) for k in ("placa", "ram", "ssd") if k in tl and len(tl[k]) == 2}
        # leituras contínuas só sobem de nível depois de 2 s (ruído de leitura não vira alerta); ping e discos não
        self.conf = {}
        self._now = time.time()
        import os
        janela = float(cfg["cpu"].get("uso_janela_s", 300))
        self.s_uso = Sustentado(cfg["cpu"].get("uso_warn", 90), janela)
        self.s_carga = Sustentado(float(cfg["cpu"].get("carga_por_nucleo", 1.5)) * (os.cpu_count() or 1), janela)
        self.fan_min = float(cfg["cpu"].get("fan_min_rpm", 600))
        self.eth_vel = 0                                   # maior velocidade de link já vista na Ethernet
        from .alertas import Alertas
        self.alertas = Alertas()

    def _cf(self, chave, lv, seg=None):
        """Nível confirmado: subida só depois de 2 s (seg=0 para leituras lentas, como o ping) e alerta mantido
        no mínimo 5 min (alertas.manter_s)."""
        if chave not in self.conf:
            a = self.cfg.get("alertas") or {}
            self.conf[chave] = Confirma(float(a.get("confirmar_s", 2)) if seg is None else seg, float(a.get("manter_s", 300)))
        return self.conf[chave].update(lv, self._now)

    def _fan_level(self, stopped, temp, limits):
        """Ventoinha parada só é problema com o componente aquecido (modo semipassivo é normal)."""
        if not stopped or temp is None:
            return OK
        if temp >= limits[0]:
            return CRIT
        if temp >= float(self.cfg["cpu"]["fan_stop_ok_below_c"]):
            return WARN
        return OK

    def build(self, s, now=None):
        now = now or time.time()
        self._now = now
        vm = {"demo": s.get("demo", False)}
        health = {}   # indicador -> nível (base da contagem do cabeçalho)

        # ---------- CPU
        c = s["cpu"]
        vm["cpu_util"] = (f"{round(c['util'])}%", NEUTRAL) if c.get("util") is not None else ND
        vm["cpu_pct"] = c.get("util")
        vm["cpu_ghz"] = (f"{c['ghz']:.2f}GHz", NEUTRAL) if c.get("ghz") else ND
        t = c.get("temp")
        if t is not None:
            vm["cpu_temp"] = (f"{round(t)}°C", self._cf("cpu_temp", self.h_cpu_t.update(t)))
        else:
            vm["cpu_temp"] = ("N/D", LOST if c.get("temp_lost") else NA)
        if t is not None:
            health["cpu_temp"] = vm["cpu_temp"][1]
        fan = c.get("fan")
        if fan is None:
            vm["cpu_fan"] = ("N/D", LOST if c.get("fan_lost") else NA)
        else:
            vm["cpu_fan"] = (f"{int(fan)}RPM", self._cf("cpu_fan", self._fan_level(fan <= 0, t, self.cpu_limits)))
            health["cpu_fan"] = vm["cpu_fan"][1]
        # temperaturas de placa, RAM e SSD (placa é informativa; RAM e SSD têm limites e entram no alerta)
        tt = c.get("temps") or {}
        for papel, chave in (("placa", "t_placa"), ("ram", "t_ram"), ("ssd", "t_ssd")):
            d = tt.get(papel)
            if d is None:
                vm[chave] = ND
            elif d.get("c") is None:
                vm[chave] = ("N/D", LOST if d.get("visto") else NA)
            else:
                x = d["c"]
                lv = self._cf(chave, self.h_t[papel].update(x)) if papel in self.h_t else NEUTRAL
                vm[chave] = (f"{round(x)}°C", lv)
                if papel in self.h_t:
                    health[chave] = lv
        # bomba e ventoinhas por papel (water cooler: o radiador substitui a ventoinha do CPU)
        cool = c.get("cool")
        for chave in ("pump", "fan_sqi", "fan_sql", "fan_sqt"):
            vm[chave] = ND
        if cool:
            def nivel(papel, d):
                rpm = (d or {}).get("rpm")
                if rpm is None:
                    return ("N/D", LOST if (d or {}).get("visto") else NA)
                if rpm > 0:                           # girando devagar demais = aviso (alarme típico de BIOS)
                    return (f"{int(rpm)}RPM", WARN if rpm < self.fan_min else OK)
                if not (d or {}).get("visto"):
                    return ("0RPM", NA)               # nunca girou: conector vazio ou mapa errado, não alarma
                return ("0RPM", CRIT if papel == "bomba" else self._fan_level(True, t, self.cpu_limits))
            for papel, chave in (("bomba", "pump"), ("sq_inf", "fan_sqi"), ("sq_lat", "fan_sql"), ("sq_tras", "fan_sqt")):
                if papel in cool:
                    vm[chave] = nivel(papel, cool[papel])
                    vm[chave] = (vm[chave][0], self._cf(chave, vm[chave][1]))
                    if vm[chave][1] not in (NA, LOST):
                        health[chave] = vm[chave][1]
            if "radiador" in cool:
                vm["cpu_fan"] = nivel("radiador", cool["radiador"])
                vm["cpu_fan"] = (vm["cpu_fan"][0], self._cf("cpu_fan", vm["cpu_fan"][1]))
                if vm["cpu_fan"][1] not in (NA, LOST):
                    health["cpu_fan"] = vm["cpu_fan"][1]
        la = c.get("load")
        vm["cpu_load"] = ("/".join(_ld(x) for x in la), NEUTRAL) if la else ND
        # uso e carga sustentados por 5 min (Zabbix): aviso; abaixo disso o número segue neutro
        lu = self._cf("cpu_uso", self.s_uso.update(c.get("util"), now), 0)
        if lu == WARN:
            vm["cpu_util"] = (vm["cpu_util"][0], WARN)
        if c.get("util") is not None:
            health["cpu_uso"] = lu
        lc = self._cf("carga", self.s_carga.update(la[0] if la else None, now), 0)
        if lc == WARN:
            vm["cpu_load"] = (vm["cpu_load"][0], WARN)
        if la:
            health["carga"] = lc

        # ---------- GPU
        gp = s["gpu"]
        gkeys = ("gpu_util", "gpu_mhz", "gpu_temp", "vram_txt", "vram_pct_txt", "gpu_fan_pct",
                 "gpu_fan_rpm", "gpu_w", "gpu_wlim")
        vm["gpu_pct"] = vm["vram_pct"] = None
        vm["gpu_wlim"] = ("", NA)
        if not gp.get("present"):
            for k in gkeys[:-1]:
                vm[k] = ND
        elif gp.get("util") is None and gp.get("temp") is None:
            lv = LOST if gp.get("lost") else NA
            for k in gkeys[:-1]:
                vm[k] = ("N/D", lv)
        else:
            vm["gpu_util"] = (f"{round(gp['util'])}%", NEUTRAL) if gp.get("util") is not None else ND
            vm["gpu_pct"] = gp.get("util")
            vm["gpu_mhz"] = (f"{int(gp['mhz'])}MHz", NEUTRAL) if gp.get("mhz") is not None else ND
            # motivos de redução de clock (NVML): térmico por software = aviso; por hardware = crítico.
            # O limite de potência (300 W) é o próprio controle da placa em jogo: não é alerta.
            rz = gp.get("throttle")
            if rz is not None and gp.get("mhz") is not None:
                lvz = CRIT if rz & (0x8 | 0x40 | 0x80) else WARN if rz & 0x20 else OK
                lvz = self._cf("gpu_clock", lvz)
                if lvz != OK:
                    vm["gpu_mhz"] = (vm["gpu_mhz"][0], lvz)
                health["gpu_clock"] = lvz
            gt = gp.get("temp")
            vm["gpu_temp"] = (f"{round(gt)}°C", self._cf("gpu_temp", self.h_gpu_t.update(gt))) if gt is not None else ND
            health["gpu_temp"] = vm["gpu_temp"][1]
            vu, vt = gp.get("vram_used"), gp.get("vram_total")
            if vu is not None and vt:
                p = 100.0 * vu / vt
                lv = self._cf("vram", self.h_vram.update(p))
                vm["vram_txt"] = (f"{vu:.1f}/{vt:.1f}GB", lv)
                vm["vram_pct_txt"] = (f"{round(p)}%", lv)
                vm["vram_pct"] = p
                health["vram"] = lv
            else:
                vm["vram_txt"] = vm["vram_pct_txt"] = ND
            rpm, pct = gp.get("fan_rpm"), gp.get("fan_pct")
            stopped = (rpm is not None and rpm <= 0) or (rpm is None and pct is not None and pct <= 0)
            fl = self._cf("gpu_fan", self._fan_level(stopped, gt, self.gpu_limits))
            # percentual = comando do driver; RPM = medição do tacômetro. Nunca se estima um pelo outro.
            vm["gpu_fan_pct"] = (f"{round(pct)}%", fl) if pct is not None else ND
            vm["gpu_fan_rpm"] = (f"{int(rpm)}RPM", fl) if rpm is not None else ("RPM -", NA)
            if pct is not None or rpm is not None:
                health["gpu_fan"] = fl
            vm["gpu_w"] = (f"{round(gp['power'])}", NEUTRAL) if gp.get("power") is not None else ND
            vm["gpu_wlim"] = (f"LIM {round(gp['power_limit'])}W", NA) if gp.get("power_limit") else ("", NA)
        f = s.get("fps")
        vm["fps"] = (f"{round(f)}", NEUTRAL) if f is not None else ND

        # ---------- RAM (nível pela memória efetivamente disponível)
        r = s["ram"]
        lv = self._cf("ram", self.h_ram.update(r["pct"]))
        vm["ram_used"] = (f"{r['used']:.1f}", lv)
        vm["ram_total"] = (f"/{r['total']:.1f}GB", NEUTRAL)
        vm["ram_avail"] = (f"{r['avail']:.1f}GB", lv)
        vm["ram_pct"] = r["pct"]
        vm["ram_lvl"] = lv
        health["ram"] = lv

        # ---------- Discos (saúde pela capacidade livre: percentual E valor absoluto)
        disks = []
        fw, fc = float(self.cfg["disco_livre_warn_gb"]) * 1e9, float(self.cfg["disco_livre_crit_gb"]) * 1e9
        for i, d in enumerate(s["disks"][:3]):
            name = d.get("nome", "---")
            if d.get("state") == "OK" and d.get("total"):
                lv = self.h_disk[i].update(d["pct"])
                if d["free"] < fc:
                    lv = CRIT
                elif d["free"] < fw and lv == OK:
                    lv = WARN
                disks.append({"name": name, "use": disk_use(d["used"], d["total"]),
                              "pct_txt": f"{round(d['pct'])}%", "free": disk_free(d["free"]),
                              "pct": d["pct"], "lvl": lv, "use_lvl": NEUTRAL})
            else:
                st = d.get("state")
                txt = {"OFF": "DESMONTADO", "CFG": "NÃO CONFIGURADO", "ND": "SEM LEITURA"}.get(st, "N/D")
                lv = WARN if st == "OFF" else NA   # configurado e ausente = atenção
                disks.append({"name": name, "use": txt, "pct_txt": "OFF" if st == "OFF" else "N/D",
                              "free": "--", "pct": None, "lvl": lv, "use_lvl": lv})
            disks[-1]["lvl"] = self._cf(f"disk{i}", disks[-1]["lvl"], 0)
            health[f"disk{i}"] = disks[-1]["lvl"]
            # temperatura do disco (HDD tem limites próprios; sem leitura = N/D, não alerta)
            x = d.get("temp")
            if x is not None:
                lv = self._cf(f"disk{i}_t", self.h_dt[i]["hdd" if d.get("hdd") else "ssd"].update(x), 0)
                disks[-1].update(temp_txt=f"{round(x)}°C", temp_lvl=lv)
                health[f"disk{i}_t"] = lv
            else:
                disks[-1].update(temp_txt="N/D", temp_lvl=NA)
        vm["disks"] = disks

        # ---------- Baias do gabinete USB (informativo: não entra na saúde nem nos alertas)
        baias = []
        for b in (s.get("baias") or []):
            e = b.get("estado")
            baias.append({"n": b["n"], "estado": e, "cap": cap_txt(b["bytes"]) if b.get("bytes") else "",
                          "palavra": {"MONT": "MONTADO", "DESM": "DESMONT.", "LIVRE": "LIVRE"}.get(e, "N/D"),
                          "curta": {"MONT": "MONT", "DESM": "DESM", "LIVRE": "LIVRE"}.get(e, "N/D"),
                          "lvl": OK if e == "MONT" else NEUTRAL if e == "DESM" else NA,
                          "modelo": b.get("modelo", "")})
            if e == "MONT" and b.get("total"):                 # uso, como na seção de discos; a cor não entra na saúde
                pct = 100.0 * b["usado"] / b["total"]
                livre = b["total"] - b["usado"]
                plv = CRIT if (pct >= float(self.cfg["disco_crit"]) or livre < fc) else \
                    WARN if (pct >= float(self.cfg["disco_warn"]) or livre < fw) else OK
                baias[-1].update(use=disk_use(b["usado"], b["total"]), pct=pct, pct_txt=f"{round(pct)}%", pct_lvl=plv)
        vm["baias"] = baias
        vm["hist"] = s.get("hist")                             # séries de 24 h (historico.py), para os gráficos

        # ---------- Total de todos os HDs (discos + baias montadas); o mesmo dispositivo conta uma vez
        t_uso = t_cap = 0.0
        devs, n, partes = set(), 0, []
        for i, d in enumerate(s["disks"][:3]):
            if d.get("state") == "OK" and d.get("total"):
                if d.get("dev") and d["dev"] in devs:
                    continue
                devs.add(d.get("dev"))
                t_uso, t_cap, n = t_uso + d["used"], t_cap + d["used"] + d["free"], n + 1
                partes.append((d.get("nome", "---"), d["used"] + d["free"], d["used"], disks[i]["lvl"] if i < len(disks) else OK))
        for b in (s.get("baias") or []):
            if b.get("estado") == "MONT" and b.get("total") and not (b.get("dev") and b["dev"] in devs):
                devs.add(b.get("dev"))
                t_uso, t_cap, n = t_uso + b["usado"], t_cap + b["total"], n + 1
                partes.append((f"B{b['n']}", b["total"], b["usado"], OK))
        if t_cap:
            tb = lambda x: f"{x / 1e12:.2f}TB" if x < 10e12 else f"{x / 1e12:.1f}TB"
            vm["total_hd"] = {"uso": tb(t_uso), "total": tb(t_cap), "livre": tb(t_cap - t_uso),
                              "pct": 100.0 * t_uso / t_cap, "pct_txt": f"{round(100.0 * t_uso / t_cap)}%", "n": n,
                              "fora": sum(1 for b in (s.get("baias") or []) if b.get("estado") == "DESM"), "partes": partes}
        else:
            vm["total_hd"] = None

        # ---------- Rede
        n = s["net"]
        vm["net_down"] = (rate(n.get("down")), NEUTRAL if n.get("down") is not None else NA)
        vm["net_up"] = (rate(n.get("up")), NEUTRAL if n.get("up") is not None else NA)
        vm["net_rx"] = (total(n.get("rx")), NEUTRAL if n.get("rx") is not None else NA)
        vm["net_tx"] = (total(n.get("tx")), NEUTRAL if n.get("tx") is not None else NA)
        e, w = n.get("eth", {}), n.get("wifi", {})
        dflt = n.get("default")
        wifi_up = bool(w.get("exists") and w.get("up"))
        eth_up = bool(e.get("exists") and e.get("up"))
        eth_req = bool(self.cfg["rede"].get("ethernet_obrigatoria", False))

        def iface(d, up, wireless):
            if not d.get("exists"):
                return {"state": ("N/D", NA), "info": ("SEM INTERFACE", NA), "rates": ("", NA)}
            if up:
                active = d.get("name") == dflt
                st = ("ATIVA" if active else "ON", OK)
                extra = speed_txt(d.get("speed")) if not wireless else (
                    f"{d['signal']:.0f}dBm" if d.get("signal") is not None else "")
                info = f"{d.get('name', '')} {extra}".strip()
                rt = f"↓{rate(d.get('rate_down'), True)} ↑{rate(d.get('rate_up'), True)}"
                return {"state": st, "info": (info, NEUTRAL), "rates": (rt, NEUTRAL)}
            return {"state": ("OFF", NA), "info": (d.get("name", ""), NA), "rates": ("", NA)}

        ei, wi = iface(e, eth_up, False), iface(w, wifi_up, True)
        any_link = eth_up or wifi_up
        any_iface = bool(e.get("exists") or w.get("exists"))
        if any_iface and not any_link:
            # nenhum enlace físico: uma única condição crítica
            health["conexao"] = CRIT
            if e.get("exists"):
                ei["state"] = ("OFF", CRIT)
                ei["info"] = (f"{e.get('name', '')} SEM LINK", CRIT)
        elif e.get("exists") and not eth_up:
            if eth_req:   # Ethernet configurada como obrigatória e o Wi-Fi assumiu
                ei["state"] = ("OFF", WARN)
                ei["info"] = (f"{e.get('name', '')} SEM LINK", WARN)
                health["conexao"] = WARN
            else:         # Wi-Fi funcionando: Ethernet desligada é só informação
                ei["state"] = ("OFF", NA)
                ei["info"] = (f"{e.get('name', '')} SEM LINK", NA)
        if "conexao" not in health and any_link:
            health["conexao"] = OK
        # Ethernet ativa abaixo da maior velocidade já vista (ex.: 1 Gb/s caiu para 100 Mb/s) = aviso
        if eth_up and e.get("speed"):
            self.eth_vel = max(self.eth_vel, int(e["speed"]))
            if int(e["speed"]) < self.eth_vel:
                ei["info"] = (f"{e.get('name', '')} {speed_txt(e['speed'])} (era {speed_txt(self.eth_vel)})", WARN)
                if health.get("conexao") == OK:
                    health["conexao"] = WARN
        if "conexao" in health:
            health["conexao"] = self._cf("conexao", health["conexao"], 0)
        vm["eth"], vm["wifi"] = ei, wi
        no_link = any_iface and not any_link

        # ---------- Sistema
        lt = time.localtime(now)
        vm["clock"] = (time.strftime("%H:%M:%S", lt), NEUTRAL)
        vm["date"] = (f"{DIAS[lt.tm_wday]} {time.strftime('%d/%m/%Y', lt)}", NEUTRAL)
        vm["os"] = (s.get("os", "LINUX"), NA)
        up = s.get("uptime")
        if up is not None:
            d, rem = divmod(int(up), 86400)
            h, rem = divmod(rem, 3600)
            vm["uptime"] = (f"{d:02d}d{h:02d}h{rem // 60:02d}m", NEUTRAL)
        else:
            vm["uptime"] = ND

        # ---------- Ping e clima
        pg = s["ping"]
        # Internet é avaliada à parte do estado físico das interfaces (pelo ping).
        if pg.get("noprobe") or pg.get("ok") is None:
            vm["ping"] = ND
            vm["inet"] = ("INTERNET N/D", NA)
        elif pg.get("ok"):
            self.s_ping.update(False)
            ms = pg["ms"]
            # uma casa decimal; classifica o número exibido (20.0ms é verde, 20.1ms já é âmbar)
            vm["ping"] = (f"{ms:.1f}ms", self._cf("ping", self.h_ping.update(round(ms, 1)), 0))
            vm["inet"] = ("INTERNET OK", OK)
        else:
            lv = self._cf("ping", max(WARN, self.s_ping.update(True)), 0)
            vm["ping"] = ("FALHA", lv)
            vm["inet"] = ("SEM REDE", CRIT) if no_link else (
                ("SEM INTERNET", lv) if lv == CRIT else ("INSTÁVEL", WARN))
        if vm["ping"][1] not in (NA,) and not no_link:
            health["ping"] = vm["ping"][1]
        wx = s["weather"]
        vm["city"] = self.cfg["clima"].get("cidade", "")
        if wx.get("state") == "ND":
            vm["wtemp"] = ND
            vm["wdesc"] = ("SEM DADOS DA API", NA)
            vm["wage"] = ("OPEN-METEO N/D", NA)
        else:
            stale = wx["state"] == "STALE"
            vm["wtemp"] = (f"{round(wx['temp'])}°C", NEUTRAL)
            vm["wdesc"] = (wx["desc"], NEUTRAL)
            vm["wage"] = (("DESATUALIZADO " if stale else "OPEN-METEO ")
                          + time.strftime("%H:%M", time.localtime(wx["ts"])), WARN if stale else NA)


        # ---------- Energia total (somente medição legítima)
        pw = s["power"]
        if pw.get("state") == "OK":
            lv = self.h_pwr.update(pw["w"]) if self.h_pwr.warn else NEUTRAL
            vm["power"] = (f"{round(pw['w'])}", lv)
            vm["power_tag"] = ({"TOMADA": "MEDIDOR TOMADA", "PSU": "FONTE DIGITAL",
                                "EST": "ESTIMATIVA"}.get(pw.get("tag"), pw.get("tag", "")), NA)
            if lv in (WARN, CRIT):
                health["energia"] = lv
        elif pw.get("state") == "LOST":
            vm["power"] = ("N/D", LOST)
            vm["power_tag"] = ("FALHA NA LEITURA", LOST)

        else:
            vm["power"] = ("N/D", NA)
            vm["power_tag"] = ("SEM MEDIDOR", NA)

        # ---------- trilhos de saúde por seção, rodapé e cabeçalho
        vm["health"] = health
        ncrit = sum(1 for x in health.values() if x == CRIT)
        nwarn = sum(1 for x in health.values() if x in (WARN, LOST))
        if ncrit and nwarn:
            vm["hdr_status"] = (f"● {ncrit} CRÍTICO{'S' if ncrit > 1 else ''} ▲{nwarn}", CRIT)
        elif ncrit:
            vm["hdr_status"] = (f"● {ncrit} CRÍTICO{'S' if ncrit > 1 else ''}", CRIT)
        elif nwarn:
            vm["hdr_status"] = (f"▲ {nwarn} AVISO{'S' if nwarn > 1 else ''}", WARN)
        else:
            vm["hdr_status"] = ("● SISTEMA OK", OK)
        # estado da COLETA (independente da saúde do computador)
        col = s.get("coleta", {"esperados": 1, "falhas": []})
        falhas = list(col.get("falhas", []))
        if col.get("esperados", 1) and len(falhas) >= col.get("esperados", 1):
            vm["coleta"] = ("COLETA FALHOU", CRIT)
        elif falhas:
            vm["coleta"] = (("COLETA PARCIAL " + " ".join(falhas))[:26], WARN)
        else:
            vm["coleta"] = ("COLETA OK", OK)
        vm["coleta_falhas"] = falhas
        if vm["coleta"][0] == "COLETA FALHOU":
            # sem dados não há como afirmar que o sistema está bem
            vm["hdr_status"] = ("■ SEM DADOS", CRIT)
        # ---------- Mudanças bruscas (só nas variantes de estudo) e LOG dos alertas por limite
        if s.get("demo_brusco") is not None:
            marcadas = s["demo_brusco"]
        else:
            marcadas, _ = self.brusco.atualizar(s, now)
        vm["brusco"] = set(marcadas)
        if s.get("demo_alertas") is not None:
            vm["registro"] = list(s["demo_alertas"])
        else:
            vm["registro"] = self.alertas.atualizar(health, vm, now)
        return vm
