# camera.py
import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import config

def interpolar_vetor3(v1, v2, t):
    """Interpela linearmente dois vetores 3D."""
    return [v1[i] + (v2[i] - v1[i]) * t for i in range(3)]

class ControladorCamera:
    MODO_PRIMEIRA_PESSOA = 0
    MODO_TERCEIRA_PESSOA = 1
    MODO_ANGULADA_LEFT = 2  # 45° para a esquerda
    MODO_ANGULADA_RIGHT = 3  # 45° para a direita

    def __init__(self):
        # Inicia no modo terceira pessoa
        self.modo = ControladorCamera.MODO_TERCEIRA_PESSOA
        self.velocidade_transicao = 2.0  # quanto maior, mais rápida a transição entre modos
        self.tab_foi_pressionado = False

        # Offsets relativos à posição da moto
        # São definidos de acordo com o modo escolhido.
        self.offset_atual = [0.0, 0.0, 0.0]
        self.alvo_offset_atual = [0.0, 0.0, 0.0]
        # Valores "desejados" para os offsets (serão atualizados na transição)
        self.offset_desejado = [0.0, 0.0, 0.0]
        self.alvo_offset_desejado = [0.0, 0.0, 0.0]

    def calcular_offsets(self, moto):
        """Calcula os offsets desejados (posição e alvo) em função do modo de câmera."""
        d = moto.direcao
        # Vetor direção (para frente) da moto
        frente = [math.sin(d), 0, math.cos(d)]
        if self.modo == ControladorCamera.MODO_PRIMEIRA_PESSOA:
            # Primeira pessoa: a câmera fica quase na "cabeça" do piloto,
            # e olha para um ponto distante à frente (para mostrar parte do guidão)
            offset_pos = [0.0, 0.5, 0.0]
            offset_alvo = [frente[0] * 10, 0.5, frente[2] * 10]
        elif self.modo == ControladorCamera.MODO_TERCEIRA_PESSOA:
            # Terceira pessoa: a câmera fica atrás da moto,
            # usando os parâmetros de distância e altura definidos em config.
            offset_pos = [
                -config.distancia_camera * math.sin(d),
                config.altura_camera,
                -config.distancia_camera * math.cos(d)
            ]
            offset_alvo = [0.0, 0.0, 0.0]  # a câmera olha exatamente para a posição da moto
        elif self.modo == ControladorCamera.MODO_ANGULADA_LEFT:
            # Câmera com 45° de inclinação para a esquerda
            d_angulo = d + math.radians(45)
            offset_pos = [
                -config.distancia_camera * math.sin(d_angulo),
                config.altura_camera,
                -config.distancia_camera * math.cos(d_angulo)
            ]
            offset_alvo = [0.0, 0.0, 0.0]
        elif self.modo == ControladorCamera.MODO_ANGULADA_RIGHT:
            # Câmera com -45° de inclinação para a direita
            d_angulo = d + math.radians(-45)
            offset_pos = [
                -config.distancia_camera * math.sin(d_angulo),
                config.altura_camera,
                -config.distancia_camera * math.cos(d_angulo)
            ]
            offset_alvo = [0.0, 0.0, 0.0]
        else:
            offset_pos = [0.0, config.altura_camera, 0.0]
            offset_alvo = [0.0, 0.0, 0.0]
        return offset_pos, offset_alvo

    def trocar_modo(self):
        """Altera para o próximo modo de câmera."""
        self.modo = (self.modo + 1) % 4
        print("Modo de câmera:", self.modo)

    def atualizar(self, janela, dt, moto):
        # Verifica se a tecla TAB foi pressionada para trocar o modo
        if glfw.get_key(janela, glfw.KEY_TAB) == glfw.PRESS:
            if not self.tab_foi_pressionado:
                self.trocar_modo()
                # Ao trocar o modo, recalculamos os offsets desejados
                self.offset_desejado, self.alvo_offset_desejado = self.calcular_offsets(moto)
                self.tab_foi_pressionado = True
        else:
            self.tab_foi_pressionado = False

        # Se não houve troca, os offsets desejados devem ser os do modo atual,
        # baseados na direção atual da moto.
        if not self.tab_foi_pressionado:
            self.offset_desejado, self.alvo_offset_desejado = self.calcular_offsets(moto)

        # Interpola suavemente os offsets (apenas a transição entre modos é suavizada)
        t = dt * self.velocidade_transicao
        self.offset_atual = interpolar_vetor3(self.offset_atual, self.offset_desejado, t)
        self.alvo_offset_atual = interpolar_vetor3(self.alvo_offset_atual, self.alvo_offset_desejado, t)

        # Calcula a posição absoluta da câmera: posição da moto + offset atual
        self.posicao_camera = [
            moto.pos[0] + self.offset_atual[0],
            moto.pos[1] + self.offset_atual[1],
            moto.pos[2] + self.offset_atual[2]
        ]
        # Calcula o alvo absoluto: posição da moto + alvo_offset atual
        self.alvo_camera = [
            moto.pos[0] + self.alvo_offset_atual[0],
            moto.pos[1] + self.alvo_offset_atual[1],
            moto.pos[2] + self.alvo_offset_atual[2]
        ]
        # Atualiza a posição global do skybox
        config.pos_camera[:] = self.posicao_camera

    def aplicar_visualizacao(self):
        """Aplica a transformação de visualização com gluLookAt."""
        glLoadIdentity()
        gluLookAt(self.posicao_camera[0], self.posicao_camera[1], self.posicao_camera[2],
                  self.alvo_camera[0], self.alvo_camera[1], self.alvo_camera[2],
                  0, 1, 0)
