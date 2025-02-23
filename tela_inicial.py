# tela_inicial.py
"""
Este módulo apresenta a tela inicial para o mapeamento da pista.
Exibe um preview 2D (vista superior) do circuito e permite que o usuário
registre cliques para definir obstáculos (vermelho), rampas/morros (azul)
ou objetos/pedras (verde) ao longo do percurso.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import config
import utils
import random

def gerar_pontos_mini():
    """
    Gera pontos interpolados para o preview da pista utilizando a interpolação Catmull-Rom.
    Retorna uma lista reduzida de pontos para visualização.
    """
    pontos = config.pontos_chave
    n = len(pontos)
    num_amostras = 100  # Número reduzido para o preview
    pts_mini = []
    amostras_por_segmento = num_amostras // n
    for i in range(n):
        p0 = pontos[(i - 1) % n]
        p1 = pontos[i]
        p2 = pontos[(i + 1) % n]
        p3 = pontos[(i + 2) % n]
        for j in range(amostras_por_segmento):
            t = j / amostras_por_segmento
            pt = utils.interpolacao_catmull_rom(p0, p1, p2, p3, t)
            pts_mini.append(pt)
    pts_mini.append(pts_mini[0])
    return pts_mini

def calcular_bbox(pts):
    """Calcula a caixa delimitadora (bounding box) dos pontos do preview."""
    xs = [pt[0] for pt in pts]
    zs = [pt[1] for pt in pts]
    return min(xs), max(xs), min(zs), max(zs)

def desenhar_track_mini(pts_mini):
    """Desenha a pista do preview como um loop de linhas brancas."""
    glColor3f(1, 1, 1)
    glLineWidth(20)
    glBegin(GL_LINE_LOOP)
    for pt in pts_mini:
        glVertex2f(pt[0], pt[1])
    glEnd()

def desenhar_textura(x, y, largura, altura, textura):
    """
    Desenha um retângulo com a textura informada.
    (x, y) é o centro do retângulo em coordenadas de tela.
    """
    metade_largura = largura / 2
    metade_altura = altura / 2
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textura)
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x - metade_largura, y - metade_altura)
    glTexCoord2f(1, 0); glVertex2f(x + metade_largura, y - metade_altura)
    glTexCoord2f(1, 1); glVertex2f(x + metade_largura, y + metade_altura)
    glTexCoord2f(0, 1); glVertex2f(x - metade_largura, y + metade_altura)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def distancia_ponto_segmento(px, py, x1, y1, x2, y2):
    """
    Calcula a distância do ponto (px,py) ao segmento definido por (x1,y1)-(x2,y2).
    Utiliza a projeção ortogonal para determinar a distância mínima.
    """
    vx = x2 - x1
    vy = y2 - y1
    if vx == 0 and vy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * vx + (py - y1) * vy) / (vx*vx + vy*vy)
    t = max(0, min(1, t))
    proj_x = x1 + t * vx
    proj_y = y1 + t * vy
    return math.hypot(px - proj_x, py - proj_y)

def tela_inicial(janela):
    """
    Exibe a tela inicial para mapeamento do circuito.
    
    Permite que o usuário registre cliques na área do preview da pista para definir:
      - Obstáculos (vermelho),
      - Rampas/morros (azul),
      - Objetos/pedras (verde).
    
    Também exibe botões para selecionar o tipo atual e para iniciar o jogo.
    Retorna três listas: obstaculos, rampas e objetos (pedras) definidos pelo usuário.
    """
    pts_mini = gerar_pontos_mini()
    min_x, max_x, min_z, max_z = calcular_bbox(pts_mini)
    margem = 20  # margem extra para visualização
    vis_left = min_x - margem
    vis_right = max_x + margem
    vis_bottom = min_z - margem
    vis_top = max_z + margem

    window_width, window_height = glfw.get_framebuffer_size(janela)

    # Carrega texturas para fundo e botões
    textura_fundo = utils.carregar_textura("assets/fundo.jpg")
    if textura_fundo == 0:
        textura_fundo = None
    textura_botao_iniciar = utils.carregar_textura("assets/botao_iniciar.jpg")
    textura_botao_obstaculo = utils.carregar_textura("assets/botao_obstaculo.jpg")
    textura_botao_rampa = utils.carregar_textura("assets/botao_rampa.jpg")
    textura_botao_objeto = utils.carregar_textura("assets/botao_objeto.jpg")

    # Define áreas dos botões em coordenadas de tela
    botao_iniciar = {'x': window_width / 2, 'y': 80, 'largura': 250, 'altura': 50}
    botao_obstaculo = {'x': window_width / 2 - 200, 'y': window_height - 80, 'largura': 195, 'altura': 40}
    botao_rampa = {'x': window_width / 2, 'y': window_height - 80, 'largura': 195, 'altura': 40}
    botao_objeto = {'x': window_width / 2 + 200, 'y': window_height - 80, 'largura': 195, 'altura': 40}

    tipo_atual = 0  # 0: obstáculo, 1: rampa, 2: objeto/pedra
    jogo_iniciado = False

    lista_cliques = []  # Armazena cliques: (world_x, world_z, tipo)
    lista_obstaculos_final = []
    lista_rampas_final = []
    lista_objetos_pedra = []

    tolerancia = 10  # Tolerância para considerar clique "na linha" da pista

    def converter_coordenadas(x, y):
        """
        Converte as coordenadas do mouse (em pixels) para o sistema do preview.
        """
        ndc_x = x / window_width
        ndc_y = 1 - y / window_height  # inverte eixo y para origem inferior
        world_x = vis_left + ndc_x * (vis_right - vis_left)
        world_z = vis_bottom + ndc_y * (vis_top - vis_bottom)
        return world_x, world_z

    while not jogo_iniciado and not glfw.window_should_close(janela):
        glfw.poll_events()

        # Processa cliques do mouse
        if glfw.get_mouse_button(janela, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            x, y = glfw.get_cursor_pos(janela)
            pos_mouse_tela = (x, window_height - y)  # coordenadas com origem inferior

            # Verifica clique no botão "Iniciar Jogo"
            bx = botao_iniciar['x']
            by = botao_iniciar['y']
            bw = botao_iniciar['largura']
            bh = botao_iniciar['altura']
            if (pos_mouse_tela[0] >= bx - bw/2 and pos_mouse_tela[0] <= bx + bw/2 and
                pos_mouse_tela[1] >= by - bh/2 and pos_mouse_tela[1] <= by + bh/2):
                jogo_iniciado = True
                glfw.wait_events_timeout(0.2)
                continue

            # Verifica clique nos botões de seleção de tipo
            bx = botao_obstaculo['x']
            by = botao_obstaculo['y']
            bw = botao_obstaculo['largura']
            bh = botao_obstaculo['altura']
            if (pos_mouse_tela[0] >= bx - bw/2 and pos_mouse_tela[0] <= bx + bw/2 and
                pos_mouse_tela[1] >= by - bh/2 and pos_mouse_tela[1] <= by + bh/2):
                tipo_atual = 0
                glfw.wait_events_timeout(0.2)
                continue

            bx = botao_rampa['x']
            by = botao_rampa['y']
            bw = botao_rampa['largura']
            bh = botao_rampa['altura']
            if (pos_mouse_tela[0] >= bx - bw/2 and pos_mouse_tela[0] <= bx + bw/2 and
                pos_mouse_tela[1] >= by - bh/2 and pos_mouse_tela[1] <= by + bh/2):
                tipo_atual = 1
                glfw.wait_events_timeout(0.2)
                continue

            bx = botao_objeto['x']
            by = botao_objeto['y']
            bw = botao_objeto['largura']
            bh = botao_objeto['altura']
            if (pos_mouse_tela[0] >= bx - bw/2 and pos_mouse_tela[0] <= bx + bw/2 and
                pos_mouse_tela[1] >= by - bh/2 and pos_mouse_tela[1] <= by + bh/2):
                tipo_atual = 2
                glfw.wait_events_timeout(0.2)
                continue

            # Se o clique não foi em um botão, verifica se foi na área do preview
            world_x, world_z = converter_coordenadas(x, y)
            if world_x < vis_left or world_x > vis_right or world_z < vis_bottom or world_z > vis_top:
                glfw.wait_events_timeout(0.2)
                continue

            # Verifica se o clique ocorreu próximo da linha da pista
            clicou_na_linha = False
            for i in range(len(pts_mini)-1):
                x1, z1 = pts_mini[i]
                x2, z2 = pts_mini[i+1]
                dist = distancia_ponto_segmento(world_x, world_z, x1, z1, x2, z2)
                if dist <= tolerancia:
                    clicou_na_linha = True
                    break

            if clicou_na_linha:
                lista_cliques.append((world_x, world_z, tipo_atual))
            glfw.wait_events_timeout(0.2)

        # Desenha o fundo (full-screen) utilizando textura ou cor sólida
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if textura_fundo:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, textura_fundo)
            glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(0, 0)
            glTexCoord2f(1, 0); glVertex2f(window_width, 0)
            glTexCoord2f(1, 1); glVertex2f(window_width, window_height)
            glTexCoord2f(0, 1); glVertex2f(0, window_height)
            glEnd()
            glDisable(GL_TEXTURE_2D)
        else:
            glClearColor(0.8, 0.8, 0.8, 1.0)

        # Desenha o preview da pista
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(vis_left, vis_right, vis_bottom, vis_top)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        desenhar_track_mini(pts_mini)

        # Desenha os pontos registrados (com cores distintas para cada tipo)
        for (px, pz, tipo) in lista_cliques:
            if tipo == 0:
                glColor3f(1, 0, 0)  # Obstáculo: vermelho
            elif tipo == 1:
                glColor3f(0, 0, 1)  # Rampa: azul
            elif tipo == 2:
                glColor3f(0, 1, 0)  # Objeto/Pedra: verde
            glPointSize(20)
            glBegin(GL_POINTS)
            glVertex2f(px, pz)
            glEnd()

        # Desenha os botões com projeção para tela (2D)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if textura_botao_iniciar:
            desenhar_textura(botao_iniciar['x'], botao_iniciar['y'], botao_iniciar['largura'], botao_iniciar['altura'], textura_botao_iniciar)
        if textura_botao_obstaculo:
            desenhar_textura(botao_obstaculo['x'], botao_obstaculo['y'], botao_obstaculo['largura'], botao_obstaculo['altura'], textura_botao_obstaculo)
        if textura_botao_rampa:
            desenhar_textura(botao_rampa['x'], botao_rampa['y'], botao_rampa['largura'], botao_rampa['altura'], textura_botao_rampa)
        if textura_botao_objeto:
            desenhar_textura(botao_objeto['x'], botao_objeto['y'], botao_objeto['largura'], botao_objeto['altura'], textura_botao_objeto)

        glfw.swap_buffers(janela)

    # Após o clique em "Iniciar Jogo", processa os cliques registrados para criar os objetos
    for (px, pz, tipo) in lista_cliques:
        if tipo == 0:
            # Cria obstáculo (bloco)
            multiplicador_altura = random.uniform(1.0, 3.0)
            obstaculo = {
                'x': px,
                'z': pz,
                'largura': config.tamanho_moto * 2.0,
                'profundidade': config.tamanho_moto * 2.0,
                'altura': config.tamanho_moto * multiplicador_altura  
            }
            lista_obstaculos_final.append(obstaculo)
        elif tipo == 1:
            # Cria rampa/morro
            multiplicador_altura = random.uniform(2.0, 4.0)
            rampa = {
                'x': px,
                'z': pz,
                'profundidade': 15.0,
                'altura_maxima': multiplicador_altura,
                'orientacao': 0.0 
            }
            lista_rampas_final.append(rampa)
        elif tipo == 2:
            # Cria objeto do tipo pedra
            objeto = {
                'x': px,
                'z': pz,
                'tamanho': config.tamanho_moto * 1.5 
            }
            lista_objetos_pedra.append(objeto)
    
    return lista_obstaculos_final, lista_rampas_final, lista_objetos_pedra
