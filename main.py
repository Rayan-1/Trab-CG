import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

import config
import utils
import pista
import skybox
import obstaculos
import controller

def main():
    # Inicializa o GLFW
    if not glfw.init():
        return
    janela = glfw.create_window(1200, 800, "Moto Titan 150 ", None, None)
    if not janela:
        glfw.terminate()
        return
    glfw.make_context_current(janela)
    glEnable(GL_DEPTH_TEST)
    
    # Configura os estados do OpenGL
    utils.configurar_opengl()
    
    # Carrega as texturas
    skybox.carregar_texturas_skybox()
    pista.carregar_texturas_chao()
    pista.carregar_textura_pista()
    # Para obstáculos e rampas, utilizamos imagens de exemplo
    config.textura_obstaculo = utils.carregar_textura("assets/obstaculo03.jpg")
    config.textura_rampa = utils.carregar_textura("assets/obstaculo.jpg")
    
    # Gera os pontos centrais da pista
    pista.gerar_pontos_pista(config.NUM_PONTOS_PISTA)
    
    # Gera obstáculos e rampas
    lista_obstaculos = obstaculos.gerar_obstaculos()
    lista_rampas = obstaculos.gerar_rampas()
    
    # Cria a instância da moto e posiciona-a no início da pista
    moto = controller.Motorcycle(modelo_path="assets/motorcycle.obj", escala=0.5)
    if config.pontos_centro_pista:
        moto.pos[0] = config.pontos_centro_pista[0][0]
        moto.pos[2] = config.pontos_centro_pista[0][1]
    
    # Define a direção inicial da moto com base na tangente da pista
    if len(config.pontos_centro_pista) > 1:
        pt_proximo = config.pontos_centro_pista[1]
        pt_anterior = config.pontos_centro_pista[-2]
        tangente_x = pt_proximo[0] - pt_anterior[0]
        tangente_z = pt_proximo[1] - pt_anterior[1]
        moto.direcao = math.atan2(tangente_x, tangente_z)
    
    tempo_anterior = glfw.get_time()
    
    while not glfw.window_should_close(janela):
        tempo_atual = glfw.get_time()
        dt = tempo_atual - tempo_anterior
        tempo_anterior = tempo_atual
        
        largura, altura = glfw.get_framebuffer_size(janela)
        glViewport(0, 0, largura, altura)
        
        # Atualiza o estado da moto
        moto.update(janela, dt, lista_obstaculos, lista_rampas)
        
        # Calcula a posição da câmera relativa à moto
        offset_cam_x = -config.distancia_camera * math.sin(moto.direcao)
        offset_cam_z = -config.distancia_camera * math.cos(moto.direcao)
        cam_x = moto.pos[0] + offset_cam_x
        cam_y = moto.pos[1] + config.altura_camera
        cam_z = moto.pos[2] + offset_cam_z
        config.pos_camera[:] = [cam_x, cam_y, cam_z]
        
        # Configura as matrizes de projeção e visão
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspecto = largura / altura if altura != 0 else 1
        gluPerspective(45, aspecto, 1, 200)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(cam_x, cam_y, cam_z,
                  moto.pos[0], moto.pos[1], moto.pos[2],
                  0, 1, 0)
        
        # Desenha os elementos da cena
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
