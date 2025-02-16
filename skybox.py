from OpenGL.GL import *
from OpenGL.GLU import *
import config
import utils

def carregar_texturas_skybox():
    """
    Carrega as texturas do skybox.
    """
    config.textura_frente   = utils.carregar_textura("assets/skybox/front.tga", True)
    config.textura_tras     = utils.carregar_textura("assets/skybox/back.tga", True)
    config.textura_direita  = utils.carregar_textura("assets/skybox/right.tga", True)
    config.textura_esquerda = utils.carregar_textura("assets/skybox/left.tga", True)
    config.textura_cima     = utils.carregar_textura("assets/skybox/up.tga", True)
    config.textura_baixo    = utils.carregar_textura("assets/skybox/bottom.tga", True)
    

def desenhar_skybox():
    """
    Desenha o skybox com as faces texturizadas.
    O skybox é sempre centrado na posição da câmera (config.pos_camera).
    """
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glDepthMask(GL_FALSE)
    glTranslatef(config.pos_camera[0], config.pos_camera[1], config.pos_camera[2])
    t = config.TAMANHO_SKYBOX / 2.0

    glEnable(GL_TEXTURE_2D)
    
    # Face frontal (vista: -Z)
    glBindTexture(GL_TEXTURE_2D, config.textura_frente)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-t, -t, -t)
    glTexCoord2f(1, 0); glVertex3f( t, -t, -t)
    glTexCoord2f(1, 1); glVertex3f( t,  t, -t)
    glTexCoord2f(0, 1); glVertex3f(-t,  t, -t)
    glEnd()

    # Face traseira (vista: +Z)
    glBindTexture(GL_TEXTURE_2D, config.textura_tras)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f( t, -t, t)
    glTexCoord2f(1, 0); glVertex3f(-t, -t, t)
    glTexCoord2f(1, 1); glVertex3f(-t,  t, t)
    glTexCoord2f(0, 1); glVertex3f( t,  t, t)
    glEnd()

    # Face esquerda (vista: -X)
    glBindTexture(GL_TEXTURE_2D, config.textura_esquerda)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-t, -t, t)
    glTexCoord2f(1, 0); glVertex3f(-t, -t, -t)
    glTexCoord2f(1, 1); glVertex3f(-t,  t, -t)
    glTexCoord2f(0, 1); glVertex3f(-t,  t, t)
    glEnd()

    # Face direita (vista: +X)
    glBindTexture(GL_TEXTURE_2D, config.textura_direita)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(t, -t, -t)
    glTexCoord2f(1, 0); glVertex3f(t, -t, t)
    glTexCoord2f(1, 1); glVertex3f(t,  t, t)
    glTexCoord2f(0, 1); glVertex3f(t,  t, -t)
    glEnd()

    # Face superior (vista: +Y)
    glBindTexture(GL_TEXTURE_2D, config.textura_cima)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-t, t, -t)
    glTexCoord2f(1, 0); glVertex3f(t, t, -t)
    glTexCoord2f(1, 1); glVertex3f(t, t, t)
    glTexCoord2f(0, 1); glVertex3f(-t, t, t)
    glEnd()

    # Face inferior (vista: -Y)
    glBindTexture(GL_TEXTURE_2D, config.textura_baixo)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-t, -t, t)
    glTexCoord2f(1, 0); glVertex3f(t, -t, t)
    glTexCoord2f(1, 1); glVertex3f(t, -t, -t)
    glTexCoord2f(0, 1); glVertex3f(-t, -t, -t)
    glEnd()

    glDepthMask(GL_TRUE)
    glEnable(GL_LIGHTING)
    glPopMatrix()
