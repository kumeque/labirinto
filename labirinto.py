from collections import deque
import heapq

if __package__:
    from .gerar import gerar_labirinto_com_caminho, gerar_labirinto_mais_desafiador
else:
    from gerar import gerar_labirinto_com_caminho, gerar_labirinto_mais_desafiador

def _dimensoes_validas(matriz, inicio, fim=None):
    """
    Valida a matriz e as posicoes.
    Retorna (linhas, colunas) se estiver tudo certo, ou None se for invalido.
    Se fim for None, valida apenas o inicio.
    """
    if not matriz or not matriz[0]:
        return None

    linhas = len(matriz)
    colunas = len(matriz[0])

    for posicao in (inicio, fim):
        if posicao is None:
            continue
        if not (0 <= posicao[0] < linhas and 0 <= posicao[1] < colunas):
            return None
        if matriz[posicao[0]][posicao[1]] == 1:
            return None

    return linhas, colunas


def iterar_resolve_labirinto(matriz, inicio, fim):
    """
    Gera eventos enquanto resolve o labirinto usando backtracking iterativo:
    - começa no ponto inicial;
    - tenta cada caminho possível;
    - quando encontra um caminho sem saída, volta ao ponto anterior;
    - testa a próxima opção disponível até encontrar a solução.

    Usa uma pilha explícita em vez de recursão, então não estoura o limite
    de recursão do Python mesmo em labirintos grandes.
    """
    dimensoes = _dimensoes_validas(matriz, inicio, fim)
    if dimensoes is None:
        yield "concluido", []
        return
    linhas, colunas = dimensoes
    if inicio == fim:
        yield "caminho", inicio
        yield "concluido", [inicio]
        return

    deslocamentos = ((-1, 0), (1, 0), (0, -1), (0, 1))

    def vizinhos_abertos(posicao):
        linha, coluna = posicao
        abertos = []
        for delta_linha, delta_coluna in deslocamentos:
            nova_linha = linha + delta_linha
            nova_coluna = coluna + delta_coluna
            if (
                0 <= nova_linha < linhas
                and 0 <= nova_coluna < colunas
                and matriz[nova_linha][nova_coluna] == 0
            ):
                abertos.append((nova_linha, nova_coluna))
        return abertos

    visitados = set()
    caminho = []

    visitados.add(inicio)
    caminho.append(inicio)
    yield "explorando", inicio

    # Cada quadro guarda: posição atual, vizinhos possíveis e o índice do
    # próximo vizinho a testar (equivale ao "estado" da chamada recursiva).
    pilha = [[inicio, vizinhos_abertos(inicio), 0]]
    encontrou = False

    while pilha:
        quadro = pilha[-1]
        posicao = quadro[0]
        candidatos = quadro[1]

        if quadro[2] >= len(candidatos):
            pilha.pop()
            caminho.pop()
            yield "retrocesso", posicao
            continue

        proximo = candidatos[quadro[2]]
        quadro[2] += 1

        if proximo in visitados:
            continue

        if proximo == fim:
            caminho.append(proximo)
            encontrou = True
            break

        visitados.add(proximo)
        caminho.append(proximo)
        yield "explorando", proximo
        pilha.append([proximo, vizinhos_abertos(proximo), 0])

    if encontrou:
        for posicao in caminho:
            yield "caminho", posicao
        yield "concluido", caminho
    else:
        yield "concluido", []


def resolve_labirinto(matriz, inicio, fim):
    """Resolve usando backtracking e retorna a lista de posições do caminho."""
    for evento, valor in iterar_resolve_labirinto(matriz, inicio, fim):
        if evento == "concluido":
            return valor
    return []


def iterar_resolve_labirinto_bfs(matriz, inicio, fim):
    """
    Gera eventos enquanto resolve o labirinto usando busca em largura (BFS).
    """
    dimensoes = _dimensoes_validas(matriz, inicio, fim)
    if dimensoes is None:
        yield "concluido", []
        return
    linhas, colunas = dimensoes

    fila = deque([inicio])
    came_from = {inicio: None}
    visitados = set()
    visitados.add(inicio)

    while fila:
        posicao_atual = fila.popleft()
        yield "explorando", posicao_atual

        if posicao_atual == fim:
            caminho = []
            while posicao_atual is not None:
                caminho.append(posicao_atual)
                posicao_atual = came_from[posicao_atual]
            caminho.reverse()
            for posicao in caminho:
                yield "caminho", posicao
            yield "concluido", caminho
            return

        linha, coluna = posicao_atual
        vizinhos = [
            (linha - 1, coluna),
            (linha + 1, coluna),
            (linha, coluna - 1),
            (linha, coluna + 1),
        ]

        for vizinho in vizinhos:
            if (
                0 <= vizinho[0] < linhas
                and 0 <= vizinho[1] < colunas
                and matriz[vizinho[0]][vizinho[1]] == 0
                and vizinho not in visitados
            ):
                visitados.add(vizinho)
                came_from[vizinho] = posicao_atual
                fila.append(vizinho)

    yield "concluido", []


