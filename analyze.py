#!/usr/bin/env python3
"""
Analisador de testes A/B de cashback — Méliuz (Growth AI-Native).

Recebe UM arquivo CSV de um teste A/B de cashback e devolve:
  1. uma analise completa (relatorio em Markdown, apresentavel para um gestor);
  2. uma decisao acionavel: qual variante escalar para 100% do trafego;
  3. o registro do teste numa planilha de acompanhamento (CSV), 1 linha por teste.

Roda em QUALQUER teste sem mudar o codigo: e so apontar o arquivo. Detecta
sozinho o numero de variantes (2, 3, ...) e o parceiro. Zero dependencias
externas — usa apenas a biblioteca padrao do Python 3.

Por que a conta fica no codigo (e nao no LLM):
  numero de dinheiro nao pode ser "achismo". Agregacao e estatistica sao
  deterministicas aqui; o LLM entra por cima para interpretar e comunicar.

Uso:
  python3 analyze.py <arquivo.csv> [--nome "Nome do teste"] [--descricao "..."]
                     [--registro registro_testes.csv] [--saida relatorios]

Metrica de decisao:
  Margem liquida do Meliuz = comissao (receita) - cashback (custo).
  Num teste A/B com split de trafego equilibrado, a variante com maior margem
  liquida total e a que mais gera lucro quando escalada. Confirmamos com um
  teste de significancia sobre a margem liquida diaria (winner vs vice).
"""

import argparse
import csv
import datetime
import math
import os
import re
import statistics
import sys
import unicodedata
from collections import defaultdict


# --------------------------------------------------------------------------- #
# Parsing robusto (dados "sujos" acontecem)
# --------------------------------------------------------------------------- #
def _norm(texto: str) -> str:
    """Minusculo, sem acento, sem espaco nas pontas — para casar nomes de coluna."""
    if texto is None:
        return ""
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return t.lower().strip()


def parse_dinheiro(valor: str) -> float:
    """
    Converte 'R$ 10.273' / 'R$ 1.234,56' / '10273' em float.
    Padrao brasileiro: ponto = milhar, virgula = decimal. Robusto a lixo.
    """
    if valor is None:
        return 0.0
    s = str(valor).strip()
    s = s.replace("R$", "").replace("r$", "").replace(" ", "").replace("\xa0", "")
    if not s:
        return 0.0
    s = s.replace(".", "").replace(",", ".")  # milhar some, decimal vira ponto
    s = re.sub(r"[^0-9.\-]", "", s)            # tira qualquer residuo
    try:
        return float(s) if s not in ("", "-", ".") else 0.0
    except ValueError:
        return 0.0


def parse_int(valor: str) -> int:
    s = re.sub(r"[^0-9\-]", "", str(valor or ""))
    try:
        return int(s) if s not in ("", "-") else 0
    except ValueError:
        return 0


def achar_coluna(cabecalhos, *palavras):
    """Acha o nome real da coluna por correspondencia flexivel (tolera variacao)."""
    normed = [(_norm(h), h) for h in cabecalhos]
    for p in palavras:
        for nh, original in normed:
            if p in nh:
                return original
    return None


# --------------------------------------------------------------------------- #
# Carregamento e agregacao
# --------------------------------------------------------------------------- #
COLUNAS_ESPERADAS = {
    "data": ("data",),
    "grupo": ("grupo", "variante"),
    "parceiro": ("parceiro",),
    "compradores": ("comprador",),
    "comissao": ("comissao",),
    "cashback": ("cashback",),
    "gmv": ("vendas", "gmv", "faturamento"),
}


