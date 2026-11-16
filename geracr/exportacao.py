import re
import unicodedata

from .funcional import compor, contar_por
from .modelo import ERRO, FALHOU, IGNORADO, PASSOU, Arquivo

CABECALHO_CSV = ("Titulo", "Severidade", "Labels", "Testes afetados", "Descricao")


celula_md = lambda texto: texto.replace("|", "\\|")

nota_de_agrupamento = lambda quantidade: (
    (f"> Os {quantidade} testes falharam com a mesma mensagem (ignorando IDs, horários e "
     "durações), por isso viraram uma CR só.", "")
    if quantidade > 1
    else ()
)

#os testes de uma CR podem ter mensagens com IDs ou horários diferentes
mensagens_diferentes = lambda cr: len(set(cr.mensagens)) > 1

legenda_do_obtido = lambda cr: (
    "Mensagem de erro do primeiro teste (a de cada teste está em Testes afetados):"
    if mensagens_diferentes(cr)
    else "Mensagem de erro do primeiro teste (a dos outros é igual):"
    if len(cr.testes) > 1
    else "Mensagem de erro do teste:"
)

#com mensagens diferentes, cada teste mostra a sua, para não perder o ID de nenhum
linhas_dos_testes = lambda cr: (
    map(lambda par: f"- `{par[0]}`: `{par[1]}`", zip(cr.testes, cr.mensagens))
    if mensagens_diferentes(cr)
    else map(lambda teste: f"- `{teste}`", cr.testes)
)

#quando o relatório só traz a mensagem, a evidência repetiria o resultado obtido
secao_de_evidencia = lambda cr: (
    ()
    if cr.evidencia.strip() == cr.resultado_obtido.strip()
    else (
        "## Evidência",
        "Trecho do relatório de testes, sem as linhas internas de bibliotecas.",
        "```text",
        cr.evidencia,
        "```",
        "",
    )
)

cr_para_markdown = lambda cr: "\n".join((
    f"# CR-{cr.numero:02d} {cr.titulo}",
    "",
    f"**Resumo:** {cr.resumo}",
    "",
    "| Campo | Valor |",
    "|---|---|",
    f"| Severidade sugerida | {celula_md(cr.severidade)} |",
    f"| Tipo do erro | {celula_md(cr.tipo_erro)} |",
    f"| Ambiente | {celula_md(cr.ambiente)} |",
    f"| Labels | {celula_md(', '.join(cr.labels))} |",
    "",
    "## Resultado obtido",
    legenda_do_obtido(cr),
    "```text",
    cr.resultado_obtido,
    "```",
    "",
    "## Resultado esperado",
    cr.resultado_esperado,
    "",
    f"## Testes afetados ({len(cr.testes)})",
    *linhas_dos_testes(cr),
    "",
    *nota_de_agrupamento(len(cr.testes)),
    *secao_de_evidencia(cr),
    "## Passos para reproduzir",
    "_A completar por quem revisar: o relatório de testes não traz essa informação._",
    "",
    "---",
    "_Rascunho gerado pelo GeraCR. Revise antes de cadastrar no Jira._",
    "",
))


sem_prefixo =lambda texto: re.sub(r"^\[[^\]]*\]\s*", "", texto)
sem_acentos = lambda texto: unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
trocar_simbolos = lambda texto: re.sub(r"[^a-z0-9]+", "-", texto).strip("-")

slug = lambda texto, limite=50: (
    compor(sem_prefixo, sem_acentos, str.lower, trocar_simbolos)(texto)[:limite].rstrip("-") or "cr"
)

nome_do_arquivo = lambda cr: f"CR-{cr.numero:02d}-{slug(cr.titulo)}.md"


celula_csv = lambda valor: '"' + valor.replace('"', '""') + '"'

linha_csv = lambda valores: ",".join(map(celula_csv, valores))

#formato do importador do Jira: vírgula, UTF-8 e a CR inteira na descrição
cr_para_valores = lambda cr: (
    cr.titulo, cr.severidade, " ".join(cr.labels), "\n".join(cr.testes), cr_para_markdown(cr)
)

gerar_csv = lambda crs: "\r\n".join(map(linha_csv, (CABECALHO_CSV, *map(cr_para_valores, crs)))) + "\r\n"


arquivos_de_saida = lambda crs, pasta: tuple(
    map(lambda cr: Arquivo(pasta / nome_do_arquivo(cr), cr_para_markdown(cr)), crs)
) + (Arquivo(pasta / "importar-no-jira.csv", gerar_csv(crs)),)

quantas_falharam = lambda por_status: por_status.get(FALHOU, 0) + por_status.get(ERRO, 0)

linhas_de_severidade = lambda crs: (
    ("Por severidade: " + " | ".join(
        map(lambda par: f"{par[0]}: {par[1]}", contar_por(lambda cr: cr.severidade, crs).items())
    ),)
    if crs
    else ("Nenhuma falha encontrada: nada para reportar.",)
)

resumo_com_contagem = lambda projeto, origem, testes, por_status, crs, pasta: "\n".join((
    f"GeraCR · {projeto}",
    f"Relatório: {origem}",
    f"Testes lidos: {len(testes)} | passaram: {por_status.get(PASSOU, 0)} "
    f"| falharam: {quantas_falharam(por_status)} | ignorados: {por_status.get(IGNORADO, 0)}",
    f"CRs geradas: {len(crs)} (a partir de {quantas_falharam(por_status)} falhas)",
    *linhas_de_severidade(crs),
    *map(lambda cr: f"  CR-{cr.numero:02d} [{cr.severidade}] {cr.titulo}", crs),
    f"Arquivos gravados em: {pasta}",
))

resumo = lambda projeto, origem, testes, crs, pasta: resumo_com_contagem(
    projeto, origem, testes, contar_por(lambda teste: teste.status, testes), crs, pasta
)
