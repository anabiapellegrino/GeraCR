from functools import partial

from .agrupamento import agrupar_falhas, criar_chave, criar_normalizador, filtrar_falhas
from .classificacao import classificar, ordenar_por_severidade, regras_do_config
from .funcional import compor
from .leitura import LEITORES
from .montagem import montar_crs

montar_linha = lambda config, normalizar: compor(
    filtrar_falhas,
    partial(agrupar_falhas, criar_chave(config["agrupar_por"], normalizar), normalizar),
    partial(classificar, regras_do_config(config), config["severidade_padrao"]),
    partial(ordenar_por_severidade, config["severidades"]),
    partial(montar_crs, config),
)

gerar_crs = lambda config: montar_linha(config, criar_normalizador(config["ignorar_na_mensagem"]))

com_crs = lambda testes, config: (testes, gerar_crs(config)(testes))

processar = lambda texto, formato, config: com_crs(tuple(LEITORES[formato](texto)), config)
