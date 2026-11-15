from itertools import count

from .funcional import primeira_resposta
from .modelo import identificador

CAMPOS_DE_REGRA = {
    "teste": lambda grupo: map(identificador, grupo.testes),
    "mensagem": lambda grupo: (grupo.mensagem,),
    "tipo": lambda grupo: (grupo.tipo_erro,),
}

em_minusculas = lambda trechos: tuple(map(str.lower, (trechos,) if isinstance(trechos, str) else trechos))

contem_algum = lambda valor, trechos: any(map(lambda trecho: trecho in valor.lower(), trechos))

regra_contem = lambda campo, trechos, severidade: lambda grupo: (
    severidade
    if any(map(lambda valor: contem_algum(valor, em_minusculas(trechos)), CAMPOS_DE_REGRA[campo](grupo)))
    else None
)

regras_do_config = lambda config: tuple(
    map(lambda r: regra_contem(r["campo"], r["contem"], r["severidade"]), config["regras_severidade"])
)

classificar = lambda regras, padrao, grupos: tuple(
    map(lambda grupo: grupo._replace(severidade=primeira_resposta(regras, grupo, padrao)), grupos)
)

posicoes = lambda severidades: dict(zip(severidades, count()))

criterio = lambda posicao: lambda grupo: (posicao.get(grupo.severidade, len(posicao)), -len(grupo.testes))

ordenar_por_severidade = lambda severidades, grupos: tuple(sorted(grupos, key=criterio(posicoes(severidades))))
