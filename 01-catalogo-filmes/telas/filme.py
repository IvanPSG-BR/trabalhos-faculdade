import os
import threading
import tkinter as tk
import requests as req
from telas.inicio import (
    COR_FUNDO, COR_DESTAQUE, COR_CARD, COR_CAPA,
    COR_TEXTO, COR_SUBTEXTO, COR_FAIXA,
    carregar_imagem,
)

_URL_BASE = "https://api.themoviedb.org/3"
_HEADERS  = {"accept": "application/json"}
_TIMEOUT  = 10

POSTER_W = 260
POSTER_H = 390


def _buscar_detalhes(film_id):
    """Busca detalhes + créditos em uma única chamada (append_to_response)."""
    params = {
        "api_key":            os.getenv("CHAVE_API"),
        "language":           "pt-BR",
        "append_to_response": "credits",
    }
    try:
        resp = req.get(f"{_URL_BASE}/movie/{film_id}",
                       headers=_HEADERS, params=params, timeout=_TIMEOUT)
        if resp.ok:
            return resp.json()
    except req.exceptions.RequestException:
        pass
    return {}


def renderizarFilme(tela, filme, voltar):
    """
    Monta a tela de detalhes de um filme.
    - `filme`  : dict TMDB (vindo de search/discover).
    - `voltar` : callable que reconstrói a tela anterior.
    """
    for w in tela.winfo_children():
        w.destroy()

    # ── Barra superior com botão Voltar ───────────────────────────────────────
    barra = tk.Frame(tela, bg=COR_FUNDO, pady=10)
    barra.pack(fill="x")
    tk.Button(barra, text="← Voltar", command=voltar,
              bg=COR_CARD, fg=COR_TEXTO, font=("Helvetica", 10),
              relief="flat", padx=12, pady=4, cursor="hand2",
              ).pack(side="left", padx=20)
    tk.Frame(tela, bg=COR_DESTAQUE, height=2).pack(fill="x")

    # ── Área scrollável ───────────────────────────────────────────────────────
    frame_ext = tk.Frame(tela, bg=COR_FUNDO)
    frame_ext.pack(fill="both", expand=True)

    canvas    = tk.Canvas(frame_ext, bg=COR_FUNDO, highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_ext, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_conteudo = tk.Frame(canvas, bg=COR_FUNDO)
    win = canvas.create_window((0, 0), window=frame_conteudo, anchor="nw")
    frame_conteudo.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
    tela.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    tela.bind_all("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
    tela.bind_all("<Button-5>",   lambda e: canvas.yview_scroll(1,  "units"))

    # ── Poster + informações lado a lado ──────────────────────────────────────
    frame_principal = tk.Frame(frame_conteudo, bg=COR_FUNDO, padx=30, pady=30)
    frame_principal.pack(fill="x")

    capa  = tk.Canvas(frame_principal, width=POSTER_W, height=POSTER_H,
                      bg=COR_CAPA, highlightthickness=0)
    ph_id = capa.create_text(POSTER_W // 2, POSTER_H // 2,
                              text="🎬", font=("Helvetica", 40), fill=COR_SUBTEXTO)
    capa.pack(side="left", padx=(0, 30), anchor="n")

    frame_info = tk.Frame(frame_principal, bg=COR_FUNDO)
    frame_info.pack(side="left", fill="both", expand=True, anchor="n")

    # Título
    tk.Label(frame_info, text=filme.get("title", "—"),
             bg=COR_FUNDO, fg=COR_TEXTO, font=("Helvetica", 22, "bold"),
             wraplength=580, justify="left", anchor="w").pack(fill="x", pady=(0, 6))

    # Ano + nota
    ano  = filme.get("release_date", "")[:4] or "—"
    nota = filme.get("vote_average")
    nota_str = f"★ {nota:.1f}/10" if nota is not None else ""
    tk.Label(frame_info, text=f"{ano}   {nota_str}".strip(),
             bg=COR_FUNDO, fg=COR_SUBTEXTO, font=("Helvetica", 12),
             ).pack(anchor="w", pady=(0, 16))

    tk.Frame(frame_info, bg=COR_FAIXA, height=1).pack(fill="x", pady=(0, 12))

    # Pares chave/valor (lançamento já disponível; restante vem da API)
    def _campo(chave):
        row = tk.Frame(frame_info, bg=COR_FUNDO)
        row.pack(fill="x", pady=4, anchor="w")
        tk.Label(row, text=f"{chave}:", bg=COR_FUNDO, fg=COR_SUBTEXTO,
                 font=("Helvetica", 10, "bold"), width=12, anchor="w").pack(side="left")
        lbl = tk.Label(row, text="—", bg=COR_FUNDO, fg=COR_TEXTO,
                       font=("Helvetica", 10), anchor="w", justify="left",
                       wraplength=460)
        lbl.pack(side="left", fill="x", expand=True)
        return lbl

    lbl_lancamento = _campo("Lançamento")
    lbl_generos    = _campo("Gêneros")
    lbl_diretor    = _campo("Diretor")
    lbl_elenco     = _campo("Elenco")

    lbl_lancamento.config(text=filme.get("release_date", "—"))

    # ── Sinopse ───────────────────────────────────────────────────────────────
    tk.Frame(frame_conteudo, bg=COR_FAIXA, height=1).pack(fill="x", padx=30, pady=(0, 20))

    frame_sinopse = tk.Frame(frame_conteudo, bg=COR_FUNDO, padx=30)
    frame_sinopse.pack(fill="x", pady=(0, 40))

    tk.Label(frame_sinopse, text="Sinopse",
             bg=COR_FUNDO, fg=COR_TEXTO,
             font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 8))

    lbl_sinopse = tk.Label(frame_sinopse,
                           text=filme.get("overview") or "Sinopse não disponível.",
                           bg=COR_FUNDO, fg=COR_SUBTEXTO,
                           font=("Helvetica", 11), wraplength=880,
                           justify="left", anchor="w")
    lbl_sinopse.pack(fill="x")

    # ── Poster em background ──────────────────────────────────────────────────
    poster = filme.get("poster_path")
    if poster:
        def _aplicar_poster(photo, c=capa, pid=ph_id):
            c.delete(pid)
            c.create_image(0, 0, anchor="nw", image=photo)
            c._img = photo
        carregar_imagem(poster, POSTER_W, POSTER_H,
                        lambda photo: capa.after(0, lambda p=photo: _aplicar_poster(p)),
                        tamanho="w342")

    # ── Detalhes (gêneros, diretor, elenco, sinopse) em background ───────────
    def _carregar():
        dados = _buscar_detalhes(filme.get("id"))
        if not dados:
            return

        generos = ", ".join(g["name"] for g in dados.get("genres", [])) or "—"
        diretor = next(
            (p["name"] for p in dados.get("credits", {}).get("crew", [])
             if p.get("job") == "Director"),
            "—",
        )
        elenco = ", ".join(
            p["name"] for p in dados.get("credits", {}).get("cast", [])[:6]
        ) or "—"
        sinopse = dados.get("overview") or filme.get("overview") or "Sinopse não disponível."

        def _atualizar():
            lbl_generos.config(text=generos)
            lbl_diretor.config(text=diretor)
            lbl_elenco.config(text=elenco)
            lbl_sinopse.config(text=sinopse)
            frame_conteudo.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        tela.after(0, _atualizar)

    threading.Thread(target=_carregar, daemon=True).start()
