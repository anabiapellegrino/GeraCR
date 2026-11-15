from functools import partial
from itertools import count

from .leitura import pilha_de_chamadas
from .modelo import CR, identificador

LIMITE_TITULO = 110

primeira_linha = lambda texto: (texto.strip().splitlines() or [""])[0]

truncar = lambda texto, limite: texto if len(texto) <= limite else texto[: limite - 1].rstrip() + "…"

formatar_ambiente = lambda ambiente: (
    " · ".join(map(lambda par: f"{par[0]}: {par[1]}", ambiente.items())) or "não informado"
)

mensagem_do_titulo = lambda grupo: (
    primeira_linha(grupo.testes[0].mensagem)
    if len(set(map(lambda teste: primeira_linha(teste.mensagem), grupo.testes))) == 1
    else grupo.mensagem
)

descricao_do_grupo = lambda grupo: (
    f"{grupo.testes[0].nome}: {mensagem_do_titulo(grupo)}"
    if len(grupo.testes) == 1
    else f"{truncar(mensagem_do_titulo(grupo), LIMITE_TITULO - 15)} ({len(grupo.testes)} testes)"
)

titulo = lambda prefixo, grupo: f"{prefixo} {truncar(descricao_do_grupo(grupo), LIMITE_TITULO)}".strip()

texto_da_evidencia = lambda teste: pilha_de_chamadas(teste.detalhe) or teste.detalhe or teste.mensagem

cortar_linhas = lambda linhas, limite: "\n".join(linhas[:limite]) + (
    f"\n... ({len(linhas) - limite} linhas omitidas)" if len(linhas) > limite else ""
)

evidencia = lambda teste, limite: cortar_linhas(texto_da_evidencia(teste).strip().splitlines(), limite)

montar_cr = lambda config, numero, grupo: CR(
    numero=numero,
    titulo=titulo(config["prefixo_titulo"], grupo),
    severidade=grupo.severidade,
    tipo_erro=grupo.tipo_erro,
    resultado_obtido=grupo.testes[0].mensagem,
    evidencia=evidencia(grupo.testes[0], config["linhas_de_evidencia"]),
    testes=tuple(map(identificador, grupo.testes)),
    ambiente=formatar_ambiente(config["ambiente"]),
    labels=tuple(config["labels"]),
)

#count(1) é infinito (lazy)
montar_crs = lambda config, grupos: tuple(map(partial(montar_cr, config), count(1), grupos))
