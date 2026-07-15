# Analise de Teste A/B de Cashback — Cashback Parceiro C

_Teste de % de cashback (2 variantes)_

**Parceiro:** Parceiro C  |  **Variantes:** 2  |  **Gerado em:** 2026-07-15

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
Comparacao da **margem liquida diaria** entre Grupo 1 e Grupo 2. **Teste t pareado por dia**, sobre 45 dias. Como as variantes rodaram nos mesmos dias, comparo a margem dia a dia e removo o ruido de demanda que atinge todas por igual.

- Diferenca media diaria: **R$ 773/dia** a favor de Grupo 1
- Intervalo de confianca 95%: [R$ 714, R$ 831]/dia
- p-valor: **0.0000** (diferenca significativa)

## Pontos de atencao
- ⚠️ Grupo 2 tem margem liquida <= 0 (R$ 0): praticamente todo o comissionamento vira cashback.

## Leitura de negocio
O cashback maior **nao moveu o volume**: a Grupo 2 e a Grupo 1 tiveram praticamente os mesmos compradores, mas a Grupo 2 gastou 7.0% do GMV em cashback contra 5.0% — puro custo, sem retorno em volume. E a **Grupo 1** ainda vence em volume: e a de maior GMV/compradores **e** a de maior margem. Sem trade-off — escalar para 100% e a escolha clara.
