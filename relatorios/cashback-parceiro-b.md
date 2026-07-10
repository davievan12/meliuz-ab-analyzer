# Analise de Teste A/B de Cashback — Cashback Parceiro B

_Teste de % de cashback (3 variantes)_

**Parceiro:** Parceiro B  |  **Variantes:** 3  |  **Gerado em:** 2026-07-10

## Decisao
> **Escalar a Grupo 1 para 100% do trafego.** Ela entrega a maior margem liquida (R$ 286.570), com o cashback custando 4.0% do GMV. A diferenca de margem para a 2a colocada e **estatisticamente significativa** (p = 0.000), entao da pra escalar com confianca.

## Resultado por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Margem liquida | Margem/comprador | Cashback %GMV |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Grupo 1 🏆 | 61 | 7.990 | R$ 4.093.818 | R$ 450.321 | R$ 163.751 | **R$ 286.570** | R$ 36 | 4.0% |
| Grupo 2 | 61 | 5.452 | R$ 2.863.019 | R$ 314.935 | R$ 171.778 | **R$ 143.157** | R$ 26 | 6.0% |
| Grupo 3 | 61 | 5.029 | R$ 2.629.963 | R$ 289.290 | R$ 236.697 | **R$ 52.593** | R$ 10 | 9.0% |

## Significancia estatistica
Comparacao da **margem liquida diaria** entre Grupo 1 e Grupo 2 (teste de Welch, aproximacao normal — 30+ dias por variante):

- Diferenca media diaria: **R$ 2.351/dia** a favor de Grupo 1
- Intervalo de confianca 95%: [R$ 1.802, R$ 2.900]/dia
- p-valor: **0.0000** → diferenca real (significativa)

## Pontos de atencao
- ⚠️ Grupo 3 gasta 9.0% do GMV em cashback — custo alto, corrol a margem.

## Leitura de negocio
O padrao e claro: **mais cashback compra volume, mas destroi margem.** A Grupo 1 maximiza GMV/compradores, porem a Grupo 1 maximiza o lucro liquido do Meliuz. Como a pergunta e qual variante escalar para lucro, a resposta e a Grupo 1. Se o objetivo fosse crescimento de base a qualquer custo, ai o trade-off mudaria — mas isso e uma decisao estrategica, nao o que os dados de margem indicam.
