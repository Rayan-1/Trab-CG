from OpenGL.GL import *
from OpenGL.GLU import *

def desenha_chao():
    # Desenha a pista contínua
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.5, 0.5)  # Cor cinza para a pista
    
    # Parte principal da pista
    glVertex3f(-5, -1, 5)
    glVertex3f(5, -1, 5)
    glVertex3f(5, -1, -50)  # Faz a pista "ir para o infinito"
    glVertex3f(-5, -1, -50)  # Parte direita da pista
    glEnd()
    
    # Desenho das faixas de pedestres (linhas brancas no meio da pista)
    glLineWidth(3)
    glColor3f(1, 1, 1)  # Faixa branca
    for i in range(-5, 5, 2):  # Desenha faixas em intervalos de 2 unidades
        glBegin(GL_LINES)
        glVertex3f(i, -0.9, 5)
        glVertex3f(i, -0.9, -50)
        glEnd()

    # Desenho das linhas centrais
    glLineWidth(2)
    glColor3f(1, 1, 0)  # Linha amarela no meio
    for i in range(-5, 5, 2):  # Alterna as linhas amarelas no centro
        glBegin(GL_LINES)
        glVertex3f(i, -0.8, 0)
        glVertex3f(i, -0.8, -50)
        glEnd()

def redimensiona(tela_largura, tela_altura):
    glViewport(0, 0, tela_largura, tela_altura)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (tela_largura / tela_altura), 0.1, 100.0)  # FOV e plano de corte ajustados
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Configura a câmera para uma visão em 3D
    gluLookAt(0, 5, 15,  # Posição da câmera (x, y, z)
              0, 0, -10,  # Ponto para onde a câmera está olhando (centro da pista)
              0, 1, 0)  # Vetor "up" (orientação da câmera) quando a moto andar a pista tbm deve seguir 