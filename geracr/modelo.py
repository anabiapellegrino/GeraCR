from collections import namedtuple

PASSOU, FALHOU, ERRO, IGNORADO = "passou", "falhou", "erro", "ignorado"
STATUS_DE_FALHA = frozenset({FALHOU, ERRO})

Teste = namedtuple("Teste", ("suite", "nome", "status", "tipo_erro", "mensagem", "detalhe"),
                   defaults=("", "", ""))

Grupo = namedtuple("Grupo", ("tipo_erro", "mensagem", "testes", "severidade"), defaults=("",))

CR = namedtuple("CR", ("numero", "titulo", "resumo", "severidade", "tipo_erro", "resultado_obtido",
                       "resultado_esperado", "evidencia", "testes", "mensagens", "ambiente", "labels"))

Arquivo = namedtuple("Arquivo", ("caminho", "conteudo"))

identificador = lambda teste: f"{teste.suite}::{teste.nome}" if teste.suite else teste.nome
