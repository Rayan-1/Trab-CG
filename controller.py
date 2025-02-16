from OpenGL.GL import *
import math
import glfw
import config
import os
import utils

def carregar_mtl(caminho_mtl: str) -> dict:
    """
    Carrega um arquivo .mtl e retorna um dicionário com os materiais.
    Cada material é um dicionário com chaves: 'Ka', 'Kd', 'Ks', 'Ns', 'd', 'map_Kd' (se disponíveis).
    """
    materiais = {}
    try:
        with open(caminho_mtl, 'r') as arquivo:
            material_atual = None
            for linha in arquivo:
                linha = linha.strip()
                if not linha or linha.startswith('#'):
                    continue
                partes = linha.split()
                chave = partes[0]
                if chave == 'newmtl':
                    material_atual = partes[1]
                    materiais[material_atual] = {}
                elif chave in ['Ka', 'Kd', 'Ks']:
                    # Ambient, Diffuse e Specular (adiciona alfa = 1.0)
                    materiais[material_atual][chave] = list(map(float, partes[1:4])) + [1.0]
                elif chave == 'Ns':
                    materiais[material_atual]['Ns'] = float(partes[1])
                elif chave == 'd':
                    materiais[material_atual]['d'] = float(partes[1])
                elif chave == 'Tr':
                    # Tr é a transparência, usamos 1-d para opacidade
                    materiais[material_atual]['d'] = 1.0 - float(partes[1])
                elif chave == 'map_Kd':
                    # Mapa difuso (textura)
                    # Assume que o caminho é relativo ao arquivo .mtl
                    materiais[material_atual]['map_Kd'] = partes[1]
    except Exception as e:
        print(f"Erro ao carregar MTL '{caminho_mtl}': {e}")
    return materiais

def carregar_objeto(caminho_obj: str) -> dict:
    """
    Carrega um arquivo .obj e o respectivo .mtl (se houver) e retorna um dicionário contendo
    vértices, normais, coordenadas de textura, faces (associadas ao material) e uma display list compilada.
    """
    vertices = []
    normais = []
    texcoords = []
    faces = []
    materiais = {}
    material_atual = None

    diretorio_obj = os.path.dirname(caminho_obj)

    try:
        with open(caminho_obj, 'r') as arquivo:
            for linha in arquivo:
                if linha.startswith('#'):
                    continue
                partes = linha.strip().split()
                if not partes:
                    continue
                chave = partes[0]
                if chave == 'v':
                    vertices.append(list(map(float, partes[1:])))
                elif chave == 'vn':
                    normais.append(list(map(float, partes[1:])))
                elif chave == 'vt':
                    texcoords.append(list(map(float, partes[1:])))
                elif chave == 'f':
                    face = []
                    for parte in partes[1:]:
                        # Pode vir no formato v/vt/vn ou v//vn ou v/vt
                        indices = parte.split('/')
                        vi = int(indices[0]) - 1 if indices[0] else None
                        ti = int(indices[1]) - 1 if len(indices) > 1 and indices[1] != '' else None
                        ni = int(indices[2]) - 1 if len(indices) > 2 and indices[2] != '' else None
                        face.append((vi, ti, ni))
                    faces.append((face, material_atual))
                elif chave == 'mtllib':
                    # Carrega o arquivo de material
                    nome_mtl = partes[1]
                    caminho_mtl = os.path.join(diretorio_obj, nome_mtl)
                    materiais = carregar_mtl(caminho_mtl)
                elif chave == 'usemtl':
                    material_atual = partes[1]
    except Exception as e:
        print(f"Erro ao carregar o objeto '{caminho_obj}': {e}")

    # Compila a display list para otimização
    lista = glGenLists(1)
    glNewList(lista, GL_COMPILE)
    material_corrente = None
    # Se houver textura carregada para um material, podemos armazená-la para não recarregar a cada face
    texturas_material = {}
    for face, mat in faces:
        # Se o material mudou, atualiza os parâmetros
        if mat != material_corrente:
            material_corrente = mat
            if material_corrente in materiais:
                props = materiais[material_corrente]
                # Configura os parâmetros de material
                if 'Ka' in props:
                    glMaterialfv(GL_FRONT, GL_AMBIENT, props['Ka'])
                if 'Kd' in props:
                    glMaterialfv(GL_FRONT, GL_DIFFUSE, props['Kd'])
                if 'Ks' in props:
                    glMaterialfv(GL_FRONT, GL_SPECULAR, props['Ks'])
                if 'Ns' in props:
                    glMaterialf(GL_FRONT, GL_SHININESS, props['Ns'])
                # Se houver mapa difuso, carrega a textura (somente uma vez por material)
                if 'map_Kd' in props:
                    if material_corrente not in texturas_material:
                        caminho_textura = os.path.join(diretorio_obj, props['map_Kd'])
                        tex_id = utils.carregar_textura(caminho_textura)
                        texturas_material[material_corrente] = tex_id
                    glBindTexture(GL_TEXTURE_2D, texturas_material[material_corrente])
                else:
                    glBindTexture(GL_TEXTURE_2D, 0)
            else:
                # Material padrão
                glColor3f(1, 1, 1)
                glBindTexture(GL_TEXTURE_2D, 0)
        # Desenha a face com triangulação (método fan)
        if len(face) < 3:
            continue
        v0 = face[0]
        for i in range(1, len(face) - 1):
            glBegin(GL_TRIANGLES)
            for v in (v0, face[i], face[i+1]):
                vi, ti, ni = v
                if ni is not None and ni < len(normais):
                    glNormal3fv(normais[ni])
                if ti is not None and ti < len(texcoords):
                    glTexCoord2fv(texcoords[ti])
                glVertex3fv(vertices[vi])
            glEnd()
    glEndList()

    return {
        'vertices': vertices,
        'normais': normais,
        'texcoords': texcoords,
        'faces': faces,
        'materiais': materiais,
        'lista': lista
    }

