import ast
from collections import Counter
from pathlib import Path

import pytest

from geracr.modelo import CR, Arquivo, Grupo, Teste

PACOTE = Path(__file__).resolve().parents[1] / "geracr"
MODULOS = sorted(PACOTE.glob("*.py"))
NUCLEO = [m for m in MODULOS if m.name not in {"cli.py", "__main__.py"}]
SEM_COMANDOS_DE_CONTROLE = [m for m in MODULOS if m.name != "__main__.py"]

PROIBIDOS_EM_TODO_O_PROGRAMA = (
    ast.FunctionDef, ast.AsyncFunctionDef,
    ast.For, ast.AsyncFor, ast.While,
    ast.comprehension,
    ast.Global, ast.Nonlocal,
    ast.AugAssign, ast.NamedExpr,
    ast.ClassDef,
)
METODOS_QUE_ALTERAM = {"append", "extend", "insert", "pop", "remove", "clear", "update",
                       "setdefault", "sort", "add", "discard", "popitem"}
ENTRADA_E_SAIDA = {"print", "input", "open", "read_text", "write_text", "read_bytes",
                   "write_bytes", "mkdir", "unlink"}


def arvore(modulo: Path) -> ast.AST:
    return ast.parse(modulo.read_text(encoding="utf-8"))


def onde(no: ast.AST) -> str:
    linha = no.lineno if hasattr(no, "lineno") else no.target.lineno
    return f"linha {linha}: {type(no).__name__}"


def nomes_chamados(modulo: Path) -> set[str]:
    chamadas = (no for no in ast.walk(arvore(modulo)) if isinstance(no, ast.Call))
    return {c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", "") for c in chamadas}


def nomes_no_alvo(alvo: ast.AST) -> list[str]:
    return [no.id for no in ast.walk(alvo) if isinstance(no, ast.Name)]


def nomes_definidos_no_modulo(modulo: Path) -> list[str]:
    comandos = arvore(modulo).body
    alvos = [alvo for c in comandos if isinstance(c, ast.Assign) for alvo in c.targets]
    alvos += [c.target for c in comandos if isinstance(c, ast.AnnAssign)]
    return [nome for alvo in alvos for nome in nomes_no_alvo(alvo)]


por_modulo = pytest.mark.parametrize("modulo", MODULOS, ids=lambda m: m.name)


@por_modulo
def test_sem_def_sem_lacos_e_sem_atribuicao_que_altera(modulo):
    #Arrange
    codigo = arvore(modulo)

    #Act
    encontrados = [onde(no) for no in ast.walk(codigo) if isinstance(no, PROIBIDOS_EM_TODO_O_PROGRAMA)]

    #Assert
    assert encontrados == []


@por_modulo
def test_colecoes_nunca_sao_alteradas(modulo):
    #Arrange
    proibidos = METODOS_QUE_ALTERAM

    #Act
    usados = nomes_chamados(modulo) & proibidos

    #Assert
    assert usados == set()


@por_modulo
def test_cada_nome_recebe_valor_uma_unica_vez(modulo):
    #Arrange
    nomes = nomes_definidos_no_modulo(modulo)

    #Act
    repetidos = [nome for nome, vezes in Counter(nomes).items() if vezes > 1]

    #Assert
    assert repetidos == []


@pytest.mark.parametrize("modulo", SEM_COMANDOS_DE_CONTROLE, ids=lambda m: m.name)
def test_decisoes_sao_expressoes_e_nao_comandos(modulo):
    #Arrange
    comandos = (ast.If, ast.Try)

    #Act
    encontrados = [onde(no) for no in ast.walk(arvore(modulo)) if isinstance(no, comandos)]

    #Assert
    assert encontrados == []


@pytest.mark.parametrize("modulo", NUCLEO, ids=lambda m: m.name)
def test_nucleo_nao_le_nem_grava_nada(modulo):
    #Arrange
    proibidas = ENTRADA_E_SAIDA

    #Act
    usadas = nomes_chamados(modulo) & proibidas

    #Assert
    assert usadas == set()


@pytest.mark.parametrize("registro", [
    Teste("s", "n", "falhou"),
    Grupo("Erro", "m", ()),
    CR(1, "t", "Alta", "Erro", "r", "e", (), "QA", ()),
    Arquivo("x.md", "conteudo"),
], ids=lambda r: type(r).__name__)
def test_registros_nao_podem_ser_alterados(registro):
    #Arrange
    primeiro_campo = registro._fields[0]

    #Act
    copia = registro._replace(**{primeiro_campo: "novo"})

    #Assert
    with pytest.raises(AttributeError):
        setattr(registro, primeiro_campo, "novo")
    assert getattr(copia, primeiro_campo) == "novo"
    assert copia is not registro
