import random

def _gerar_labirinto(linhas, colunas, taxa_atalhos):
    if linhas <= 0 or colunas <= 0:
        return []
    if linhas < 3 or colunas < 3:
        return [[0] * colunas for _ in range(linhas)]

    matriz = [[1 for _ in range(colunas)] for _ in range(linhas)]
    celulas = [
        (linha, coluna)
        for linha in range(1, linhas - 1, 2)
        for coluna in range(1, colunas - 1, 2)
    ]
    inicio = celulas[0]
    visitados = {inicio}
    pilha = [inicio]
    matriz[0][0] = matriz[0][1] = matriz[1][1] = 0

    while pilha:
        linha, coluna = pilha[-1]
        vizinhos = [
            (linha - 2, coluna),
            (linha + 2, coluna),
            (linha, coluna - 2),
            (linha, coluna + 2),
        ]
        candidatos = [
            posicao
            for posicao in vizinhos
            if 1 <= posicao[0] < linhas - 1
            and 1 <= posicao[1] < colunas - 1
            and posicao not in visitados
        ]

        if not candidatos:
            pilha.pop()
            continue

        proxima_linha, proxima_coluna = random.choice(candidatos)
        matriz[(linha + proxima_linha) // 2][(coluna + proxima_coluna) // 2] = 0
        matriz[proxima_linha][proxima_coluna] = 0
        visitados.add((proxima_linha, proxima_coluna))
        pilha.append((proxima_linha, proxima_coluna))

    ultima_linha, ultima_coluna = celulas[-1]
    for linha in range(ultima_linha + 1, linhas):
        matriz[linha][ultima_coluna] = 0
    for coluna in range(ultima_coluna + 1, colunas):
        matriz[linhas - 1][coluna] = 0

    paredes_entre_celulas = []
    for linha, coluna in celulas:
        if coluna + 2 < colunas - 1 and matriz[linha][coluna + 1] == 1:
            paredes_entre_celulas.append((linha, coluna + 1))
        if linha + 2 < linhas - 1 and matriz[linha + 1][coluna] == 1:
            paredes_entre_celulas.append((linha + 1, coluna))

    quantidade_atalhos = int(len(paredes_entre_celulas) * taxa_atalhos)
    for linha, coluna in random.sample(paredes_entre_celulas, quantidade_atalhos):
        matriz[linha][coluna] = 0

    return matriz


def gerar_labirinto_com_caminho(linhas=20, colunas=40):
    """Gera um labirinto aleatório conectado entre os cantos do mapa."""
    return _gerar_labirinto(linhas, colunas, taxa_atalhos=0.08)


def gerar_labirinto_mais_desafiador(linhas=20, colunas=40):
    """Gera um labirinto profundo, com poucos atalhos e muitos becos."""
    return _gerar_labirinto(linhas, colunas, taxa_atalhos=0.02)

# Função auxiliar para visualizar
def imprimir_labirinto(matriz):
    for linha in matriz:
        print("".join("1" if celula == 1 else "0" for celula in linha))

if __name__ == "__main__":
    matrix = gerar_labirinto_mais_desafiador(20, 40)
    print("Labirinto gerado (20x40) - Versão mais desafiadora:\n")
    imprimir_labirinto(matrix)
    print(f"\nDimensões: {len(matrix)} linhas x {len(matrix[0])} colunas")