def carregar(caminho: str):
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f)
        cabecalhos = leitor.fieldnames or []
        col = {chave: achar_coluna(cabecalhos, *palavras)
               for chave, palavras in COLUNAS_ESPERADAS.items()}

        faltando = [k for k in ("grupo", "compradores", "comissao", "cashback")
                    if not col[k]]
        if faltando:
            raise ValueError(
                f"CSV nao tem as colunas essenciais: {faltando}. "
                f"Cabecalhos encontrados: {cabecalhos}")

        linhas, ignoradas = [], 0
        for r in leitor:
            grupo = (r.get(col["grupo"]) or "").strip()
            if not grupo:                     # linha sem variante = lixo, pula
                ignoradas += 1
                continue
            linhas.append({
                "data": (r.get(col["data"]) or "").strip() if col["data"] else "",
                "grupo": grupo,
                "parceiro": (r.get(col["parceiro"]) or "").strip() if col["parceiro"] else "",
                "compradores": parse_int(r.get(col["compradores"])),
                "comissao": parse_dinheiro(r.get(col["comissao"])),
                "cashback": parse_dinheiro(r.get(col["cashback"])),
                "gmv": parse_dinheiro(r.get(col["gmv"])) if col["gmv"] else 0.0,
            })
    if not linhas:
        raise ValueError("Nenhuma linha valida encontrada no CSV.")
    return linhas, ignoradas


def agregar(linhas):
    """Totais por variante + serie diaria de margem liquida (para estatistica)."""
    g = defaultdict(lambda: {
        "dias": 0, "compradores": 0, "comissao": 0.0, "cashback": 0.0,
        "gmv": 0.0, "margem_diaria": [], "margem_por_dia": {},
    })
    for r in linhas:
        d = g[r["grupo"]]
        d["dias"] += 1
        d["compradores"] += r["compradores"]
        d["comissao"] += r["comissao"]
        d["cashback"] += r["cashback"]
        d["gmv"] += r["gmv"]
        m_dia = r["comissao"] - r["cashback"]
        d["margem_diaria"].append(m_dia)
        if r["data"]:                          # guarda a margem por data p/ teste pareado
            d["margem_por_dia"][r["data"]] = d["margem_por_dia"].get(r["data"], 0.0) + m_dia

    variantes = {}
    for nome, d in g.items():
        margem = d["comissao"] - d["cashback"]
        variantes[nome] = {
            **d,
            "margem_liquida": margem,
            "margem_por_comprador": margem / d["compradores"] if d["compradores"] else 0.0,
            "cashback_pct_gmv": 100 * d["cashback"] / d["gmv"] if d["gmv"] else 0.0,
            "take_rate": 100 * d["comissao"] / d["gmv"] if d["gmv"] else 0.0,
        }
    return variantes


# --------------------------------------------------------------------------- #
# Estatistica (sem dependencias). Aproximacao normal (z), justificada pelo TCL
# com 30+ observacoes diarias por variante.
#
# Teste PAREADO por dia: as variantes rodam nos mesmos dias, entao o "clima" de
# cada dia (fim de semana, promo, sazonalidade) afeta todas por igual. Comparar
# a margem dia a dia cancela esse ruido comum e mede a diferenca real. Se as
# datas nao baterem, caimos no Welch nao-pareado.
# --------------------------------------------------------------------------- #
def _p_bicaudal(z: float) -> float:
    return 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))


def _resultado(diff, se, metodo, n):
    if se == 0:
        return {"diff_media_diaria": diff, "z": 0.0, "p": 1.0, "ic95": (diff, diff),
                "significativo": False, "metodo": metodo, "n": n}
    z = diff / se
    p = _p_bicaudal(z)
    return {"diff_media_diaria": diff, "z": z, "p": p,
            "ic95": (diff - 1.96 * se, diff + 1.96 * se),
            "significativo": p < 0.05, "metodo": metodo, "n": n}


