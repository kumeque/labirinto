# Labirinto

Gerador e resolvedor de labirintos em Python, com visualização animada em
Tkinter. Você gera um labirinto aleatório, escolhe o algoritmo de busca e vê
passo a passo como ele procura a saída.

## Como executar

Interface gráfica:

```bash
python exibir.py
```

Pelo módulo principal (abre a mesma interface):

```bash
python labirinto.py
```

Apenas gerar e imprimir um labirinto no terminal:

```bash
python gerar.py
```

## Como rodar os testes

```bash
pip install -r requirements-dev.txt
pytest
```

O `pytest.ini` coloca a raiz do projeto no `sys.path`, então `pytest` e
`python -m pytest` funcionam igual.

## Arquitetura

O projeto tem três camadas, e a dependência aponta **num sentido só**:

```
gerar.py  ──matriz──►  labirinto.py  ──eventos──►  exibir.py  ──pixels──►  tela
  dados                 lógica                     apresentação
```

| Arquivo | Responsabilidade |
| --- | --- |
| `gerar.py` | Cria a matriz do labirinto (`0` = livre, `1` = parede) |
| `labirinto.py` | Resolve o labirinto e mede distâncias |
| `exibir.py` | Janela Tkinter, desenho e animação |

`exibir.py` **não conhece nenhum algoritmo**. Ele recebe um dicionário
(`ALGORITMOS`) e reage a eventos. É por isso que adicionar um algoritmo novo não
exige tocar na interface.

## O contrato de eventos

Os resolvedores são **geradores**: em vez de devolver só o caminho final, eles
emitem eventos que a interface consome para animar a busca.

| Evento | Significado | Backtracking | BFS | A* |
| --- | --- | --- | --- | --- |
| `"explorando"` | célula visitada | ✅ | ✅ | ✅ |
| `"retrocesso"` | beco sem saída | ✅ | — | — |
| `"caminho"` | célula do caminho final | ✅ | ✅ | ✅ |
| `"concluido"` | fim (traz a lista do caminho) | ✅ | ✅ | ✅ |

BFS e A* nunca emitem `"retrocesso"`: eles não voltam atrás, só avançam.

Cada algoritmo existe em duas formas:

- `iterar_resolve_labirinto_*` — o gerador que narra os eventos (usado pela interface)
- `resolve_labirinto_*` — o atalho que consome os eventos e devolve só a lista final (usado nos testes e no terminal)

## Algoritmos

A diferença entre os três **não é o que fazem — é em que ordem escolhem a
próxima célula**. Mesmo grafo, mesmos vizinhos, mesma marcação de visitados.

| Algoritmo | Garante caminho mínimo? | Escolhe a próxima célula por... | Estrutura |
| --- | --- | --- | --- |
| **Backtracking** | Não | a mais recente (mergulha até o fundo) | pilha — LIFO |
| **BFS** | Sim | a mais antiga (camada por camada de distância) | fila — FIFO |
| **A\*** | Sim | a de menor `g + h` (já andei + falta estimado) | fila de prioridade |

`g` é o custo real percorrido até a célula. `h` é a distância de Manhattan até o
destino (estimativa que nunca supera a real). A\* equilibra os dois; olhar só
`h` seria *Greedy Best-First*, que é mais rápido e **não** garante o mínimo.

Células exploradas numa amostra de 200 labirintos 15x31 (média):

| Backtracking | BFS | A\* |
| --- | --- | --- |
| 188 | 184 | **124** |

BFS e A\* acham o mesmo caminho; A\* chega lá explorando cerca de um terço
menos.

## Como adicionar um algoritmo novo

1. Escreva `iterar_resolve_labirinto_<nome>(matriz, inicio, fim)` como gerador,
   emitindo os eventos do contrato acima.
2. Escreva `resolve_labirinto_<nome>(matriz, inicio, fim)`, que consome o
   gerador e devolve só a lista final.
3. Acrescente uma linha em `ALGORITMOS` (`labirinto.py`).
4. Adicione um teste em `tests/test_labirinto.py`.

Os passos 1, 2 e 3 acontecem todos em `labirinto.py`; o passo 4, em `tests/`.
Nenhum deles toca o `exibir.py` — a interface lê as opções do Combobox direto do
dicionário.

## Como usar a interface

- **Algoritmo**: Backtracking, BFS ou A*.
- **Iniciar resolução**: anima a busca do início (azul) até o destino (vermelho).
- **Novo labirinto**: gera outro com as dimensões atuais.
- **Intervalo (ms)**: velocidade da animação.
- **Dimensões (linhas x colunas)**: mínimo 3. Valores altos geram muitos eventos
  e animação longa.

Para labirintos maiores que a janela, use as barras de rolagem.

## Legenda de cores

| Cor | Significado |
| --- | --- |
| Azul | Início |
| Vermelho | Destino |
| Escuro | Parede |
| Amarelo | Célula sendo explorada |
| Laranja | Retrocesso (só no backtracking) |
| Verde | Caminho final |

## Detalhes de implementação

- A entrada é sempre `(0, 0)` e a saída, o canto inferior direito.
- O miolo do labirinto usa dimensões ímpares; o gerador parte de uma árvore
  geradora e depois abre atalhos (`gerar_labirinto_com_caminho` 8%,
  `gerar_labirinto_mais_desafiador` 2%).
- Em dimensões menores que 3x3, o gerador devolve uma grade totalmente livre.
- `celula_mais_distante(matriz, inicio)` devolve a célula mais longe da entrada e
  a distância até ela. Ainda não é usada pela interface.

## Próximos passos

- Modo difícil: colocar a saída em `celula_mais_distante`, tornando o caminho
  mínimo o mais longo possível. Isso finalmente daria uso ao
  `gerar_labirinto_mais_desafiador`, hoje acessível só pelo `python gerar.py`.
- Testar o contrato de eventos (hoje os 61 testes cobrem o resultado dos
  algoritmos, não a sequência de eventos que a interface consome).
- Separar o `exibir.py`: hoje ele concentra layout, estado, desenho e animação.
