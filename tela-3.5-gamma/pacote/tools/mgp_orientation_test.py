#!/usr/bin/env python3
# MATRIX GREEN PRO | versão 2.1.0 | 01/11/2026 00:25 (-03) | referência ao scripts/instalar.sh
# histórico: 2.0.0 31/10/2026 23:50 criação: teste físico de orientação retrato
# Envia ao TUS-35 (revisão A) uma imagem 320x480 com seta "TOPO" e mantém
# por alguns segundos. O serviço turing-smart-screen precisa estar PARADO
# (o scripts/instalar.sh --teste-orientacao faz isso e o religa ao final).
# Uso: .venv/bin/python3 tools/mgp_orientation_test.py [--invertido] [--segundos 15]
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import os  # noqa: E402
os.chdir(ROOT)

from PIL import Image, ImageDraw  # noqa: E402
from library.sensors.matrixgreenpro.render import font  # noqa: E402


def ts():
    return time.strftime("[%d/%m/%Y %H:%M:%S]")


def pattern():
    im = Image.new("RGB", (320, 480), (0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 319, 479), outline=(0, 255, 0), width=2)
    d.polygon([(160, 14), (230, 100), (185, 100), (185, 170), (135, 170), (135, 100), (90, 100)], fill=(0, 255, 0))
    d.text((160, 200), "TOPO", font=font(40, "Bold"), fill=(255, 255, 255), anchor="mm")
    d.text((160, 250), "320 x 480 RETRATO", font=font(18, "Bold"), fill=(255, 208, 0), anchor="mm")
    d.text((160, 285), "A seta deve apontar", font=font(15), fill=(176, 184, 176), anchor="mm")
    d.text((160, 305), "para CIMA", font=font(15), fill=(176, 184, 176), anchor="mm")
    d.text((8, 470), "INF. ESQ.", font=font(13, "Bold"), fill=(255, 48, 48), anchor="ls")
    d.text((312, 470), "INF. DIR.", font=font(13, "Bold"), fill=(255, 255, 255), anchor="rs")
    return im


def main():
    secs = 15
    if "--segundos" in sys.argv:
        secs = int(sys.argv[sys.argv.index("--segundos") + 1])
    reverse = "--invertido" in sys.argv
    from library.lcd.lcd_comm import Orientation
    from library.lcd.lcd_comm_rev_a import LcdCommRevA
    import yaml
    cfg = yaml.safe_load(open(ROOT / "config.yaml", encoding="utf-8"))
    port = cfg["config"].get("COM_PORT", "AUTO")
    print(f"{ts()} porta={port} orientação={'REVERSE_PORTRAIT' if reverse else 'PORTRAIT'}")
    lcd = LcdCommRevA(com_port=port, display_width=320, display_height=480)
    lcd.InitializeComm()
    lcd.SetBrightness(int(cfg["display"].get("BRIGHTNESS", 20)))
    lcd.SetOrientation(Orientation.REVERSE_PORTRAIT if reverse else Orientation.PORTRAIT)
    lcd.DisplayPILImage(pattern())
    print(f"{ts()} padrão enviado; observe a tela por {secs} s")
    time.sleep(secs)
    try:
        lcd.closeSerial()
    except Exception:
        pass
    print(f"{ts()} fim do teste")


if __name__ == "__main__":
    if "--png" in sys.argv:
        pattern().save(sys.argv[sys.argv.index("--png") + 1])
    else:
        main()
