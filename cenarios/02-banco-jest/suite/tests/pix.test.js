const { enviarPix } = require('../src/transferencias');

describe('Pix', () => {
  test('envia Pix para chave e-mail', () => {
    //Arrange
    const origem = { saldo: 300 };
    const chave = 'ana@exemplo.com';

    //Act
    const resultado = enviarPix(origem, chave, 50);

    //Assert
    expect(resultado.status).toBe('concluida');
  });

  test('envia Pix para chave CPF', () => {
    //Arrange
    const origem = { saldo: 300 };
    const chave = '12345678901';

    //Act
    const resultado = enviarPix(origem, chave, 50);

    //Assert
    expect(resultado.status).toBe('concluida');
  });

  test('envia Pix para chave aleatória', () => {
    //Arrange
    const origem = { saldo: 300 };
    const chave = 'f3a1c9e2-7b44-4d1a-9c55-0e2b8d6f1a77';

    //Act
    const resultado = enviarPix(origem, chave, 50);

    //Assert
    expect(resultado.status).toBe('concluida');
  });

  test('envia Pix para chave telefone', () => {
    //Arrange
    const origem = { saldo: 300 };
    const chave = '+5581999990000';

    //Act
    const resultado = enviarPix(origem, chave, 50);

    //Assert
    expect(resultado.status).toBe('concluida');
  });
});
