import io
import threading
import tkinter as tk
import requests as req
from PIL import Image, ImageTk

# ── Cache de posters ──────────────────────────────────────────────────────────
_IMAGE_CACHE: dict = {}
_cache_lock         = threading.Lock()

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


# ── Carregamento assíncrono de posters ───────────────────────────────────────
def carregar_imagem(poster_path, largura, altura, callback, tamanho="w185"):
    """
    Baixa o poster do TMDB em background e chama callback(photo) quando pronto.
    `tamanho` é o bucket TMDB (w92, w185, w342, w500, w780, original).
    A chave de cache inclui o tamanho para evitar colisões entre resoluções distintas.
    """
    if not poster_path:
        return
    url = f"https://image.tmdb.org/t/p/{tamanho}{poster_path}"
    with _cache_lock:
        if url in _IMAGE_CACHE:
            callback(_IMAGE_CACHE[url])
            return

    def _fetch():
        try:
            resp = req.get(url, timeout=10)
            if resp.ok:
                img   = Image.open(io.BytesIO(resp.content)).resize(
                    (largura, altura), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                with _cache_lock:
                    _IMAGE_CACHE[url] = photo
                callback(photo)
        except Exception:
            pass

    threading.Thread(target=_fetch, daemon=True).start()


# ── Helpers de renderização das faixas ───────────────────────────────────────
def _extrair_lista(filmes):
    """
    Recebe o dict {genero: Response} e devolve uma lista plana de filmes
    no formato TMDB, sem duplicatas (deduplicados pelo campo 'id').
    """
    vistos = set()
    todos  = []
    for response in filmes.values():
        if response is None or not response.ok:
            continue
        for filme in response.json().get("results", []):
            if filme["id"] not in vistos:
                vistos.add(filme["id"])
                todos.append(filme)
    return todos


def _criar_card(pai, filme, ao_clicar=None):
    """
    Cria o widget de card (poster + título) de um filme.
    Espera um dict no formato TMDB: campos 'title', 'release_date', 'poster_path'.
    `ao_clicar`, se fornecido, é chamado com o dict do filme ao clicar no card.
    """
    titulo = filme.get("title", "")
    ano    = filme.get("release_date", "")[:4] or "—"
    poster = filme.get("poster_path")

    card = tk.Frame(pai, bg=COR_FUNDO, padx=CARD_PADDING)
    card.pack(side="left", anchor="n")

    capa = tk.Canvas(card, width=CAPA_LARGURA, height=CAPA_ALTURA,
                     bg=COR_CAPA, highlightthickness=0, cursor="hand2")
    ph_id = capa.create_text(CAPA_LARGURA // 2, CAPA_ALTURA // 2,
                              text="🎬", font=("Helvetica", 28), fill=COR_SUBTEXTO)
    capa.pack()

    lbl_titulo = tk.Label(card, text=titulo, bg=COR_FUNDO, fg=COR_TEXTO,
                          font=("Helvetica", 9), wraplength=CAPA_LARGURA,
                          justify="center", cursor="hand2")
    lbl_titulo.pack(pady=(5, 0))

    if ao_clicar:
        handler = lambda e, f=filme: ao_clicar(f)
        capa.bind("<Button-1>", handler)
        lbl_titulo.bind("<Button-1>", handler)

    if poster:
        def _aplicar(photo, c=capa, pid=ph_id):
            c.delete(pid)
            c.create_image(0, 0, anchor="nw", image=photo)
            c._img = photo  # impede GC
        carregar_imagem(poster, CAPA_LARGURA, CAPA_ALTURA,
                        lambda photo: capa.after(0, lambda p=photo: _aplicar(p)))


def _criar_botao_mais(pai, genero, callback):
    """Botão 'Ver mais' no final de uma faixa; chama callback(genero) ao clicar."""
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


def _construir_faixas(frame_pai, filmes, ao_clicar_mais=None, ao_clicar_filme=None):
    """
    Cria todas as faixas de gênero dentro do frame pai.
    `filmes` deve ser um dict {genero: requests.Response} (formato de dados.py).
    Ignora silenciosamente gêneros com resposta inválida ou lista vazia.
    `ao_clicar_mais`  : callback(genero) para o botão 'Ver mais'.
    `ao_clicar_filme` : callback(filme)  para clicar em um card.
    """
    for genero, response in filmes.items():
        if response is None or not response.ok:
            continue

        lista = response.json().get("results", [])
        if not lista:
            continue

        faixa = tk.Frame(frame_pai, bg=COR_FUNDO)
        faixa.pack(fill="x", pady=(10, 0))

        tk.Label(faixa, text=genero, bg=COR_FUNDO, fg=COR_TEXTO,
                 font=("Helvetica", 15, "bold"), anchor="w",
                 padx=20).pack(fill="x", pady=(0, 8))

        linha = tk.Frame(faixa, bg=COR_FUNDO, padx=10)
        linha.pack(fill="x", anchor="w")

        for filme in lista[:6]:
            _criar_card(linha, filme, ao_clicar=ao_clicar_filme)

        if ao_clicar_mais:
            _criar_botao_mais(linha, genero, ao_clicar_mais)


# ── Tela inicial ──────────────────────────────────────────────────────────────
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

    def _ao_clicar_filme(filme):
        from telas.filme import renderizarFilme
        renderizarFilme(tela, filme, voltar=lambda: renderizarInicio(tela, filmes))

    _construir_faixas(frame_conteudo, filmes,
                      ao_clicar_mais=_ao_clicar_mais,
                      ao_clicar_filme=_ao_clicar_filme)
