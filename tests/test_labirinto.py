"""
Testes do labirinto. Rode com:  python -m pytest -v

Cada teste aqui e uma PROMESSA que o codigo faz.
Se um teste quebra, o codigo deixou de cumprir a promessa.
"""
import random

import pytest

from gerar import gerar_labirinto_com_caminho
from labirinto import (
    resolve_labirinto,
    resolve_labirinto_a_star,
    resolve_labirinto_bfs,
)


def construir_labirinto(semente, linhas=15, colunas=31):
    """Gera sempre o mesmo labirinto para a mesma semente (teste reproduzivel)."""
    random.seed(semente)
    return gerar_labirinto_com_caminho(linhas, colunas)


def validar_caminho(matriz, caminho, inicio, fim):
    """
    Verifica se um caminho e de fato um caminho valido dentro do labirinto:
    - comeca no inicio e termina no fim;
    - cada passo e para uma celula ADJACENTE (sem pular);
    - nenhuma celula do caminho e parede.
    """
    assert caminho, "o caminho nao pode estar vazio"
    assert caminho[0] == inicio, "o caminho deve comecar no inicio"
    assert caminho[-1] == fim, "o caminho deve terminar no fim"

    for linha, coluna in caminho:
        assert matriz[linha][coluna] == 0, f"a celula {(linha, coluna)} e parede"

    for anterior, atual in zip(caminho, caminho[1:]):
        dist = abs(anterior[0] - atual[0]) + abs(anterior[1] - atual[1])
        assert dist == 1, f"salto invalido de {anterior} para {atual}"


@pytest.mark.parametrize("semente", range(10))
def test_backtracking_encontra_caminho_valido(semente):
    """Promessa: o backtracking sempre encontra algum caminho valido."""
    matriz = construir_labirinto(semente)
    inicio = (0, 0)
    fim = (len(matriz) - 1, len(matriz[0]) - 1)

    caminho = resolve_labirinto(matriz, inicio, fim)

    validar_caminho(matriz, caminho, inicio, fim)


@pytest.mark.parametrize("semente", range(10))
def test_a_star_encontra_caminho_valido(semente):
    """Promessa: o A* sempre encontra um caminho valido."""
    matriz = construir_labirinto(semente)
    inicio = (0, 0)
    fim = (len(matriz) - 1, len(matriz[0]) - 1)

    caminho = resolve_labirinto_a_star(matriz, inicio, fim)

    validar_caminho(matriz, caminho, inicio, fim)


@pytest.mark.parametrize("semente", range(10))
def test_a_star_nunca_e_maior_que_backtracking(semente):
    """Promessa: A* e otimo, entao nunca devolve caminho maior que o backtracking."""
    matriz = construir_labirinto(semente)
    inicio = (0, 0)
    fim = (len(matriz) - 1, len(matriz[0]) - 1)

    caminho_backtracking = resolve_labirinto(matriz, inicio, fim)
    caminho_a_star = resolve_labirinto_a_star(matriz, inicio, fim)

    assert len(caminho_a_star) <= len(caminho_backtracking)


# ---------------------------------------------------------------------------
# TDD: este teste esta VERMELHO de proposito.
# Sua missao e escrever iterar_resolve_labirinto_bfs para ele ficar VERDE.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("semente", range(10))
def test_bfs_devolve_o_mesmo_comprimento_do_a_star(semente):
    """
    Promessa a ser cumprida: BFS e A* sao os dois otimos,
    entao devem achar caminhos do MESMO comprimento no mesmo labirinto.
    """
    from labirinto import resolve_labirinto_bfs

    matriz = construir_labirinto(semente)
    inicio = (0, 0)
    fim = (len(matriz) - 1, len(matriz[0]) - 1)

    caminho_bfs = resolve_labirinto_bfs(matriz, inicio, fim)
    caminho_a_star = resolve_labirinto_a_star(matriz, inicio, fim)

    validar_caminho(matriz, caminho_bfs, inicio, fim)
    assert len(caminho_bfs) == len(caminho_a_star)


# ---------------------------------------------------------------------------
# TDD (transferencia): teste VERMELHO. Escreva celula_mais_distante.
#
# Truque de design de teste: nao sabemos qual celula e a mais distante,
# entao NAO comparamos com um numero fixo. Usamos o proprio BFS como
# ORACULO: medimos o caminho real ate a celula devolvida e conferimos
# se a distancia declarada bate, e se nenhuma outra celula esta mais longe.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("semente", range(3))
def test_celula_mais_distante_esta_realmente_na_mais_longe(semente):
    from labirinto import celula_mais_distante, resolve_labirinto_bfs

    matriz = construir_labirinto(semente, linhas=9, colunas=15)
    inicio = (0, 0)
    linhas, colunas = len(matriz), len(matriz[0])

    posicao, distancia = celula_mais_distante(matriz, inicio)

    # 1. a celula devolvida existe e nao e parede
    assert matriz[posicao[0]][posicao[1]] == 0

    # 2. a distancia declarada bate com o caminho real ate essa celula
    caminho = resolve_labirinto_bfs(matriz, inicio, posicao)
    assert caminho, "a celula devolvida nem e alcancavel a partir da entrada"
    assert len(caminho) - 1 == distancia, (
        f"declarou distancia {distancia}, mas o caminho real tem {len(caminho) - 1} passos"
    )

    # 3. nenhuma outra celula livre esta mais longe
    for linha in range(linhas):
        for coluna in range(colunas):
            if matriz[linha][coluna] != 0:
                continue
            outro = resolve_labirinto_bfs(matriz, inicio, (linha, coluna))
            if not outro:
                continue
            real = len(outro) - 1
            assert real <= distancia, (
                f"a celula {(linha, coluna)} esta a {real} passos, "
                f"mais longe que a devolvida ({distancia})"
            )


# ---------------------------------------------------------------------------
# Caracterizacao: fixam o comportamento ATUAL nos casos de borda.
# Escritos ANTES do refactor das validacoes, para provar que ele nao
# muda nada. Se algum destes quebrar, o refactor quebrou o comportamento.
# ---------------------------------------------------------------------------
TODOS_OS_RESOLVEDORES = [
    resolve_labirinto,
    resolve_labirinto_bfs,
    resolve_labirinto_a_star,
]


CASOS_INVALIDOS = [
    ([], (0, 0), (0, 0)),
    ([[1, 1], [1, 1]], (0, 0), (1, 1)),
    ([[0, 0], [0, 0]], (5, 5), (1, 1)),
    ([[0, 0], [0, 0]], (0, 0), (5, 5)),
]


@pytest.mark.parametrize("resolver", TODOS_OS_RESOLVEDORES)
@pytest.mark.parametrize("matriz,inicio,fim", CASOS_INVALIDOS)
def test_entrada_invalida_devolve_caminho_vazio(resolver, matriz, inicio, fim):
    assert resolver(matriz, inicio, fim) == []


@pytest.mark.parametrize("resolver", TODOS_OS_RESOLVEDORES)
def test_inicio_igual_ao_fim_devolve_uma_celula(resolver):
    matriz = [[0, 0], [0, 0]]
    assert resolver(matriz, (0, 0), (0, 0)) == [(0, 0)]


@pytest.mark.parametrize("matriz,inicio", [
    ([], (0, 0)),
    ([[1, 1], [1, 1]], (0, 0)),
    ([[0, 0], [0, 0]], (5, 5)),
])
def test_celula_mais_distante_entrada_invalida(matriz, inicio):
    from labirinto import celula_mais_distante

    assert celula_mais_distante(matriz, inicio) == (inicio, 0)
