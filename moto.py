import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def mover_moto(teclas, posicao):
    """Move a moto com base nas teclas pressionadas."""
    velocidade = 0.2  # Ajuste a velocidade de movimento conforme necessário

    if teclas[K_LEFT]:
        posicao[0] -= velocidade  # Move a moto para a esquerda
    if teclas[K_RIGHT]:
        posicao[0] += velocidade  # Move a moto para a direita

    if teclas[K_UP]:
        posicao[2] -= velocidade  # Move a moto para frente (diminuindo o valor de Z)
    if teclas[K_DOWN]:
        posicao[2] += velocidade  # Move a moto para trás (aumentando o valor de Z)