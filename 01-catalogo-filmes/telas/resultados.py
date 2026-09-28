import tkinter as tk
from tkinter import ttk
from funcionalidades.busca import buscar, listar_generos
from utils import (
    COR_FUNDO, COR_PESQUISA, COR_SUBTEXTO, COR_TEXTO,
    COR_DESTAQUE, COR_CAPA, COR_CARD,
)

_SEM_FILTRO = "Todos os gêneros"

# ── Constantes da grade de resultados ────────────────────────────────────────
COLS    = 6
POR_PAG = COLS * 5
CARD_W  = 120
CARD_H  = 168


# ── Helper privado ────────────────────────────────────────────────────────────
def _criar_card(frame_grade, filme, row, col):
    """Card menor, posicionado via grid(), para a grade de resultados."""
    card = tk.Frame(frame_grade, bg=COR_FUNDO)
    card.grid(row=row, column=col, padx=6, pady=8, sticky="n")

    capa = tk.Canvas(card, width=CARD_W, height=CARD_H, bg=COR_CAPA,
                     highlightthickness=0, cursor="hand2")
    capa.create_text(CARD_W // 2, CARD_H // 2 - 10,
                     text="🎬", font=("Helvetica", 22))
    capa.create_text(CARD_W // 2, CARD_H // 2 + 18,
                     text=filme["ano"], fill=COR_SUBTEXTO, font=("Helvetica", 9))
    capa.pack()

    tk.Label(card, text=filme["titulo"], bg=COR_FUNDO, fg=COR_TEXTO,
             font=("Helvetica", 8), wraplength=CARD_W,
             justify="center").pack(pady=(4, 0))


