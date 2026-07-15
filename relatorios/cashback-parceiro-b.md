# Analise de Teste A/B de Cashback — Cashback Parceiro B

_Teste de % de cashback (3 variantes)_

**Parceiro:** Parceiro B  |  **Variantes:** 3  |  **Gerado em:** 2026-07-15

## Decisao
> **Escalar a Grupo 1 para 100% do trafego.** Ela entrega a maior margem liquida (R$ 286.570), com o cashback custando 4.0% do GMV. A diferenca de margem para a 2a colocada e **estatisticamente significativa** (p = 0.000), entao da pra escalar com confianca.

## Resultado por variante

| Variante | Dias | Compradores | GMV | Comissao | Cashback | Margem liquida | Margem/comprador | Cashback %GMV |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Grupo 1 🏆 | 61 | 7.990 | R$ 4.093.818 | R$ 450.321 | R$ 163.751 | **R$ 286.570** | R$ 36 | 4.0% |
| Grupo 2 | 61 | 5.452 | R$ 2.863.019 | R$ 314.935 | R$ 171.778 | **R$ 143.157** | R$ 26 | 6.0% |
| Grupo 3 | 61 | 5.029 | R$ 2.629.963 | R$ 289.290 | R$ 236.697 | **R$ 52.593** | R$ 10 | 9.0% |

## Margem liquida por variante
```
Grupo 1  ██████████████████████████ R$ 286.570
Grupo 2  █████████████              R$ 143.157
Grupo 3  █████                      R$ 52.593
```

## Impacto da decisao
A **Grupo 1** vence por margem **e** e a de maior volume — escolha segura. Ainda assim, vale dimensionar: ela supera a 2a colocada (**Grupo 2**) em **+R$ 143.413** no periodo de 61 dias, ~**R$ 858.127/ano**.

## Significancia estatistica
Comparacao da **margem liquida diaria** entre Grupo 1 e Grupo 2 (teste de Welch, aproximacao normal — 30+ dias por variante):

- Diferenca media diaria: **R$ 2.351/dia** a favor de Grupo 1
- Intervalo de confianca 95%: [R$ 1.802, R$ 2.900]/dia
- p-valor: **0.0000** → diferenca real (significativa)

## Pontos de atencao
- ⚠️ Grupo 3 gasta 9.0% do GMV em cashback — custo alto, corroi a margem.

## Leitura de negocio
Aqui nem volume o cashback comprou: a Grupo 3 (9.0% do GMV em cashback) teve 37% **menos** compradores que a Grupo 1 (que gasta so 4.0%). Mais cashback significou **menos volume e menos margem** ao mesmo tempo. E a **Grupo 1** ainda vence em volume: e a de maior GMV/compradores **e** a de maior margem. Sem trade-off — escalar para 100% e a escolha clara.
