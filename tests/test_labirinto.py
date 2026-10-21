"""
Testes do labirinto. Rode com:  python -m pytest -v

Cada teste aqui e uma PROMESSA que o codigo faz.
Se um teste quebra, o codigo deixou de cumprir a promessa.
"""
import random

import pytest

from gerar import gerar_labirinto_com_caminho
from labirinto import resolve_labirinto, resolve_labirinto_a_star


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
