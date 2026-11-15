const { transferir, extrato, LIMITE_NOTURNO } = require('../src/transferencias');

describe('Transferências', () => {
  test('transfere valor válido entre contas', () => {
    //Arrange
    const origem = { saldo: 500 };

    //Act
    const resultado = transferir(origem, 100);

    //Assert
    expect(resultado.status).toBe('concluida');
  });

  test('recusa valor negativo', () => {
    //Arrange
    const origem = { saldo: 500 };

    //Act
    const acao = () => transferir(origem, -10);

    //Assert
    expect(acao).toThrow('Valor inválido');
  });

  test('recusa transferência sem saldo suficiente', () => {
    //Arrange
    const origem = { saldo: 50 };

    //Act
    const resultado = transferir(origem, 100);

    //Assert
    expect(resultado).toEqual({ status: 'recusada', motivo: 'saldo insuficiente' });
  });

  test('respeita o limite noturno', () => {
    //Arrange
    const origem = { saldo: 5000 };
    const valorAcimaDoLimite = LIMITE_NOTURNO + 1;

    //Act
    const resultado = transferir(origem, valorAcimaDoLimite, { horario: 23 });

    //Assert
    expect(resultado).toEqual({ status: 'recusada', motivo: 'limite noturno excedido' });
  });

  test('consulta antifraude em transferência alta', () => {
    //Arrange
    const origem = { saldo: 9000 };

    //Act
    const resultado = transferir(origem, 8000, { verificarFraude: true });

    //Assert
    expect(resultado.status).toBe('concluida');
  });
});

describe('Extrato', () => {
  test('lista movimentos da conta', () => {
    //Arrange
    const conta = { movimentos: [{ valor: 10 }] };

    //Act
    const movimentos = extrato(conta);

    //Assert
    expect(movimentos).toHaveLength(1);
  });
});
