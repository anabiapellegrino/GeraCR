import json
import re
import xml.etree.ElementTree as ET
from itertools import chain, dropwhile, takewhile
from pathlib import Path

from .modelo import ERRO, FALHOU, IGNORADO, PASSOU, Teste

STATUS_POR_TAG = {"failure": FALHOU, "error": ERRO, "skipped": IGNORADO}

STATUS_JSON = {
    "passou": PASSOU, "passed": PASSOU, "pass": PASSOU,
    "falhou": FALHOU, "failed": FALHOU, "fail": FALHOU,
    "erro": ERRO, "error": ERRO,
    "ignorado": IGNORADO, "skipped": IGNORADO, "skip": IGNORADO,
}

TIPO_PADRAO = {FALHOU: "Falha", ERRO: "Erro", IGNORADO: "", PASSOU: ""}

EXCECAO_NO_INICIO = re.compile(r"^(?:[A-Za-z_$][\w$]*\.)*(\w*(?:Error|Exception))\b")
LINHA_DA_PILHA = re.compile(r'^\s*(?:at |File "|Traceback \()')


fora_da_pilha = lambda linha: not LINHA_DA_PILHA.match(linha)

resumo_do_erro = lambda texto: "\n".join(filter(str.strip, takewhile(fora_da_pilha, texto.strip().splitlines())))

pilha_de_chamadas = lambda texto: "\n".join(dropwhile(fora_da_pilha, texto.strip().splitlines()))

tipo_na_mensagem = lambda mensagem: (
    (EXCECAO_NO_INICIO.findall(mensagem) or [""])[0]
    or ("AssertionError" if mensagem.startswith("assert ") else "")
)

tipo_do_erro = lambda mensagem, tipo_declarado, status: (
    tipo_na_mensagem(mensagem) or tipo_declarado or TIPO_PADRAO[status]
)


#recursão
casos_de_teste = lambda suite: chain(
    suite.iterfind("testcase"),
    chain.from_iterable(map(casos_de_teste, suite.iterfind("testsuite"))),
)

primeiro_problema = lambda caso: next(filter(lambda filho: filho.tag in STATUS_POR_TAG, caso), None)

texto_do_problema = lambda problema: (problema.text or "").strip()

mensagem_do_problema = lambda problema: (
    problema.get("message") or resumo_do_erro(texto_do_problema(problema)) or "sem mensagem"
)

com_problema = lambda teste, problema, status, mensagem: teste._replace(
    status=status,
    tipo_erro=tipo_do_erro(mensagem, problema.get("type"), status),
    mensagem=mensagem,
    detalhe=texto_do_problema(problema),
)

aplicar_problema = lambda teste, problema: (
    teste
    if problema is None
    else com_problema(teste, problema, STATUS_POR_TAG[problema.tag], mensagem_do_problema(problema))
)

caso_para_teste = lambda caso: aplicar_problema(
    Teste(suite=caso.get("classname", ""), nome=caso.get("name", "sem nome"), status=PASSOU),
    primeiro_problema(caso),
)

ler_junit = lambda texto: map(caso_para_teste, casos_de_teste(ET.fromstring(texto)))


status_do_registro = lambda registro: STATUS_JSON.get(str(registro.get("status", "")).lower(), ERRO)

campo_texto = lambda registro, chave: str(registro.get(chave) or "")

montar_teste = lambda registro, status, mensagem: Teste(
    suite=campo_texto(registro, "suite"),
    nome=campo_texto(registro, "nome") or "sem nome",
    status=status,
    tipo_erro=campo_texto(registro, "tipo") or tipo_do_erro(mensagem, None, status),
    mensagem=mensagem or ("" if status == PASSOU else "sem mensagem"),
    detalhe=campo_texto(registro, "detalhe"),
)

registro_para_teste = lambda registro: montar_teste(
    registro, status_do_registro(registro), campo_texto(registro, "mensagem")
)

lista_de_testes = lambda dados: (
    dados.get("testes") if isinstance(dados, dict) and isinstance(dados.get("testes"), list) else ()
)

registros = lambda dados: filter(lambda registro: isinstance(registro, dict), lista_de_testes(dados))

ler_json = lambda texto: map(registro_para_teste, registros(json.loads(texto)))


LEITORES = {
    "junit": ler_junit,
    "json": ler_json,
}

FORMATO_POR_EXTENSAO = {".xml": "junit", ".json": "json"}

detectar_formato = lambda caminho: FORMATO_POR_EXTENSAO.get(Path(caminho).suffix.lower())
