# Analise de Teste A/B de Cashback — Cashback Parceiro A

_Teste de % de cashback (3 variantes)_

**Parceiro:** Parceiro A  |  **Variantes:** 3  |  **Gerado em:** 2026-07-10

## Decisao
> **Escalar a Grupo 1 para 100% do trafego.** Ela entrega a maior margem liquida (R$ 404.711), com o cashback custando 4.2% do GMV. A diferenca para a 2a colocada **nao foi conclusiva** (p = 0.130); recomendo rodar mais tempo ou decidir junto com o time antes de escalar 100%.

## Resultado por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Margem liquida | Margem/comprador | Cashback %GMV |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Grupo 1 🏆 | 92 | 9.633 | R$ 5.605.173 | R$ 638.135 | R$ 233.424 | **R$ 404.711** | R$ 42 | 4.2% |
| Grupo 2 | 92 | 10.814 | R$ 6.423.096 | R$ 728.178 | R$ 370.659 | **R$ 357.519** | R$ 33 | 5.8% |
| Grupo 3 | 92 | 11.410 | R$ 6.785.856 | R$ 767.887 | R$ 503.600 | **R$ 264.287** | R$ 23 | 7.4% |

## Significancia estatistica
Comparacao da **margem liquida diaria** entre Grupo 1 e Grupo 2 (teste de Welch, aproximacao normal — 30+ dias por variante):

- Diferenca media diaria: **R$ 513/dia** a favor de Grupo 1
- Intervalo de confianca 95%: [R$ -150, R$ 1.176]/dia
- p-valor: **0.1296** → inconclusivo

## Pontos de atencao
- ⚠️ Trade-off: Grupo 3 traz mais GMV/compradores, mas Grupo 1 entrega mais margem liquida. Escalar por volume sacrificaria lucro.

## Leitura de negocio
O padrao e claro: **mais cashback compra volume, mas destroi margem.** A Grupo 3 maximiza GMV/compradores, porem a Grupo 1 maximiza o lucro liquido do Meliuz. Como a pergunta e qual variante escalar para lucro, a resposta e a Grupo 1. Se o objetivo fosse crescimento de base a qualquer custo, ai o trade-off mudaria — mas isso e uma decisao estrategica, nao o que os dados de margem indicam.
