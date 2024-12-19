from OpenGL.GL import *
from OpenGL.GLU import *

def desenha_chao(posicao_moto):
    # Pista contínua
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.5, 0.5)  # Cor cinza para a pista
    
    # Parte principal da pista
    glVertex3f(-5, -1, posicao_moto[2] + 5)
    glVertex3f(5, -1, posicao_moto[2] + 5)
    glVertex3f(5, -1, posicao_moto[2] - 50)  # Faz a pista "ir para o infinito"
    glVertex3f(-5, -1, posicao_moto[2] - 50)  # Parte direita da pista
    glEnd()
    
    # Desenho das faixas de pedestres (linhas brancas no meio da pista)
    glLineWidth(3)
    glColor3f(1, 1, 1)  # Faixa branca
    for i in range(-5, 5, 2):  # Desenha faixas em intervalos de 2 unidades
        glBegin(GL_LINES)
        glVertex3f(i, -0.9, posicao_moto[2] + 5)
        glVertex3f(i, -0.9, posicao_moto[2] - 50)
        glEnd()

    # Desenho das linhas centrais
    glLineWidth(2)
    glColor3f(1, 1, 0)  # Linha amarela no meio
    for i in range(-5, 5, 2):  # Alterna as linhas amarelas no centro
        glBegin(GL_LINES)
        glVertex3f(i, -0.8, posicao_moto[2])
        glVertex3f(i, -0.8, posicao_moto[2] - 50)
        glEnd()

def desenha_pista_continua(posicao_moto):
    # Reposiciona a pista para criar o efeito de continuidade
    if posicao_moto[2] < -50:
        posicao_moto[2] = 5  # Reposiciona a moto e a pista ao iniciar novamente
    desenha_chao(posicao_moto)  # Desenha o chão

def redimensiona(tela_largura, tela_altura):
    glViewport(0, 0, tela_largura, tela_altura)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (tela_largura / tela_altura), 0.1, 100.0)  # FOV e plano de corte ajustados
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def ajusta_camera(posicao_moto):
    glLoadIdentity()
    gluLookAt(posicao_moto[0], posicao_moto[1] + 0.5, posicao_moto[2] + 2,  # Posição da câmera
              posicao_moto[0], posicao_moto[1], posicao_moto[2],  # Para onde a câmera está olhando
              0, 1, 0)  # Vetor 'up' da câmera