def comparar(a: dict, b: dict):
    """Compara a margem diaria de duas variantes. Pareia por dia quando as datas
    coincidem (o certo para um A/B simultaneo); senao usa Welch nao-pareado.
    Retorna diff media diaria, z, p, IC95% e qual metodo foi usado."""
    dia_a, dia_b = a.get("margem_por_dia") or {}, b.get("margem_por_dia") or {}
    comuns = sorted(set(dia_a) & set(dia_b))
    lista_a, lista_b = a["margem_diaria"], b["margem_diaria"]

    # pareado so quando as datas cobrem quase toda a serie (evita parear meia duzia
    # de dias em comum e jogar fora o resto)
    if len(comuns) >= 2 and len(comuns) >= 0.8 * min(len(lista_a), len(lista_b)):
        difs = [dia_a[d] - dia_b[d] for d in comuns]        # margem G1 - G2 no mesmo dia
        media = statistics.mean(difs)
        se = statistics.stdev(difs) / math.sqrt(len(difs))
        return _resultado(media, se, "pareado", len(difs))

    if len(lista_a) < 2 or len(lista_b) < 2:
        return None
    diff = statistics.mean(lista_a) - statistics.mean(lista_b)
    se = math.sqrt(statistics.variance(lista_a) / len(lista_a)
                   + statistics.variance(lista_b) / len(lista_b))
    return _resultado(diff, se, "nao-pareado", min(len(lista_a), len(lista_b)))


# --------------------------------------------------------------------------- #
# Decisao + deteccao de problemas (o "olho critico")
# --------------------------------------------------------------------------- #
def analisar(variantes):
    ordenadas = sorted(variantes.items(),
                       key=lambda kv: kv[1]["margem_liquida"], reverse=True)
    vencedora_nome, vencedora = ordenadas[0]
    vice_nome, vice = ordenadas[1] if len(ordenadas) > 1 else (None, None)

    teste = comparar(vencedora, vice) if vice else None

    # a variante de maior GMV/volume (para expor o trade-off)
    maior_volume_nome = max(variantes.items(), key=lambda kv: kv[1]["gmv"])[0]

    alertas = []
    # dias desiguais entre variantes => possivel problema de alocacao
    dias = {n: v["dias"] for n, v in variantes.items()}
    if len(set(dias.values())) > 1:
        alertas.append(f"Numero de dias difere entre variantes ({dias}) — "
                       "verificar se o split foi equilibrado.")
    for n, v in variantes.items():
        if v["margem_liquida"] <= 0:
            alertas.append(f"{n} tem margem liquida <= 0 (R$ {v['margem_liquida']:,.0f}): "
                           "praticamente todo o comissionamento vira cashback.")
        if v["cashback_pct_gmv"] >= 8:
            alertas.append(f"{n} gasta {v['cashback_pct_gmv']:.1f}% do GMV em cashback — "
                           "custo alto, corroi a margem.")
    if maior_volume_nome != vencedora_nome:
        alertas.append(
            f"Trade-off: {maior_volume_nome} traz mais GMV/compradores, mas "
            f"{vencedora_nome} entrega mais margem liquida. Escalar por volume "
            "sacrificaria lucro.")

    # Impacto: quanto se perde escalando a "escolha instintiva" (maior volume/GMV)
    # em vez da vencedora por margem. E o custo, em R$, de decidir errado.
    tem_armadilha = maior_volume_nome != vencedora_nome  # a de maior volume nao e a mais lucrativa
    tentadora_nome = maior_volume_nome if tem_armadilha else vice_nome
    if tentadora_nome and tentadora_nome in variantes:
        gap_periodo = vencedora["margem_liquida"] - variantes[tentadora_nome]["margem_liquida"]
        dias = vencedora["dias"] or 1
        gap_anual = gap_periodo / dias * 365
    else:
        tentadora_nome, gap_periodo, gap_anual = None, 0.0, 0.0

    return {
        "ordenadas": ordenadas,
        "vencedora_nome": vencedora_nome,
        "vencedora": vencedora,
        "vice_nome": vice_nome,
        "teste": teste,
        "maior_volume_nome": maior_volume_nome,
        "alertas": alertas,
        "impacto": {"tentadora_nome": tentadora_nome, "tem_armadilha": tem_armadilha,
                    "gap_periodo": gap_periodo, "gap_anual": gap_anual},
    }


