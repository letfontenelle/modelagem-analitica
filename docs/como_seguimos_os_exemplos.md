# Como seguimos os exemplos fornecidos

O projeto mantém a sequência didática dos exemplos: organização mensal, inspeção gráfica, estacionariedade, transformações, ACF/PACF, ARIMA, SARIMA, diagnóstico e previsão. Os exemplos são materiais de orientação, não instruções que substituem o pedido do projeto. Os resultados de Sobradinho neles apresentados não são resultados de Ilha Solteira.

A correspondência abaixo usa a numeração física dos PDFs anexados. `EXEMPLO.pdf` tem 37 páginas; `EXEMPLO_01.pdf` tem somente cinco páginas físicas, apesar dos rodapés indicarem “1/20” a “5/20”. Não presumimos acesso às páginas restantes.

| Material e páginas | O que aparece no exemplo | Implementação e adaptação em Ilha Solteira |
|---|---|---|
| EXEMPLO, 1–2 | Instalação no Colab, leitura Excel, índice de datas, série e boxplot anual | Notebook §§1–3. Extração do PDF entregue, CSV auditável e índice mensal `MS`; ambiente local reproduzível, sem autenticação do Google Drive. |
| EXEMPLO_01, 1–2 | Tabela larga com ANO, JAN–DEZ e MED; laços para montar a série; exclusão de MED e das três últimas linhas | Notebook §1 e `src/dados.py`. Unimos as páginas JAN–SET e OUT–DEZ e preservamos os 1.032 meses. Não há coluna MED no nosso CSV. Não excluímos três linhas arbitrariamente nem transferimos regras de outro arquivo. |
| EXEMPLO_01, 3 | Série temporal | Notebook §2, com as divisões de treino, validação e teste visíveis. |
| EXEMPLO, 3 | Boxplot mensal e ADF | Notebook §§3 e 5. Boxplots, ADF e KPSS calculados no treino inicial. Os testes têm hipóteses nulas diferentes; divergências são reportadas. |
| EXEMPLO, 3–4; EXEMPLO_01, 4–5 | Decomposição aditiva/multiplicativa; parte do código está cortada no segundo PDF | Notebook §4. Exibimos as duas decomposições com `period=12`, que corresponde ao ciclo anual de uma série mensal. Corrigimos `period=int(len(serie)/2)`, que produziria 516 meses no exemplo, e evitamos o erro de nome `esult_add`/`result_add`. |
| EXEMPLO, 5–7 | Autocorrelação, log, primeira diferença, ACF e PACF | Notebook §§4–6. Mantemos log e diferenças, acrescentamos diferença sazonal e mostramos até 36 defasagens, com método PACF explícito. |
| EXEMPLO, 8–19 | Diferenças comuns de primeira e segunda ordem e escolha de ARIMA(1,1,2) | Notebook §§5–8. Corrigimos a interpretação: d é a ordem de diferenciação, q é a ordem MA. As ordens do exemplo não são copiadas para outro conjunto de dados; são escolhidas em uma grade limitada com validação temporal. |
| EXEMPLO, 19–21 | Ajuste, resumo dos parâmetros, resíduos e predição dentro da amostra | Notebook §§9 e 12. Tabelas de parâmetros e quatro painéis de resíduos; métricas principais vêm de previsão fora da amostra. |
| EXEMPLO, 22–24 | Corte treino/teste por posição (900/132), previsão e tentativa de faixa de 95% | Notebook §§2 e 10. Corte por datas, teste 2014–2016 com 36 meses. Usamos `ajuste.get_forecast(...).conf_int(alpha=0.05)`; `ajuste.conf_int()` fornece intervalos dos coeficientes, não de observações futuras. |
| EXEMPLO, 25–26 | Função de erros (MAPE, MAE, RMSE etc.) | Notebook §11 e `metricas()`. Métricas sobre vetores temporalmente alinhados, MAPE multiplicado por 100 e identificado como percentual, mais MASE e dois baselines. Não reutilizamos variáveis globais desalinhadas na ACF de erro. |
| EXEMPLO, 26–29 | Busca `auto_arima` não sazonal por AIC em toda a série | Notebook §§7–8. Grade explícita em statsmodels, AIC apenas no treino inicial e dentro de grupos com mesmos d,D. Finalistas passam por cinco origens anuais. A grade é pequena; não se afirma ótimo global. |
| EXEMPLO, 30–33 | Diferença sazonal, SARIMA com m=12, d=1 e D=1 impostos | Notebook §§5–8. Período 12 preservado. SARIMA explora D=0 e D=1, com d=0 na grade reduzida. Não impomos simultaneamente as duas diferenças nem copiamos ordens de Sobradinho. |
| EXEMPLO, 28–29 e 32–33 | Previsão final com datas construídas manualmente | Notebook §13. Datas produzidas a partir do índice mensal: jan–dez/2017 após dez/2016. A projeção é histórica e não tem observações futuras disponíveis para validação. |
| EXEMPLO, 33–37 | Proposta de SARIMAX e índice sazonal tratado como exógeno | Escopo limitado aos ARIMA/SARIMA pedidos. O trecho ajusta sem variável exógena e tenta passá-la apenas na previsão, com `.reshape` sem chamada. Não reproduzimos esse erro nem inventamos covariáveis hidrológicas. O nome da classe `SARIMAX` não significa que o projeto usou variáveis exógenas. |

