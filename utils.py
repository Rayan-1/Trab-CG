from OpenGL.GL import *
from PIL import Image
import math

def carregar_textura(caminho_imagem: str) -> int:
    """
    Carrega uma imagem e cria uma textura OpenGL.
    Se a extensão for .tga, utiliza RGBA; caso contrário, utiliza RGB.
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
    return id_textura

def configurar_opengl():
    """
    Configura os estados iniciais do OpenGL, incluindo teste de profundidade,
    texturas e iluminação Phong.
    """
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    # Configuração da iluminação Phong (pipeline fixo)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glShadeModel(GL_SMOOTH)
    luz_ambiente = [0.2, 0.2, 0.2, 1.0]
    luz_diffusa  = [0.8, 0.8, 0.8, 1.0]
    luz_especular= [1.0, 1.0, 1.0, 1.0]
    posicao_luz  = [0.0, 50.0, 0.0, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_diffusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    # Modulação de textura com iluminação
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

def interpolacao_catmull_rom(p0, p1, p2, p3, t):
    """
    Realiza a interpolação Catmull-Rom 2D e retorna um ponto (x, z).
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
