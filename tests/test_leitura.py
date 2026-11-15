import json

import pytest

from geracr.leitura import LEITORES, detectar_formato, ler_json, ler_junit, pilha_de_chamadas, resumo_do_erro
from geracr.modelo import ERRO, FALHOU, IGNORADO, PASSOU

SUITES_ANINHADAS = """
<testsuite name="Raiz">
  <testcase classname="Raiz" name="nivel 1"/>
  <testsuite name="Filha">
    <testcase classname="Raiz.Filha" name="nivel 2"><failure message="falhou aqui"/></testcase>
    <testsuite name="Neta">
      <testcase classname="Raiz.Filha.Neta" name="nivel 3"><error message="KeyError: 'x'"/></testcase>
      <testcase classname="Raiz.Filha.Neta" name="pulado"><skipped message="depois"/></testcase>
    </testsuite>
  </testsuite>
</testsuite>
"""


def test_junit_le_suites_dentro_de_suites_recursivamente():
    #Arrange
    xml = SUITES_ANINHADAS

    #Act
    testes = tuple(ler_junit(xml))

    #Assert
    assert [t.nome for t in testes] == ["nivel 1", "nivel 2", "nivel 3", "pulado"]
    assert [t.status for t in testes] == [PASSOU, FALHOU, ERRO, IGNORADO]


def test_junit_e_preguicoso():
    #Arrange
    leitura = ler_junit(SUITES_ANINHADAS)

    #Act
    primeiro = next(leitura)

    #Assert
    assert primeiro.nome == "nivel 1"


def test_junit_sem_atributo_message_usa_o_texto_ate_a_pilha():
    #Arrange
    xml = """<testsuites><testsuite name="s"><testcase classname="c" name="t"><failure>Error: Timeout em 5012ms
    at consultar (src/api.js:9:9)
    at Object.transferir (src/api.js:13:24)</failure></testcase></testsuite></testsuites>"""

    #Act
    (teste,) = ler_junit(xml)

    #Assert
    assert teste.mensagem == "Error: Timeout em 5012ms"
    assert teste.tipo_erro == "Error"
    assert "src/api.js:9:9" in teste.detalhe


def test_tipo_citado_na_mensagem_tem_prioridade_sobre_o_atributo_type():
    #Arrange
    xml = ('<testsuite name="s"><testcase classname="c" name="t">'
           '<failure message="ConnectionError: banco caiu" type="AssertionError"/></testcase></testsuite>')

    #Act
    (teste,) = ler_junit(xml)

    #Assert
    assert teste.tipo_erro == "ConnectionError"


@pytest.mark.parametrize("mensagem, tipo", [
    ("assert 89.9 == 89.91", "AssertionError"),
    ("java.lang.IllegalStateException: Fragment não anexado", "IllegalStateException"),
    ("algo deu errado", "Falha"),
])
def test_tipo_do_erro_em_mensagens_de_varias_linguagens(mensagem, tipo):
    #Arrange
    xml = f'<testsuite><testcase name="t"><failure message="{mensagem}"/></testcase></testsuite>'

    #Act
    teste = next(ler_junit(xml))

    #Assert
    assert teste.tipo_erro == tipo


def test_json_aceita_status_em_portugues_e_em_ingles():
    #Arrange
    texto = """{"testes": [
        {"suite": "Login", "nome": "a", "status": "passou"},
        {"suite": "Login", "nome": "b", "status": "FAILED", "mensagem": "botão sumiu"},
        {"suite": "Login", "nome": "c", "status": "skipped"}
    ]}"""

    #Act
    testes = tuple(ler_json(texto))

    #Assert
    assert [t.status for t in testes] == [PASSOU, FALHOU, IGNORADO]


def test_json_com_dados_faltando_e_lido_sem_quebrar():
    #Arrange
    texto = '{"testes": [{"nome": "a", "status": "talvez"}, {"status": "passou"}, "lixo"]}'

    #Act
    testes = tuple(ler_json(texto))

    #Assert
    assert [(t.nome, t.status) for t in testes] == [("a", ERRO), ("sem nome", PASSOU)]


def test_json_com_campos_numericos_vira_texto():
    #Arrange
    texto = '{"testes": [{"suite": 7, "nome": 3, "status": "failed", "mensagem": 42}]}'

    #Act
    (teste,) = tuple(ler_json(texto))

    #Assert
    assert (teste.suite, teste.nome, teste.mensagem) == ("7", "3", "42")


@pytest.mark.parametrize("texto", ['{"testes": 5}', '{"testes": "x"}', '{"testes": {"a": 1}}', "[1, 2]"])
def test_json_com_testes_que_nao_sao_lista_nao_tem_o_que_ler(texto):
    #Arrange

    #Act
    testes = tuple(ler_json(texto))

    #Assert
    assert testes == ()


def test_json_sem_a_lista_de_testes_nao_tem_o_que_ler():
    #Arrange
    texto = '{"outra_coisa": []}'

    #Act
    testes = tuple(ler_json(texto))

    #Assert
    assert testes == ()


def test_json_quebrado_gera_erro_do_proprio_python():
    #Arrange
    texto = '{"testes": ['

    #Act + Assert
    with pytest.raises(json.JSONDecodeError):
        tuple(ler_json(texto))


def test_resumo_e_pilha_dividem_o_texto():
    #Arrange
    texto = "Error: deu ruim\n\nlinha 2\n    at f (a.js:1:1)\n    at g (a.js:2:2)"

    #Act
    resumo, pilha = resumo_do_erro(texto), pilha_de_chamadas(texto)

    #Assert
    assert resumo == "Error: deu ruim\nlinha 2"
    assert pilha.split("\n") == ["    at f (a.js:1:1)", "    at g (a.js:2:2)"]


def test_formatos_registrados_e_deteccao_pela_extensao():
    #Arrange
    arquivos = ("relatorio.XML", "saida.json", "relatorio.txt")

    #Act
    formatos = tuple(map(detectar_formato, arquivos))

    #Assert
    assert set(LEITORES) == {"junit", "json"}
    assert formatos == ("junit", "json", None)
