# main.py
"""
Este módulo é o ponto de entrada do jogo “Moto Titan 150”.
Utiliza OpenGL (modo legacy), GLFW, PyGLM e Pillow para renderizar
um circuito com pista, skybox, obstáculos, rampas e colisões com a moto.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import tela_inicial   # Tela de mapeamento e posicionamento inicial (obstáculos, rampas, pedras)
import config         # Configurações globais (parâmetros do jogo)
import utils          # Funções utilitárias (carregamento de texturas, interpolação, etc.)
import pista          # Lógica da pista: geração dos pontos centrais e desenho do chão/pista
import skybox         # Carregamento e desenho do skybox
import obstaculos     # Desenho dos obstáculos e verificação de colisões
import controller     # Gerencia o modelo e a física da moto
import camera         # Controle e interpolação da câmera

def main():
    # Inicializa o GLFW (janela e contexto OpenGL)
    if not glfw.init():
        return
    # Cria uma janela com resolução 1200x800 e título
    janela = glfw.create_window(1200, 800, "Moto Titan 150", None, None)
    if not janela:
        glfw.terminate()
        return
    glfw.make_context_current(janela)

    # A tela inicial permite definir manualmente a posição de obstáculos, rampas e pedras (objetos)
    lista_obstaculos, lista_rampas, lista_objetos_pedra = tela_inicial.tela_inicial(janela)
    
    # Habilita o teste de profundidade e configura parâmetros adicionais do OpenGL
    glEnable(GL_DEPTH_TEST)
    utils.configurar_opengl()

    # Carrega as texturas para o skybox, chão e pista
    skybox.carregar_texturas_skybox()
    pista.carregar_texturas_chao()
    pista.carregar_textura_pista()
    # Texturas para obstáculos e rampas (usadas no desenho dos blocos)
    config.textura_obstaculo = utils.carregar_textura("assets/obstaculo03.jpg")
    config.textura_rampa = utils.carregar_textura("assets/obstaculo.jpg")
    
    # Gera os pontos centrais interpolados da pista a partir dos pontos-chave
    pista.gerar_pontos_pista(config.NUM_PONTOS_PISTA)
    
    # Carrega o modelo dos obstáculos "pedra" (usado para colisões e desenho)
    modelo_objeto_pedra = controller.carregar_objeto("assets/pedra/roc.obj")
    # Carrega o modelo da moto; o arquivo .obj e escala são definidos
    moto = controller.Motorcycle(modelo_path="bike/moto_crfv2.obj", escala=0.5)
    
    # Posiciona a moto no início da pista (primeiro ponto central)
    if config.pontos_centro_pista:
        moto.pos[0] = config.pontos_centro_pista[0][0]
        moto.pos[2] = config.pontos_centro_pista[0][1]
    
    # Define a direção inicial da moto, baseada na tangente do caminho da pista
    if len(config.pontos_centro_pista) > 1:
        pt_proximo = config.pontos_centro_pista[1]
        pt_anterior = config.pontos_centro_pista[-2]
        moto.direcao = math.atan2(pt_proximo[0] - pt_anterior[0], pt_proximo[1] - pt_anterior[1])
    
    # Cria o controlador da câmera e calcula os offsets iniciais (posição relativa à moto)
    controlador_camera = camera.ControladorCamera()
    controlador_camera.offset_atual, controlador_camera.alvo_offset_atual = controlador_camera.calcular_offsets(moto)
    
    tempo_anterior = glfw.get_time()
    
    # Loop principal de renderização e atualização
    while not glfw.window_should_close(janela):
        tempo_atual = glfw.get_time()
        dt = tempo_atual - tempo_anterior  # delta de tempo (para atualizações suaves)
        tempo_anterior = tempo_atual
        
        # Atualiza a viewport de acordo com o tamanho da janela
        largura, altura = glfw.get_framebuffer_size(janela)
        glViewport(0, 0, largura, altura)
        
        # Atualiza a física e entrada da moto (incluindo colisões com obstáculos, rampas e pedras)
        moto.update(janela, dt, lista_obstaculos, lista_rampas, lista_objetos_pedra)
        
        # Atualiza o controlador da câmera (incluindo troca de modo com TAB)
        controlador_camera.atualizar(janela, dt, moto)
        
        # Limpa o buffer de cor e profundidade para o novo frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Define uma perspectiva com campo de visão de 45° e plano de recorte de 1 a 200 unidades
        aspecto = largura / altura if altura != 0 else 1
        gluPerspective(45, aspecto, 1, 200)
        
        glMatrixMode(GL_MODELVIEW)
        # Aplica a visualização com base na posição e alvo da câmera
        controlador_camera.aplicar_visualizacao()
        
        # Desenha a cena: skybox, chão, pista, obstáculos, rampas, pedras e a moto
        skybox.desenhar_skybox()
        pista.desenhar_chao()
        pista.desenhar_pista()
        for obs in lista_obstaculos:
            obstaculos.desenhar_obstaculo(obs)
        for rampa in lista_rampas:
            obstaculos.desenhar_rampa(rampa)
        for objeto in lista_objetos_pedra:
            obstaculos.desenhar_lista_objetos_pedra(modelo_objeto_pedra, objeto)
            
        moto.draw()
        
        # Troca os buffers e processa os eventos
        glfw.swap_buffers(janela)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()
