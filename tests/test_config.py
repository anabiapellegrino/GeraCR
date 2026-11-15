import pytest

from geracr.config import CONFIG_PADRAO, eh_objeto, mesclar_config, validar_config

TIPOS_ERRADOS = [
    ({"projeto": 123}, "'projeto'"),
    ({"prefixo_titulo": ["[BUG]"]}, "'prefixo_titulo'"),
    ({"ambiente": "QA"}, "'ambiente'"),
    ({"labels": "automacao"}, "'labels'"),
    ({"labels": ["ok", 7]}, "'labels'"),
    ({"severidades": []}, "'severidades'"),
    ({"severidade_padrao": 1}, "'severidade_padrao'"),
    ({"regras_severidade": "oops"}, "'regras_severidade'"),
    ({"regras_severidade": ["pagamento"]}, "'regras_severidade'"),
    ({"agrupar_por": "tipo"}, "'agrupar_por'"),
    ({"agrupar_por": []}, "'agrupar_por'"),
    ({"ignorar_na_mensagem": "\\d+"}, "'ignorar_na_mensagem'"),
    ({"linhas_de_evidencia": "dez"}, "'linhas_de_evidencia'"),
    ({"linhas_de_evidencia": 0}, "'linhas_de_evidencia'"),
    ({"linhas_de_evidencia": True}, "'linhas_de_evidencia'"),
]


def test_config_padrao_e_valido():
    #Arrange
    config = mesclar_config({})

    #Act
    problemas = validar_config(config)

    #Assert
    assert problemas == ()


@pytest.mark.parametrize("lida, chave", TIPOS_ERRADOS, ids=lambda v: str(v))
def test_tipo_errado_vira_problema_e_nao_excecao(lida, chave):
    #Arrange
    config = mesclar_config(lida)

    #Act
    problemas = validar_config(config)

    #Assert
    assert len(problemas) == 1
    assert chave in problemas[0]


def test_com_tipo_errado_os_valores_nem_sao_conferidos():
    #Arrange
    config = mesclar_config({"severidades": "Alta", "severidade_padrao": "Urgente"})

    #Act
    problemas = validar_config(config)

    #Assert
    assert problemas == ("'severidades' deve ser uma lista de textos com pelo menos um item",)


@pytest.mark.parametrize("regra, trecho", [
    ({"campo": ["teste"], "contem": "x", "severidade": "Alta"}, "'campo'"),
    ({"campo": "cor", "contem": "x", "severidade": "Alta"}, "'campo'"),
    ({"campo": "teste", "severidade": "Alta"}, "'contem'"),
    ({"campo": "teste", "contem": 5, "severidade": "Alta"}, "'contem'"),
    ({"campo": "teste", "contem": [], "severidade": "Alta"}, "'contem'"),
    ({"campo": "teste", "contem": "x", "severidade": "Urgente"}, "severidade 'Urgente'"),
], ids=["campo-lista", "campo-desconhecido", "sem-contem", "contem-numero", "contem-vazio", "severidade-fora"])
def test_regra_com_problema_aponta_o_numero_e_o_campo(regra, trecho):
    #Arrange
    config = mesclar_config({"regras_severidade": [regra]})

    #Act
    problemas = validar_config(config)

    #Assert
    assert len(problemas) == 1
    assert problemas[0].startswith("regra 1:")
    assert trecho in problemas[0]


@pytest.mark.parametrize("lido, esperado", [({}, True), ([], False), ("texto", False), (None, False)])
def test_config_lido_precisa_ser_um_objeto(lido, esperado):
    #Arrange

    #Act
    resposta = eh_objeto(lido)

    #Assert
    assert resposta is esperado


def test_mesclar_nao_altera_o_padrao():
    #Arrange
    antes = dict(CONFIG_PADRAO)

    #Act
    mesclar_config({"projeto": "Outro"})

    #Assert
    assert dict(CONFIG_PADRAO) == antes
