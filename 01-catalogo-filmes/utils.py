import tkinter as tk

# ── Paleta ───────────────────────────────────────────────────────────────────
COR_FUNDO    = "#141414"
COR_FAIXA    = "#1f1f1f"
COR_CARD     = "#2a2a2a"
COR_CAPA     = "#3a3a3a"
COR_TEXTO    = "#ffffff"
COR_SUBTEXTO = "#b3b3b3"
COR_DESTAQUE = "#e50914"
COR_PESQUISA = "#333333"

# ── Dimensões ────────────────────────────────────────────────────────────────
CAPA_LARGURA = 130
CAPA_ALTURA  = 190
CARD_PADDING = 10


# ── Helpers ──────────────────────────────────────────────────────────────────
def agrupar_por_genero(filmes):
    """Retorna um dict {gênero: [filmes...]} mantendo a ordem de aparição."""
    grupos = {}
    for filme in filmes:
        for genero in filme["generos"].split(","):
            genero = genero.strip()
            grupos.setdefault(genero, []).append(filme)
    return grupos


def criar_card(pai, filme):
    """Cria o widget de card (capa placeholder + título) de um filme."""
    card = tk.Frame(pai, bg=COR_FUNDO, padx=CARD_PADDING)
    card.pack(side="left", anchor="n")

    capa = tk.Canvas(
        card,
        width=CAPA_LARGURA,
        height=CAPA_ALTURA,
        bg=COR_CAPA,
        highlightthickness=0,
        cursor="hand2",
    )
    capa.create_text(
        CAPA_LARGURA // 2,
        CAPA_ALTURA // 2 - 14,
        text="🎬",
        font=("Helvetica", 28),
    )
    capa.create_text(
        CAPA_LARGURA // 2,
        CAPA_ALTURA // 2 + 20,
        text=filme["ano"],
        fill=COR_SUBTEXTO,
        font=("Helvetica", 10),
    )
    capa.pack()

    tk.Label(
        card,
        text=filme["titulo"],
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Helvetica", 9),
        wraplength=CAPA_LARGURA,
        justify="center",
    ).pack(pady=(5, 0))


def _criar_botao_mais(pai, genero, callback):
    """Botão 'Mais' no final de uma faixa; chama callback(genero) ao clicar."""
    frame = tk.Frame(pai, bg=COR_FUNDO, padx=CARD_PADDING)
    frame.pack(side="left", anchor="center")

    btn = tk.Canvas(frame, width=70, height=CAPA_ALTURA, bg=COR_FAIXA,
                    highlightthickness=0, cursor="hand2")
    btn.create_text(35, CAPA_ALTURA // 2 - 12,
                    text="›", font=("Helvetica", 34), fill=COR_TEXTO)
    btn.create_text(35, CAPA_ALTURA // 2 + 18,
                    text="Ver mais", font=("Helvetica", 8), fill=COR_SUBTEXTO)
    btn.pack()
    btn.bind("<Button-1>", lambda e: callback(genero))


def construir_faixas(frame_pai, filmes, ao_clicar_mais=None):
    """
    Cria todas as faixas de gênero dentro do frame pai.
    Se `ao_clicar_mais` for fornecido, adiciona um botão 'Mais' ao fim de cada faixa.
    """
    grupos = agrupar_por_genero(filmes)

    for genero, filmes_do_genero in grupos.items():
        faixa = tk.Frame(frame_pai, bg=COR_FUNDO)
        faixa.pack(fill="x", pady=(10, 0))

        tk.Label(
            faixa,
            text=genero,
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Helvetica", 15, "bold"),
            anchor="w",
            padx=20,
        ).pack(fill="x", pady=(0, 8))

        linha = tk.Frame(faixa, bg=COR_FUNDO, padx=10)
        linha.pack(fill="x", anchor="w")

        for filme in filmes_do_genero:
            criar_card(linha, filme)

        if ao_clicar_mais:
            _criar_botao_mais(linha, genero, ao_clicar_mais)
