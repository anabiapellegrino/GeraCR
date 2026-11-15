import re
from functools import partial, reduce

from .funcional import agrupar_por
from .modelo import STATUS_DE_FALHA, Grupo

#o que muda a cada execução
PADROES_VARIAVEIS = (
    (re.compile(r"\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b"), "[id]"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?"), "[data-hora]"),
    (re.compile(r"\b\d{2}:\d{2}:\d{2}(?:\.\d+)?\b"), "[hora]"),
    (re.compile(r"\b0x[0-9a-fA-F]+\b"), "[endereço]"),
    (re.compile(r"\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{6,}\b"), "[id]"),
    (re.compile(r"\b\d+(?:\.\d+)?\s?(?:ms|s)\b"), "[tempo]"),
)
ESPACOS = re.compile(r"\s+")


eh_falha = lambda teste: teste.status in STATUS_DE_FALHA

filtrar_falhas = lambda testes: filter(eh_falha, testes)


aplicar_padrao = lambda texto, par: par[0].sub(par[1], texto)

compilar = lambda padroes: tuple(map(lambda padrao: (re.compile(padrao), "[...]"), padroes))

normalizar_com = lambda padroes, mensagem: ESPACOS.sub(" ", reduce(aplicar_padrao, padroes, mensagem)).strip()

criar_normalizador = lambda padroes_do_time: partial(normalizar_com, compilar(padroes_do_time) + PADROES_VARIAVEIS)


EXTRATORES_DE_CHAVE = {
    "suite": lambda teste, normalizar: teste.suite,
    "tipo": lambda teste, normalizar: teste.tipo_erro,
    "mensagem": lambda teste, normalizar: normalizar(teste.mensagem),
}
CAMPOS_DE_AGRUPAMENTO = tuple(EXTRATORES_DE_CHAVE)

criar_chave = lambda campos, normalizar: lambda teste: tuple(
    map(lambda campo: EXTRATORES_DE_CHAVE[campo](teste, normalizar), campos)
)

para_grupo = lambda normalizar, testes: Grupo(
    tipo_erro=testes[0].tipo_erro, mensagem=normalizar(testes[0].mensagem), testes=testes
)

agrupar_falhas = lambda chave, normalizar, falhas: tuple(
    map(partial(para_grupo, normalizar), agrupar_por(chave, falhas).values())
)
