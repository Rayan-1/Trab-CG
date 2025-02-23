# obstaculos.py
"""
Este módulo gerencia os obstáculos do jogo.
Contém funções para desenhar blocos (obstáculos), rampas e objetos 3D (pedras),
além de funções para verificação de colisões (tanto horizontal quanto com pedras).

Nota: Funções de geração de obstáculos que não são utilizadas foram removidas.
"""

from OpenGL.GL import *
import math
import random
import config
import controller
import glm

def desenhar_lista_objetos_pedra(modelo: dict, objeto: dict):
    """
    Desenha o objeto 3D representando uma pedra, usando o modelo carregado.
    
    Parâmetros:
      - modelo: dicionário com os dados do objeto 3D (vértices, display list, etc.);
      - objeto: dicionário com as chaves 'x', 'z' (posição no plano) e 'tamanho' (fator de escala).
    
    A pedra é desenhada repousando no chão (nível da pista) e sem rotação extra.
    """
    x = objeto['x']
    z = objeto['z']
    fator_escala = objeto['tamanho']
    y = config.nível_pista  # assume que a pedra repousa sobre o chão
    posicao = glm.vec3(x, y, z)
    
    glPushMatrix()
    glTranslatef(posicao.x, posicao.y, posicao.z)
    glScalef(fator_escala, fator_escala, fator_escala)
    # Se necessário, pode ser aplicada uma rotação para corrigir a orientação do modelo
    controller.desenhar_objeto_carregado(modelo)
    glPopMatrix()

def verificar_colisao_horizontal_obstaculo(pos_objeto, tamanho, lista_obstaculos):
    """
    Verifica colisões horizontais (no plano XZ) entre o objeto e obstáculos do tipo bloco.
    
    pos_objeto: lista [x, y, z] representando a posição do objeto.
    tamanho: tamanho de referência do objeto (usado para definir o bounding box).
    
    Retorna o obstáculo com o qual há colisão ou None.
    """
    meio = tamanho / 2
    c_minx = pos_objeto[0] - meio
    c_maxx = pos_objeto[0] + meio
    c_minz = pos_objeto[2] - meio
    c_maxz = pos_objeto[2] + meio
    for obs in lista_obstaculos:
        o_minx = obs['x'] - obs['largura'] / 2
        o_maxx = obs['x'] + obs['largura'] / 2
        o_minz = obs['z'] - obs['profundidade'] / 2
        o_maxz = obs['z'] + obs['profundidade'] / 2
        if ((c_minx < o_maxx) and (c_maxx > o_minx) and
            (c_minz < o_maxz) and (c_maxz > o_minz)):
            # Verifica também se a altura do objeto colide com o obstáculo
            if pos_objeto[1] - meio < obs['altura'] + config.nível_chão:
                return obs
    return None

def verificar_colisao_pedra(pos_objeto, tamanho_moto, lista_objetos_pedra):
    """
    Verifica colisão horizontal (plano XZ) entre a moto e as pedras.
    
    A colisão é calculada usando bounding boxes quadrados centrados na posição do objeto.
    
    Parâmetros:
      - pos_objeto: [x, y, z] posição da moto.
      - tamanho_moto: tamanho de referência da moto.
      - lista_objetos_pedra: lista de dicionários com 'x', 'z' e 'tamanho' para cada pedra.
      
    Retorna o objeto em colisão ou None.
    """
    meio_moto = tamanho_moto / 2.0
    moto_min_x = pos_objeto[0] - meio_moto
    moto_max_x = pos_objeto[0] + meio_moto
    moto_min_z = pos_objeto[2] - meio_moto
    moto_max_z = pos_objeto[2] + meio_moto

    for objeto in lista_objetos_pedra:
        meio_objeto = objeto['tamanho'] / 2.0
        objeto_min_x = objeto['x'] - meio_objeto
        objeto_max_x = objeto['x'] + meio_objeto
        objeto_min_z = objeto['z'] - meio_objeto
        objeto_max_z = objeto['z'] + meio_objeto
        if (moto_min_x < objeto_max_x and moto_max_x > objeto_min_x and
            moto_min_z < objeto_max_z and moto_max_z > objeto_min_z):
            return objeto
    return None

