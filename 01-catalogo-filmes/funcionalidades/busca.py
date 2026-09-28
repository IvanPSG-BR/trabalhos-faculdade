def listar_generos(filmes):
    """Retorna a lista ordenada de gêneros únicos presentes na coleção."""
    generos = set()
    for filme in filmes:
        for g in filme.get("generos", "").split(","):
            g = g.strip()
            if g:
                generos.add(g)
    return sorted(generos)


def filtrar_por_genero(genero, filmes):
    """
    Retorna apenas os filmes que pertencem ao gênero informado.
    Comparação case-insensitive com cada gênero do campo 'generos'.
    """
    genero_lower = genero.strip().lower()
    return [
        f for f in filmes
        if any(g.strip().lower() == genero_lower for g in f.get("generos", "").split(","))
    ]


def buscar(query, filmes, genero=None):
    """
    Retorna os filmes que correspondem à query e, opcionalmente, ao gênero.

    - Se `genero` for fornecido, restringe a busca aos filmes desse gênero.
    - A `query` é pesquisada nos campos: título, gêneros, diretor, sinopse e ano.
    - Todos os termos da query devem estar presentes (AND implícito).
    - Case-insensitive. Query vazia com genero ativo retorna todos do gênero.
    """
    candidatos = filtrar_por_genero(genero, filmes) if genero else filmes

    if not query or not query.strip():
        return list(candidatos)

    termos = query.strip().lower().split()

    resultado = []
    for filme in candidatos:
        texto_completo = " ".join([
            filme.get("titulo",  ""),
            filme.get("generos", ""),
            filme.get("diretor", ""),
            filme.get("sinopse", ""),
            filme.get("ano",     ""),
        ]).lower()

        if all(termo in texto_completo for termo in termos):
            resultado.append(filme)

    return resultado
