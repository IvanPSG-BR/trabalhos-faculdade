import tkinter as tk
from utils import COR_FUNDO, COR_PESQUISA, COR_SUBTEXTO, COR_TEXTO, COR_DESTAQUE, construir_faixas


def renderizarInicio(tela, filmes):
    """Monta toda a interface da tela inicial dentro da janela recebida."""
    for w in tela.winfo_children():
        w.destroy()

    # ── Cabeçalho / barra de pesquisa ────────────────────────────────────────
    cabecalho = tk.Frame(tela, bg=COR_FUNDO, pady=18)
    cabecalho.pack(fill="x")

    frame_pesquisa = tk.Frame(cabecalho, bg=COR_PESQUISA, pady=6, padx=10)
    frame_pesquisa.pack()

    tk.Label(
        frame_pesquisa,
        text="🔍",
        bg=COR_PESQUISA,
        fg=COR_SUBTEXTO,
        font=("Helvetica", 13),
    ).pack(side="left", padx=(0, 4))

    entrada_pesquisa = tk.Entry(
        frame_pesquisa,
        width=42,
        font=("Helvetica", 13),
        bg=COR_PESQUISA,
        fg=COR_SUBTEXTO,
        insertbackground=COR_TEXTO,
        relief="flat",
    )
    entrada_pesquisa.insert(0, "Buscar filmes...")
    entrada_pesquisa.pack(side="left")

    # Comportamento de placeholder
    def _on_focus_in(event):
        if entrada_pesquisa.get() == "Buscar filmes...":
            entrada_pesquisa.delete(0, "end")
            entrada_pesquisa.configure(fg=COR_TEXTO)

    def _on_focus_out(event):
        if not entrada_pesquisa.get().strip():
            entrada_pesquisa.insert(0, "Buscar filmes...")
            entrada_pesquisa.configure(fg=COR_SUBTEXTO)

    entrada_pesquisa.bind("<FocusIn>",  _on_focus_in)
    entrada_pesquisa.bind("<FocusOut>", _on_focus_out)

    # Navega para resultados ao pressionar Enter
    def _pesquisar(event=None):
        termo = entrada_pesquisa.get().strip()
        if termo and termo != "Buscar filmes...":
            from telas.resultados import renderizarResultados
            renderizarResultados(tela, filmes, termo)

    entrada_pesquisa.bind("<Return>", _pesquisar)

    # Separador colorido
    tk.Frame(tela, bg=COR_DESTAQUE, height=2).pack(fill="x")

    # ── Área de conteúdo com scroll ───────────────────────────────────────────
    frame_externo = tk.Frame(tela, bg=COR_FUNDO)
    frame_externo.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame_externo, bg=COR_FUNDO, highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_externo, orient="vertical", command=canvas.yview)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_conteudo = tk.Frame(canvas, bg=COR_FUNDO)
    janela_canvas = canvas.create_window((0, 0), window=frame_conteudo, anchor="nw")

    # Atualiza scrollregion quando o conteúdo muda de tamanho
    frame_conteudo.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    # Frame interno ocupa toda a largura do canvas
    canvas.bind(
        "<Configure>",
        lambda e: canvas.itemconfig(janela_canvas, width=e.width),
    )
    # Scroll com o mouse (Linux e Windows)
    tela.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
    tela.bind_all("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
    tela.bind_all("<Button-5>",   lambda e: canvas.yview_scroll(1,  "units"))

    # ── Faixas de gênero ─────────────────────────────────────────────────────
    def _ao_clicar_mais(genero):
        from telas.resultados import renderizarResultados
        renderizarResultados(tela, filmes, "", genero=genero)

    construir_faixas(frame_conteudo, filmes, ao_clicar_mais=_ao_clicar_mais)
