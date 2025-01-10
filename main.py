import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from pista import desenha_chao, redimensiona, ajusta_camera, desenha_pista_continua
from moto import desenha_moto, mover_moto
from obj import carregar_objeto, desenhar_objeto

def inicio():
    """Configurações iniciais para a cena, incluindo cor de fundo e antialiasing."""
    glClearColor(0.53, 0.81, 0.98, 1)  # Cor do fundo (azul claro)
    glPointSize(10)

    # Ativa o antialiasing
    glEnable(GL_MULTISAMPLE)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    inicio()

    # Substitua 'seu_modelo.obj' pelo caminho para o arquivo OBJ
    caminho_modelo = 'Motorcycle.obj'
    vertices, faces = carregar_objeto(caminho_modelo)

    # Ajusta a projeção inicial
    redimensiona(display[0], display[1])

    # Posição inicial da moto
    posicao_moto = [0, -0.6, -8]  # x, y, z

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == VIDEORESIZE:
                redimensiona(event.w, event.h)

        # Verifica as teclas pressionadas
        keys = pygame.key.get_pressed()
        
        # Mover a moto com base nas teclas pressionadas
        mover_moto(keys, posicao_moto)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Desenha o chão contínuo
        desenha_pista_continua(posicao_moto)

        # Ajusta a câmera para acompanhar a moto
        ajusta_camera(posicao_moto)

        # Desenha a moto na posição atual
        glPushMatrix()
        glTranslatef(posicao_moto[0], posicao_moto[1], posicao_moto[2])  # Move a moto para a posição atual
        glScalef(0.1, 0.1, 0.1)
        # desenha_moto()  # Desenha a moto
        desenhar_objeto(vertices, faces)  # Desenha o modelo
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()