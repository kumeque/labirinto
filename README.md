# Labirinto

Gerador e resolvedor de labirintos em Python, com visualização animada em
Tkinter. O projeto cria um labirinto aleatório, permite escolher o algoritmo de
busca e mostra passo a passo como a solução é encontrada.

## Requisitos

- Python 3.10+ (testado com 3.12)
- Tkinter (já incluso na instalação padrão do Python)

Não há dependências externas.

## Como executar

Pela interface gráfica:

```bash
python exibir.py
```

Ou pelo módulo principal:

```bash
python labirinto.py
```

Para apenas gerar e imprimir um labirinto no terminal:

```bash
python gerar.py
```

## Estrutura

| Arquivo | Responsabilidade |
| --- | --- |
| `gerar.py` | Geração do labirinto (recursive backtracker + atalhos) |
| `labirinto.py` | Resolução por Backtracking e por A* (como geradores) |
| `exibir.py` | Interface Tkinter com animação passo a passo |

Os resolvedores são **geradores**: em vez de devolver só o caminho final, eles
emitem eventos (`explorando`, `retrocesso`, `caminho`, `concluido`) que a
interface consome para animar a busca.

## Algoritmos

### Backtracking

Busca em profundidade (DFS) com pilha explícita. Testa cada caminho possível,
volta quando encontra um beco sem saída e segue até achar uma solução.

- Garante encontrar um caminho, se existir.
- **Não** garante o caminho mais curto.
- Ocorre iterativamente, sem recursão, então funciona em labirintos grandes.

### A*

Busca informada com heurística de distância de Manhattan até o destino.

- Encontra o caminho mais curto.
- Explora menos células que o backtracking na maioria dos casos.

## Como usar a interface

- **Algoritmo**: escolhe entre Backtracking e A*.
- **Iniciar resolução**: começa a animar a busca.
- **Novo labirinto**: gera um novo labirinto com as dimensões atuais.
- **Intervalo (ms)**: velocidade da animação (tempo entre passos).
- **Dimensões (linhas x colunas)**: tamanho do labirinto (mínimo 3). Valores
  altos aumentam bastante o número de eventos e o tempo da animação.

Para labirintos maiores que a janela, use as barras de rolagem do painel.

## Legenda de cores

| Cor | Significado |
| --- | --- |
| Azul | Início |
| Vermelho | Destino |
| Escuro | Parede |
| Amarelo | Célula sendo explorada |
| Laranja | Retrocesso (caminho sem saída) |
| Verde | Caminho final encontrado |

## Detalhes de implementação

- O labirinto é gerado com dimensões ímpares no miolo; a entrada fica em
  `(0, 0)` e a saída no canto oposto.
- Em dimensões menores que 3x3, o gerador devolve uma grade totalmente livre.
- A densidade de atalhos difere entre os modos disponíveis em `gerar.py`:
  `gerar_labirinto_com_caminho` (8%) e `gerar_labirinto_mais_desafiador` (2%).
