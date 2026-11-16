# GeraCR

Programa de terminal que lê o relatório de uma bateria de testes automatizados e escreve os rascunhos de CR (relatório de bug). A pessoa de QA só revisa e cadastra no Jira.

Feito em Python, no paradigma funcional, para a disciplina de Paradigmas de Linguagens de Programação da UNICAP, por Ana Pellegrino e André Mota.

O código do programa não tem `def`, `for`, `while` nem `class`. Toda função é uma `lambda` com nome e toda repetição usa `map`, `filter`, `reduce` ou recursão. Só usa a biblioteca padrão.

## O problema

Uma bateria de testes roda e 20, 30 testes falham. Alguém abre uma CR à mão para cada falha. Isso demora, cada pessoa escreve de um jeito, o stack trace se perde no caminho e, quando uma causa só derruba vários testes, aparecem várias CRs repetidas.

Exemplo: o gateway de pagamento cai e três testes falham com `ConnectionError: gateway indisponível`, cada um com um ID de requisição diferente. Quem não percebe abre três CRs. O GeraCR junta as três em uma.

## Como rodar

Precisa de Python 3.10 ou mais novo. Não tem nada para instalar.

```bash
python -m geracr cenarios/01-loja-pytest/relatorio.xml --config cenarios/01-loja-pytest/config.json --saida saida/loja
```

No Windows dá para usar `py` no lugar de `python`.

Saída:

```
GeraCR · Loja Virtual
Relatório: cenarios/01-loja-pytest/relatorio.xml (junit)
Testes lidos: 9 | passaram: 4 | falharam: 5 | ignorados: 0
CRs geradas: 3 (a partir de 5 falhas)
Por severidade: Crítica: 1 | Alta: 1 | Média: 1
  CR-01 [Crítica] [BUG] ConnectionError: gateway indisponível (req=[id]) (3 testes)
  CR-02 [Alta] [BUG] cupom 10 porcento: assert 89.9 == 89.91
  CR-03 [Média] [BUG] frete gratis a partir de 200: assert 19.9 == 0.0
```

Na pasta `saida/loja` ficam um Markdown por CR e um `importar-no-jira.csv` para importar todas no Jira de uma vez.

Cada CR começa com um resumo em português ("3 testes falharam pelo mesmo motivo: um serviço demorou demais para responder") e segue a ordem de um relatório de bug: resultado obtido, resultado esperado, testes afetados, evidência e passos para reproduzir. Na evidência, o GeraCR tira as linhas internas de bibliotecas (`node_modules`, `site-packages`) e as pastas do computador de quem rodou os testes, deixando só arquivo e linha.

Opções:

| Opção | Para quê |
|---|---|
| `relatorio` | arquivo gerado pela ferramenta de testes (`.xml` ou `.json`) |
| `--config` | `config.json` do time. Sem ele, usa o padrão |
| `--saida` | pasta das CRs (padrão: `saida`) |
| `--formato` | força `junit` ou `json` quando a extensão não ajuda |

## Como funciona

O programa é uma linha de montagem. Cada etapa é um módulo só com funções puras, e só o `cli.py` lê e grava arquivos.

| Etapa | Módulo | O que faz |
|---|---|---|
| 1. Ler | `leitura.py` | transforma o relatório em registros `Teste` |
| 2. Filtrar | `agrupamento.py` | fica só com os testes que falharam |
| 3. Agrupar | `agrupamento.py` | junta falhas com o mesmo tipo e mensagem, ignorando IDs, horários e durações |
| 4. Classificar | `classificacao.py` | sugere a severidade pela primeira regra do config que bater |
| 5. Montar | `montagem.py` | escreve título, resumo, testes afetados, resultados obtido e esperado, evidência, ambiente e labels |
| 6. Exportar | `exportacao.py` e `cli.py` | gera o texto do Markdown e do CSV e grava os arquivos |

As etapas 2 a 5 viram uma função só com `compor`, em `pipeline.py`:

```python
montar_linha = lambda config, normalizar: compor(
    filtrar_falhas,
    partial(agrupar_falhas, criar_chave(config["agrupar_por"], normalizar), normalizar),
    partial(classificar, regras_do_config(config), config["severidade_padrao"]),
    partial(ordenar_por_severidade, config["severidades"]),
    partial(montar_crs, config),
)
```

Os outros arquivos são `modelo.py` (os registros), `funcional.py` (funções genéricas), `config.py` (config padrão e validação) e `__main__.py` (ponto de entrada).

## Programação funcional no projeto

| Conceito | Onde está |
|---|---|
| Funções puras | todos os módulos menos `cli.py` e `__main__.py` |
| Sem `def`, `for`, `while` e `class` | toda função é `lambda` com nome, e não tem compreensão de lista |
| Imutabilidade | registros criados com a função `namedtuple`, `_replace` para criar cópias, tuplas no lugar de listas, `CONFIG_PADRAO` somente leitura |
| Funções de primeira classe | dicionários de funções: `LEITORES`, `CAMPOS_DE_REGRA`, `EXTRATORES_DE_CHAVE`, `TIPOS_DO_CONFIG` |
| Função como parâmetro | `agrupar_por`, `contar_por`, `primeira_resposta`, `compor` |
| Função que retorna função | `regra_contem`, `criar_chave`, `criterio`, `criar_normalizador`, `compor`, `gerar_crs` |
| `map`, `filter` e `reduce` | `ler_junit`, `filtrar_falhas`, `agrupar_por`, `normalizar_com`, `compor` |
| Composição e aplicação parcial | `compor` em `montar_linha` e `slug`, `functools.partial` em `montar_linha` e `criar_normalizador` |
| Expressão condicional e curto-circuito | `x if cond else y` no lugar de `if`, cadeias de `or` em `tipo_do_erro` e `validar_config` |
| Recursão | `casos_de_teste` lê suítes dentro de suítes no XML, em qualquer profundidade |
| Avaliação preguiçosa | `primeira_resposta` para na primeira regra que responde, `count(1)` infinito em `montar_crs` |
| Avaliação ansiosa | `em_sequencia` no `cli.py` encadeia imprimir e gravar sem comandos |
| Polimorfismo paramétrico | as funções de `funcional.py` servem para qualquer tipo, com assinatura no estilo do Haskell |

