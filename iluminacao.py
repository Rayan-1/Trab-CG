from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from obj import desenhar_objeto

def configurar_iluminacao():
    """Configura a iluminação spot para iluminar o objeto e projetar a sombra no chão."""
    glEnable(GL_LIGHTING)  # Habilita a iluminação
    glEnable(GL_LIGHT0)    # Ativa a primeira luz
    glEnable(GL_COLOR_MATERIAL)  # Permite que as cores dos materiais influenciem a luz

    # Configuração da luz spot
    luz_ambiente = [0.3, 0.3, 0.3, 1.0]  # Luz ambiente suave (não escurece o ambiente)
    luz_difusa = [1.0, 1.0, 1.0, 1.0]    # Luz branca intensa (ilumina o objeto)
    luz_especular = [1.0, 1.0, 1.0, 1.0] # Reflexos da luz
    posicao_luz = [5.0, 10.0, 10.0, 1.0]  # Posição da luz (fonte spot)
    direcao_luz = [0.0, -1.0, -1.0]  # Direção da luz (apontando para o objeto)

    # Aplicando a configuração da luz spot
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)  # Luz ambiente suave
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)    # Luz difusa intensa
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular) # Reflexos da luz
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)   # Posição da luz
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, direcao_luz)  # Direção da luz
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 30.0)  # Ângulo de abertura do spot (30 graus)
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 2.0)  # Especifica a suavidade da transição da luz spot

    # Ajuste no material do objeto (sem afetar a cor do ambiente)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])  # Ambiente
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])   # Difusa
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])  # Reflexos
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, [50])  # Intensidade do brilho

def projetar_sombra(vertices, faces, luz_posicao, plano_y=0.0):
    """Projeta a sombra de um objeto no plano y=0."""
    # Matriz de projeção para gerar a sombra
    glPushMatrix()
    
    # Calcular a matriz de projeção da sombra
    sombra = [
        [luz_posicao[1] / (luz_posicao[1] - plano_y), 0.0, 0.0, 0.0],
        [0.0, luz_posicao[2] / (luz_posicao[2] - plano_y), 0.0, 0.0],
        [0.0, 0.0, luz_posicao[3] / (luz_posicao[3] - plano_y), 0.0],
        [0.0, 0.0, 0.0, luz_posicao[0] / (luz_posicao[0] - plano_y)]
    ]

    glMultMatrixf(sombra)  # Aplica a matriz de projeção
    
    # Desenhar a sombra projetada no plano
    glColor4f(0.0, 0.0, 0.0, 0.5)  # Cor da sombra (preto com transparência)
    desenhar_objeto(vertices, faces)  # Desenha o objeto no plano da sombra
    
    glPopMatrix()