# ── Tela de resultados ────────────────────────────────────────────────────────
def renderizarResultados(tela, todos_os_filmes, query, genero=None):
    """
    Limpa a janela e monta a tela de resultados.
    - `query`  : texto digitado na barra de pesquisa (pode ser vazio).
    - `genero` : filtro de gênero ativo (None = sem filtro).
    Redireciona para a tela inicial se ambos estiverem vazios.
    """
    # Guarda: sem query e sem gênero → volta para o início
    if not query.strip() and not genero:
        from telas.inicio import renderizarInicio
        renderizarInicio(tela, todos_os_filmes)
        return

    for w in tela.winfo_children():
        w.destroy()

    resultados = buscar(query, todos_os_filmes, genero=genero)
    total_pags = max(1, (len(resultados) + POR_PAG - 1) // POR_PAG)
    pagina     = [0]

    # ── Cabeçalho / barra de pesquisa + filtro de gênero ─────────────────────
    cabecalho = tk.Frame(tela, bg=COR_FUNDO, pady=14)
    cabecalho.pack(fill="x")

    frame_pesquisa = tk.Frame(cabecalho, bg=COR_PESQUISA, pady=6, padx=10)
    frame_pesquisa.pack()

    tk.Label(frame_pesquisa, text="🔍", bg=COR_PESQUISA, fg=COR_SUBTEXTO,
             font=("Helvetica", 13)).pack(side="left", padx=(0, 4))

    entrada = tk.Entry(frame_pesquisa, width=30, font=("Helvetica", 13),
                       bg=COR_PESQUISA, fg=COR_TEXTO,
                       insertbackground=COR_TEXTO, relief="flat")
    entrada.insert(0, query)
    entrada.pack(side="left")

    # Separador visual entre a entrada e o combobox
    tk.Frame(frame_pesquisa, bg="#555555", width=1,
             height=22).pack(side="left", padx=10)

    # Combobox de gênero — permite selecionar/trocar/remover filtro manualmente
    generos_disponiveis = [_SEM_FILTRO] + listar_generos(todos_os_filmes)
    combo_genero = ttk.Combobox(frame_pesquisa, values=generos_disponiveis,
                                width=16, state="readonly")
    combo_genero.set(genero if genero else _SEM_FILTRO)
    combo_genero.pack(side="left")

    def _nova_busca(event=None):
        """Ponto único de navegação: lê entrada + combobox e decide para onde ir."""
        termo      = entrada.get().strip()
        sel        = combo_genero.get()
        genero_sel = None if sel == _SEM_FILTRO else sel
        renderizarResultados(tela, todos_os_filmes, termo, genero=genero_sel)

    entrada.bind("<Return>", _nova_busca)
    combo_genero.bind("<<ComboboxSelected>>", _nova_busca)

    tk.Frame(tela, bg=COR_DESTAQUE, height=2).pack(fill="x")

    # ── Área scrollável ───────────────────────────────────────────────────────
    frame_externo = tk.Frame(tela, bg=COR_FUNDO)
    frame_externo.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame_externo, bg=COR_FUNDO, highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_externo, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_conteudo = tk.Frame(canvas, bg=COR_FUNDO)
    win = canvas.create_window((0, 0), window=frame_conteudo, anchor="nw")
    frame_conteudo.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
    tela.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
    tela.bind_all("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
    tela.bind_all("<Button-5>",   lambda e: canvas.yview_scroll(1,  "units"))

    # ── Contador de resultados ────────────────────────────────────────────────
    n      = len(resultados)
    sufixo = "s" if n != 1 else ""
    if genero and query:
        descricao = f'"{query}" em {genero}'
    elif genero:
        descricao = f"gênero {genero}"
    else:
        descricao = f'"{query}"'
    tk.Label(frame_conteudo,
             text=f'{n} resultado{sufixo} para {descricao}',
             bg=COR_FUNDO, fg=COR_SUBTEXTO, font=("Helvetica", 11),
             anchor="w", padx=20).pack(fill="x", pady=(12, 6))

    # ── Grade de filmes ───────────────────────────────────────────────────────
    frame_grade = tk.Frame(frame_conteudo, bg=COR_FUNDO)
    frame_grade.pack(padx=14, anchor="w")
    for c in range(COLS):
        frame_grade.columnconfigure(c, weight=1)

    # ── Paginação ─────────────────────────────────────────────────────────────
    frame_pag = tk.Frame(frame_conteudo, bg=COR_FUNDO, pady=18)
    frame_pag.pack()

    # ── Funções internas ──────────────────────────────────────────────────────
    def _renderizar_pagina():
        for w in frame_grade.winfo_children():
            w.destroy()

        inicio         = pagina[0] * POR_PAG
        filmes_pagina  = resultados[inicio:inicio + POR_PAG]

        if not filmes_pagina:
            tk.Label(frame_grade,
                     text="Nenhum filme encontrado para esta busca.",
                     bg=COR_FUNDO, fg=COR_SUBTEXTO,
                     font=("Helvetica", 13)).grid(row=0, column=0,
                                                  columnspan=COLS, pady=40)
        else:
            for i, filme in enumerate(filmes_pagina):
                _criar_card(frame_grade, filme, i // COLS, i % COLS)

        _atualizar_paginacao()
        tela.update_idletasks()
        canvas.yview_moveto(0)

    def _atualizar_paginacao():
        for w in frame_pag.winfo_children():
            w.destroy()
        if total_pags <= 1:
            return

        def _anterior():
            pagina[0] -= 1
            _renderizar_pagina()

        def _proxima():
            pagina[0] += 1
            _renderizar_pagina()

        tk.Button(frame_pag, text="◀  Anterior", command=_anterior,
                  bg=COR_CARD, fg=COR_TEXTO, font=("Helvetica", 10),
                  relief="flat", padx=10, pady=4,
                  state="normal" if pagina[0] > 0 else "disabled"
                  ).pack(side="left", padx=6)

        tk.Label(frame_pag,
                 text=f"Página {pagina[0] + 1} de {total_pags}",
                 bg=COR_FUNDO, fg=COR_SUBTEXTO,
                 font=("Helvetica", 10)).pack(side="left", padx=14)

        tk.Button(frame_pag, text="Próxima  ▶", command=_proxima,
                  bg=COR_CARD, fg=COR_TEXTO, font=("Helvetica", 10),
                  relief="flat", padx=10, pady=4,
                  state="normal" if pagina[0] < total_pags - 1 else "disabled"
                  ).pack(side="left", padx=6)

    _renderizar_pagina()
