# Analisador de Testes A/B de Cashback — Méliuz

Ferramenta **reutilizável e AI-native** que recebe o CSV de um teste A/B de
cashback e devolve uma **análise completa + uma decisão acionável**: *qual
variante de cashback escalar para 100% do tráfego?*

Hoje essa análise leva de 2 a 4 horas e depende de quem está olhando. Aqui,
qualquer pessoa do time roda em segundos, para qualquer teste, com resultado
consistente.

## A ideia de arquitetura (o ponto central)

> **Código faz a conta. IA interpreta e comunica.**

- **`analyze.py`** (Python puro, **zero dependências**) faz o trabalho que não pode
  errar: parsing dos valores, agregação por variante e teste de significância.
  Número de dinheiro não pode ser "achismo de LLM".
- **A camada de IA** (`CLAUDE.md` + `prompts/`) é a interface: a pessoa pede em
  linguagem natural, a IA roda o script, lê o relatório e explica a decisão.

Assim junto o melhor dos dois: a **confiabilidade** de um script determinístico com
a **facilidade** de conversar em linguagem natural. É o que faz a solução ser
"AI-native" de verdade, e não "joguei o CSV no ChatGPT".

## Como usar

### Modo AI-native (recomendado)
Abra o repositório no **Claude Code** (ou Cursor) e peça em português:

> "Analisa esse teste A/B: `datasets/dataset_01_parceiroA.csv`"

A IA lê o `CLAUDE.md`, roda o script, e te devolve a decisão + o porquê.
Para ferramentas que não executam código (GPT personalizado, Gemini), use o
prompt em [`prompts/analisar-teste.md`](prompts/analisar-teste.md).

### Modo direto (linha de comando)
```bash
python3 analyze.py <arquivo.csv> --nome "Nome do teste" --descricao "descricao curta"
```
Exemplo:
```bash
python3 analyze.py datasets/dataset_01_parceiroA.csv --nome "Cashback Parceiro A"
```
Roda em **qualquer** teste sem mudar o código — detecta o parceiro e o número de
variantes (2, 3, ...) sozinho. Gera o relatório em `relatorios/` e registra o
teste em `registro_testes.csv`.

## Metodologia

| Passo | O que faz |
|---|---|
| **Métrica de decisão** | Margem líquida = `comissão − cashback` (o lucro do Méliuz). |
| **Regra** | Escalar a variante de **maior margem líquida** — não a de maior GMV. |
| **Significância** | Teste de Welch (aproximação normal, 30+ dias por variante) na margem diária: a 1ª é de fato melhor que a 2ª, ou é ruído? |
| **Olho crítico** | Sinaliza margem ≤ 0, cashback alto (≥ 8% do GMV), split desigual e o trade-off volume × margem. |

**Por que margem e não GMV?** Mais cashback quase sempre traz mais vendas — e um
analista desatento escalaria a variante de maior GMV. Mas essa costuma ser a de
**pior margem**: o cashback come o lucro. A decisão certa maximiza o que sobra
para o Méliuz.

## Resultado nos 3 datasets do case

| Parceiro | Variantes | Decisão | Observação |
|---|--:|---|---|
| A | 3 | Escalar **Grupo 1** | Maior margem, mas diferença vs Grupo 2 **inconclusiva** (p≈0,13) — rodar mais tempo. |
| B | 3 | Escalar **Grupo 1** | Vitória **significativa** (p<0,001). |
| C | 2 | Escalar **Grupo 1** | Grupo 2 tem margem ~zero (dá todo o comissionamento em cashback). |

Nos três, **mais cashback trouxe volume mas destruiu margem** — o Grupo 1 (menor
cashback) foi o mais lucrativo. Os relatórios completos estão em [`relatorios/`](relatorios/).

## Planilha de acompanhamento
Cada análise adiciona uma linha em `registro_testes.csv` (nome, parceiro,
variante vencedora, margem, significância, decisão).

📊 **Google Sheets (acesso de leitura):** _<colar o link aqui>_

## Estrutura
```
analyze.py              # engine de análise (Python, zero dependências)
CLAUDE.md               # instruções para a IA orquestrar (AI-native)
prompts/analisar-teste.md  # prompt para IAs sem execução de código
datasets/               # os 3 CSVs do case
relatorios/             # relatórios gerados (1 por teste)
registro_testes.csv     # planilha de acompanhamento (1 linha por teste)
```

---
Feito por Davi Evangelista · [github.com/davievan12](https://github.com/davievan12) · [davievan12.github.io](https://davievan12.github.io)
