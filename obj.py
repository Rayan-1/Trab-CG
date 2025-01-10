import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Função para carregar um arquivo OBJ
def carregar_objeto(filename):
    vertices = []
    faces = []

    try:
        with open(filename, "r") as file:
            for line in file:
                # Identifica vértices
                if line.startswith("v "):
                    parts = line.split()
                    vertex = (float(parts[1]), float(parts[2]), float(parts[3]))
                    vertices.append(vertex)
                
                # Identifica faces
                elif line.startswith("f "):
                    parts = line.split()
                    face = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                    faces.append(face)

        return vertices, faces

    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        return [], []


def desenhar_objeto(vertices, faces):
    glBegin(GL_TRIANGLES)  # Desenhar como triângulos
    for face in faces:
        for vertex in face:
            # Define cores diferentes para cada vértice
            glColor3f(vertex / len(vertices), (vertex + 1) / len(vertices), 0.8)
            glVertex3fv(vertices[vertex])
    glEnd()
