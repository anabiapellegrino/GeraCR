import re
from functools import partial
from itertools import count
from textwrap import dedent

from .leitura import pilha_de_chamadas
from .modelo import CR, identificador

LIMITE_TITULO = 110

#não acrescenta nada ao título
PREFIXO_GENERICO = re.compile(r"^(?:Assertion)?Error:\s*")

#vale a primeira que bater
EXPLICACOES = (
    (("timeout", "timed out"), "um serviço demorou demais para responder (timeout)"),
    (("connection", "conexão", "indisponível"), "a conexão com um serviço ou banco de dados falhou"),
    (("keyerror", "não encontrad", "not found"), "o sistema procurou um dado que não existe"),
    (("assert", "expect(", "deveria"), "o sistema devolveu um resultado diferente do esperado"),
)

LINHA_DE_BIBLIOTECA = re.compile(r"node_modules|node:internal|<anonymous>|site-packages|[\\/]lib[\\/]python")

SUBLINHADO = re.compile(r"^\s*[~^_][~^_\s]*$")

PASTAS = re.compile(r"""(?:\b[A-Za-z]:\\|(?<=[\s("'])/)(?:[^\\/\s"'()][^\\/\n"'()]*[\\/])+""")


primeira_linha = lambda texto: (texto.strip().splitlines() or [""])[0]

truncar = lambda texto, limite: texto if len(texto) <= limite else texto[: limite - 1].rstrip() + "…"


nome_legivel = lambda nome: re.sub(r"^test_?", "", nome).replace("_", " ").strip() or nome

formatar_ambiente = lambda ambiente: (
    " · ".join(map(lambda par: f"{par[0]}: {par[1]}", ambiente.items())) or "não informado"
)

mensagem_do_titulo = lambda grupo: PREFIXO_GENERICO.sub("", (
    primeira_linha(grupo.testes[0].mensagem)
    if len(set(map(lambda teste: primeira_linha(teste.mensagem), grupo.testes))) == 1
    else grupo.mensagem
))

descricao_do_grupo = lambda grupo: (
    f"{nome_legivel(grupo.testes[0].nome)}: {mensagem_do_titulo(grupo)}"
    if len(grupo.testes) == 1
    else f"{truncar(mensagem_do_titulo(grupo), LIMITE_TITULO - 15)} ({len(grupo.testes)} testes)"
)

titulo = lambda prefixo, grupo: f"{prefixo} {truncar(descricao_do_grupo(grupo), LIMITE_TITULO)}".strip()


contem_algum = lambda texto, trechos: any(map(lambda trecho: trecho in texto, trechos))

explicar = lambda texto: next(
    map(lambda par: par[1], filter(lambda par: contem_algum(texto, par[0]), EXPLICACOES)), None
)

explicacao_do_grupo = lambda grupo: (
    explicar(f"{grupo.tipo_erro} {grupo.testes[0].mensagem}".lower())
    or f"o relatório não diz a causa (tipo do erro: {grupo.tipo_erro})"
)

resumo_do_grupo = lambda grupo: (
    f'O teste "{nome_legivel(grupo.testes[0].nome)}" falhou: {explicacao_do_grupo(grupo)}.'
    if len(grupo.testes) == 1
    else f"{len(grupo.testes)} testes falharam pelo mesmo motivo: {explicacao_do_grupo(grupo)}."
)

esperado_do_grupo = lambda grupo: (
    f'O teste "{nome_legivel(grupo.testes[0].nome)}" passa, ou seja, o sistema faz o que o nome do teste descreve.'
    if len(grupo.testes) == 1
    else f"Os {len(grupo.testes)} testes listados passam, ou seja, o sistema faz o que o nome de cada teste descreve."
)


texto_da_evidencia = lambda teste: pilha_de_chamadas(teste.detalhe) or teste.detalhe or teste.mensagem

sem_pastas = lambda texto: PASTAS.sub("", texto)

linha_do_projeto = lambda linha: not (LINHA_DE_BIBLIOTECA.search(linha) or SUBLINHADO.match(linha))

#filtra antes de encurtar os caminhos
linhas_do_projeto = lambda texto: tuple(
    map(sem_pastas, filter(linha_do_projeto, dedent(texto.strip("\n")).rstrip().splitlines()))
)

cortar_linhas = lambda linhas, limite: "\n".join(linhas[:limite]) + (
    f"\n... ({len(linhas) - limite} linhas omitidas)" if len(linhas) > limite else ""
)

evidencia = lambda teste, limite: cortar_linhas(linhas_do_projeto(texto_da_evidencia(teste)), limite)

montar_cr = lambda config, numero, grupo: CR(
    numero=numero,
    titulo=titulo(config["prefixo_titulo"], grupo),
    resumo=resumo_do_grupo(grupo),
    severidade=grupo.severidade,
    tipo_erro=grupo.tipo_erro,
    resultado_obtido=grupo.testes[0].mensagem,
    resultado_esperado=esperado_do_grupo(grupo),
    evidencia=evidencia(grupo.testes[0], config["linhas_de_evidencia"]),
    testes=tuple(map(identificador, grupo.testes)),
    mensagens=tuple(map(lambda teste: primeira_linha(teste.mensagem), grupo.testes)),
    ambiente=formatar_ambiente(config["ambiente"]),
    labels=tuple(config["labels"]),
)

#count(1) é infinito (lazy)
montar_crs = lambda config, grupos: tuple(map(partial(montar_cr, config), count(1), grupos))
