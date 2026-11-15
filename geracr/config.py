from itertools import chain
from types import MappingProxyType

from .agrupamento import CAMPOS_DE_AGRUPAMENTO
from .classificacao import CAMPOS_DE_REGRA

CONFIG_PADRAO = MappingProxyType({
    "projeto": "Projeto sem nome",
    "prefixo_titulo": "[BUG]",
    "ambiente": {},
    "labels": ("automacao",),
    "severidades": ("Crítica", "Alta", "Média", "Baixa"),
    "severidade_padrao": "Média",
    "regras_severidade": (),
    "agrupar_por": ("tipo", "mensagem"),
    "ignorar_na_mensagem": (),
    "linhas_de_evidencia": 15,
})

eh_objeto = lambda valor: isinstance(valor, dict)

mesclar_config = lambda lida: {**CONFIG_PADRAO, **lida}


eh_texto = lambda valor: isinstance(valor, str)
eh_lista = lambda valor: isinstance(valor, (list, tuple))
eh_lista_de_textos = lambda valor: eh_lista(valor) and all(map(eh_texto, valor))
eh_lista_cheia_de_textos = lambda valor: eh_lista_de_textos(valor) and len(valor) > 0
eh_lista_de_objetos = lambda valor: eh_lista(valor) and all(map(eh_objeto, valor))
#bool também é int no python
eh_inteiro_positivo = lambda valor: isinstance(valor, int) and not isinstance(valor, bool) and valor > 0

TIPOS_DO_CONFIG = MappingProxyType({
    "projeto": (eh_texto, "um texto"),
    "prefixo_titulo": (eh_texto, "um texto"),
    "ambiente": (eh_objeto, 'um objeto, como {"Ambiente": "QA"}'),
    "labels": (eh_lista_de_textos, "uma lista de textos"),
    "severidades": (eh_lista_cheia_de_textos, "uma lista de textos com pelo menos um item"),
    "severidade_padrao": (eh_texto, "um texto"),
    "regras_severidade": (eh_lista_de_objetos, "uma lista de objetos (uma regra por objeto)"),
    "agrupar_por": (eh_lista_cheia_de_textos, "uma lista de textos com pelo menos um item"),
    "ignorar_na_mensagem": (eh_lista_de_textos, "uma lista de textos (expressões regulares)"),
    "linhas_de_evidencia": (eh_inteiro_positivo, "um número inteiro maior que zero"),
})

mensagens_das_falhas = lambda checagens: tuple(map(lambda par: par[1], filter(lambda par: not par[0], checagens)))

checar_tipo = lambda config, chave, tipo: (tipo[0](config[chave]), f"'{chave}' deve ser {tipo[1]}")

problemas_de_tipo = lambda config: mensagens_das_falhas(
    map(lambda par: checar_tipo(config, par[0], par[1]), TIPOS_DO_CONFIG.items())
)


contem_valido = lambda trechos: eh_texto(trechos) or eh_lista_cheia_de_textos(trechos)

problemas_da_regra = lambda numero, regra, severidades: mensagens_das_falhas((
    (regra.get("campo") in tuple(CAMPOS_DE_REGRA),
     f"regra {numero}: 'campo' deve ser um destes: {', '.join(CAMPOS_DE_REGRA)}"),
    (contem_valido(regra.get("contem")),
     f"regra {numero}: 'contem' deve ser um texto ou uma lista de textos"),
    (regra.get("severidade") in severidades,
     f"regra {numero}: severidade '{regra.get('severidade')}' não está na lista 'severidades'"),
))

problemas_gerais = lambda config: mensagens_das_falhas((
    (config["severidade_padrao"] in config["severidades"],
     f"severidade_padrao '{config['severidade_padrao']}' não está na lista 'severidades'"),
    (all(map(lambda campo: campo in CAMPOS_DE_AGRUPAMENTO, config["agrupar_por"])),
     f"agrupar_por só aceita: {', '.join(CAMPOS_DE_AGRUPAMENTO)}"),
))

problemas_das_regras = lambda config: tuple(chain.from_iterable(map(
    lambda par: problemas_da_regra(par[0], par[1], config["severidades"]),
    enumerate(config["regras_severidade"], 1),
)))

problemas_de_valor = lambda config: problemas_gerais(config) + problemas_das_regras(config)

#curto-circuito: com erro de tipo nem olha os valores
validar_config = lambda config: problemas_de_tipo(config) or problemas_de_valor(config)
