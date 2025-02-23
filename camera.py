# camera.py
"""
Este módulo gerencia a câmera do jogo.
Permite alternar entre diferentes modos (primeira pessoa, terceira pessoa, ângulos laterais)
e realiza a interpolação suave entre os offsets desejados e atuais, garantindo transições
gradativas na posição e no alvo da câmera.
"""

import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import config
import glm

class ControladorCamera:
    # Constantes para os modos de câmera
    MODO_PRIMEIRA_PESSOA = 0
    MODO_TERCEIRA_PESSOA = 1
    MODO_ANGULADA_LEFT = 2  # 45° para a esquerda
    MODO_ANGULADA_RIGHT = 3  # 45° para a direita

    def __init__(self):
        # Inicializa no modo terceira pessoa
        self.modo = ControladorCamera.MODO_TERCEIRA_PESSOA
        self.velocidade_transicao = 2.0  # Velocidade para interpolação dos offsets
        self.tab_foi_pressionado = False

        # Vetores que representam os offsets atuais e desejados da câmera em relação à moto
        self.offset_atual = glm.vec3(0.0, 0.0, 0.0)
        self.alvo_offset_atual = glm.vec3(0.0, 0.0, 0.0)
        self.offset_desejado = glm.vec3(0.0, 0.0, 0.0)
        self.alvo_offset_desejado = glm.vec3(0.0, 0.0, 0.0)

        # Posição absoluta da câmera e seu alvo (usados no gluLookAt)
        self.posicao_camera = glm.vec3(0.0, 0.0, 0.0)
        self.alvo_camera = glm.vec3(0.0, 0.0, 0.0)

    def calcular_offsets(self, moto):
        """
        Calcula os offsets desejados (posição e alvo) com base na posição e direção da moto.
        
        Utiliza funções trigonométricas para definir a direção “para frente” e calcula o deslocamento
        de acordo com o modo de câmera selecionado.
        """
        d = moto.direcao
        # Vetor que aponta para a frente da moto
        frente = glm.vec3(math.sin(d), 0.0, math.cos(d))
        
        if self.modo == ControladorCamera.MODO_PRIMEIRA_PESSOA:
            offset_pos = glm.vec3(0.0, 0.5, 0.0)
            offset_alvo = glm.vec3(frente.x * 10, 0.5, frente.z * 10)
        elif self.modo == ControladorCamera.MODO_TERCEIRA_PESSOA:
            offset_pos = glm.vec3(-config.distancia_camera * math.sin(d),
                                  config.altura_camera,
                                  -config.distancia_camera * math.cos(d))
            offset_alvo = glm.vec3(0.0, 0.0, 0.0)  # A câmera olhará para a posição da moto
        elif self.modo == ControladorCamera.MODO_ANGULADA_LEFT:
            d_angulo = d + math.radians(45)
            offset_pos = glm.vec3(-config.distancia_camera * math.sin(d_angulo),
                                  config.altura_camera,
                                  -config.distancia_camera * math.cos(d_angulo))
            offset_alvo = glm.vec3(0.0, 0.0, 0.0)
        elif self.modo == ControladorCamera.MODO_ANGULADA_RIGHT:
            d_angulo = d - math.radians(45)
            offset_pos = glm.vec3(-config.distancia_camera * math.sin(d_angulo),
                                  config.altura_camera,
                                  -config.distancia_camera * math.cos(d_angulo))
            offset_alvo = glm.vec3(0.0, 0.0, 0.0)
        else:
            offset_pos = glm.vec3(0.0, config.altura_camera, 0.0)
            offset_alvo = glm.vec3(0.0, 0.0, 0.0)
        return offset_pos, offset_alvo

    def trocar_modo(self):
        """
        Alterna para o próximo modo de câmera e imprime no console o modo atual.
        """
        self.modo = (self.modo + 1) % 4
        print("Modo de câmera:", self.modo)

    def atualizar(self, janela, dt, moto):
        """
        Atualiza os offsets da câmera com base na entrada do usuário (tecla TAB)
        e na posição/direção atual da moto.
        
        Utiliza interpolação (glm.mix) para transição suave dos offsets.
        Também atualiza a posição global da câmera (config.pos_camera) para o desenho do skybox.
        """
        if glfw.get_key(janela, glfw.KEY_TAB) == glfw.PRESS:
            if not self.tab_foi_pressionado:
                self.trocar_modo()
                self.offset_desejado, self.alvo_offset_desejado = self.calcular_offsets(moto)
                self.tab_foi_pressionado = True
        else:
            self.tab_foi_pressionado = False

        if not self.tab_foi_pressionado:
            self.offset_desejado, self.alvo_offset_desejado = self.calcular_offsets(moto)

        # Interpolação suave dos offsets atuais para os desejados
        self.offset_atual = glm.mix(self.offset_atual, self.offset_desejado, dt * self.velocidade_transicao)
        self.alvo_offset_atual = glm.mix(self.alvo_offset_atual, self.alvo_offset_desejado, dt * self.velocidade_transicao)

        # Calcula a posição absoluta da câmera com base na posição da moto e no offset atual
        self.posicao_camera = moto.pos + self.offset_atual
        # Calcula o alvo absoluto (para onde a câmera aponta)
        self.alvo_camera = moto.pos + self.alvo_offset_atual
        # Atualiza a posição global da câmera para o skybox
        config.pos_camera[:] = [self.posicao_camera.x, self.posicao_camera.y, self.posicao_camera.z]

    def aplicar_visualizacao(self):
        """
        Aplica a transformação de visualização usando gluLookAt.
        Define a posição da câmera, o alvo e o vetor "up".
        """
        glLoadIdentity()
        gluLookAt(self.posicao_camera.x, self.posicao_camera.y, self.posicao_camera.z,
                  self.alvo_camera.x, self.alvo_camera.y, self.alvo_camera.z,
                  0, 1, 0)