# --------------------------------------------------------------------------- #
# Saidas: relatorio Markdown + registro CSV
# --------------------------------------------------------------------------- #
def brl(v):
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def _barra(valor, maximo, largura=26):
    """Barra de texto (sem biblioteca) para o grafico de margem no relatorio."""
    if maximo <= 0:
        return ""
    return "█" * int(round(largura * max(valor, 0) / maximo))


def slug(texto):
    t = _norm(texto).replace(" ", "-")
    return re.sub(r"[^a-z0-9\-]", "", t) or "teste"


def gerar_relatorio(nome_teste, descricao, parceiro, variantes, res):
    v = res["vencedora"]
    vn = res["vencedora_nome"]
    teste = res["teste"]
    linhas = []
    A = linhas.append

    A(f"# Analise de Teste A/B de Cashback — {nome_teste}")
    A("")
    if descricao:
        A(f"_{descricao}_")
        A("")
    A(f"**Parceiro:** {parceiro or '-'}  |  **Variantes:** {len(variantes)}  |  "
      f"**Gerado em:** {DATA_HOJE}")
    A("")

    # --- decisao em destaque ---
    A("## Decisao")
    if teste and teste["significativo"]:
        conf = (f"A diferenca de margem para a 2a colocada e **estatisticamente "
                f"significativa** (p = {teste['p']:.3f}), entao da pra escalar com confianca.")
    elif teste:
        conf = (f"A diferenca para a 2a colocada **nao foi conclusiva** "
                f"(p = {teste['p']:.3f}); recomendo rodar mais tempo ou decidir "
                f"junto com o time antes de escalar 100%.")
    else:
        conf = "Apenas uma variante — sem comparacao possivel."
    A(f"> **Escalar a {vn} para 100% do trafego.** Ela entrega a maior margem "
      f"liquida ({brl(v['margem_liquida'])}), com o cashback custando "
      f"{v['cashback_pct_gmv']:.1f}% do GMV. {conf}")
    A("")

    # --- tabela por variante ---
    A("## Resultado por variante")
    A("")
    A("| Variante | Dias | Compradores | GMV | Comissao | Cashback | "
      "Margem liquida | Margem/comprador | Cashback %GMV |")
    A("|---|--:|--:|--:|--:|--:|--:|--:|--:|")
    for nome, d in res["ordenadas"]:
        marca = " 🏆" if nome == vn else ""
        A(f"| {nome}{marca} | {d['dias']} | {d['compradores']:,} | {brl(d['gmv'])} | "
          f"{brl(d['comissao'])} | {brl(d['cashback'])} | **{brl(d['margem_liquida'])}** | "
          f"{brl(d['margem_por_comprador'])} | {d['cashback_pct_gmv']:.1f}% |"
          .replace(",", "."))
    A("")

    # --- visual: margem liquida por variante (grafico sem biblioteca) ---
    maxm = max((d["margem_liquida"] for _, d in res["ordenadas"]), default=0)
    A("## Margem liquida por variante")
    A("```")
    for nome, d in res["ordenadas"]:
        A(f"{nome:8} {_barra(d['margem_liquida'], maxm):26} {brl(d['margem_liquida'])}")
    A("```")
    A("")

    # --- impacto da decisao (em R$) ---
    imp = res["impacto"]
    if imp["tentadora_nome"] and imp["gap_periodo"] > 0:
        A("## Impacto da decisao")
        if imp["tem_armadilha"]:
            A(f"Escalar a **{vn}** em vez da **{imp['tentadora_nome']}** (a de maior volume — a "
              f"escolha instintiva) representa **+{brl(imp['gap_periodo'])} de margem** no periodo "
              f"de {v['dias']} dias, o equivalente a cerca de **{brl(imp['gap_anual'])}/ano**. "
              f"Esse e o custo, em dinheiro, de decidir pela variante errada.")
        else:
            A(f"A **{vn}** vence por margem **e** e a de maior volume — escolha segura. Ainda assim, "
              f"vale dimensionar: ela supera a 2a colocada (**{imp['tentadora_nome']}**) em "
              f"**+{brl(imp['gap_periodo'])}** no periodo de {v['dias']} dias, ~**{brl(imp['gap_anual'])}/ano**.")
        A("")

    # --- estatistica ---
    if teste:
        ic = teste["ic95"]
        if teste.get("metodo") == "pareado":
            como = (f"**Teste t pareado por dia**, sobre {teste['n']} dias. Como as variantes "
                    f"rodaram nos mesmos dias, comparo a margem dia a dia e removo o ruido de "
                    f"demanda que atinge todas por igual.")
        else:
            como = "**Teste de Welch** (amostras nao-pareadas, aproximacao normal)."
        A("## Significancia estatistica")
        A(f"Comparacao da **margem liquida diaria** entre {vn} e {res['vice_nome']}. {como}")
        A("")
        A(f"- Diferenca media diaria: **{brl(teste['diff_media_diaria'])}/dia** a favor de {vn}")
        A(f"- Intervalo de confianca 95%: [{brl(ic[0])}, {brl(ic[1])}]/dia")
        veredito = "significativa" if teste["significativo"] else "inconclusiva"
        A(f"- p-valor: **{teste['p']:.4f}** (diferenca {veredito})")
        A("")

    # --- olho critico ---
    A("## Pontos de atencao")
    if res["alertas"]:
        for a in res["alertas"]:
            A(f"- ⚠️ {a}")
    else:
        A("- Nenhum problema relevante detectado nos dados.")
    A("")

    # --- leitura de negocio (data-driven: descreve o que ESTES dados mostram) ---
    A("## Leitura de negocio")
    # 1) relacao cashback x volume: compara a variante de MENOR cashback com a de MAIOR
    por_cb = sorted(variantes.items(), key=lambda kv: kv[1]["cashback_pct_gmv"])
    menor_cb_nome, menor_cb = por_cb[0]
    maior_cb_nome, maior_cb = por_cb[-1]
    vol_menor = menor_cb["compradores"] or 0
    delta_vol = (maior_cb["compradores"] - vol_menor) / vol_menor if vol_menor else 0.0

    if delta_vol > 0.03:
        frase_volume = (
            f"Mais cashback **trouxe volume**: a {maior_cb_nome} "
            f"({maior_cb['cashback_pct_gmv']:.1f}% do GMV em cashback) teve "
            f"{delta_vol*100:.0f}% mais compradores que a {menor_cb_nome}. Mas esse "
            f"volume veio **as custas da margem** — o cashback extra custou mais do "
            f"que a receita adicional que gerou.")
    elif delta_vol < -0.03:
        frase_volume = (
            f"Aqui nem volume o cashback comprou: a {maior_cb_nome} "
            f"({maior_cb['cashback_pct_gmv']:.1f}% do GMV em cashback) teve "
            f"{abs(delta_vol)*100:.0f}% **menos** compradores que a {menor_cb_nome} "
            f"(que gasta so {menor_cb['cashback_pct_gmv']:.1f}%). Mais cashback "
            f"significou **menos volume e menos margem** ao mesmo tempo.")
    else:
        frase_volume = (
            f"O cashback maior **nao moveu o volume**: a {maior_cb_nome} e a "
            f"{menor_cb_nome} tiveram praticamente os mesmos compradores, mas a "
            f"{maior_cb_nome} gastou {maior_cb['cashback_pct_gmv']:.1f}% do GMV em "
            f"cashback contra {menor_cb['cashback_pct_gmv']:.1f}% — puro custo, sem "
            f"retorno em volume.")

    # 2) tem ou nao trade-off volume x margem (a de maior volume e a vencedora?)
    if res["maior_volume_nome"] == vn:
        frase_decisao = (
            f"E a **{vn}** ainda vence em volume: e a de maior GMV/compradores **e** a "
            f"de maior margem. Sem trade-off — escalar para 100% e a escolha clara.")
    else:
        frase_decisao = (
            f"Ha um trade-off classico: a **{res['maior_volume_nome']}** traz mais "
            f"GMV/compradores, mas a **{vn}** entrega mais lucro liquido. Como a "
            f"pergunta e qual variante da mais lucro ao escalar, a resposta e a "
            f"**{vn}**; escalar por volume sacrificaria margem. Se o objetivo fosse "
            f"crescer a base a qualquer custo, a decisao seria estrategica — mas nao e "
            f"o que os dados de margem indicam.")

    A(frase_volume + " " + frase_decisao)
    A("")
    return "\n".join(linhas)


