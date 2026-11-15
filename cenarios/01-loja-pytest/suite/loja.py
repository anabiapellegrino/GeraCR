#loja virtual de mentira
#só pra gerar um relatório de testes real
#bugs de propósito no cupom e no frete
#e o gateway de pagamento fora do ar

import uuid


def total(itens):
    return round(sum(preco * qtd for preco, qtd in itens), 2)


def aplicar_cupom(valor, percentual):
    #bug proposital: trunca pra 1 casa em vez de arredondar pra 2
    return int(valor * (1 - percentual / 100) * 10) / 10


def cupom_valido(codigo, expirados=("NATAL2025",)):
    return codigo not in expirados


def frete(valor):
    #bug proposital: frete grátis devia ser a partir de 200 (>=), não acima (>)
    return 0.0 if valor > 200 else 19.90


def pagar(metodo, valor):
    raise ConnectionError(f"gateway indisponível (req={uuid.uuid4().hex[:8]})")
