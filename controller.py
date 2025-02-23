# controller.py
"""
Este módulo é responsável pelo carregamento e desenho dos modelos 3D,
além de implementar a física e as interações da moto.
Utiliza OpenGL para renderização e PyGLM para operações vetoriais.
"""

from OpenGL.GL import *
import math
import glfw
import os
import utils
import config
import glm  # PyGLM para manipulação de vetores/matrizes
import obstaculos

def carregar_mtl(caminho_mtl: str) -> dict:
    """
    Carrega um arquivo .mtl e retorna um dicionário com os materiais.
    
    Cada material é um dicionário com chaves:
      - 'Ka': cor ambiente (RGBA),
      - 'Kd': cor difusa (RGBA),
      - 'Ks': cor especular (RGBA),
      - 'Ns': coeficiente de brilho,
      - 'd': opacidade,
      - 'map_Kd': caminho para a textura difusa (se houver).
    
    A função lê linha a linha e interpreta os parâmetros conforme o padrão MTL.
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
                    # Converte os três valores e adiciona alfa igual a 1.0
                    materiais[material_atual][chave] = list(map(float, partes[1:4])) + [1.0]
                elif chave == 'Ns':
                    materiais[material_atual]['Ns'] = float(partes[1])
                elif chave == 'd':
                    materiais[material_atual]['d'] = float(partes[1])
                elif chave == 'Tr':
                    # 'Tr' representa transparência; converte para opacidade (1 - valor)
                    materiais[material_atual]['d'] = 1.0 - float(partes[1])
                elif chave == 'map_Kd':
                    materiais[material_atual]['map_Kd'] = partes[1]
    except Exception as e:
        print(f"Erro ao carregar MTL '{caminho_mtl}': {e}")
    return materiais

def carregar_objeto(caminho_obj: str) -> dict:
    """
    Carrega um arquivo .obj e, se presente, seu arquivo .mtl associado.
    
    Retorna um dicionário contendo:
      - 'vertices': lista de vértices,
      - 'normais': lista de normais,
      - 'texcoords': coordenadas de textura,
      - 'faces': faces (cada face é uma tupla com os índices e material usado),
      - 'materiais': dicionário dos materiais,
      - 'lista': display list compilada para desenho otimizado.
    
    O carregamento usa a notação padrão dos arquivos OBJ e compila uma display list
    para acelerar o desenho em tempo real.
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
                    # Vértices: coordenadas x, y, z
                    vertices.append(list(map(float, partes[1:])))
                elif chave == 'vn':
                    # Normais: vetores de normalização
                    normais.append(list(map(float, partes[1:])))
                elif chave == 'vt':
                    # Coordenadas de textura: u, v (opcionalmente w)
                    texcoords.append(list(map(float, partes[1:])))
                elif chave == 'f':
                    # Faces: cada face pode conter índices para vértice/texcoord/normal
                    face = []
                    for parte in partes[1:]:
                        indices = parte.split('/')
                        vi = int(indices[0]) - 1 if indices[0] else None
                        ti = int(indices[1]) - 1 if len(indices) > 1 and indices[1] != '' else None
                        ni = int(indices[2]) - 1 if len(indices) > 2 and indices[2] != '' else None
                        face.append((vi, ti, ni))
                    faces.append((face, material_atual))
                elif chave == 'mtllib':
                    nome_mtl = partes[1]
                    caminho_mtl = os.path.join(diretorio_obj, nome_mtl)
                    materiais = carregar_mtl(caminho_mtl)
                elif chave == 'usemtl':
                    material_atual = partes[1]
    except Exception as e:
        print(f"Erro ao carregar o objeto '{caminho_obj}': {e}")

    # Compila uma display list para otimizar o desenho
    lista = glGenLists(1)
    glNewList(lista, GL_COMPILE)
    material_corrente = None
    texturas_material = {}
    for face, mat in faces:
        # Se o material mudar, atualiza os parâmetros de material e textura
        if mat != material_corrente:
            material_corrente = mat
            if material_corrente in materiais:
                props = materiais[material_corrente]
                if 'Ka' in props:
                    glMaterialfv(GL_FRONT, GL_AMBIENT, props['Ka'])
                if 'Kd' in props:
                    glMaterialfv(GL_FRONT, GL_DIFFUSE, props['Kd'])
                if 'Ks' in props:
                    glMaterialfv(GL_FRONT, GL_SPECULAR, props['Ks'])
                if 'Ns' in props:
                    glMaterialf(GL_FRONT, GL_SHININESS, props['Ns'])
                if 'map_Kd' in props:
                    if material_corrente not in texturas_material:
                        caminho_textura = os.path.join(diretorio_obj, props['map_Kd'])
                        tex_id = utils.carregar_textura(caminho_textura)
                        texturas_material[material_corrente] = tex_id
                    glBindTexture(GL_TEXTURE_2D, texturas_material[material_corrente])
                else:
                    glBindTexture(GL_TEXTURE_2D, 0)
            else:
                glBindTexture(GL_TEXTURE_2D, 0)
        # Desenha a face utilizando triangulação em fan (cada face é subdividida em triângulos)
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
    Desenha o objeto 3D utilizando a display list compilada.
    Se a display list não estiver disponível, utiliza o método tradicional (menos performático).
    """
    if 'lista' in obj and obj['lista'] != 0:
        glCallList(obj['lista'])
    else:
        for face, _ in obj['faces']:
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

def desenhar_moto_model(objeto_moto, posicao: glm.vec3, direcao, angulo_inclinacao, escala):
    """
    Desenha o modelo da moto aplicando transformações: translação, rotação e escala.
    
    Parâmetros:
      - objeto_moto: objeto carregado (dicionário com display list, vértices, etc.);
      - posicao (glm.vec3): posição da moto no mundo;
      - direcao: ângulo (radianos) que define a orientação da moto;
      - angulo_inclinacao: ângulo de banking (inclinação lateral) em graus;
      - escala: fator de escala para ajustar o tamanho do modelo.
    
    Nota gráfica: Uma rotação extra de 180° no eixo Y é aplicada para corrigir a orientação do modelo.
    """
    # Define cor e materiais para diminuir a luminosidade do modelo (efeito de sombreamento)
    glColor3f(0.6, 0.6, 0.6)
    material_ambient = [0.3, 0.3, 0.3, 1.0]
    material_diffuse = [0.2, 0.2, 0.2, 1.0]
    glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)

    glPushMatrix()
    # Translada a moto para sua posição; ajusta a altura (y - 0.5 para alinhamento com o chão)
    glTranslatef(posicao.x, posicao.y - 0.5, posicao.z)
    # Aplica rotação conforme a direção (convertida de radianos para graus)
    glRotatef(math.degrees(direcao), 0, 1, 0)
    # Rotação extra de 180° para corrigir a orientação do modelo
    glRotatef(180, 0, 1, 0)
    # Aplica inclinação lateral (banking)
    glRotatef(angulo_inclinacao, 0, 0, 1)
    glScalef(escala, escala, escala)
    desenhar_objeto_carregado(objeto_moto)
    glPopMatrix()

class Motorcycle:
    """
    Classe que representa a moto no jogo.
    Gerencia a posição, velocidade, direção, física (gravidade, pulo) e colisões.
    Utiliza vetores glm.vec3 para facilitar as operações matemáticas.
    """
    def __init__(self, modelo_path="motorcycle.obj", escala=0.5):
        # Define a posição inicial: x, y (altura baseada no nível da pista) e z
        self.pos = glm.vec3(0.0, config.nível_pista + (config.tamanho_moto / 2), 0.0)
        self.velocidade = config.velocidade_moto_inicial
        self.direcao = config.direcao_moto_inicial
        self.velocidade_vertical = config.velocidade_vertical_inicial
        self.angulo_inclinacao = config.angulo_inclinacao_inicial
        # Carrega o modelo 3D da moto (arquivo .obj e texturas associadas)
        self.modelo = carregar_objeto(modelo_path)
        if not self.modelo['vertices']:
            print("Falha ao carregar o modelo da moto.")
        self.escala = escala
        # Variável para evitar múltiplos impulsos ao passar por uma mesma rampa
        self.rampa_acionada = False  

    def esta_na_pista(self, x, z):
        """
        Verifica se a posição (x, z) está dentro dos limites da pista.
        Compara a distância mínima entre o ponto e os pontos centrais da pista
        com a metade da largura da pista, considerando uma margem baseada no tamanho da moto.
        """
        margem = config.tamanho_moto / 2
        dist_min = float('inf')
        for (cx, cz) in config.pontos_centro_pista:
            dist = math.hypot(x - cx, z - cz)
            if dist < dist_min:
                dist_min = dist
        return dist_min <= ((config.largura_pista / 2) - margem)

    def update(self, window, dt, lista_obstaculos, lista_rampas, lista_objetos_pedra):
        """
        Atualiza o estado da moto:
          - Processa entradas do teclado para acelerar, desacelerar e virar.
          - Aplica física horizontal e vertical (gravidade e pulo).
          - Verifica colisões com os limites da pista, obstáculos e pedras.
          - Trata a interação com rampas, permitindo um impulso vertical se apropriado.
        
        dt: delta de tempo desde a última atualização (para suavizar a física).
        """
        # Processamento das entradas de movimento
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

        # Lógica de pulo: se o espaço for pressionado e a moto estiver no chão, aplica impulso vertical
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            if (self.pos.y <= config.nível_pista + (config.tamanho_moto / 2) + 0.001) and (self.velocidade_vertical == 0.0):
                self.velocidade_vertical = config.velocidade_salto

        # Atualiza a velocidade horizontal conforme a entrada
        if entrada_frente > 0:
            self.velocidade += config.aceleracao * dt
        elif entrada_frente < 0:
            self.velocidade -= config.desaceleracao * dt
        else:
            # Aplica atrito para reduzir a velocidade se nenhuma tecla for pressionada
            if self.velocidade > 0:
                self.velocidade -= config.atrito * dt
                if self.velocidade < 0:
                    self.velocidade = 0
            elif self.velocidade < 0:
                self.velocidade += config.atrito * dt
                if self.velocidade > 0:
                    self.velocidade = 0

        # Limita a velocidade máxima permitida
        self.velocidade = max(-config.velocidade_maxima/2, min(self.velocidade, config.velocidade_maxima))
        # Atualiza a direção da moto com base na taxa de rotação e na entrada de virar
        self.direcao += config.taxa_rotacao * entrada_virar * dt

        # Atualiza o ângulo de inclinação (banking) para efeito visual nas curvas
        alvo_inclinacao = config.inclinacao_maxima * entrada_virar
        if self.angulo_inclinacao < alvo_inclinacao:
            self.angulo_inclinacao += config.taxa_alteracao_inclinacao * dt
            if self.angulo_inclinacao > alvo_inclinacao:
                self.angulo_inclinacao = alvo_inclinacao
        elif self.angulo_inclinacao > alvo_inclinacao:
            self.angulo_inclinacao -= config.taxa_alteracao_inclinacao * dt
            if self.angulo_inclinacao < alvo_inclinacao:
                self.angulo_inclinacao = alvo_inclinacao

        # Atualiza a posição horizontal (no plano XZ) utilizando funções trigonométricas
        dx = self.velocidade * math.sin(self.direcao) * dt
        dz = self.velocidade * math.cos(self.direcao) * dt
        pos_anterior = glm.vec3(self.pos)  # Cópia para rollback em caso de colisão
        self.pos.x += dx
        self.pos.z += dz

        # Verifica se a moto permanece dentro da pista
        if not self.esta_na_pista(self.pos.x, self.pos.z):
            self.pos.x = pos_anterior.x
            self.pos.z = pos_anterior.z
            self.velocidade = 0

        # Verifica colisões horizontais com obstáculos (blocos) usando bounding box
        if obstaculos.verificar_colisao_horizontal_obstaculo(list(self.pos), config.tamanho_moto, lista_obstaculos) is not None:
            self.pos.x = pos_anterior.x
            self.pos.z = pos_anterior.z
            self.velocidade = 0

        # Verifica se há colisão com um objeto pedra, utilizando a função específica
        colisao_objeto = obstaculos.verificar_colisao_pedra(list(self.pos), config.tamanho_moto, lista_objetos_pedra)
        if colisao_objeto is not None:
            meio = config.tamanho_moto / 2  # Metade do tamanho da moto (usado para o bounding box)
            # Calcula a altura do objeto pedra, assumindo que ele repousa no chão
            altura_pedra = config.nível_chão + colisao_objeto['tamanho']
            # Se a base da moto (pos.y - meio) estiver abaixo do topo da pedra, há penetração
            if self.pos.y - meio < altura_pedra:
                # Se a moto estiver em queda (velocidade vertical negativa), ajusta a posição vertical para "pisar" na pedra
                if self.velocidade_vertical < 0:
                    self.pos.y = altura_pedra + meio
                    self.velocidade_vertical = 0.0
                else:
                    # Caso contrário, reverte a posição horizontal para evitar que a moto entre na pedra
                    self.pos.x = pos_anterior.x
                    self.pos.z = pos_anterior.z
                    self.velocidade = 0

        # Física vertical: aplica gravidade se a moto estiver no ar ou pulando
        if self.pos.y > (config.nível_pista + config.tamanho_moto / 2) or self.velocidade_vertical != 0.0:
            self.velocidade_vertical -= config.gravidade * dt
            self.pos.y += self.velocidade_vertical * dt

        # Ajusta a posição vertical caso haja colisão com obstáculos (para “pisar” nos blocos)
        for obs in lista_obstaculos:
            meio = config.tamanho_moto / 2
            if (self.pos.x + meio > obs['x'] - obs['largura'] / 2 and
                self.pos.x - meio < obs['x'] + obs['largura'] / 2 and
                self.pos.z + meio > obs['z'] - obs['profundidade'] / 2 and
                self.pos.z - meio < obs['z'] + obs['profundidade'] / 2):
                if self.pos.y - meio < obs['altura'] + config.nível_chão:
                    self.pos.y = config.nível_chão + obs['altura'] + meio
                    self.velocidade_vertical = 0.0

        # Processa interação com rampas: verifica se a moto está sobre alguma rampa e aplica correção na altura
        sobre_alguma_rampa = False
        for rampa in lista_rampas:
            theta = rampa['orientacao']
            dx_r = self.pos.x - rampa['x']
            dz_r = self.pos.z - rampa['z']
            # Converte para coordenadas locais da rampa:
            #   u: direção de avanço (longitudinal)
            #   v: direção lateral
            u = dx_r * math.cos(theta) + dz_r * math.sin(theta)
            v = -dx_r * math.sin(theta) + dz_r * math.cos(theta)
            if -rampa['profundidade'] / 2 <= u <= rampa['profundidade'] / 2 and abs(v) <= (config.largura_pista / 2):
                sobre_alguma_rampa = True
                # Função que calcula a altura da rampa em um ponto (u, v)
                def altura_atual_rampa(u_val, v_val):
                    return rampa['altura_maxima'] * (1 - (2 * u_val / rampa['profundidade']) ** 2) * (1 - (2 * v_val / config.largura_pista) ** 2)
                alt_rampa = altura_atual_rampa(u, v) - config.deslocamento_rampa
                meio_moto = config.tamanho_moto / 2
                if self.pos.y - meio_moto < (config.nível_chão + alt_rampa):
                    self.pos.y = config.nível_chão + alt_rampa + meio_moto
                    self.velocidade_vertical = 0.0
                # Impulso vertical se estiver centralizado lateralmente e na parte final da rampa (apenas uma vez)
                if abs(v) < (config.largura_pista * 0.1) and u > (0.3 * rampa['profundidade']) and self.velocidade > 0 and self.velocidade_vertical == 0 and not self.rampa_acionada:
                    self.velocidade_vertical = config.velocidade_salto_rampa
                    self.rampa_acionada = True
        if not sobre_alguma_rampa:
            self.rampa_acionada = False

        # Garante que a moto não fique abaixo do nível da pista (chão)
        if self.pos.y < (config.nível_pista + config.tamanho_moto / 2):
            self.pos.y = config.nível_pista + config.tamanho_moto / 2
            self.velocidade_vertical = 0.0

    def draw(self):
        """
        Desenha a moto na posição e orientação atuais.
        Chama a função 'desenhar_moto_model' passando os parâmetros necessários.
        """
        desenhar_moto_model(self.modelo, self.pos, self.direcao, self.angulo_inclinacao, self.escala)
