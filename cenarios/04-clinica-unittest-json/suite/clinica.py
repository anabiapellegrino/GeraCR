#agenda de clínica de mentira
#só pra gerar um relatório de testes real
#bugs de propósito: conflito de horário e convênio com maiúscula
#e o serviço de agenda fora do ar

import random
from datetime import datetime

CONVENIOS = {"unimed": 0.8, "bradesco saude": 0.7, "particular": 0.0}


def chamar_servico_de_agenda(acao):
    #serviço remoto não responde, duração e horário mudam sempre
    espera = random.randint(3000, 3999)
    raise TimeoutError(
        f"serviço de agenda não respondeu em {espera}ms (tentativa às {datetime.now():%H:%M:%S})"
    )


def horario_livre(ocupados, inicio, duracao_min=30):
    #bug proposital: só compara o início, não a sobreposição
    return inicio not in ocupados


def desconto_do_convenio(nome):
    #bug proposital: não passa pra minúsculas antes de procurar
    return CONVENIOS[nome]


def valor_da_consulta(preco, convenio):
    return round(preco * (1 - desconto_do_convenio(convenio)), 2)


def idade_minima_ok(idade, especialidade):
    return idade >= 12 or especialidade != "psiquiatria"
