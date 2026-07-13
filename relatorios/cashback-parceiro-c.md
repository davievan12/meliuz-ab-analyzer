# Analise de Teste A/B de Cashback — Cashback Parceiro C

_Teste de % de cashback (2 variantes)_

**Parceiro:** Parceiro C  |  **Variantes:** 2  |  **Gerado em:** 2026-07-13

## Decisao
> **Escalar a Grupo 1 para 100% do trafego.** Ela entrega a maior margem liquida (R$ 34.769), com o cashback custando 5.0% do GMV. A diferenca de margem para a 2a colocada e **estatisticamente significativa** (p = 0.000), entao da pra escalar com confianca.

## Resultado por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Margem liquida | Margem/comprador | Cashback %GMV |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Grupo 1 🏆 | 45 | 4.549 | R$ 1.738.460 | R$ 121.693 | R$ 86.924 | **R$ 34.769** | R$ 8 | 5.0% |
| Grupo 2 | 45 | 4.522 | R$ 1.685.235 | R$ 117.967 | R$ 117.967 | **R$ 0** | R$ 0 | 7.0% |

## Margem liquida por variante
```
Grupo 1  ██████████████████████████ R$ 34.769
Grupo 2                             R$ 0
```

## Impacto da decisao
A **Grupo 1** vence por margem **e** e a de maior volume — escolha segura. Ainda assim, vale dimensionar: ela supera a 2a colocada (**Grupo 2**) em **+R$ 34.769** no periodo de 45 dias, ~**R$ 282.015/ano**.

## Significancia estatistica
Comparacao da **margem liquida diaria** entre Grupo 1 e Grupo 2 (teste de Welch, aproximacao normal — 30+ dias por variante):

- Diferenca media diaria: **R$ 773/dia** a favor de Grupo 1
- Intervalo de confianca 95%: [R$ 714, R$ 831]/dia
- p-valor: **0.0000** → diferenca real (significativa)

## Pontos de atencao
- ⚠️ Grupo 2 tem margem liquida <= 0 (R$ 0): praticamente todo o comissionamento vira cashback.

## Leitura de negocio
O padrao e claro: **mais cashback compra volume, mas destroi margem.** A Grupo 1 maximiza GMV/compradores, porem a Grupo 1 maximiza o lucro liquido do Meliuz. Como a pergunta e qual variante escalar para lucro, a resposta e a Grupo 1. Se o objetivo fosse crescimento de base a qualquer custo, ai o trade-off mudaria — mas isso e uma decisao estrategica, nao o que os dados de margem indicam.
