import json
from pathlib import Path

import pytest

from geracr.config import mesclar_config, validar_config
from geracr.leitura import detectar_formato
from geracr.modelo import STATUS_DE_FALHA
from geracr.pipeline import processar

PASTA_CENARIOS = Path(__file__).resolve().parents[1] / "cenarios"
CENARIOS = sorted(p for p in PASTA_CENARIOS.iterdir() if (p / "esperado.json").is_file())
por_cenario = pytest.mark.parametrize("pasta", CENARIOS, ids=lambda p: p.name)


def ler_json(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_cenario(pasta: Path):
    relatorio = next(pasta.glob("relatorio.*"))
    config = mesclar_config(ler_json(pasta / "config.json"))
    return relatorio.read_text(encoding="utf-8"), detectar_formato(relatorio.name), config


def quantas_falhas(testes) -> int:
    return sum(t.status in STATUS_DE_FALHA for t in testes)


def test_existem_pelo_menos_tres_cenarios():
    #Arrange + Act
    quantidade = len(CENARIOS)

    #Assert
    assert quantidade >= 3


@por_cenario
def test_config_do_cenario_e_valido(pasta):
    #Arrange
    _, _, config = carregar_cenario(pasta)

    #Act
    problemas = validar_config(config)

    #Assert
    assert problemas == ()


@por_cenario
def test_cenario_gera_as_crs_esperadas(pasta):
    #Arrange
    texto, formato, config = carregar_cenario(pasta)
    esperado = ler_json(pasta / "esperado.json")

    #Act
    testes, crs = processar(texto, formato, config)

    #Assert
    assert len(testes) == esperado["testes"]
    assert quantas_falhas(testes) == esperado["falhas"]
    assert [(cr.severidade, len(cr.testes), cr.tipo_erro) for cr in crs] == [
        (e["severidade"], e["testes"], e["tipo"]) for e in esperado["crs"]
    ]
    assert all(e["titulo_contem"] in cr.titulo for cr, e in zip(crs, esperado["crs"]))


@por_cenario
def test_nenhuma_falha_se_perde_no_agrupamento(pasta):
    #Arrange
    texto, formato, config = carregar_cenario(pasta)

    #Act
    testes, crs = processar(texto, formato, config)

    #Assert
    assert sum(len(cr.testes) for cr in crs) == quantas_falhas(testes)


@por_cenario
def test_cada_cr_usa_o_ambiente_e_as_labels_do_proprio_time(pasta):
    #Arrange
    texto, formato, config = carregar_cenario(pasta)

    #Act
    _, crs = processar(texto, formato, config)

    #Assert
    assert all(cr.labels == tuple(config["labels"]) for cr in crs)
    assert all(str(valor) in crs[0].ambiente for valor in config["ambiente"].values())
