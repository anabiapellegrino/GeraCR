from pathlib import Path

from geracr.config import mesclar_config, validar_config
from geracr.exportacao import arquivos_de_saida, cr_para_markdown, gerar_csv, slug
from geracr.modelo import FALHOU, Grupo, Teste
from geracr.montagem import evidencia, montar_crs, titulo

CONFIG = mesclar_config({"ambiente": {"Ambiente": "QA", "Versão": "2"}, "labels": ["automacao"]})
CARTAO = Teste("checkout", "cartao", FALHOU, "ConnectionError", "ConnectionError: gateway indisponível (req=8f3a)")
PIX = Teste("checkout", "pix", FALHOU, "ConnectionError", "ConnectionError: gateway indisponível (req=1b9e)")


def grupo(*testes, mensagem="ConnectionError: gateway indisponível (req=[id])", severidade="Crítica"):
    return Grupo("ConnectionError", mensagem, testes, severidade)


def test_titulo_de_grupo_mostra_a_mensagem_normalizada_e_a_quantidade():
    #Arrange
    dois_testes = grupo(CARTAO, PIX)

    #Act
    resultado = titulo("[BUG]", dois_testes)

    #Assert
    assert resultado == "[BUG] ConnectionError: gateway indisponível (req=[id]) (2 testes)"


def test_titulo_de_um_teste_so_mostra_o_nome_do_teste():
    #Arrange
    um_teste = grupo(CARTAO)

    #Act
    resultado = titulo("[BUG]", um_teste)

    #Assert
    assert resultado == "[BUG] cartao: ConnectionError: gateway indisponível (req=8f3a)"


def test_evidencia_e_cortada_no_limite_de_linhas():
    #Arrange
    teste = CARTAO._replace(detalhe="\n".join(f"linha {n}" for n in range(1, 21)))

    #Act
    resultado = evidencia(teste, 3)

    #Assert
    assert resultado == "linha 1\nlinha 2\nlinha 3\n... (17 linhas omitidas)"


def test_crs_sao_numeradas_em_sequencia():
    #Arrange
    grupos = (grupo(CARTAO, PIX), grupo(CARTAO))

    #Act
    crs = montar_crs(CONFIG, grupos)

    #Assert
    assert [cr.numero for cr in crs] == [1, 2]
    assert crs[0].ambiente == "Ambiente: QA · Versão: 2"


def test_markdown_tem_as_secoes_de_uma_boa_cr():
    #Arrange
    (cr,) = montar_crs(CONFIG, (grupo(CARTAO, PIX),))
    secoes = ("Severidade sugerida", "Ambiente", "Testes afetados (2)", "Resultado esperado",
              "Resultado obtido", "Evidência", "Passos para reproduzir")

    #Act
    markdown = cr_para_markdown(cr)

    #Assert
    assert all(secao in markdown for secao in secoes)


def test_csv_escapa_aspas_e_tem_o_cabecalho():
    #Arrange
    (cr,) = montar_crs(CONFIG, (grupo(CARTAO._replace(nome='diz "oi"')),))

    #Act
    csv = gerar_csv((cr,))

    #Assert
    assert csv.startswith('"Titulo","Severidade"')
    assert 'diz ""oi""' in csv


def test_slug_tira_prefixo_acentos_e_simbolos():
    #Arrange
    titulo_da_cr = "[BUG] Conexão: falhou! (2 testes)"

    #Act
    resultado = slug(titulo_da_cr)

    #Assert
    assert resultado == "conexao-falhou-2-testes"


def test_arquivos_de_saida_so_descreve_o_que_gravar():
    #Arrange
    crs = montar_crs(CONFIG, (grupo(CARTAO),))

    #Act
    arquivos = arquivos_de_saida(crs, Path("saida"))

    #Assert
    assert [a.caminho.name for a in arquivos] == ["CR-01-cartao-connectionerror-gateway-indisponivel-req-8f.md", "crs.csv"]
    assert arquivos[0].conteudo.startswith("# CR-01")


def test_config_valido_e_invalido():
    #Arrange
    ruim = mesclar_config({"severidade_padrao": "Urgente",
                           "regras_severidade": [{"campo": "cor", "contem": "x", "severidade": "Alta"}]})

    #Act
    problemas_do_bom, problemas_do_ruim = validar_config(CONFIG), validar_config(ruim)

    #Assert
    assert problemas_do_bom == ()
    assert len(problemas_do_ruim) == 2
