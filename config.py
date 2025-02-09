import math

# ============================================================
# Parâmetros globais do circuito (pista, moto, obstáculos, etc.)
# ============================================================
# Tamanho de referência da moto (bounding box)
tamanho_moto = 1.0

# Skybox
TAMANHO_SKYBOX = 10.0
nível_chão = - (TAMANHO_SKYBOX / 2)  # Ex: -5.0

# Pista
nível_pista = nível_chão + 0.1
largura_pista = 20  # Largura da pista

# Parâmetros de movimento da moto
velocidade_moto_inicial = 0.0      # (unidades/segundo)
direcao_moto_inicial = 0.0         # (radianos)
velocidade_vertical_inicial = 0.0  # para o pulo
angulo_inclinacao_inicial = 0.0    # ângulo de banking

aceleracao = 10.0         # aceleração
desaceleracao = 10.0      # desaceleração
atrito = 2.0              # atrito
velocidade_maxima = 20.0   # velocidade máxima
taxa_rotacao = 1.0        # taxa de rotação (rad/s)

inclinacao_maxima = 5.0         # ângulo máximo de inclinação (graus)
taxa_alteracao_inclinacao = 60.0 # taxa de variação (graus/s)

# Parâmetros para o salto
altura_salto = 2 * tamanho_moto
gravidade = 20.0
velocidade_salto = math.sqrt(2 * gravidade * altura_salto)
velocidade_salto_rampa = 5.0   # impulso vertical na rampa

# Câmera (posição relativa à moto)
distancia_camera = 4.0
altura_camera = 1.0

# Pontos-chave (waypoints) da pista
pontos_chave = [
    (0.0, 0.0),         # A – Início/linha de chegada
    (137.5, 0.0),       # B – Fim da reta principal
    (181.5, 16.5),      # F – Início da curva de alta velocidade
    (165.0, 55.0),      # G – Pico da curva
    (82.5, 66.0),       # H – Longa curva que aproxima a reta final
    (0.0, 66.0),        # I
    (-82.5, 11.0)       # K
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

# Texturas para pista, rampa e obstáculo
textura_pista = None
textura_rampa = None
textura_obstaculo = None

# Centro do skybox (atualizado com a posição da câmera)
pos_camera = [0.0, 0.0, 0.0]

# Deslocamento vertical para as rampas (para evitar recortes visuais)
deslocamento_rampa = 1.0