## Complementos que tornam a comparação verificável

1. **Rastreabilidade:** o CSV preserva página e linha de cada valor; o notebook confronta os 1.032 valores com uma nova extração do PDF. O JSON de metadados registra SHA-256 da fonte. A unidade e o tipo de vazão não são confirmados pela fonte; m³/s é apenas uma hipótese.
2. **Separação temporal:** a busca usa 1931–2008; a validação prevê, sucessivamente, 2009, 2010, 2011, 2012 e 2013. O teste de 2014–2016 tem uma única origem em dezembro de 2013, sem reestimação mensal.
3. **Log e retorno à unidade original:** o ajuste comprime a escala dos picos. A previsão média usa `exp(mu + variancia/2)` e a mediana usa `exp(mu)`; os limites são quantis transformados. A centralização do log dentro de cada treino é revertida antes dessas operações e não usa o futuro.
4. **Incerteza explícita:** faixas de 95% são intervalos preditivos pontuais, condicionais ao modelo. A cobertura empírica e a largura média são mostradas junto com os erros. Não são intervalos dos parâmetros nem garantia sobre toda a trajetória.
5. **Diagnósticos verificáveis:** testes Ljung–Box em 12/24 defasagens, Jarque–Bera, ACF residual, histograma, série residual e Q–Q plot. Avisos de ajuste e falhas de convergência são registrados e candidatos inválidos não são selecionados.
6. **Reprodução:** `scripts/analisar.py` executa a busca completa. O notebook usa a seleção salva por padrão, mas reajusta os modelos e recalcula previsões, métricas e diagnósticos. `REFAZER_BUSCA=True` também repete a seleção. As células finais comparam numericamente os cálculos com os CSVs.

## Materiais indicados pela disciplina

- [DigitalOcean: guia de previsão ARIMA em Python](https://www.digitalocean.com/community/tutorials/a-guide-to-time-series-forecasting-with-arima-in-python-3).
- [GeeksforGeeks: ARIMA para séries temporais](https://www.geeksforgeeks.org/python-arima-model-for-time-series-forecasting/amp/).
- [Aarshay Jain: notebook Time Series AirPassenger](https://github.com/aarshayj/analytics_vidhya/blob/master/Articles/Time_Series_Analysis/Time_Series_AirPassenger.ipynb).

Esses links são referências de orientação fornecidas pelo usuário. As APIs e os resultados executados no projeto estão documentados no notebook e nas dependências fixadas; versões antigas e parâmetros específicos de passageiros ou de outro reservatório não foram transferidos sem adaptação.
