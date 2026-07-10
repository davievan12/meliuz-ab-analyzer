# Instruções para a IA — Analisador de Testes A/B de Cashback

Este repositório é uma ferramenta **AI-native**: uma pessoa do time de Growth abre
uma ferramenta de IA (Claude Code, Cursor, etc.), pede em linguagem natural para
analisar um teste A/B novo e recebe de volta a análise e a recomendação.

## Divisão de responsabilidades (importante)
- **A conta fica no `analyze.py`** (Python, determinístico). Nunca calcule margem,
  somas ou estatística "de cabeça" — número de dinheiro não pode ser achismo.
- **A IA (você) orquestra e comunica**: roda o script, lê o relatório gerado e
  explica a decisão em linguagem natural para a pessoa.

## O que fazer quando pedirem para analisar um teste
1. Descubra o caminho do CSV que a pessoa indicou.
2. Rode:
   ```bash
   python3 analyze.py <caminho_do_csv> --nome "<nome do teste>" --descricao "<descricao curta>"
   ```
   (não precisa passar mais nada — ele detecta parceiro e nº de variantes sozinho.)
3. Leia o relatório gerado em `relatorios/<slug>.md`.
4. Responda à pessoa, em português claro, com:
   - a **decisão** (qual variante escalar para 100%);
   - o **porquê** (margem líquida vs volume; o trade-off);
   - a **ressalva estatística** (se a diferença foi significativa ou não);
   - qualquer **alerta** que o script tenha levantado.
5. Confirme que o teste foi registrado em `registro_testes.csv` (1 linha por teste).
   Se um Google Sheets estiver conectado, adicione a mesma linha lá também
   (colunas em `CABECALHO_REGISTRO` do `analyze.py`).

## Metodologia (para explicar se perguntarem)
- **Métrica de decisão:** margem líquida do Méliuz = `comissão − cashback`.
- Num A/B com split equilibrado, a variante de **maior margem líquida** é a que
  mais dá lucro ao escalar. Mais cashback costuma trazer volume, mas corrói margem.
- **Significância:** teste de Welch (aproximação normal, pois há 30+ dias por
  variante) sobre a margem líquida diária, comparando a 1ª com a 2ª colocada.
- Se a diferença **não** for significativa, não afirme vitória: recomende rodar
  mais tempo ou decidir com o time.

## Não faça
- Não recomende a variante de maior GMV/vendas por reflexo — quase sempre é a de
  maior cashback e **pior** margem. Sempre olhe a margem líquida.
- Não altere o `analyze.py` para um teste específico. Ele tem que servir para
  qualquer teste só apontando o arquivo.
