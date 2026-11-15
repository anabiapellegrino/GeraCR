#biblioteca de mentira pra gerar um relatório real
#bugs de propósito: prazo de empréstimo errado
#e leitor com multa conseguindo emprestar
#o banco cai no meio da execução
#e a mensagem traz o horário, que muda sempre

from datetime import datetime

PRAZO_DIAS = 7  # BUG: o certo seria 14
LEITORES_COM_MULTA = {"L-002"}


def prazo_de_devolucao():
    return PRAZO_DIAS


def emprestar(leitor, livro):
    #bug: não verifica multa pendente
    return "emprestado"


def consultar_banco(*_):
    agora = datetime.now().isoformat(timespec="seconds")
    raise ConnectionError(f"conexão com o banco perdida às {agora}")


def buscar_livro(titulo):
    return titulo in {"Dom Casmurro", "Vidas Secas"}
