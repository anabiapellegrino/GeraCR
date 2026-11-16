import argparse
import json
import sys
from pathlib import Path

from .config import eh_objeto, mesclar_config, validar_config
from .exportacao import arquivos_de_saida, resumo
from .leitura import LEITORES, detectar_formato
from .pipeline import processar

#eager: os argumentos rodam em ordem antes da chamada
em_sequencia = lambda *valores: valores[-1]

avisar = lambda mensagem: em_sequencia(print(f"geracr: {mensagem}", file=sys.stderr), 2)

ler_argumentos = lambda argv: (lambda parser: em_sequencia(
    parser.add_argument("relatorio", help="relatório de testes (JUnit XML ou JSON)"),
    parser.add_argument("--config", help="config.json do time (opcional)"),
    parser.add_argument("--saida", default="saida", help="pasta onde gravar as CRs (padrão: saida)"),
    parser.add_argument("--formato", choices=sorted(LEITORES), help="força o formato (padrão: pela extensão)"),
    parser.parse_args(argv),
))(argparse.ArgumentParser(
    prog="geracr", description="Gera rascunhos de CR a partir do relatório de uma bateria de testes."
))

ler_texto = lambda caminho: Path(caminho).read_text(encoding="utf-8")

ler_config = lambda caminho: json.loads(ler_texto(caminho)) if caminho else {}

formato_de = lambda args: args.formato or detectar_formato(args.relatorio)

#newline="": grava as quebras de linha como estão (sem isso o Windows dobra o CR das linhas do CSV)
gravar = lambda arquivo: em_sequencia(
    arquivo.caminho.write_text(arquivo.conteudo, encoding="utf-8", newline=""), arquivo.caminho
)

gravar_todos = lambda pasta, arquivos: em_sequencia(
    pasta.mkdir(parents=True, exist_ok=True), tuple(map(gravar, arquivos))
)

mostrar = lambda args, config, testes, crs, gravados: em_sequencia(
    print(resumo(config["projeto"], f"{args.relatorio} ({formato_de(args)})", testes, crs, Path(args.saida))),
    print(f"{len(gravados)} arquivo(s): {len(crs)} CR(s) em Markdown + importar-no-jira.csv"),
    0,
)

gravar_e_mostrar = lambda args, config, testes, crs: (
    avisar("nenhum teste encontrado no relatório")
    if not testes
    else mostrar(args, config, testes, crs, gravar_todos(Path(args.saida), arquivos_de_saida(crs, Path(args.saida))))
)

avisar_config_invalido = lambda problemas: avisar("config inválido:\n  - " + "\n  - ".join(problemas))

com_config = lambda args, config: (
    avisar_config_invalido(validar_config(config))
    if validar_config(config)
    else gravar_e_mostrar(args, config, *processar(ler_texto(args.relatorio), formato_de(args), config))
)

com_config_lido = lambda args, lido: (
    com_config(args, mesclar_config(lido))
    if eh_objeto(lido)
    else avisar_config_invalido(('o config.json deve ser um objeto JSON, como {"projeto": "Loja"}',))
)

executar_com = lambda args: (
    avisar(f"relatório não encontrado: {args.relatorio}")
    if not Path(args.relatorio).is_file()
    else avisar(f"não sei ler '{Path(args.relatorio).suffix}'. Use --formato ({', '.join(LEITORES)})")
    if formato_de(args) not in LEITORES
    else avisar(f"config não encontrado: {args.config}")
    if args.config and not Path(args.config).is_file()
    else com_config_lido(args, ler_config(args.config))
)

executar = lambda argv: executar_com(ler_argumentos(argv))
