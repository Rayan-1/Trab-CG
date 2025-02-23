# utils.py
"""
Módulo utilitário para funções comuns, como:
  - Carregamento de texturas (usando Pillow);
  - Configuração inicial do OpenGL (iluminação, texturas, etc.);
  - Função de interpolação (Catmull-Rom) para gerar curvas suaves.
"""

from OpenGL.GL import *
from PIL import Image

def carregar_textura(caminho_imagem: str, skybox: bool = False) -> int:
    """
    Carrega uma imagem e cria uma textura OpenGL.
    
    Se a extensão for .tga, utiliza o modo RGBA; caso contrário, utiliza RGB.
    skybox: se True, configura o wrap mode para CLAMP_TO_EDGE (necessário para skybox).
    
    Retorna o identificador da textura ou 0 em caso de erro.
    """
    try:
        imagem = Image.open(caminho_imagem)
    except Exception as erro:
        print(f"Erro ao carregar {caminho_imagem}: {erro}")
        return 0

    imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)
    if caminho_imagem.lower().endswith('.tga'):
        imagem = imagem.convert("RGBA")
        modo = GL_RGBA
    else:
        imagem = imagem.convert("RGB")
        modo = GL_RGB

    dados_imagem = imagem.tobytes()
    largura, altura = imagem.size

    id_textura = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, id_textura)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, modo, largura, altura, 0, modo, GL_UNSIGNED_BYTE, dados_imagem)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    if skybox:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return id_textura

def configurar_opengl():
    """
    Configura os estados iniciais do OpenGL:
      - Ativa teste de profundidade e texturização.
      - Configura o sistema de iluminação: luz principal (simulando sol poente)
        e luz de preenchimento para evitar sombras excessivas.
      - Define o ambiente de textura para modulação com a iluminação.
    """
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)

    # Configuração da Luz Principal (GL_LIGHT0)
    glEnable(GL_LIGHT0)
    cor_ambiente_principal = [0.3, 0.2, 0.1, 1.0]
    cor_diffusa_principal = [1.0, 0.6, 0.2, 1.0]
    cor_especular_principal = [1.0, 0.6, 0.2, 1.0]
    posicao_luz_principal = [-50.0, 50.0, 0.0, 0.0]  # luz direcional (w = 0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, cor_ambiente_principal)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, cor_diffusa_principal)
    glLightfv(GL_LIGHT0, GL_SPECULAR, cor_especular_principal)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz_principal)

    # Configuração da Luz de Preenchimento (GL_LIGHT1)
    glEnable(GL_LIGHT1)
    cor_ambiente_preenchimento = [0.4, 0.3, 0.2, 1.0]
    cor_diffusa_preenchimento = [0.6, 0.4, 0.3, 1.0]
    cor_especular_preenchimento = [0.6, 0.4, 0.3, 1.0]
    posicao_luz_preenchimento = [50.0, 30.0, 0.0, 0.0]
    glLightfv(GL_LIGHT1, GL_AMBIENT, cor_ambiente_preenchimento)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, cor_diffusa_preenchimento)
    glLightfv(GL_LIGHT1, GL_SPECULAR, cor_especular_preenchimento)
    glLightfv(GL_LIGHT1, GL_POSITION, posicao_luz_preenchimento)

    # Luz Ambiente Global
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

def interpolacao_catmull_rom(p0, p1, p2, p3, t):
    """
    Realiza a interpolação Catmull-Rom para gerar um ponto na curva.
    
    p0, p1, p2, p3: pontos de controle (cada um uma tupla com duas coordenadas).
    t: parâmetro de interpolação, variando de 0 a 1.
    
    Retorna uma tupla (x, z) representando o ponto interpolado.
    """
    t2 = t * t
    t3 = t2 * t
    x = 0.5 * ((2 * p1[0]) +
               (-p0[0] + p2[0]) * t +
               (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
               (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
    z = 0.5 * ((2 * p1[1]) +
               (-p0[1] + p2[1]) * t +
               (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
               (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
    return (x, z)
