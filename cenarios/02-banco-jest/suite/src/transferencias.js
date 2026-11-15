//api de transferências de mentira pra gerar o relatório
//bugs de propósito: aceita sem saldo e ignora o limite noturno
//antifraude lento, o tempo do timeout muda a cada execução

const LIMITE_NOTURNO = 1000;

function consultarAntifraude() {
  const ms = 5000 + Math.floor(Math.random() * 400);
  throw new Error(`Timeout: serviço antifraude não respondeu em ${ms}ms`);
}

function transferir(origem, valor, { horario = 14, verificarFraude = false } = {}) {
  if (verificarFraude) consultarAntifraude();
  if (valor <= 0) throw new Error('Valor inválido');
  //bug: falta checar saldo e limite noturno
  return { status: 'concluida', saldo: origem.saldo - valor };
}

function enviarPix(origem, chave, valor) {
  const protocolo = Date.now().toString() + Math.floor(Math.random() * 1000);
  if (!chave.includes('@') && !/^\d{11}$/.test(chave)) {
    throw new Error(`Chave Pix não encontrada no DICT (protocolo ${protocolo})`);
  }
  return transferir(origem, valor, { verificarFraude: true });
}

function extrato(conta) {
  return conta.movimentos.map((m) => ({ ...m }));
}

module.exports = { transferir, enviarPix, extrato, LIMITE_NOTURNO };
