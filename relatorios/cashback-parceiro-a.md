# Analise de Teste A/B de Cashback — Cashback Parceiro A

_Teste de % de cashback (3 variantes)_

**Parceiro:** Parceiro A  |  **Variantes:** 3  |  **Gerado em:** 2026-07-15

## Decisao
> **Escalar a Grupo 1 para 100% do trafego.** Ela entrega a maior margem liquida (R$ 404.711), com o cashback custando 4.2% do GMV. A diferenca de margem para a 2a colocada e **estatisticamente significativa** (p = 0.000), entao da pra escalar com confianca.

## Resultado por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Margem liquida | Margem/comprador | Cashback %GMV |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Grupo 1 🏆 | 92 | 9.633 | R$ 5.605.173 | R$ 638.135 | R$ 233.424 | **R$ 404.711** | R$ 42 | 4.2% |
| Grupo 2 | 92 | 10.814 | R$ 6.423.096 | R$ 728.178 | R$ 370.659 | **R$ 357.519** | R$ 33 | 5.8% |
| Grupo 3 | 92 | 11.410 | R$ 6.785.856 | R$ 767.887 | R$ 503.600 | **R$ 264.287** | R$ 23 | 7.4% |

## Margem liquida por variante
```
Grupo 1  ██████████████████████████ R$ 404.711
Grupo 2  ███████████████████████    R$ 357.519
Grupo 3  █████████████████          R$ 264.287
```

## Impacto da decisao
Escalar a **Grupo 1** em vez da **Grupo 3** (a de maior volume — a escolha instintiva) representa **+R$ 140.424 de margem** no periodo de 92 dias, o equivalente a cerca de **R$ 557.117/ano**. Esse e o custo, em dinheiro, de decidir pela variante errada.

## Significancia estatistica
Comparacao da **margem liquida diaria** entre Grupo 1 e Grupo 2. **Teste t pareado por dia**, sobre 92 dias. Como as variantes rodaram nos mesmos dias, comparo a margem dia a dia e removo o ruido de demanda que atinge todas por igual.

- Diferenca media diaria: **R$ 513/dia** a favor de Grupo 1
- Intervalo de confianca 95%: [R$ 285, R$ 741]/dia
- p-valor: **0.0000** (diferenca significativa)

## Pontos de atencao
- ⚠️ Trade-off: Grupo 3 traz mais GMV/compradores, mas Grupo 1 entrega mais margem liquida. Escalar por volume sacrificaria lucro.

## Leitura de negocio
Mais cashback **trouxe volume**: a Grupo 3 (7.4% do GMV em cashback) teve 18% mais compradores que a Grupo 1. Mas esse volume veio **as custas da margem** — o cashback extra custou mais do que a receita adicional que gerou. Ha um trade-off classico: a **Grupo 3** traz mais GMV/compradores, mas a **Grupo 1** entrega mais lucro liquido. Como a pergunta e qual variante da mais lucro ao escalar, a resposta e a **Grupo 1**; escalar por volume sacrificaria margem. Se o objetivo fosse crescer a base a qualquer custo, a decisao seria estrategica — mas nao e o que os dados de margem indicam.
