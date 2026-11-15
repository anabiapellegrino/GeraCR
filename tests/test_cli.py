import os
import subprocess
import sys
from pathlib import Path

import pytest

from geracr.cli import executar

RAIZ = Path(__file__).resolve().parents[1]
LOJA = RAIZ / "cenarios" / "01-loja-pytest"


def rodar_no_terminal(*argumentos: str) -> subprocess.CompletedProcess:
    #windows usa cp1252 e quebraria os acentos
    return subprocess.run([sys.executable, "-m", "geracr", *argumentos],
                          cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})


def test_gera_um_markdown_por_cr_e_um_csv(tmp_path, capsys):
    #Arrange
    argumentos = [str(LOJA / "relatorio.xml"), "--config", str(LOJA / "config.json"), "--saida", str(tmp_path)]

    #Act
    codigo = executar(argumentos)

    #Assert
    assert codigo == 0
    assert len(list(tmp_path.glob("CR-*.md"))) == 3
    assert (tmp_path / "crs.csv").is_file()
    assert "CRs geradas: 3" in capsys.readouterr().out


def test_funciona_sem_config_usando_o_padrao(tmp_path):
    #Arrange
    argumentos = [str(LOJA / "relatorio.xml"), "--saida", str(tmp_path)]

    #Act
    codigo = executar(argumentos)

    #Assert
    assert codigo == 0


def test_relatorio_inexistente_retorna_erro(tmp_path, capsys):
    #Arrange
    argumentos = [str(tmp_path / "nao_existe.xml")]

    #Act
    codigo = executar(argumentos)

    #Assert
    assert codigo == 2
    assert "não encontrado" in capsys.readouterr().err


def test_config_invalido_retorna_erro_sem_gerar_nada(tmp_path, capsys):
    #Arrange
    config = tmp_path / "config.json"
    config.write_text('{"severidades": ["Alta"]}', encoding="utf-8")
    saida = tmp_path / "saida"

    #Act
    codigo = executar([str(LOJA / "relatorio.xml"), "--config", str(config), "--saida", str(saida)])

    #Assert
    assert codigo == 2
    assert "config inválido" in capsys.readouterr().err
    assert not saida.exists()


@pytest.mark.parametrize("conteudo, trecho", [
    ("[]", "deve ser um objeto JSON"),
    ('"só um texto"', "deve ser um objeto JSON"),
    ('{"regras_severidade": "oops"}', "'regras_severidade'"),
    ('{"ambiente": "QA"}', "'ambiente'"),
    ('{"linhas_de_evidencia": "dez"}', "'linhas_de_evidencia'"),
    ('{"regras_severidade": [{"campo": ["teste"], "contem": "x", "severidade": "Alta"}]}', "regra 1"),
    ('{"ignorar_na_mensagem": ["(abc"]}', "padrão inválido"),
], ids=["lista", "texto", "regras-texto", "ambiente-texto", "evidencia-texto", "campo-lista", "regex-invalida"])
def test_config_malformado_avisa_sem_stack_trace(tmp_path, conteudo, trecho):
    #Arrange
    config = tmp_path / "config.json"
    config.write_text(conteudo, encoding="utf-8")
    saida = tmp_path / "saida"

    #Act
    resultado = rodar_no_terminal(str(LOJA / "relatorio.xml"), "--config", str(config), "--saida", str(saida))

    #Assert
    assert resultado.returncode == 2
    assert "config inválido" in resultado.stderr
    assert trecho in resultado.stderr
    assert "Traceback" not in resultado.stderr
    assert not saida.exists()


@pytest.mark.parametrize("conteudo", [
    '{"testes": 5}',
    '{"testes": [{"nome": 3, "status": "failed", "mensagem": 42, "suite": ["x"]}]}',
], ids=["testes-numero", "campos-numericos"])
def test_relatorio_json_estranho_nao_derruba_o_programa(tmp_path, conteudo):
    #Arrange
    relatorio = tmp_path / "relatorio.json"
    relatorio.write_text(conteudo, encoding="utf-8")

    #Act
    resultado = rodar_no_terminal(str(relatorio), "--saida", str(tmp_path / "saida"))

    #Assert
    assert "Traceback" not in resultado.stderr


def test_relatorio_quebrado_retorna_erro_sem_stack_trace(tmp_path):
    #Arrange
    quebrado = tmp_path / "quebrado.xml"
    quebrado.write_text("<testsuite><testcase", encoding="utf-8")

    #Act
    resultado = rodar_no_terminal(str(quebrado), "--saida", str(tmp_path))

    #Assert
    assert resultado.returncode == 2
    assert "não consegui ler o arquivo" in resultado.stderr
    assert "Traceback" not in resultado.stderr
