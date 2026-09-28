import os
import requests as req
from dados import GENEROS as _GENEROS

_URL_BASE     = "https://api.themoviedb.org/3"
_HEADERS      = {"accept": "application/json"}
_TIMEOUT      = 10
_MAPA_GENEROS    = {g["id"]: g["name"] for g in _GENEROS}
_MAPA_GENEROS_ID = {v: k for k, v in _MAPA_GENEROS.items()}  # nome → id


def buscar_api(query, page=1):
    """
    Chama /search/movie/ com language=pt-BR.
    Retorna (results, total_pages); em caso de erro ou query vazia retorna ([], 0).
    `page` é repassado diretamente à API (TMDB aceita até 500 páginas).
    """
    if not query or not query.strip():
        return [], 0
    params = {
        "api_key":  os.getenv("CHAVE_API"),
        "query":    query.strip(),
        "language": "pt-BR",
        "page":     max(1, int(page)),
    }
    try:
        resp = req.get(f"{_URL_BASE}/search/movie",
                       headers=_HEADERS, params=params, timeout=_TIMEOUT)
        if resp.ok:
            data = resp.json()
            return data.get("results", []), data.get("total_pages", 1)
    except req.exceptions.RequestException:
        pass
    return [], 0


def listar_generos(filmes):
    """
    Retorna lista ordenada de nomes de gênero presentes nos filmes.
    Funciona com dicts TMDB (campo genre_ids).
    """
    generos = set()
    for filme in filmes:
        for gid in filme.get("genre_ids", []):
            nome = _MAPA_GENEROS.get(gid)
            if nome:
                generos.add(nome)
    return sorted(generos)


def filtrar_por_genero(genero, filmes):
    """
    Filtragem local por nome de gênero (case-insensitive) usando genre_ids.
    """
    genero_lower = genero.strip().lower()
    return [
        f for f in filmes
        if any(_MAPA_GENEROS.get(gid, "").lower() == genero_lower
               for gid in f.get("genre_ids", []))
    ]


def buscar_por_genero(genero_nome, page=1):
    """
    Browse por gênero via /discover/movie (igual ao carregamento inicial).
    Retorna (results, total_pages); ([], 0) em caso de erro ou gênero desconhecido.
    """
    genero_id = _MAPA_GENEROS_ID.get(genero_nome)
    if not genero_id:
        return [], 0
    params = {
        "api_key":       os.getenv("CHAVE_API"),
        "language":      "pt-BR",
        "page":          max(1, int(page)),
        "sort_by":       "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "with_genres":   genero_id,
    }
    try:
        resp = req.get(f"{_URL_BASE}/discover/movie",
                       headers=_HEADERS, params=params, timeout=_TIMEOUT)
        if resp.ok:
            data = resp.json()
            return data.get("results", []), data.get("total_pages", 1)
    except req.exceptions.RequestException:
        pass
    return [], 0


def buscar_com_filtro(query, genero, pagina_local=1, por_pagina=30, max_api_pages=5):
    """
    Busca via /search/movie com filtro de gênero aplicado localmente.

    Como a API não suporta filtro de gênero, são buscadas até `max_api_pages`
    páginas consecutivas e os resultados filtrados são agregados. A paginação
    exibida ao usuário é local (garante páginas com tamanho uniforme).

    Retorna (resultados_da_pagina_local, total_paginas_locais).
    """
    todos_filtrados = []
    for api_page in range(1, max_api_pages + 1):
        results, total_api_pages = buscar_api(query, page=api_page)
        todos_filtrados.extend(filtrar_por_genero(genero, results))
        if api_page >= total_api_pages:
            break

    total_local = max(1, (len(todos_filtrados) + por_pagina - 1) // por_pagina)
    inicio = (pagina_local - 1) * por_pagina
    return todos_filtrados[inicio:inicio + por_pagina], total_local