CABECALHO_REGISTRO = ["data_analise", "nome_teste", "parceiro", "descricao",
                      "variantes", "variante_vencedora", "margem_vencedora",
                      "significancia", "impacto_anual_estimado", "decisao"]


def registrar(caminho_registro, nome_teste, descricao, parceiro, variantes, res):
    v = res["vencedora"]
    teste = res["teste"]
    if teste is None:
        sig = "variante unica"
    elif teste["significativo"]:
        sig = f"significativo (p={teste['p']:.3f})"
    else:
        sig = f"inconclusivo (p={teste['p']:.3f})"
    linha = {
        "data_analise": DATA_HOJE,
        "nome_teste": nome_teste,
        "parceiro": parceiro or "-",
        "descricao": descricao or "-",
        "variantes": len(variantes),
        "variante_vencedora": res["vencedora_nome"],
        "margem_vencedora": f"{v['margem_liquida']:.2f}",
        "significancia": sig,
        "impacto_anual_estimado": f"{res['impacto']['gap_anual']:.0f}",
        "decisao": f"Escalar {res['vencedora_nome']} para 100%",
    }
    existe = os.path.exists(caminho_registro)
    with open(caminho_registro, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CABECALHO_REGISTRO)
        if not existe:
            w.writeheader()
        w.writerow(linha)
    return linha


