import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

def desenha_roda(x, y, z, raio, largura):
    """Desenha uma roda da moto como um cilindro."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(90, 1, 0, 0)  # Gira o cilindro para ficar na orientação correta
    glColor3f(0, 0, 0)  # Preto para as rodas
    quadric = gluNewQuadric()
    gluCylinder(quadric, raio, raio, largura, 32, 32)
    glPopMatrix()

def desenha_cubo(x, y, z, largura, altura, profundidade, cor):
    """Desenha um cubo para representar partes da moto."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3fv(cor)
    glScalef(largura, altura, profundidade)

    glBegin(GL_QUADS)

    # Face frontal
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)

    # Face traseira
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)

    # Face esquerda
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)

    # Face direita
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)

    # Face superior
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)

    # Face inferior
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glEnd()
    glPopMatrix()

def desenha_moto():
    """Desenha uma moto simples com cubos e cilindros."""
    # Rodas da moto
    desenha_roda(-0.5, -0.8, -8, 0.2, 0.1)  # Roda traseira
    desenha_roda(0.5, -0.8, -8, 0.2, 0.1)   # Roda dianteira

    # Corpo da moto
    desenha_cubo(0, -0.6, -8, 1, 0.3, 0.2, (1, 0, 0))  # Corpo principal (vermelho)

    # Assento
    desenha_cubo(0, -0.5, -8, 0.6, 0.2, 0.3, (0.2, 0.2, 0.2))  # Assento (cinza escuro)

    # Guidão
    desenha_cubo(0.5, -0.4, -7.9, 0.3, 0.1, 0.1, (0, 0, 1))  # Guidão direito (azul)
    desenha_cubo(-0.5, -0.4, -7.9, 0.3, 0.1, 0.1, (0, 0, 1))  # Guidão esquerdo (azul)
    
def mover_moto(keys, posicao):
    """Move a moto com base nas teclas pressionadas."""
    if keys[pygame.K_LEFT]:
        posicao[0] -= 0.1
    if keys[pygame.K_RIGHT]:
        posicao[0] += 0.1
    if keys[pygame.K_DOWN]:
        posicao[2] += 0.1 
    if keys[pygame.K_UP]:
        posicao[2] -= 0.1