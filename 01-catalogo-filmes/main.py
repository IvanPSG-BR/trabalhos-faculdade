import tkinter as tk
from dotenv import load_dotenv
from telas.inicio import COR_FUNDO, renderizarInicio

load_dotenv()

from dados import FILMES  # importado após load_dotenv para a API_KEY estar disponível

# ── Janela principal ──────────────────────────────────────────────────────────
tela = tk.Tk()
tela.title("Catálogo de Filmes")
tela.geometry("1000x680")
tela.configure(bg=COR_FUNDO)
tela.resizable(True, True)

renderizarInicio(tela, FILMES)

tela.mainloop()