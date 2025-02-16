# main.py (apenas a parte relevante)
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import tela_inicial
import config
import utils
import pista
import skybox
import obstaculos
import controller
import camera  

def main():
    # Inicializa o GLFW e configura o OpenGL
    if not glfw.init():
        return
    janela = glfw.create_window(1200, 800, "Moto Titan 150 ", None, None)
    if not janela:
        glfw.terminate()
        return
    glfw.make_context_current(janela)
    lista_obstaculos, lista_rampas,lista_objetos_final = tela_inicial.tela_inicial(janela)
    
    glEnable(GL_DEPTH_TEST)
    utils.configurar_opengl()
    # Carrega as texturas
    skybox.carregar_texturas_skybox()
    pista.carregar_texturas_chao()
    pista.carregar_textura_pista()
    config.textura_obstaculo = utils.carregar_textura("assets/obstaculo03.jpg")
    config.textura_rampa = utils.carregar_textura("assets/obstaculo.jpg")
    
    
    # Gera os pontos centrais da pista
    pista.gerar_pontos_pista(config.NUM_PONTOS_PISTA)
    
    moto = controller.Motorcycle(modelo_path="bike/moto_crfv2.obj", escala=0.5)
    # moto = controller.Motorcycle(modelo_path="assets/moto_piloto_240.obj", escala=0.5)
    
    # Cria a instância da moto e posiciona-a no início da pista
    if config.pontos_centro_pista:
        moto.pos[0] = config.pontos_centro_pista[0][0]
        moto.pos[2] = config.pontos_centro_pista[0][1]
    
    if len(config.pontos_centro_pista) > 1:
        pt_proximo = config.pontos_centro_pista[1]
        pt_anterior = config.pontos_centro_pista[-2]
        moto.direcao = math.atan2(pt_proximo[0] - pt_anterior[0], pt_proximo[1] - pt_anterior[1])
    
    # Cria o controlador de câmera
    controlador_camera = camera.ControladorCamera()
    # Inicializa os offsets conforme o modo atual
    controlador_camera.offset_atual, controlador_camera.alvo_offset_atual = controlador_camera.calcular_offsets(moto)
    
    tempo_anterior = glfw.get_time()
    
    while not glfw.window_should_close(janela):
        tempo_atual = glfw.get_time()
        dt = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual
        
        largura, altura = glfw.get_framebuffer_size(janela)
        glViewport(0, 0, largura, altura)
        
        # Atualiza a moto
        moto.update(janela, dt, lista_obstaculos, lista_rampas)
        
        # Atualiza o controlador da câmera (incluindo a troca de modo com TAB)
        controlador_camera.atualizar(janela, dt, moto)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspecto = largura / altura if altura != 0 else 1
        gluPerspective(45, aspecto, 1, 200)
        
        glMatrixMode(GL_MODELVIEW)
        controlador_camera.aplicar_visualizacao()
        
        skybox.desenhar_skybox()
        pista.desenhar_chao()
        pista.desenhar_pista()
        for obs in lista_obstaculos:
            obstaculos.desenhar_obstaculo(obs)
        for rampa in lista_rampas:
            obstaculos.desenhar_rampa(rampa)
        moto.draw()
        
        glfw.swap_buffers(janela)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()
