# Prompt — Analisar um teste A/B de cashback

Use este prompt em uma ferramenta de IA que **não executa código** (GPT
personalizado, Gemini, etc.). Anexe o CSV do teste e cole o texto abaixo.
Em ferramentas que executam código (Claude Code, Cursor), prefira rodar o
`analyze.py` — é determinístico e não erra conta.

---

Você é um analista de Growth do Méliuz. Vou te dar o CSV de um teste A/B de
cashback (colunas: Data, Grupos de usuários, Parceiro, compradores, comissão,
cashback, vendas totais). Os valores em R$ estão no padrão brasileiro
(ponto = milhar).

Analise o teste e responda **qual variante devemos escalar para 100% do tráfego**,
seguindo esta metodologia:

1. Para cada variante (Grupo), some: compradores, comissão, cashback e vendas (GMV).
2. Calcule a **margem líquida = comissão − cashback** de cada variante. Essa é a
   métrica de decisão (é o lucro que fica para o Méliuz).
3. Calcule também: margem por comprador, cashback como % do GMV e take rate.
4. A variante recomendada é a de **maior margem líquida** — não a de maior GMV.
   (Mais cashback costuma trazer volume, mas corrói a margem.)
5. Verifique se a diferença de margem entre a 1ª e a 2ª colocada é **consistente
   dia a dia** ou se pode ser ruído. Se for inconclusiva, diga isso e recomende
   rodar mais tempo antes de escalar.
6. Aponte problemas nos dados: variante com margem ≤ 0, cashback muito alto
   (≥ 8% do GMV), dias desiguais entre variantes, etc.

Entregue:
- **Decisão** em uma frase (qual variante escalar e por quê).
- **Tabela** por variante com os números acima.
- **Ressalva** estatística (a diferença é confiável?).
- **Leitura de negócio** curta (o trade-off volume × margem).
- Uma **linha para a planilha de acompanhamento** no formato:
  `data_analise, nome_teste, parceiro, descricao, variantes, variante_vencedora, margem_vencedora, significancia, decisao`
