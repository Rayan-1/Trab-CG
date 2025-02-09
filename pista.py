from OpenGL.GL import *
import math
import utils
import config

def carregar_texturas_chao():
    """
    Carrega as texturas para o chão a partir de arquivos de imagem.
    """
    arquivos = ["assets/floor01.jpg", "assets/floor02.jpg"]
    for arq in arquivos:
        tex = utils.carregar_textura(arq)
        if tex != 0:
            config.lista_texturas_chao.append(tex)
    if not config.lista_texturas_chao:
        print("Nenhuma textura do chão foi carregada.")

def carregar_textura_pista():
    """
    Carrega a textura para a pista.
    """
    config.textura_pista = utils.carregar_textura("assets/obstaculo.jpg")

def gerar_pontos_pista(num_pontos):
    """
    Gera pontos interpolados ao longo da pista usando os pontos-chave.
    Atualiza a lista config.pontos_centro_pista.
    """
    pts = []
    pontos = config.pontos_chave
    n = len(pontos)
    segmentos = n  
    amostras_por_segmento = num_pontos // segmentos
    for i in range(segmentos):
        p0 = pontos[(i - 1) % n]
        p1 = pontos[i]
        p2 = pontos[(i + 1) % n]
        p3 = pontos[(i + 2) % n]
        for j in range(amostras_por_segmento):
            t = j / amostras_por_segmento
            pts.append(utils.interpolacao_catmull_rom(p0, p1, p2, p3, t))
    pts.append(pts[0])
    config.pontos_centro_pista[:] = pts

def desenhar_chao():
    """
    Desenha o chão como uma malha (grid) texturizada que se estende por EXTENSAO_CHAO.
    """
    glPushMatrix()
    pos_y = config.nível_chão

    subdivisoes = 20
    tamanho_total = config.EXTENSAO_CHAO
    passo = tamanho_total / subdivisoes
    inicio = -tamanho_total / 2.0

    num_texturas = len(config.lista_texturas_chao) if config.lista_texturas_chao else 1
    alpha = 5.0 / num_texturas

    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    for i in range(subdivisoes):
        for j in range(subdivisoes):
            x0 = inicio + i * passo
            z0 = inicio + j * passo
            x1 = x0 + passo
            z1 = z0 + passo
            for tex in config.lista_texturas_chao:
                glBindTexture(GL_TEXTURE_2D, tex)
                glColor4f(1.0, 1.0, 1.0, alpha)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex3f(x0, pos_y, z0)
                glTexCoord2f(1, 0); glVertex3f(x1, pos_y, z0)
                glTexCoord2f(1, 1); glVertex3f(x1, pos_y, z1)
                glTexCoord2f(0, 1); glVertex3f(x0, pos_y, z1)
                glEnd()
            glColor4f(1.0, 1.0, 1.0, 1.0)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def desenhar_pista():
    """
    Desenha a pista utilizando um quad strip com a textura e iluminação apropriadas.
    """
    # Configura material da pista
    material_ambiente = [0.2, 0.2, 0.2, 1.0]
    material_diffuso  = [1.0, 1.0, 1.0, 1.0]
    material_especular = [0.1, 0.1, 0.1, 1.0]
    brilho = [50.0]
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambiente)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuso)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_especular)
    glMaterialfv(GL_FRONT, GL_SHININESS, brilho)
    
    glBindTexture(GL_TEXTURE_2D, config.textura_pista)
    glColor3f(1.0, 1.0, 1.0)
    
    glNormal3f(0, 1, 0)
    glBegin(GL_QUAD_STRIP)
    n = len(config.pontos_centro_pista)
    escala_textura = 0.1
    for i in range(n):
        (cx, cz) = config.pontos_centro_pista[i]
        pt_anterior = config.pontos_centro_pista[i - 1]
        pt_proximo = config.pontos_centro_pista[(i + 1) % n]
        dx = pt_proximo[0] - pt_anterior[0]
        dz = pt_proximo[1] - pt_anterior[1]
        comprimento = math.hypot(dx, dz)
        if comprimento != 0:
            nx = -dz / comprimento
            nz = dx / comprimento
        else:
            nx, nz = 0, 0
        x_externo = cx + (config.largura_pista / 2) * nx
        z_externo = cz + (config.largura_pista / 2) * nz
        x_interno = cx - (config.largura_pista / 2) * nx
        z_interno = cz - (config.largura_pista / 2) * nz
        
        glTexCoord2f(x_externo * escala_textura, z_externo * escala_textura)
        glVertex3f(x_externo, config.nível_pista, z_externo)
        glTexCoord2f(x_interno * escala_textura, z_interno * escala_textura)
        glVertex3f(x_interno, config.nível_pista, z_interno)
    glEnd()