O único comando de controle é o `try` do `__main__.py`, porque um XML ou JSON quebrado chega como exceção e o Python só captura exceção com `try`. Config com tipo errado não vira exceção: `validar_config` devolve os problemas como valor e o programa só avisa.

## Cenários

A pasta `cenarios/` tem quatro sistemas de exemplo, cada um testado com uma ferramenta diferente e com bugs de propósito. Os relatórios foram gerados rodando as ferramentas de verdade. O código do GeraCR é o mesmo nos quatro, só mudam o relatório e o `config.json`.

| Cenário | Ferramenta | Formato | Severidades | Testes | Falhas | CRs |
|---|---|---|---|---|---|---|
| 01 Loja virtual | pytest | JUnit XML | Crítica a Baixa | 9 | 5 | 3 |
| 02 Banco digital | Jest (JavaScript) | JUnit XML sem `message` | P1 a P4 | 10 | 7 | 4 |
| 03 Biblioteca | Robot Framework | JUnit XML com 3 níveis de suíte | Highest a Lowest | 9 | 6 | 3 |
| 04 Clínica | unittest | JSON | Bloqueante a Leve | 10 | 5 | 3 |
| Total | | | | 38 | 23 | 13 |

Para um contexto novo basta criar `cenarios/05-.../` com o `relatorio.*` e o `config.json`.

Para gerar os relatórios de novo (opcional):

```bash
cd cenarios/01-loja-pytest/suite && python -m pytest --junitxml=../relatorio.xml
cd cenarios/02-banco-jest/suite && npm install && npm test
cd cenarios/03-biblioteca-robot/suite && python -m robot --xunit ../relatorio.xml --output NONE --log NONE --report NONE Biblioteca
cd cenarios/04-clinica-unittest-json/suite && python gerar_relatorio.py ../relatorio.json
```

Os IDs, durações e horários mudam toda vez, mas as CRs geradas continuam as mesmas.

## config.json

Só precisa escrever o que for diferente do padrão.

| Chave | Exemplo | Padrão |
|---|---|---|
| `projeto` | `"Loja Virtual"` | `"Projeto sem nome"` |
| `prefixo_titulo` | `"[BUG]"` | `"[BUG]"` |
| `ambiente` | `{"Ambiente": "QA", "Versão": "2.4.1"}` | vazio |
| `labels` | `["automacao", "checkout"]` | `["automacao"]` |
| `severidades` | `["P1", "P2", "P3"]`, da mais grave para a menos grave | `["Crítica", "Alta", "Média", "Baixa"]` |
| `severidade_padrao` | `"P3"` | `"Média"` |
| `regras_severidade` | ver abaixo | nenhuma |
| `agrupar_por` | `["suite", "tipo", "mensagem"]` | `["tipo", "mensagem"]` |
| `ignorar_na_mensagem` | `["\\d{10,}"]` (regex) | nenhuma |
| `linhas_de_evidencia` | `6` | `15` |

Nas regras de severidade vale a primeira que bater. `campo` pode ser `teste`, `mensagem` ou `tipo`, e `contem` aceita um texto ou uma lista, sem diferenciar maiúsculas.

```json
"regras_severidade": [
  {"campo": "teste", "contem": ["pagamento", "pix"], "severidade": "Crítica"},
  {"campo": "tipo", "contem": "Timeout", "severidade": "Alta"}
]
```

Se o config tiver erro, o programa avisa o que está errado e não gera nada.

## Formato JSON

Para ferramentas que não geram JUnit XML. No cenário 04, o `gerar_relatorio.py` roda os testes com unittest e grava neste formato.

```json
{
  "testes": [
    {"suite": "Login", "nome": "login com e-mail válido", "status": "passou"},
    {"suite": "Checkout", "nome": "finalizar pedido", "status": "falhou",
     "tipo": "NoSuchElementException", "mensagem": "botão não encontrado", "detalhe": "stack trace..."}
  ]
}
```

`status` aceita `passou`, `falhou`, `erro` e `ignorado` (ou em inglês). `tipo`, `mensagem` e `detalhe` são opcionais. Status desconhecido conta como erro, para nenhuma falha sumir.

## Como estender

- Formato novo: escrever uma função que transforma o texto do relatório em registros `Teste` e acrescentar uma linha em `LEITORES`, no `leitura.py`.
- Contexto novo: criar uma pasta em `cenarios/`.

## Limites

- Não abre a CR direto no Jira, porque isso exigiria login e efeitos fora do programa.
- O agrupamento é uma estimativa. Falhas com a mesma mensagem podem ter causas diferentes, por isso o resultado é rascunho.
- O relatório de testes não traz os passos para reproduzir, então quem revisa completa.
- O CSV é feito para o importador do Jira: vírgula, UTF-8 e a CR inteira na descrição. Aberto direto no Excel ele fica bagunçado, porque o Excel em português espera ponto e vírgula e não reconhece UTF-8 sem aviso.
- O resumo em português vem de uma tabela de palavras-chave (`EXPLICACOES`, em `montagem.py`). Quando nenhuma bate, a CR diz que o relatório não informa a causa.

## Estrutura

```
geracr/      código do programa
cenarios/    quatro sistemas de exemplo com relatórios reais
```
