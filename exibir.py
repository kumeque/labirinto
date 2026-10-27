import tkinter as tk
from tkinter import ttk

if __package__:
    from .labirinto import celula_mais_distante
else:
    from labirinto import celula_mais_distante


class VisualizadorLabirinto:
    TAMANHO_CELULA = 22
    CORES = {
        "parede": "#263238",
        "livre": "#f4f6f8",
        "explorando": "#ffd166",
        "retrocesso": "#f4976c",
        "caminho": "#51c878",
        "inicio": "#4a90e2",
        "fim": "#e45858",
        "grade": "#cbd3da",
    }

    def __init__(self, janela, gerar_labirinto, algoritmos):
        self.algoritmos = algoritmos
        self.janela = janela
        self.gerar_labirinto = gerar_labirinto
        self.matriz = []
        self.inicio = (0, 0)
        self.fim = (0, 0)
        self.eventos = None
        self.id_after = None
        self.celulas = []

        janela.title("Visualizador de Labirinto")
        janela.minsize(760, 480)

        controles = ttk.Frame(janela, padding=(12, 12, 12, 6))
        controles.pack(fill=tk.X)

        ttk.Label(controles, text="Algoritmo:").pack(side=tk.LEFT)
        self.algoritmo = tk.StringVar(value="Backtracking")
        self.seletor_algoritmo = ttk.Combobox(
            controles,
            textvariable=self.algoritmo,
            values=tuple(algoritmos),
            state="readonly",
            width=16,
        )
        self.seletor_algoritmo.pack(side=tk.LEFT, padx=(6, 14))

        self.botao_iniciar = ttk.Button(
            controles, text="Iniciar resolução", command=self.iniciar
        )
        self.botao_iniciar.pack(side=tk.LEFT)
        ttk.Button(
            controles, text="Novo labirinto", command=self.novo_labirinto
        ).pack(side=tk.LEFT, padx=8)

        ttk.Label(controles, text="Intervalo (ms):").pack(side=tk.LEFT, padx=(10, 4))
        self.intervalo = tk.IntVar(value=35)
        ttk.Scale(
            controles,
            from_=5,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.intervalo,
            length=150,
        ).pack(side=tk.LEFT)

        dimensoes = ttk.Frame(janela, padding=(12, 0, 12, 6))
        dimensoes.pack(fill=tk.X)
        ttk.Label(dimensoes, text="Dimensões (linhas x colunas):").pack(side=tk.LEFT)
        self.linhas_var = tk.IntVar(value=20)
        self.colunas_var = tk.IntVar(value=40)
        tk.Spinbox(
            dimensoes, from_=3, to=201, width=5, textvariable=self.linhas_var
        ).pack(side=tk.LEFT, padx=(6, 2))
        ttk.Label(dimensoes, text="x").pack(side=tk.LEFT)
        tk.Spinbox(
            dimensoes, from_=3, to=201, width=5, textvariable=self.colunas_var
        ).pack(side=tk.LEFT, padx=(2, 0))
        ttk.Label(
            dimensoes, text="(mínimo 3; valores altos deixam a animação longa)"
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.status = tk.StringVar(value="Pronto para resolver.")
        ttk.Label(janela, textvariable=self.status, padding=(12, 4)).pack(
            fill=tk.X
        )

        area_labirinto = ttk.Frame(janela, padding=(12, 4, 12, 8))
        area_labirinto.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(
            area_labirinto,
            background=self.CORES["livre"],
            highlightthickness=0,
        )
        barra_vertical = ttk.Scrollbar(
            area_labirinto, orient=tk.VERTICAL, command=self.canvas.yview
        )
        barra_horizontal = ttk.Scrollbar(
            area_labirinto, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.canvas.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set,
        )
        barra_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        barra_horizontal.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        legenda = ttk.Frame(janela, padding=(12, 4, 12, 10))
        legenda.pack(fill=tk.X)
        self._criar_item_legenda(legenda, "Início", self.CORES["inicio"])
        self._criar_item_legenda(legenda, "Destino", self.CORES["fim"])
        self._criar_item_legenda(legenda, "Explorando", self.CORES["explorando"])
        self._criar_item_legenda(legenda, "Retrocesso", self.CORES["retrocesso"])
        self._criar_item_legenda(legenda, "Caminho", self.CORES["caminho"])

        self.novo_labirinto()
        janela.protocol("WM_DELETE_WINDOW", self.fechar)

    @staticmethod
    def _criar_item_legenda(pai, texto, cor):
        amostra = tk.Canvas(pai, width=14, height=14, highlightthickness=0)
        amostra.create_rectangle(1, 1, 13, 13, fill=cor, outline=cor)
        amostra.pack(side=tk.LEFT, padx=(0, 4))
        ttk.Label(pai, text=texto).pack(side=tk.LEFT, padx=(0, 14))

    def _parar_animacao(self):
        if self.id_after is not None:
            self.janela.after_cancel(self.id_after)
            self.id_after = None
        self.eventos = None
        self.botao_iniciar.configure(state=tk.NORMAL)
        self.seletor_algoritmo.configure(state="readonly")

    def _ler_dimensoes(self):
        try:
            linhas = int(self.linhas_var.get())
        except (tk.TclError, ValueError):
            linhas = 20
        try:
            colunas = int(self.colunas_var.get())
        except (tk.TclError, ValueError):
            colunas = 40
        linhas = min(max(linhas, 3), 201)
        colunas = min(max(colunas, 3), 201)
        # Reflete no formulário o valor efetivamente usado.
        self.linhas_var.set(linhas)
        self.colunas_var.set(colunas)
        return linhas, colunas

    def novo_labirinto(self):
        self._parar_animacao()
        linhas, colunas = self._ler_dimensoes()
        self.matriz = self.gerar_labirinto(linhas, colunas)
        self.inicio = (0, 0)
        self.fim = (len(self.matriz) - 1, len(self.matriz[0]) - 1)
        self._desenhar_labirinto()
        self.status.set(
            f"Novo labirinto {linhas}x{colunas} gerado. Pronto para resolver."
        )

    def _desenhar_labirinto(self):
        self.canvas.delete("all")
        self.celulas = []
        tamanho = self.TAMANHO_CELULA
        linhas = len(self.matriz)
        colunas = len(self.matriz[0])
        self.canvas.configure(
            width=colunas * tamanho,
            height=linhas * tamanho,
            scrollregion=(0, 0, colunas * tamanho, linhas * tamanho),
        )

        for linha in range(linhas):
            linha_celulas = []
            for coluna in range(colunas):
                posicao = (linha, coluna)
                cor = self.CORES["parede"] if self.matriz[linha][coluna] == 1 else self.CORES["livre"]
                if posicao == self.inicio:
                    cor = self.CORES["inicio"]
                elif posicao == self.fim:
                    cor = self.CORES["fim"]

                x1, y1 = coluna * tamanho, linha * tamanho
                celula = self.canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + tamanho,
                    y1 + tamanho,
                    fill=cor,
                    outline=self.CORES["grade"],
                )
                linha_celulas.append(celula)
            self.celulas.append(linha_celulas)

    def iniciar(self):
        self._desenhar_labirinto()
        resolver = self.algoritmos[self.algoritmo.get()]

        self.eventos = iter(resolver(self.matriz, self.inicio, self.fim))
        self.botao_iniciar.configure(state=tk.DISABLED)
        self.seletor_algoritmo.configure(state=tk.DISABLED)
        self.status.set(f"Executando {self.algoritmo.get()}...")
        self._avancar()

    def _avancar(self):
        try:
            evento, valor = next(self.eventos)
        except StopIteration:
            self._finalizar([])
            return
        except Exception as erro:
            self._finalizar([])
            self.status.set(f"Erro ao resolver: {type(erro).__name__}: {erro}")
            return

        if evento == "explorando":
            self._colorir(valor, "explorando")
        elif evento == "retrocesso":
            self._colorir(valor, "retrocesso")
        elif evento == "caminho":
            self._colorir(valor, "caminho")
        elif evento == "concluido":
            self._finalizar(valor)
            return

        self.id_after = self.janela.after(
            max(1, int(self.intervalo.get())), self._avancar
        )

    def _colorir(self, posicao, estado):
        if posicao == self.inicio or posicao == self.fim:
            return
        linha, coluna = posicao
        self.canvas.itemconfigure(
            self.celulas[linha][coluna], fill=self.CORES[estado]
        )

    def _finalizar(self, caminho):
        self.id_after = None
        self.eventos = None
        self.botao_iniciar.configure(state=tk.NORMAL)
        self.seletor_algoritmo.configure(state="readonly")
        if caminho:
            self.status.set(f"Caminho encontrado: {len(caminho)} células.")
        else:
            self.status.set("Não foi encontrado um caminho até o destino.")

    def fechar(self):
        if self.id_after is not None:
            self.janela.after_cancel(self.id_after)
        self.janela.destroy()


def abrir_interface(gerar_labirinto, algoritmos):
    janela = tk.Tk()
    VisualizadorLabirinto(janela, gerar_labirinto, algoritmos)
    janela.mainloop()

# Registro dos algoritmos disponiveis na interface.
# Para adicionar um novo: basta uma linha aqui.

if __name__ == "__main__":
    if __package__:
        from .gerar import gerar_labirinto_com_caminho
        from .labirinto import (
            iterar_resolve_labirinto,
            iterar_resolve_labirinto_a_star,
            ALGORITMOS,
        )
    else:
        from gerar import gerar_labirinto_com_caminho
        from labirinto import (
            iterar_resolve_labirinto,
            iterar_resolve_labirinto_a_star,
            ALGORITMOS,
        )

    abrir_interface(gerar_labirinto_com_caminho, ALGORITMOS)
