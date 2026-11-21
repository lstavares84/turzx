# GAMMA | tela.py | versão 1.0.0 | 08/11/2026 13:18 (-03) | criação original (Claude, para Lucas Tavares)
# Qual tela este pacote desenha. O instalador grava aqui "3.5" ou "5.2" (opção --tela).
# A variável de ambiente MGP_TELA tem prioridade (prévias e testes das duas telas).
import os

TELAS = {
    # nome: (largura, altura, escala) em pixels reais. O desenho é feito em coordenadas de 320 de largura
    # e multiplicado pela escala, com fontes e traços na resolução real (nada é esticado).
    "3.5": (320, 480, 1.0),      # TURZX / Turing 3,5" (TUS-35), revisão A, USB 1a86:5722
    "5.2": (720, 1280, 2.25),    # TURZX / Turing 5,2", revisão TUR_USB, USB 1cbe:0050
}
TELA = "3.5"
TELA = os.environ.get("MGP_TELA", TELA)
if TELA not in TELAS:
    TELA = "3.5"
LARGURA, ALTURA, ESCALA = TELAS[TELA]
