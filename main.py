import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pista import desenha_chao, redimensiona 

def inicio():
    glClearColor(0.53, 0.81, 0.98, 1)  # Cor do fundo (azul claro)
    glPointSize(10)

    # Ativa o antialiasing
    glEnable(GL_MULTISAMPLE)  # Habilita o antialiasing com múltiplos samples
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)  # Melhora a qualidade do antialiasing

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    inicio()

    # Ajusta a projeção inicial
    redimensiona(display[0], display[1])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            # Verifica o evento de redimensionamento da janela
            if event.type == VIDEORESIZE:
                redimensiona(event.w, event.h)  # Atualiza a projeção com o novo tamanho da janela

        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        desenha_chao()

        pygame.display.flip()  
        pygame.time.wait(10)  

if __name__ == "__main__":
    main()