def desenhar_objeto_carregado(obj: dict):
    """
    Desenha o objeto carregado utilizando a display list compilada.
    """
    if 'lista' in obj and obj['lista'] != 0:
        glCallList(obj['lista'])
    else:
        # Fallback: desenho tradicional (menos performático)
        for face, mat in obj['faces']:
            if len(face) < 3:
                continue
            v0 = face[0]
            for i in range(1, len(face) - 1):
                glBegin(GL_TRIANGLES)
                for v in (v0, face[i], face[i+1]):
                    vi, ti, ni = v
                    if ni is not None and ni < len(obj['normais']):
                        glNormal3fv(obj['normais'][ni])
                    if ti is not None and ti < len(obj['texcoords']):
                        glTexCoord2fv(obj['texcoords'][ti])
                    glVertex3fv(obj['vertices'][vi])
                glEnd()

def desenhar_moto_model(objeto_moto, x, y, z, direcao, angulo_inclinacao, escala):
    """
    Desenha o modelo da moto com translação, rotação e escala.
    Uma rotação adicional de 180° no eixo Y é aplicada para corrigir a orientação.
    """
    glPushMatrix()
    glTranslatef(x, y - 0.5, z)
    glRotatef(math.degrees(direcao), 0, 1, 0)
    glRotatef(180, 0, 1, 0)
    glRotatef(angulo_inclinacao, 0, 0, 1)
    glScalef(escala, escala, escala)
    desenhar_objeto_carregado(objeto_moto)
    glPopMatrix()

