# config.py
"""
Este módulo contém as configurações globais do jogo,
incluindo parâmetros da pista, da moto, da câmera, texturas e pontos-chave.
"""

import math

# ============================================================
# Parâmetros do circuito (pista, moto, obstáculos, etc.)
# ============================================================

# Tamanho de referência da moto (usado para bounding box e colisões)
tamanho_moto = 1.0

# Skybox
TAMANHO_SKYBOX = 10.0
nível_chão = - (TAMANHO_SKYBOX / 2)  # Nível base do chão

# Pista
nível_pista = nível_chão + 0.1
largura_pista = 20  # Largura total da pista

# Parâmetros de movimento da moto
velocidade_moto_inicial = 0.0      # Velocidade inicial (unidades/segundo)
direcao_moto_inicial = 0.0         # Direção inicial (radianos)
velocidade_vertical_inicial = 0.0  # Velocidade vertical inicial (para pulo)
angulo_inclinacao_inicial = 0.0    # Inclinação inicial (banking)

aceleracao = 10.0         # Aceleração da moto
desaceleracao = 10.0      # Desaceleração (freada)
atrito = 2.0              # Atrito (reduz velocidade quando sem aceleração)
velocidade_maxima = 20.0   # Velocidade máxima permitida
taxa_rotacao = 1.0        # Taxa de rotação (radianos por segundo)

inclinacao_maxima = 5.0         # Ângulo máximo de inclinação em curvas (graus)
taxa_alteracao_inclinacao = 60.0 # Taxa de alteração da inclinação (graus por segundo)

# Parâmetros para o pulo
altura_salto = 2 * tamanho_moto
gravidade = 20.0
# Calcula a velocidade de salto para atingir a altura desejada (física do movimento)
velocidade_salto = math.sqrt(2 * gravidade * altura_salto)
velocidade_salto_rampa = 5.0   # Impulso vertical ao sair de uma rampa

# Parâmetros da câmera (posição relativa à moto)
distancia_camera = 4.0
altura_camera = 1.0

# Pontos-chave (waypoints) da pista
pontos_chave = [
    (0.0, 0.0),         # Início/linha de chegada
    (137.5, 0.0),       # Fim da reta principal
    (181.5, 16.5),      # Início da curva de alta velocidade
    (165.0, 55.0),      # Pico da curva
    (82.5, 66.0),       # Longa curva que aproxima da reta final
    (0.0, 66.0),
    (-82.5, 11.0)
]
NUM_PONTOS_PISTA = 400
# Lista que será preenchida com os pontos centrais interpolados da pista
pontos_centro_pista = []

# Chão (floor)
EXTENSAO_CHAO = TAMANHO_SKYBOX * 100.0

# Variáveis globais para texturas (serão carregadas posteriormente)
textura_frente = None
textura_tras = None
textura_direita = None
textura_esquerda = None
textura_cima = None
textura_baixo = None

# Lista de texturas para o chão
lista_texturas_chao = []

# Texturas para a pista, rampas e obstáculos
textura_pista = None
textura_rampa = None
textura_obstaculo = None

# Centro do skybox (atualizado com a posição da câmera)
pos_camera = [0.0, 0.0, 0.0]

# Deslocamento vertical aplicado às rampas para evitar recortes visuais
deslocamento_rampa = 1.0