def _formatar_planilha(ws):
    """Deixa a planilha apresentavel para um gestor: cabecalho em negrito e
    congelado, e colunas de dinheiro formatadas como R$. Cosmetico — se falhar,
    nao atrapalha o registro."""
    try:
        ultima = chr(ord("A") + len(CABECALHO_REGISTRO) - 1)
        ws.format(f"A1:{ultima}1", {"textFormat": {"bold": True},
                  "backgroundColor": {"red": 0.94, "green": 0.94, "blue": 0.96}})
        ws.freeze(rows=1)
        brl = {"numberFormat": {"type": "CURRENCY", "pattern": '"R$" #,##0'}}
        for campo in ("margem_vencedora", "impacto_anual_estimado"):
            if campo in CABECALHO_REGISTRO:
                col = chr(ord("A") + CABECALHO_REGISTRO.index(campo))
                ws.format(f"{col}2:{col}1000", brl)
    except Exception:
        pass


def sincronizar_sheets(linha, spreadsheet_id, aba="Testes", creds_path=None):
    """
    Escreve a MESMA linha do registro numa planilha do Google Sheets, via API.

    Autenticacao por Service Account (padrao para automacao servidor-a-servidor):
      - a credencial (JSON) vem de --creds ou da env GOOGLE_APPLICATION_CREDENTIALS;
      - a credencial NUNCA vai para o git (esta no .gitignore).
    Import preguicoso: se gspread nao estiver instalado, o resto do script roda
    normalmente (o CSV ja foi gravado) e so avisa que pulou o Sheets.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("  (Sheets: gspread nao instalado — pulei. Rode: pip install gspread google-auth)")
        return False

    creds_path = creds_path or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    if not os.path.exists(creds_path):
        print(f"  (Sheets: credencial nao encontrada em '{creds_path}' — pulei. Veja o README.)")
        return False

    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        planilha = gspread.authorize(creds).open_by_key(spreadsheet_id)
        try:
            ws = planilha.worksheet(aba)
        except gspread.WorksheetNotFound:
            ws = planilha.add_worksheet(title=aba, rows=1000, cols=len(CABECALHO_REGISTRO))
        existentes = ws.get_all_values()
        tem_header = bool(existentes) and existentes[0][:len(CABECALHO_REGISTRO)] == CABECALHO_REGISTRO
        if not tem_header:                               # garante o cabecalho no topo
            ws.insert_row(CABECALHO_REGISTRO, index=1)
            _formatar_planilha(ws)                       # negrito, congela, colunas R$
        ws.append_row([str(linha[c]) for c in CABECALHO_REGISTRO],
                      value_input_option="USER_ENTERED")
        print("  -> Google Sheets atualizado.")
        return True
    except Exception as e:
        print(f"  (Sheets: falhou ({e.__class__.__name__}) — o registro em CSV continua valendo.)")
        return False


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
DATA_HOJE = datetime.date.today().isoformat()


def main():
    ap = argparse.ArgumentParser(description="Analisa um teste A/B de cashback e decide qual variante escalar.")
    ap.add_argument("csv", help="Caminho do CSV do teste A/B")
    ap.add_argument("--nome", help="Nome do teste (default: nome do arquivo)")
    ap.add_argument("--descricao", default="", help="Descricao curta do teste")
    ap.add_argument("--registro", default="registro_testes.csv", help="Planilha de acompanhamento (CSV)")
    ap.add_argument("--saida", default="relatorios", help="Pasta dos relatorios .md")
    ap.add_argument("--sheets", help="ID da planilha do Google Sheets (opcional; escreve via API)")
    ap.add_argument("--aba", default="Testes", help="Nome da aba no Google Sheets")
    ap.add_argument("--creds", help="Caminho do JSON da Service Account (ou use a env GOOGLE_APPLICATION_CREDENTIALS)")
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        sys.exit(f"Arquivo nao encontrado: {args.csv}")

    linhas, ignoradas = carregar(args.csv)
    parceiro = next((l["parceiro"] for l in linhas if l["parceiro"]), "")
    nome = args.nome or os.path.splitext(os.path.basename(args.csv))[0]
    variantes = agregar(linhas)
    res = analisar(variantes)

    os.makedirs(args.saida, exist_ok=True)
    relatorio = gerar_relatorio(nome, args.descricao, parceiro, variantes, res)
    destino = os.path.join(args.saida, f"{slug(nome)}.md")
    with open(destino, "w", encoding="utf-8") as f:
        f.write(relatorio)
    linha = registrar(args.registro, nome, args.descricao, parceiro, variantes, res)
    if args.sheets:
        sincronizar_sheets(linha, args.sheets, aba=args.aba, creds_path=args.creds)

    # resumo curto no terminal (o LLM/pessoa le isso e comunica)
    v = res["vencedora"]
    print(f"[OK] {nome} | parceiro {parceiro or '-'} | {len(variantes)} variantes"
          + (f" | {ignoradas} linha(s) ignorada(s)" if ignoradas else ""))
    print(f"  -> DECISAO: escalar {res['vencedora_nome']} para 100% "
          f"(margem liquida {brl(v['margem_liquida'])}, cashback {v['cashback_pct_gmv']:.1f}% do GMV)")
    if res["teste"]:
        t = res["teste"]
        print(f"     significancia vs {res['vice_nome']}: p={t['p']:.4f} "
              f"({'significativo' if t['significativo'] else 'inconclusivo'})")
    imp = res["impacto"]
    if imp["tentadora_nome"] and imp["gap_periodo"] > 0:
        if imp["tem_armadilha"]:
            print(f"     impacto: decidir pela {imp['tentadora_nome']} (maior volume) custaria "
                  f"~{brl(imp['gap_anual'])}/ano de margem")
        else:
            print(f"     impacto: vencedora tambem e a de maior volume; supera a 2a colocada "
                  f"em ~{brl(imp['gap_anual'])}/ano")
    print(f"  -> relatorio: {destino}")
    print(f"  -> registrado em: {args.registro}")


if __name__ == "__main__":
    main()
