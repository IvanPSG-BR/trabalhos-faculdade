import tkinter as tk
from tkinter import ttk
from funcionalidades.busca import buscar_api, buscar_por_genero, buscar_com_filtro
from dados import GENEROS as _GENEROS
from telas.inicio import (
    COR_FUNDO, COR_PESQUISA, COR_SUBTEXTO, COR_TEXTO,
    COR_DESTAQUE, COR_CAPA, COR_CARD,
    carregar_imagem,
)

_SEM_FILTRO = "Todos os gêneros"

# ── Constantes da grade de resultados ────────────────────────────────────────
COLS    = 6
POR_PAG = COLS * 5
CARD_W  = 120
CARD_H  = 168


# ── Helper privado ────────────────────────────────────────────────────────────
def _criar_card(frame_grade, filme, row, col, ao_clicar=None):
    """Card menor, posicionado via grid(), para a grade de resultados."""
    titulo = filme.get("title", "")
    poster = filme.get("poster_path")

    card = tk.Frame(frame_grade, bg=COR_FUNDO)
    card.grid(row=row, column=col, padx=6, pady=8, sticky="n")

    capa = tk.Canvas(card, width=CARD_W, height=CARD_H, bg=COR_CAPA,
                     highlightthickness=0, cursor="hand2")
    ph_id = capa.create_text(CARD_W // 2, CARD_H // 2,
                              text="🎬", font=("Helvetica", 22), fill=COR_SUBTEXTO)
    capa.pack()

    lbl_titulo = tk.Label(card, text=titulo, bg=COR_FUNDO, fg=COR_TEXTO,
                          font=("Helvetica", 8), wraplength=CARD_W,
                          justify="center", cursor="hand2")
    lbl_titulo.pack(pady=(4, 0))

    if ao_clicar:
        handler = lambda e, f=filme: ao_clicar(f)
        capa.bind("<Button-1>", handler)
        lbl_titulo.bind("<Button-1>", handler)

    if poster:
        def _aplicar(photo, c=capa, pid=ph_id):
            c.delete(pid)
            c.create_image(0, 0, anchor="nw", image=photo)
            c._img = photo
        carregar_imagem(poster, CARD_W, CARD_H,
                        lambda photo: capa.after(0, lambda p=photo: _aplicar(p)))


# ── Tela de resultados ────────────────────────────────────────────────────────
def renderizarResultados(tela, filmes_inicio, query, genero=None, _pagina=1):
    """
    Limpa a janela e monta a tela de resultados.
    - `filmes_inicio` : dict {genero: Response} retornado por dados.carregar_filmes().
    - `query`         : texto digitado na barra de pesquisa (pode ser vazio).
    - `genero`        : filtro de gênero ativo (None = sem filtro).
    - `_pagina`       : página atual (1-indexed); para busca via API cada página
                        corresponde a uma chamada ao endpoint /search/movie/.
    Redireciona para a tela inicial se query e genero estiverem vazios.
    """
    # Guarda: sem query e sem gênero → volta para o início
    if not query.strip() and not genero:
        from telas.inicio import renderizarInicio
        renderizarInicio(tela, filmes_inicio)
        return

    for w in tela.winfo_children():
        w.destroy()

    # ── Busca — três casos distintos ─────────────────────────────────────────
    if query.strip() and genero:
        # Query + filtro de gênero: agrega múltiplas páginas da API e pagina
        # localmente para garantir páginas com tamanho uniforme (≤ POR_PAG).
        resultados, total_pags = buscar_com_filtro(
            query, genero, pagina_local=_pagina, por_pagina=POR_PAG)

    elif query.strip():
        # Só query: paginação direta via API (cada _pagina = 1 chamada).
        resultados, total_pags = buscar_api(query, page=_pagina)
        total_pags = max(1, total_pags)

    else:
        # Só gênero (vindo do "Ver Mais"): usa /discover/movie com paginação.
        resultados, total_pags = buscar_por_genero(genero, page=_pagina)
        total_pags = max(1, total_pags)

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

    # Combobox de gênero — lista fixa de todos os gêneros disponíveis
    generos_disponiveis = [_SEM_FILTRO] + [g["name"] for g in _GENEROS]
    combo_genero = ttk.Combobox(frame_pesquisa, values=generos_disponiveis,
                                width=16, state="readonly")
    combo_genero.set(genero if genero else _SEM_FILTRO)
    combo_genero.pack(side="left")

    def _nova_busca(event=None):
        """Ponto único de navegação: lê entrada + combobox e decide para onde ir."""
        termo      = entrada.get().strip()
        sel        = combo_genero.get()
        genero_sel = None if sel == _SEM_FILTRO else sel
        # Nova busca sempre começa na página 1
        renderizarResultados(tela, filmes_inicio, termo, genero=genero_sel, _pagina=1)

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

    def _ao_clicar_filme(f):
        from telas.filme import renderizarFilme
        renderizarFilme(tela, f,
                        voltar=lambda: renderizarResultados(
                            tela, filmes_inicio, query,
                            genero=genero, _pagina=_pagina))

    if not resultados:
        tk.Label(frame_grade,
                 text="Nenhum filme encontrado para esta busca.",
                 bg=COR_FUNDO, fg=COR_SUBTEXTO,
                 font=("Helvetica", 13)).grid(row=0, column=0,
                                              columnspan=COLS, pady=40)
    else:
        for i, filme in enumerate(resultados):
            _criar_card(frame_grade, filme, i // COLS, i % COLS,
                        ao_clicar=_ao_clicar_filme)

    # ── Paginação ─────────────────────────────────────────────────────────────
    # Cada página corresponde a uma chamada à API; navegar reconstrói a tela.
    if total_pags > 1:
        frame_pag = tk.Frame(frame_conteudo, bg=COR_FUNDO, pady=18)
        frame_pag.pack()

        tk.Button(frame_pag, text="◀  Anterior",
                  command=lambda: renderizarResultados(
                      tela, filmes_inicio, query, genero=genero, _pagina=_pagina - 1),
                  bg=COR_CARD, fg=COR_TEXTO, font=("Helvetica", 10),
                  relief="flat", padx=10, pady=4,
                  state="normal" if _pagina > 1 else "disabled",
                  ).pack(side="left", padx=6)

        tk.Label(frame_pag,
                 text=f"Página {_pagina} de {total_pags}",
                 bg=COR_FUNDO, fg=COR_SUBTEXTO,
                 font=("Helvetica", 10)).pack(side="left", padx=14)

        tk.Button(frame_pag, text="Próxima  ▶",
                  command=lambda: renderizarResultados(
                      tela, filmes_inicio, query, genero=genero, _pagina=_pagina + 1),
                  bg=COR_CARD, fg=COR_TEXTO, font=("Helvetica", 10),
                  relief="flat", padx=10, pady=4,
                  state="normal" if _pagina < total_pags else "disabled",
                  ).pack(side="left", padx=6)
