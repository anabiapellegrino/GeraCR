from geracr.funcional import agrupar_por, compor, contar_por, primeira_resposta


def test_compor_aplica_da_esquerda_para_a_direita():
    #Arrange
    dobrar, somar_um = (lambda x: x * 2), (lambda x: x + 1)

    #Act
    resultado = compor(dobrar, somar_um)(5)

    #Assert
    assert resultado == 11


def test_compor_sem_funcoes_devolve_o_proprio_valor():
    #Arrange
    nenhuma_funcao = ()

    #Act
    resultado = compor(*nenhuma_funcao)("igual")

    #Assert
    assert resultado == "igual"


def test_agrupar_por_com_numeros_e_com_textos():
    #Arrange
    numeros, textos = [1, 2, 3, 4], ["oi", "olá", "eu"]

    #Act
    por_paridade = agrupar_por(lambda n: n % 2 == 0, numeros)
    por_tamanho = agrupar_por(len, textos)

    #Assert
    assert por_paridade == {False: (1, 3), True: (2, 4)}
    assert por_tamanho == {2: ("oi", "eu"), 3: ("olá",)}


def test_agrupar_por_nao_altera_a_entrada():
    #Arrange
    entrada = (3, 1, 3)

    #Act
    agrupar_por(lambda n: n, entrada)

    #Assert
    assert entrada == (3, 1, 3)


def test_contar_por():
    #Arrange
    letras = ["A", "a", "b"]

    #Act
    contagem = contar_por(str.lower, letras)

    #Assert
    assert contagem == {"a": 2, "b": 1}


def test_primeira_resposta_devolve_a_primeira_nao_vazia():
    #Arrange
    regras = (lambda x: None, lambda x: "segunda", lambda x: "terceira")

    #Act
    resposta = primeira_resposta(regras, 0, "padrão")

    #Assert
    assert resposta == "segunda"


def test_primeira_resposta_usa_o_padrao_quando_nenhuma_responde():
    #Arrange
    regras = (lambda x: None,)

    #Act
    resposta = primeira_resposta(regras, 0, "padrão")

    #Assert
    assert resposta == "padrão"


def test_primeira_resposta_e_preguicosa():
    #Arrange
    regras = (lambda x: "Crítica", lambda x: 1 / 0)

    #Act
    resposta = primeira_resposta(regras, 0, "padrão")

    #Assert
    assert resposta == "Crítica"
