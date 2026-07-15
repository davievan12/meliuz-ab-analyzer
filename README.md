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

Nos três, **o Grupo 1 (menor cashback) foi o mais lucrativo** — mas por caminhos
diferentes: no Parceiro A o cashback maior trouxe volume às custas da margem
(trade-off clássico); em B e C o cashback maior nem volume trouxe — só encareceu.
É por isso que a leitura de negócio de cada relatório é gerada a partir dos dados
do próprio teste, não de um texto fixo. Os relatórios completos estão em
[`relatorios/`](relatorios/).

## Decisões de projeto (meu raciocínio)

Escolhas que fiz de propósito, e o porquê:

- **Código para a conta, IA para a linguagem.** Não deixo o LLM somar 276 linhas de
  dinheiro — modelo erra número e não é auditável. Toda a agregação e a estatística
  ficam num script determinístico; a IA entra só para interpretar e comunicar. Assim
  eu tenho confiabilidade e, ao mesmo tempo, a interface em linguagem natural.

- **Decidir por margem líquida, não por GMV.** O instinto é escalar a variante que
  mais vende. Mas mais cashback quase sempre traz mais vendas *e* come a margem. Como
  a pergunta é qual dá mais lucro ao escalar, a métrica certa é `comissão − cashback`.
  No Parceiro A isso inverteu a "resposta óbvia" (a de maior GMV era a de pior margem);
  em B e C a de menor cashback já ganhava em tudo.

- **Medir se a diferença é real.** Margem maior no total pode ser sorte de alguns dias.
  Por isso comparo a margem diária da 1ª com a 2ª colocada (teste de Welch). No Parceiro
  A deu inconclusivo (p≈0,13) — e preferi dizer isso e sugerir rodar mais tempo a fingir
  certeza. Decisão honesta vale mais que decisão bonita.

- **Botar R$ no erro.** "Escale o Grupo 1" é fraco. "Escalar errado custaria ~R$ 557 mil/ano"
  fala a língua de quem decide. Por isso o relatório quantifica o custo da decisão errada.

- **Reutilizável de verdade.** Nada de valor chumbado: o script acha as colunas por nome,
  trata o "R$" e funciona com 2 ou 3 variantes sem tocar no código. E escolhi **zero
  dependências no núcleo** para qualquer pessoa do time rodar com um `python3`.

- **Cuidado com dado confidencial.** Como o teste é confidencial, os datasets do processo
  **não** vão para o repositório público — a ferramenta roda em qualquer CSV no mesmo
  schema. Só o código, os relatórios e o resumo ficam públicos.

- **O que eu faria com mais tempo.** Gráficos em imagem, checagem de sazonalidade (dia da
  semana) e um resumo executivo consolidado de vários testes na mesma planilha.

## Planilha de acompanhamento
Cada análise adiciona uma linha em `registro_testes.csv` (nome, parceiro,
variante vencedora, margem, significância, decisão) — 1 teste por linha.

📊 **Google Sheets (acesso de leitura):** https://docs.google.com/spreadsheets/d/1eoMqzp3N-elZyPeOyiKGH0h8sqry5h_3yPHUMtkSL_Y/edit?usp=sharing

### Escrever direto no Google Sheets (via API)
A solução também escreve o registro **diretamente numa planilha do Google Sheets**,
usando a **Google Sheets API** com uma **Service Account** (autenticação
servidor-a-servidor, sem interação humana — o padrão para automação):

```bash
pip install -r requirements.txt        # gspread + google-auth
export GOOGLE_APPLICATION_CREDENTIALS=credentials.json   # JSON da service account (gitignored)
python3 analyze.py datasets/dataset_01_parceiroA.csv --nome "Cashback Parceiro A" \
        --sheets <ID_DA_PLANILHA>
```

Setup (uma vez):
1. No [Google Cloud Console](https://console.cloud.google.com), crie um projeto e
   **habilite a Google Sheets API**.
2. Crie uma **Service Account** e gere uma **chave JSON**; salve como `credentials.json`
   (ela **não** vai para o git — está no `.gitignore`).
3. Crie a planilha no Google Sheets e **compartilhe com o e-mail da service account**
   (aquele `...@...iam.gserviceaccount.com`) como *Editor*.
4. Deixe a planilha com **acesso de leitura público** (para o link do entregável) e
   pegue o `<ID_DA_PLANILHA>` da URL.

> A credencial fica só na máquina de quem roda — nada de segredo no repositório.
> Se `gspread`/credencial não estiverem presentes, o script grava só o CSV e avisa.

## Estrutura
```
analyze.py              # engine de análise (Python, zero dependências)
CLAUDE.md               # instruções para a IA orquestrar (AI-native)
prompts/analisar-teste.md  # prompt para IAs sem execução de código
datasets/               # (não versionado — confidencial; coloque aqui os CSVs para rodar)
relatorios/             # relatórios gerados (1 por teste)
registro_testes.csv     # planilha de acompanhamento (1 linha por teste)
```

---
Feito por Davi Evangelista · [github.com/davievan12](https://github.com/davievan12) · [davievan12.github.io](https://davievan12.github.io)
