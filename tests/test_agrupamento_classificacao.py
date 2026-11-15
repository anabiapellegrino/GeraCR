import pytest

from geracr.agrupamento import agrupar_falhas, criar_chave, criar_normalizador, filtrar_falhas
from geracr.classificacao import classificar, ordenar_por_severidade, regra_contem
from geracr.modelo import ERRO, FALHOU, PASSOU, Grupo, Teste

normalizar = criar_normalizador(())


def falha(nome, mensagem, suite="checkout", tipo="ConnectionError"):
    return Teste(suite, nome, ERRO, tipo, mensagem)


def grupo(*nomes, mensagem="erro", tipo="Error", severidade=""):
    return Grupo(tipo, mensagem, tuple(Teste("loja", nome, FALHOU) for nome in nomes), severidade)


PAGAMENTOS = (
    falha("cartao", "ConnectionError: gateway indisponível (req=8f3a2c1d)"),
    falha("pix", "ConnectionError: gateway indisponível (req=1b9e44aa)"),
    falha("cupom", "assert 90.0 == 89.9", tipo="AssertionError"),
)


@pytest.mark.parametrize("original, esperado", [
    ("gateway indisponível (req=54c2c533)", "gateway indisponível (req=[id])"),
    ("pedido f3a1c9e2-7b44-4d1a-9c55-0e2b8d6f1a77 sumiu", "pedido [id] sumiu"),
    ("banco perdido às 2026-11-08T07:59:21", "banco perdido às [data-hora]"),
    ("não respondeu em 5284ms", "não respondeu em [tempo]"),
    ("objeto em 0x7f3a2b1c", "objeto em [endereço]"),
    ("assert 89.9 == 89.91", "assert 89.9 == 89.91"),
])
def test_normalizador_ignora_o_que_muda_a_cada_execucao(original, esperado):
    #Arrange

    #Act
    normalizada = normalizar(original)

    #Assert
    assert normalizada == esperado


def test_normalizador_aceita_padroes_do_time():
    #Arrange
    normalizar_banco = criar_normalizador([r"\d{10,}"])

    #Act
    normalizada = normalizar_banco("protocolo 1794135351265640")

    #Assert
    assert normalizada == "protocolo [...]"


def test_filtrar_mantem_so_falhas_e_erros():
    #Arrange
    testes = (Teste("s", "a", PASSOU), Teste("s", "b", FALHOU), Teste("s", "c", ERRO))

    #Act
    falhas = tuple(filtrar_falhas(testes))

    #Assert
    assert [t.nome for t in falhas] == ["b", "c"]


def test_falhas_com_mesma_mensagem_viram_um_grupo():
    #Arrange
    chave = criar_chave(("tipo", "mensagem"), normalizar)

    #Act
    grupos = agrupar_falhas(chave, normalizar, PAGAMENTOS)

    #Assert
    assert [len(g.testes) for g in grupos] == [2, 1]
    assert grupos[0].mensagem == "ConnectionError: gateway indisponível (req=[id])"


def test_agrupar_tambem_pela_suite_quando_o_time_prefere():
    #Arrange
    outra_suite = falha("boleto", "ConnectionError: gateway indisponível (req=77aa11bb)", suite="outra")
    testes = PAGAMENTOS[:2] + (outra_suite,)
    chave = criar_chave(("suite", "tipo", "mensagem"), normalizar)

    #Act
    grupos = agrupar_falhas(chave, normalizar, testes)

    #Assert
    assert [len(g.testes) for g in grupos] == [2, 1]


def test_regra_contem_procura_no_campo_escolhido_sem_diferenciar_maiusculas():
    #Arrange
    regra = regra_contem("teste", ["pagamento", "pix"], "Crítica")

    #Act
    com_pix, com_frete = regra(grupo("test_PIX")), regra(grupo("test_frete"))

    #Assert
    assert com_pix == "Crítica"
    assert com_frete is None


def test_vale_a_primeira_regra_que_se_aplicar():
    #Arrange
    regras = (regra_contem("tipo", "Connection", "Crítica"), regra_contem("teste", "pix", "Baixa"))
    grupos = (grupo("pix", tipo="ConnectionError"),)

    #Act
    (classificado,) = classificar(regras, "Média", grupos)

    #Assert
    assert classificado.severidade == "Crítica"


def test_sem_regra_aplicavel_usa_a_severidade_padrao():
    #Arrange
    sem_regras, grupos = (), (grupo("qualquer"),)

    #Act
    (classificado,) = classificar(sem_regras, "Média", grupos)

    #Assert
    assert classificado.severidade == "Média"


def test_classificar_nao_altera_o_grupo_original():
    #Arrange
    original = grupo("a")

    #Act
    classificar((), "Média", (original,))

    #Assert
    assert original.severidade == ""


def test_ordenar_poe_mais_grave_primeiro_e_desempata_pela_quantidade():
    #Arrange
    grupos = (grupo("a", severidade="Baixa"), grupo("b", severidade="Alta"), grupo("c", "d", severidade="Alta"))

    #Act
    ordenados = ordenar_por_severidade(("Alta", "Baixa"), grupos)

    #Assert
    assert [len(g.testes) for g in ordenados] == [2, 1, 1]
    assert [g.severidade for g in ordenados] == ["Alta", "Alta", "Baixa"]
