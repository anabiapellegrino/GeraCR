#adaptador: roda os testes com unittest e grava o json do geracr
#o unittest não gera junit xml sem plugin
#então converte o resultado pro formato json do readme
#não faz parte do geracr, igual as outras suítes de cenarios/

#uso, de dentro desta pasta:
#python gerar_relatorio.py ../relatorio.json

import json
import sys
import unittest
from pathlib import Path

AQUI = str(Path(__file__).resolve().parent) + "/"


class ResultadoComTodos(unittest.TestResult):
    #guarda também os testes que passaram

    def __init__(self):
        super().__init__()
        self.passaram = []

    def addSuccess(self, test):
        self.passaram.append(test)


def sem_caminho_da_maquina(texto):
    return texto.replace(AQUI, "")


def registro(teste, status, texto_da_falha=""):
    linhas = texto_da_falha.strip().splitlines()
    ultima = linhas[-1] if linhas else ""
    return {
        "suite": f"{type(teste).__module__}.{type(teste).__name__}",
        "nome": teste._testMethodName,
        "status": status,
        "tipo": ultima.split(":")[0] if ":" in ultima else "",
        "mensagem": ultima,
        "detalhe": sem_caminho_da_maquina(texto_da_falha.strip()),
    }


def main(destino):
    sys.path.insert(0, AQUI)
    suite = unittest.defaultTestLoader.discover(AQUI, pattern="test_*.py")
    resultado = ResultadoComTodos()
    suite.run(resultado)

    testes = (
        [registro(t, "passou") for t in resultado.passaram]
        + [registro(t, "falhou", tb) for t, tb in resultado.failures]
        + [registro(t, "erro", tb) for t, tb in resultado.errors]
        + [registro(t, "ignorado", motivo) | {"mensagem": motivo} for t, motivo in resultado.skipped]
    )
    testes.sort(key=lambda r: (r["suite"], r["nome"]))

    Path(destino).write_text(
        json.dumps({"ferramenta": "unittest", "testes": testes}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(testes)} testes gravados em {destino}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "relatorio.json")
