#testes da agenda com unittest, padrão AAA
import unittest

from clinica import chamar_servico_de_agenda, horario_livre, idade_minima_ok, valor_da_consulta


class TestAgenda(unittest.TestCase):
    def test_agendar_consulta(self):
        #Arrange
        acao = "agendar"

        #Act
        confirmacao = chamar_servico_de_agenda(acao)

        #Assert
        self.assertTrue(confirmacao)

    def test_remarcar_consulta(self):
        #Arrange
        acao = "remarcar"

        #Act
        confirmacao = chamar_servico_de_agenda(acao)

        #Assert
        self.assertTrue(confirmacao)

    def test_cancelar_consulta(self):
        #Arrange
        acao = "cancelar"

        #Act
        confirmacao = chamar_servico_de_agenda(acao)

        #Assert
        self.assertTrue(confirmacao)

    def test_horario_vago_esta_livre(self):
        #Arrange
        ocupados = {"14:00"}

        #Act
        livre = horario_livre(ocupados, "15:00")

        #Assert
        self.assertTrue(livre)

    def test_horario_sobreposto_nao_esta_livre(self):
        #Arrange (consulta de 30 min às 14:00 vai até 14:30)
        ocupados = {"14:00"}

        #Act
        livre = horario_livre(ocupados, "14:15")

        #Assert
        self.assertFalse(livre, "14:15 se sobrepõe à consulta das 14:00")

    @unittest.skip("lembrete por SMS ainda não foi implementado")
    def test_lembrete_por_sms(self):
        pass


class TestFaturamento(unittest.TestCase):
    def test_consulta_particular_paga_valor_cheio(self):
        #Arrange
        preco, convenio = 250.0, "particular"

        #Act
        valor = valor_da_consulta(preco, convenio)

        #Assert
        self.assertEqual(valor, 250.0)

    def test_convenio_escrito_com_maiusculas(self):
        #Arrange
        preco, convenio = 250.0, "Unimed"

        #Act
        valor = valor_da_consulta(preco, convenio)

        #Assert
        self.assertEqual(valor, 50.0)

    def test_convenio_em_minusculas(self):
        #Arrange
        preco, convenio = 250.0, "unimed"

        #Act
        valor = valor_da_consulta(preco, convenio)

        #Assert
        self.assertEqual(valor, 50.0)


class TestRegras(unittest.TestCase):
    def test_psiquiatria_exige_idade_minima(self):
        #Arrange
        idade, especialidade = 10, "psiquiatria"

        #Act
        permitido = idade_minima_ok(idade, especialidade)

        #Assert
        self.assertFalse(permitido)


if __name__ == "__main__":
    unittest.main()
