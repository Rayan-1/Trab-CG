# skybox.py
"""
Este módulo gerencia o carregamento e desenho do skybox,
que é uma caixa que envolve toda a cena para simular um ambiente infinito.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import config
import utils

def carregar_texturas_skybox():
    """
    Carrega as texturas do skybox para cada face:
      - frente, trás, direita, esquerda, cima e baixo.
    
    As texturas são carregadas com a opção 'skybox=True' para configurar o wrap mode.
    """
    config.textura_frente   = utils.carregar_textura("assets/skybox/front.tga", True)
    config.textura_tras     = utils.carregar_textura("assets/skybox/back.tga", True)
    config.textura_direita  = utils.carregar_textura("assets/skybox/right.tga", True)
    config.textura_esquerda = utils.carregar_textura("assets/skybox/left.tga", True)
    config.textura_cima     = utils.carregar_textura("assets/skybox/up.tga", True)
    config.textura_baixo    = utils.carregar_textura("assets/skybox/bottom.tga", True)

def desenhar_skybox():
    """
    Desenha o skybox com cada face texturizada.
    
    A câmera é transladada para a posição atual (para manter o skybox centralizado),
    e a profundidade é desabilitada temporariamente para evitar conflitos de renderização.
    A iluminação global é aplicada, permitindo que as faces opostas à luz fiquem mais claras.
    """
    glPushMatrix()
    glDepthMask(GL_FALSE)  # Desativa a escrita no buffer de profundidade
    # Translada o skybox para a posição da câmera (mantendo a ilusão de infinito)
    glTranslatef(config.pos_camera[0], config.pos_camera[1], config.pos_camera[2])
    tamanho = config.TAMANHO_SKYBOX / 2.0

    glEnable(GL_TEXTURE_2D)
    
    # Face frontal (vista: -Z)
    glBindTexture(GL_TEXTURE_2D, config.textura_frente)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-tamanho, -tamanho, -tamanho)
    glTexCoord2f(1, 0); glVertex3f(tamanho, -tamanho, -tamanho)
    glTexCoord2f(1, 1); glVertex3f(tamanho, tamanho, -tamanho)
    glTexCoord2f(0, 1); glVertex3f(-tamanho, tamanho, -tamanho)
    glEnd()

    # Face traseira (vista: +Z)
    glBindTexture(GL_TEXTURE_2D, config.textura_tras)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(tamanho, -tamanho, tamanho)
    glTexCoord2f(1, 0); glVertex3f(-tamanho, -tamanho, tamanho)
    glTexCoord2f(1, 1); glVertex3f(-tamanho, tamanho, tamanho)
    glTexCoord2f(0, 1); glVertex3f(tamanho, tamanho, tamanho)
    glEnd()

    # Face esquerda (vista: -X)
    glBindTexture(GL_TEXTURE_2D, config.textura_esquerda)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-tamanho, -tamanho, tamanho)
    glTexCoord2f(1, 0); glVertex3f(-tamanho, -tamanho, -tamanho)
    glTexCoord2f(1, 1); glVertex3f(-tamanho, tamanho, -tamanho)
    glTexCoord2f(0, 1); glVertex3f(-tamanho, tamanho, tamanho)
    glEnd()

    # Face direita (vista: +X)
    glBindTexture(GL_TEXTURE_2D, config.textura_direita)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(tamanho, -tamanho, -tamanho)
    glTexCoord2f(1, 0); glVertex3f(tamanho, -tamanho, tamanho)
    glTexCoord2f(1, 1); glVertex3f(tamanho, tamanho, tamanho)
    glTexCoord2f(0, 1); glVertex3f(tamanho, tamanho, -tamanho)
    glEnd()

    # Face superior (vista: +Y)
    glBindTexture(GL_TEXTURE_2D, config.textura_cima)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-tamanho, tamanho, -tamanho)
    glTexCoord2f(1, 0); glVertex3f(tamanho, tamanho, -tamanho)
    glTexCoord2f(1, 1); glVertex3f(tamanho, tamanho, tamanho)
    glTexCoord2f(0, 1); glVertex3f(-tamanho, tamanho, tamanho)
    glEnd()

    # Face inferior (vista: -Y)
    glBindTexture(GL_TEXTURE_2D, config.textura_baixo)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-tamanho, -tamanho, tamanho)
    glTexCoord2f(1, 0); glVertex3f(tamanho, -tamanho, tamanho)
    glTexCoord2f(1, 1); glVertex3f(tamanho, -tamanho, -tamanho)
    glTexCoord2f(0, 1); glVertex3f(-tamanho, -tamanho, -tamanho)
    glEnd()

    glDepthMask(GL_TRUE)  # Reativa a escrita no buffer de profundidade
    glPopMatrix()
