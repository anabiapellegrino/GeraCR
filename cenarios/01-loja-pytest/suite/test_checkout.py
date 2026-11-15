from loja import aplicar_cupom, cupom_valido, frete, pagar, total


def test_adicionar_item():
    #Arrange
    carrinho = [(50.0, 1)]

    #Act
    valor = total(carrinho)

    #Assert
    assert valor == 50.0


def test_total_com_varios_itens():
    #Arrange
    carrinho = [(50.0, 2), (19.9, 1)]

    #Act
    valor = total(carrinho)

    #Assert
    assert valor == 119.9


def test_cupom_10_porcento():
    #Arrange
    subtotal, desconto = 99.90, 10

    #Act
    valor = aplicar_cupom(subtotal, desconto)

    #Assert
    assert valor == 89.91


def test_cupom_expirado_rejeitado():
    #Arrange
    codigo = "NATAL2025"

    #Act
    valido = cupom_valido(codigo)

    #Assert
    assert not valido


def test_frete_gratis_a_partir_de_200():
    #Arrange
    subtotal = 200.0

    #Act
    valor = frete(subtotal)

    #Assert
    assert valor == 0.0


def test_frete_padrao():
    #Arrange
    subtotal = 80.0

    #Act
    valor = frete(subtotal)

    #Assert
    assert valor == 19.90


def test_pagamento_cartao():
    #Arrange
    metodo, valor = "cartao", 89.91

    #Act
    resultado = pagar(metodo, valor)

    #Assert
    assert resultado == "aprovado"


def test_pagamento_pix():
    #Arrange
    metodo, valor = "pix", 89.91

    #Act
    resultado = pagar(metodo, valor)

    #Assert
    assert resultado == "aprovado"


def test_pagamento_boleto():
    #Arrange
    metodo, valor = "boleto", 89.91

    #Act
    resultado = pagar(metodo, valor)

    #Assert
    assert resultado == "aprovado"
