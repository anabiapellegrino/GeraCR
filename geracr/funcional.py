from functools import reduce

#T -> T
identidade = lambda valor: valor

#(A -> B), (B -> C),...-> (A -> Z)
compor = lambda *funcoes: reduce(lambda anterior, proxima: (lambda x: proxima(anterior(x))), funcoes, identidade)

#{K: (T, ...)}, K, T -> {K: (T, ...)}
juntar_no_grupo = lambda grupos, k, item: {**grupos, k: grupos.get(k, ()) + (item,)}

#(T -> K), [T] -> {K:(T,...)}
agrupar_por = lambda chave, itens: reduce(
    lambda grupos, item: juntar_no_grupo(grupos, chave(item), item), itens, {}
)

#(T -> K), [T] -> {K: int}
contar_por = lambda chave, itens: dict(
    map(lambda par: (par[0], len(par[1])), agrupar_por(chave, itens).items())
)

#[T -> R | None], T, R -> R
primeira_resposta = lambda funcoes, valor, padrao: next(
    filter(None, map(lambda funcao: funcao(valor), funcoes)), padrao
)
