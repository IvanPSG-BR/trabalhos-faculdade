import os
import requests as req
from concurrent.futures import ThreadPoolExecutor

API_KEY  = os.getenv("CHAVE_API")
URL_BASE = "https://api.themoviedb.org/3"
HEADERS  = {"accept": "application/json"}
TIMEOUT  = 10  # segundos por requisição

GENEROS = [
    {"id": 28,    "name": "Ação"},
    {"id": 12,    "name": "Aventura"},
    {"id": 16,    "name": "Animação"},
    {"id": 35,    "name": "Comédia"},
    {"id": 80,    "name": "Crime"},
    {"id": 99,    "name": "Documentário"},
    {"id": 18,    "name": "Drama"},
    {"id": 10751, "name": "Família"},
    {"id": 14,    "name": "Fantasia"},
    {"id": 36,    "name": "História"},
    {"id": 27,    "name": "Terror"},
    {"id": 10402, "name": "Música"},
    {"id": 9648,  "name": "Mistério"},
    {"id": 10749, "name": "Romance"},
    {"id": 878,   "name": "Ficção científica"},
    {"id": 10770, "name": "Cinema TV"},
    {"id": 53,    "name": "Thriller"},
    {"id": 10752, "name": "Guerra"},
    {"id": 37,    "name": "Faroeste"},
]


def _buscar_genero(genero):
    """Faz a requisição para um gênero. Retorna None em caso de erro de rede."""
    params = {
        "api_key":        API_KEY,
        "language":       "pt-BR",
        "page":           1,
        "sort_by":        "popularity.desc",
        "include_adult":  "false",
        "include_video":  "false",
        "with_genres":    genero["id"],
    }
    try:
        return req.get(f"{URL_BASE}/discover/movie",
                       headers=HEADERS, params=params, timeout=TIMEOUT)
    except req.exceptions.RequestException:
        return None


def carregar_filmes():
    """
    Busca os filmes de todos os gêneros em paralelo.
    Retorna um dict {nome_genero: Response | None}, mantendo a ordem de GENEROS.
    """
    with ThreadPoolExecutor(max_workers=len(GENEROS)) as executor:
        respostas = list(executor.map(_buscar_genero, GENEROS))
    return {g["name"]: r for g, r in zip(GENEROS, respostas)}


FILMES = carregar_filmes()