def resolve_labirinto_bfs(matriz, inicio, fim):
    """Resolve usando BFS e retorna a lista de posições do caminho."""
    for evento, valor in iterar_resolve_labirinto_bfs(matriz, inicio, fim):
        if evento == "concluido":
            return valor
    return []


def iterar_resolve_labirinto_a_star(matriz, inicio, fim):
    """
    Gera eventos enquanto resolve o labirinto usando o algoritmo A*.
    """
    dimensoes = _dimensoes_validas(matriz, inicio, fim)
    if dimensoes is None:
        yield "concluido", []
        return
    linhas, colunas = dimensoes

    total_celulas = linhas * colunas
    inicio_indice = inicio[0] * colunas + inicio[1]
    fim_indice = fim[0] * colunas + fim[1]
    heuristica_inicial = abs(inicio[0] - fim[0]) + abs(inicio[1] - fim[1])

    fila_prioridade = [(heuristica_inicial, heuristica_inicial, inicio_indice)]
    came_from = [-1] * total_celulas
    custo_g = [float("inf")] * total_celulas
    custo_g[inicio_indice] = 0
    visitados = bytearray(total_celulas)

    while fila_prioridade:
        _, _, indice_atual = heapq.heappop(fila_prioridade)

        if visitados[indice_atual]:
            continue
        visitados[indice_atual] = 1
        linha, coluna = divmod(indice_atual, colunas)
        posicao_atual = (linha, coluna)
        yield "explorando", posicao_atual

        if indice_atual == fim_indice:
            caminho = []
            indice_caminho = indice_atual
            while indice_caminho != -1:
                caminho.append(divmod(indice_caminho, colunas))
                indice_caminho = came_from[indice_caminho]
            caminho.reverse()
            for posicao in caminho:
                yield "caminho", posicao
            yield "concluido", caminho
            return

        vizinhos = []
        if linha > 0 and matriz[linha - 1][coluna] == 0:
            vizinhos.append(indice_atual - colunas)
        if linha + 1 < linhas and matriz[linha + 1][coluna] == 0:
            vizinhos.append(indice_atual + colunas)
        if coluna > 0 and matriz[linha][coluna - 1] == 0:
            vizinhos.append(indice_atual - 1)
        if coluna + 1 < colunas and matriz[linha][coluna + 1] == 0:
            vizinhos.append(indice_atual + 1)

        for indice_vizinho in vizinhos:
            if visitados[indice_vizinho]:
                continue

            novo_custo_g = custo_g[indice_atual] + 1
            if novo_custo_g < custo_g[indice_vizinho]:
                custo_g[indice_vizinho] = novo_custo_g
                came_from[indice_vizinho] = indice_atual
                linha_vizinho, coluna_vizinho = divmod(indice_vizinho, colunas)
                heuristica = abs(linha_vizinho - fim[0]) + abs(coluna_vizinho - fim[1])
                prioridade = novo_custo_g + heuristica
                heapq.heappush(
                    fila_prioridade,
                    (prioridade, heuristica, indice_vizinho),
                )

    yield "concluido", []


def resolve_labirinto_a_star(matriz, inicio, fim):
    """Resolve usando A* e retorna a lista de posições do caminho."""
    for evento, valor in iterar_resolve_labirinto_a_star(matriz, inicio, fim):
        if evento == "concluido":
            return valor
    return []


def celula_mais_distante(matriz, inicio):
    """Retorna (posicao, distancia) da célula mais longe da entrada."""
    dimensoes = _dimensoes_validas(matriz, inicio)
    if dimensoes is None:
        return inicio, 0
    linhas, colunas = dimensoes

    fila = deque([(inicio, 0)])
    visitados = {inicio}
    posicao_mais_distante = inicio
    distancia_maxima = 0

    while fila:
        posicao, distancia = fila.popleft()
        if distancia > distancia_maxima:
            posicao_mais_distante = posicao
            distancia_maxima = distancia

        linha, coluna = posicao
        vizinhos = (
            (linha - 1, coluna),
            (linha + 1, coluna),
            (linha, coluna - 1),
            (linha, coluna + 1),
        )
        for vizinho in vizinhos:
            if (
                0 <= vizinho[0] < linhas
                and 0 <= vizinho[1] < colunas
                and matriz[vizinho[0]][vizinho[1]] == 0
                and vizinho not in visitados
            ):
                visitados.add(vizinho)
                fila.append((vizinho, distancia + 1))

    return posicao_mais_distante, distancia_maxima

# Registro dos algoritmos disponiveis na interface.
# Para adicionar um novo: basta uma linha aqui.
ALGORITMOS = {
    "Backtracking": iterar_resolve_labirinto,
    "BFS": iterar_resolve_labirinto_bfs,
    "A*": iterar_resolve_labirinto_a_star,
}

if __name__ == "__main__":
    if __package__:
        from .exibir import abrir_interface
    else:
        from exibir import abrir_interface

    abrir_interface(gerar_labirinto_com_caminho, ALGORITMOS)