def desenhar_obstaculo(obstaculo):
    """
    Desenha um obstáculo (bloco) com material e textura.
    A base do obstáculo é posicionada em config.nível_chão.
    
    Parâmetros do obstáculo (dicionário):
      - 'x', 'z': posição central;
      - 'largura', 'profundidade': dimensões do bloco;
      - 'altura': altura do bloco.
    """
    glPushMatrix()
    # Define propriedades de material para o obstáculo
    material_ambiente = [0.2, 0.2, 0.2, 1.0]
    material_diffuso  = [1.0, 1.0, 1.0, 1.0]
    material_especular = [0.3, 0.3, 0.3, 1.0]
    brilho = [30.0]
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambiente)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuso)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_especular)
    glMaterialfv(GL_FRONT, GL_SHININESS, brilho)
    
    # Liga a textura configurada para obstáculos
    glBindTexture(GL_TEXTURE_2D, config.textura_obstaculo)
    x = obstaculo['x']
    z = obstaculo['z']
    largura = obstaculo['largura']
    profundidade = obstaculo['profundidade']
    altura = obstaculo['altura']
    meio_largura = largura / 2
    meio_profundidade = profundidade / 2
    # Calcula a posição vertical para centralizar o bloco (em y)
    y_centro = config.nível_chão + (altura / 2)
    
    glTranslatef(x, y_centro, z)
    glBegin(GL_QUADS)
    # Face frontal
    glTexCoord2f(0, 0); glVertex3f(-meio_largura, -altura/2, meio_profundidade)
    glTexCoord2f(1, 0); glVertex3f(meio_largura, -altura/2, meio_profundidade)
    glTexCoord2f(1, 1); glVertex3f(meio_largura, altura/2, meio_profundidade)
    glTexCoord2f(0, 1); glVertex3f(-meio_largura, altura/2, meio_profundidade)
    # Face traseira
    glTexCoord2f(0, 0); glVertex3f(-meio_largura, -altura/2, -meio_profundidade)
    glTexCoord2f(1, 0); glVertex3f(-meio_largura, altura/2, -meio_profundidade)
    glTexCoord2f(1, 1); glVertex3f(meio_largura, altura/2, -meio_profundidade)
    glTexCoord2f(0, 1); glVertex3f(meio_largura, -altura/2, -meio_profundidade)
    # Face esquerda
    glTexCoord2f(0, 0); glVertex3f(-meio_largura, -altura/2, -meio_profundidade)
    glTexCoord2f(1, 0); glVertex3f(-meio_largura, -altura/2, meio_profundidade)
    glTexCoord2f(1, 1); glVertex3f(-meio_largura, altura/2, meio_profundidade)
    glTexCoord2f(0, 1); glVertex3f(-meio_largura, altura/2, -meio_profundidade)
    # Face direita
    glTexCoord2f(0, 0); glVertex3f(meio_largura, -altura/2, -meio_profundidade)
    glTexCoord2f(1, 0); glVertex3f(meio_largura, altura/2, -meio_profundidade)
    glTexCoord2f(1, 1); glVertex3f(meio_largura, altura/2, meio_profundidade)
    glTexCoord2f(0, 1); glVertex3f(meio_largura, -altura/2, meio_profundidade)
    # Face superior
    glTexCoord2f(0, 0); glVertex3f(-meio_largura, altura/2, -meio_profundidade)
    glTexCoord2f(1, 0); glVertex3f(-meio_largura, altura/2, meio_profundidade)
    glTexCoord2f(1, 1); glVertex3f(meio_largura, altura/2, meio_profundidade)
    glTexCoord2f(0, 1); glVertex3f(meio_largura, altura/2, -meio_profundidade)
    # Face inferior
    glTexCoord2f(0, 0); glVertex3f(-meio_largura, -altura/2, -meio_profundidade)
    glTexCoord2f(1, 0); glVertex3f(meio_largura, -altura/2, -meio_profundidade)
    glTexCoord2f(1, 1); glVertex3f(meio_largura, -altura/2, meio_profundidade)
    glTexCoord2f(0, 1); glVertex3f(-meio_largura, -altura/2, meio_profundidade)
    glEnd()
    glPopMatrix()


def desenhar_rampa(rampa):
    """
    Desenha uma rampa com material e textura.
    A rampa é definida a partir de um ponto central e orientação.
    """
    profundidade = rampa['profundidade']
    meio_profundidade = profundidade / 2
    meio_largura = config.largura_pista / 2  # a rampa ocupa toda a largura da pista
    cx, cz = rampa['x'], rampa['z']
    theta = rampa['orientacao']
    
    def altura_rampa(u, v):
        return rampa['altura_maxima'] * (1 - (2*u/profundidade)**2) * (1 - (2*v/config.largura_pista)**2)
    
    subdivisoes_u = 12
    subdivisoes_v = 10
    du = profundidade / subdivisoes_u
    dv = config.largura_pista / subdivisoes_v

    malha = []
    for i in range(subdivisoes_u + 1):
        linha = []
        u = -meio_profundidade + i * du
        for j in range(subdivisoes_v + 1):
            v = -meio_largura + j * dv
            h = altura_rampa(u, v)
            x_mundial = cx + u * math.cos(theta) - v * math.sin(theta)
            z_mundial = cz + u * math.sin(theta) + v * math.cos(theta)
            linha.append((x_mundial, config.nível_chão + h - config.deslocamento_rampa, z_mundial))
        malha.append(linha)
    
    # Configura material para a rampa
    material_ambiente = [0.3, 0.3, 0.3, 1.0]
    material_diffuso  = [1.0, 1.0, 1.0, 1.0]
    material_especular = [0.2, 0.2, 0.2, 1.0]
    brilho = [40.0]
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambiente)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuso)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_especular)
    glMaterialfv(GL_FRONT, GL_SHININESS, brilho)
    
    glBindTexture(GL_TEXTURE_2D, config.textura_rampa)
    
    # Desenha o topo da rampa (malha de quads)
    for i in range(subdivisoes_u):
        glBegin(GL_QUAD_STRIP)
        for j in range(subdivisoes_v + 1):
            s = j / subdivisoes_v
            t_coord = i / subdivisoes_u
            glTexCoord2f(s, t_coord)
            glVertex3f(*malha[i][j])
            glTexCoord2f(s, t_coord + 1/subdivisoes_u)
            glVertex3f(*malha[i+1][j])
        glEnd()