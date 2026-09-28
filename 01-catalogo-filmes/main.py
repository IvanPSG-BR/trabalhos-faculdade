import tkinter as tk
from utils import COR_FUNDO
from telas.inicio import renderizarInicio

# ── Dados placeholder ────────────────────────────────────────────────────────
listaDeFilmes = [
    # Animação
    {
        "capa": "https://m.media-amazon.com/images/M/{ID1}.jpg",
        "titulo": "Filme 1",
        "ano": "2009",
        "lancamento": "18 Maio 2009",
        "duracao": "90 min",
        "generos": "Animação, Aventura",
        "diretor": "Diretor Placeholder",
        "sinopse": "O protagonista vai em busca do fim do mundo",
        "nota": "85/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID4}.jpg",
        "titulo": "Filme 4",
        "ano": "2011",
        "lancamento": "10 Jun 2011",
        "duracao": "102 min",
        "generos": "Animação, Drama",
        "diretor": "Diretor Placeholder",
        "sinopse": "Dois amigos descobrem um segredo antigo",
        "nota": "91/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID5}.jpg",
        "titulo": "Filme 5",
        "ano": "2014",
        "lancamento": "03 Out 2014",
        "duracao": "88 min",
        "generos": "Animação, Família",
        "diretor": "Diretor Placeholder",
        "sinopse": "Uma família de robôs salva o planeta",
        "nota": "79/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID6}.jpg",
        "titulo": "Filme 6",
        "ano": "2017",
        "lancamento": "22 Nov 2017",
        "duracao": "110 min",
        "generos": "Animação, Musical",
        "diretor": "Diretor Placeholder",
        "sinopse": "Um garoto sonha em ser músico",
        "nota": "96/100",
    },
    # Ação
    {
        "capa": "https://m.media-amazon.com/images/M/{ID2}.jpg",
        "titulo": "Filme 2",
        "ano": "2009",
        "lancamento": "20 Maio 2009",
        "duracao": "97 min",
        "generos": "Ação, Aventura",
        "diretor": "Diretor Placeholder",
        "sinopse": "Tiro, porrada e bomba",
        "nota": "78/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID7}.jpg",
        "titulo": "Filme 7",
        "ano": "2015",
        "lancamento": "14 Jul 2015",
        "duracao": "136 min",
        "generos": "Ação, Ficção Científica",
        "diretor": "Diretor Placeholder",
        "sinopse": "Agentes do governo enfrentam uma ameaça alienígena",
        "nota": "82/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID8}.jpg",
        "titulo": "Filme 8",
        "ano": "2018",
        "lancamento": "05 Abr 2018",
        "duracao": "149 min",
        "generos": "Ação, Fantasia",
        "diretor": "Diretor Placeholder",
        "sinopse": "Heróis se unem para salvar o universo",
        "nota": "89/100",
    },
    # Comédia
    {
        "capa": "https://m.media-amazon.com/images/M/{ID3}.jpg",
        "titulo": "Filme 3",
        "ano": "2009",
        "lancamento": "29 Maio 2009",
        "duracao": "84 min",
        "generos": "Comédia, Animação",
        "diretor": "Diretor Placeholder",
        "sinopse": "O protagonista tem o maior azar do mundo",
        "nota": "95/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID9}.jpg",
        "titulo": "Filme 9",
        "ano": "2013",
        "lancamento": "17 Jan 2013",
        "duracao": "93 min",
        "generos": "Comédia, Romance",
        "diretor": "Diretor Placeholder",
        "sinopse": "Dois estranhos se perdem na mesma cidade",
        "nota": "74/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID10}.jpg",
        "titulo": "Filme 10",
        "ano": "2020",
        "lancamento": "02 Mar 2020",
        "duracao": "101 min",
        "generos": "Comédia, Drama",
        "diretor": "Diretor Placeholder",
        "sinopse": "Um chef fracassado tenta recomeçar do zero",
        "nota": "80/100",
    },
    # Drama
    {
        "capa": "https://m.media-amazon.com/images/M/{ID11}.jpg",
        "titulo": "Filme 11",
        "ano": "2016",
        "lancamento": "09 Set 2016",
        "duracao": "118 min",
        "generos": "Drama",
        "diretor": "Diretor Placeholder",
        "sinopse": "Uma família enfrenta a perda de um ente querido",
        "nota": "88/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID12}.jpg",
        "titulo": "Filme 12",
        "ano": "2019",
        "lancamento": "21 Fev 2019",
        "duracao": "127 min",
        "generos": "Drama, Thriller",
        "diretor": "Diretor Placeholder",
        "sinopse": "Um advogado descobre uma conspiração milionária",
        "nota": "87/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID13}.jpg",
        "titulo": "Filme 13",
        "ano": "2022",
        "lancamento": "30 Jun 2022",
        "duracao": "133 min",
        "generos": "Drama, Ficção Científica",
        "diretor": "Diretor Placeholder",
        "sinopse": "Astronautas buscam um novo lar para a humanidade",
        "nota": "92/100",
    },
    # Terror
    {
        "capa": "https://m.media-amazon.com/images/M/{ID14}.jpg",
        "titulo": "Filme 14",
        "ano": "2018",
        "lancamento": "12 Out 2018",
        "duracao": "112 min",
        "generos": "Terror",
        "diretor": "Diretor Placeholder",
        "sinopse": "Uma família se muda para uma mansão assombrada",
        "nota": "76/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID15}.jpg",
        "titulo": "Filme 15",
        "ano": "2021",
        "lancamento": "29 Out 2021",
        "duracao": "98 min",
        "generos": "Terror, Thriller",
        "diretor": "Diretor Placeholder",
        "sinopse": "Um vírus misterioso transforma os moradores da cidade",
        "nota": "71/100",
    },
    {
        "capa": "https://m.media-amazon.com/images/M/{ID16}.jpg",
        "titulo": "Filme 16",
        "ano": "2023",
        "lancamento": "15 Set 2023",
        "duracao": "105 min",
        "generos": "Terror",
        "diretor": "Diretor Placeholder",
        "sinopse": "Crianças desaparecem misteriosamente no interior",
        "nota": "83/100",
    },
]


# ── Janela principal ──────────────────────────────────────────────────────────
tela = tk.Tk()
tela.title("Catálogo de Filmes")
tela.geometry("1000x680")
tela.configure(bg=COR_FUNDO)
tela.resizable(True, True)

renderizarInicio(tela, listaDeFilmes)

tela.mainloop()