class Motorcycle:
    """
    Classe que representa a moto.
    Gerencia o estado (posição, velocidade, direção, etc.), processa a entrada,
    atualiza a física e realiza o desenho do modelo.
    """
    def __init__(self, modelo_path="motorcycle.obj", escala=0.5):
        self.pos = [0.0, config.nível_pista + (config.tamanho_moto / 2), 0.0]
        self.velocidade = config.velocidade_moto_inicial
        self.direcao = config.direcao_moto_inicial
        self.velocidade_vertical = config.velocidade_vertical_inicial
        self.angulo_inclinacao = config.angulo_inclinacao_inicial
        self.modelo = carregar_objeto(modelo_path)
        if not self.modelo['vertices']:
            print("Falha ao carregar o modelo da moto.")
        self.escala = escala
        self.rampa_acionada = False  # Para evitar múltiplos impulsos na mesma rampa

    def esta_na_pista(self, x, z):
        """
        Verifica se a moto está dentro dos limites da pista.
        """
        margem = config.tamanho_moto / 2
        dist_min = float('inf')
        for (cx, cz) in config.pontos_centro_pista:
            dist = math.hypot(x - cx, z - cz)
            if dist < dist_min:
                dist_min = dist
        return dist_min <= ((config.largura_pista / 2) - margem)

    def update(self, window, dt, lista_obstaculos, lista_rampas):
        """
        Atualiza o estado da moto com base na entrada do usuário, aplica física,
        detecção de colisões e interações com rampas.
        """
        # Processa entrada
        entrada_frente = 0.0
        entrada_virar = 0.0
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            entrada_frente = 1.0
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            entrada_frente = -1.0
        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            entrada_virar += 1.0
        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            entrada_virar -= 1.0

        # Lógica de pulo
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            if (self.pos[1] <= config.nível_pista + (config.tamanho_moto / 2) + 0.001) and (self.velocidade_vertical == 0.0):
                self.velocidade_vertical = config.velocidade_salto

        # Atualiza velocidade horizontal
        if entrada_frente > 0:
            self.velocidade += config.aceleracao * dt
        elif entrada_frente < 0:
            self.velocidade -= config.desaceleracao * dt
        else:
            if self.velocidade > 0:
                self.velocidade -= config.atrito * dt
                if self.velocidade < 0:
                    self.velocidade = 0
            elif self.velocidade < 0:
                self.velocidade += config.atrito * dt
                if self.velocidade > 0:
                    self.velocidade = 0

        self.velocidade = max(-config.velocidade_maxima/2, min(self.velocidade, config.velocidade_maxima))
        self.direcao += config.taxa_rotacao * entrada_virar * dt

        # Atualiza o ângulo de inclinação (banking)
        alvo_inclinacao = config.inclinacao_maxima * entrada_virar
        if self.angulo_inclinacao < alvo_inclinacao:
            self.angulo_inclinacao += config.taxa_alteracao_inclinacao * dt
            if self.angulo_inclinacao > alvo_inclinacao:
                self.angulo_inclinacao = alvo_inclinacao
        elif self.angulo_inclinacao > alvo_inclinacao:
            self.angulo_inclinacao -= config.taxa_alteracao_inclinacao * dt
            if self.angulo_inclinacao < alvo_inclinacao:
                self.angulo_inclinacao = alvo_inclinacao

        # Atualiza a posição horizontal
        dx = self.velocidade * math.sin(self.direcao) * dt
        dz = self.velocidade * math.cos(self.direcao) * dt
        pos_anterior_x = self.pos[0]
        pos_anterior_z = self.pos[2]
        self.pos[0] += dx
        self.pos[2] += dz

        # Verifica se permanece na pista
        if not self.esta_na_pista(self.pos[0], self.pos[2]):
            self.pos[0] = pos_anterior_x
            self.pos[2] = pos_anterior_z
            self.velocidade = 0

        # Verifica colisão com obstáculos
        from obstaculos import verificar_colisao_horizontal_obstaculo
        if verificar_colisao_horizontal_obstaculo(self.pos, config.tamanho_moto, lista_obstaculos) is not None:
            self.pos[0] = pos_anterior_x
            self.pos[2] = pos_anterior_z
            self.velocidade = 0

        # Física vertical: gravidade e pulo
        if self.pos[1] > (config.nível_pista + config.tamanho_moto / 2) or self.velocidade_vertical != 0.0:
            self.velocidade_vertical -= config.gravidade * dt
            self.pos[1] += self.velocidade_vertical * dt

        # Ajusta colisão vertical com obstáculos
        for obs in lista_obstaculos:
            meio = config.tamanho_moto / 2
            if (self.pos[0] + meio > obs['x'] - obs['largura']/2 and
                self.pos[0] - meio < obs['x'] + obs['largura']/2 and
                self.pos[2] + meio > obs['z'] - obs['profundidade']/2 and
                self.pos[2] - meio < obs['z'] + obs['profundidade']/2):
                if self.pos[1] - meio < obs['altura'] + config.nível_chão:
                    self.pos[1] = config.nível_chão + obs['altura'] + meio
                    self.velocidade_vertical = 0.0

        # Processa interação com rampas
        sobre_alguma_rampa = False
        for rampa in lista_rampas:
            theta = rampa['orientacao']
            dx_r = self.pos[0] - rampa['x']
            dz_r = self.pos[2] - rampa['z']
            # Converte para coordenadas locais da rampa (u: avanço, v: lateral)
            u = dx_r * math.cos(theta) + dz_r * math.sin(theta)
            v = -dx_r * math.sin(theta) + dz_r * math.cos(theta)
            if -rampa['profundidade']/2 <= u <= rampa['profundidade']/2 and abs(v) <= (config.largura_pista/2):
                sobre_alguma_rampa = True
                def altura_atual_rampa(u_val, v_val):
                    return rampa['altura_maxima'] * (1 - (2*u_val/rampa['profundidade'])**2) * (1 - (2*v_val/config.largura_pista)**2)
                alt_rampa = altura_atual_rampa(u, v) - config.deslocamento_rampa
                meio_moto = config.tamanho_moto / 2
                if self.pos[1] - meio_moto < (config.nível_chão + alt_rampa):
                    self.pos[1] = config.nível_chão + alt_rampa + meio_moto
                    self.velocidade_vertical = 0.0
                # Impulso vertical se estiver centralizado lateralmente e na parte final da rampa (apenas uma vez)
                if abs(v) < (config.largura_pista * 0.1) and u > (0.3 * rampa['profundidade']) and self.velocidade > 0 and self.velocidade_vertical == 0 and not self.rampa_acionada:
                    self.velocidade_vertical = config.velocidade_salto_rampa
                    self.rampa_acionada = True
        if not sobre_alguma_rampa:
            self.rampa_acionada = False

        # Impede que a moto fique abaixo do nível da pista
        if self.pos[1] < (config.nível_pista + config.tamanho_moto / 2):
            self.pos[1] = config.nível_pista + config.tamanho_moto / 2
            self.velocidade_vertical = 0.0

    def draw(self):
        """
        Desenha a moto na posição e orientação atuais.
        """
        desenhar_moto_model(self.modelo, self.pos[0], self.pos[1], self.pos[2],
                             self.direcao, self.angulo_inclinacao, self.escala)
