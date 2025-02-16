from OpenGL.GL import *
import math
import random
import config
import utils

def verificar_colisao_horizontal_obstaculo(pos_objeto, tamanho, lista_obstaculos):
    """
    Verifica colisões horizontais (x, z) do objeto com os obstáculos.
    Retorna o obstáculo em colisão (se houver) ou None.
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
            if pos_objeto[1] - meio < obs['altura'] + config.nível_chão:
                return obs
    return None

def desenhar_obstaculo(obstaculo):
    """
    Desenha um obstáculo (bloco) com material e textura.
    A base do obstáculo é posicionada em config.nível_chão.
    """
    glPushMatrix()
    material_ambiente = [0.2, 0.2, 0.2, 1.0]
    material_diffuso  = [1.0, 1.0, 1.0, 1.0]
    material_especular = [0.3, 0.3, 0.3, 1.0]
    brilho = [30.0]
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambiente)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuso)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_especular)
    glMaterialfv(GL_FRONT, GL_SHININESS, brilho)
    
    glBindTexture(GL_TEXTURE_2D, config.textura_obstaculo)
    glColor3f(1.0, 1.0, 1.0)
    
    x = obstaculo['x']
    z = obstaculo['z']
    largura = obstaculo['largura']
    profundidade = obstaculo['profundidade']
    altura = obstaculo['altura']
    meio_largura = largura / 2
    meio_profundidade = profundidade / 2
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

def gerar_obstaculos():
    """
    Gera uma lista de obstáculos (blocos) posicionados aleatoriamente na pista,
    garantindo um espaçamento mínimo entre eles.
    """
    obstaculos = []
    n = len(config.pontos_centro_pista)
    min_intervalo = n // (10 * 2)
    indices_escolhidos = []
    tentativas = 0
    while len(indices_escolhidos) < 10 and tentativas < 1000:
        idx = random.randint(0, n - 2)
        if all(min(abs(idx - outro), n - abs(idx - outro)) >= min_intervalo for outro in indices_escolhidos):
            indices_escolhidos.append(idx)
        tentativas += 1
    for idx in indices_escolhidos:
        cx, cz = config.pontos_centro_pista[idx]
        pt_anterior = config.pontos_centro_pista[idx - 1]
        pt_proximo = config.pontos_centro_pista[(idx + 1) % n]
        dx = pt_proximo[0] - pt_anterior[0]
        dz = pt_proximo[1] - pt_anterior[1]
        comprimento = math.hypot(dx, dz)
        if comprimento != 0:
            nx = -dz / comprimento
            nz = dx / comprimento
        else:
            nx, nz = 0, 0
        max_offset = (config.largura_pista / 2) - (config.tamanho_moto * 2 / 2) - 1.0
        offset = random.uniform(0.5, max_offset)
        if random.choice([True, False]):
            offset = -offset
        ox = cx + offset * nx
        oz = cz + offset * nz
        altura_obs = random.uniform(config.tamanho_moto, config.tamanho_moto * 4.0)
        obstaculos.append({
            'x': ox,
            'z': oz,
            'largura': config.tamanho_moto * 2.0,
            'profundidade': config.tamanho_moto * 2.0,
            'altura': altura_obs
        })
    return obstaculos

def gerar_rampas():
    """
    Gera uma lista de rampas posicionadas aleatoriamente na pista.
    Cada rampa é definida a partir de um ponto central e orientação dada pela tangente.
    """
    rampas = []
    n = len(config.pontos_centro_pista)
    min_intervalo = n // (12 * 2)
    indices_escolhidos = []
    tentativas = 0
    while len(indices_escolhidos) < 12 and tentativas < 1000:
        idx = random.randint(0, n - 2)
        if all(min(abs(idx - outro), n - abs(idx - outro)) >= min_intervalo for outro in indices_escolhidos):
            indices_escolhidos.append(idx)
        tentativas += 1
    for idx in indices_escolhidos:
        cx, cz = config.pontos_centro_pista[idx]
        pt_anterior = config.pontos_centro_pista[idx - 1]
        pt_proximo = config.pontos_centro_pista[(idx + 1) % n]
        dx = pt_proximo[0] - pt_anterior[0]
        dz = pt_proximo[1] - pt_anterior[1]
        theta = math.atan2(dx, dz)  # orientação da rampa
        variacao = random.uniform(-0.2, 0.2)
        rampas.append({
            'x': cx,
            'z': cz,
            'profundidade': 20.0,
            'altura_maxima': 3.5,
            'orientacao': theta + variacao
        })
    return rampas

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
    glColor3f(1.0, 1.0, 1.0)
    
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
