import json
import warnings
from itertools import product

import numpy as np
import pandas as pd
from scipy.stats import jarque_bera
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResultsWrapper
from statsmodels.tsa.stattools import adfuller, kpss

from src.dados import ROOT


def especificacoes():
    candidatos = []
    for p, d, q in product(range(3), range(2), range(3)):
        candidatos.append({"familia": "ARIMA", "order": (p, d, q),
                           "seasonal_order": (0, 0, 0, 0), "trend": "c" if d == 0 else "n"})
    for p, q, P, D, Q in product(range(2), range(2), range(2), range(2), range(2)):
        if P == D == Q == 0:
            continue
        candidatos.append({"familia": "SARIMA", "order": (p, 0, q),
                           "seasonal_order": (P, D, Q, 12), "trend": "c" if D == 0 else "n"})
    for i, spec in enumerate(candidatos):
        spec["id"] = f"{spec['familia']}_{i:02d}"
    return candidatos


def ajustar(serie, spec) -> tuple[SARIMAXResultsWrapper, list[str]]:
    log = np.log(serie)
    centro = float(log.mean())
    modelo = SARIMAX(log - centro, order=tuple(spec["order"]),
                     seasonal_order=tuple(spec["seasonal_order"]), trend=spec["trend"],
                     enforce_stationarity=True, enforce_invertibility=True)
    with warnings.catch_warnings(record=True) as capturados:
        warnings.simplefilter("always")
        ajuste = modelo.fit(disp=False, maxiter=250)
    if not isinstance(ajuste, SARIMAXResultsWrapper):
        raise TypeError("Esperado resultado completo do SARIMAX, não apenas parâmetros.")
    avisos = sorted({str(w.message) for w in capturados})
    if not ajuste.mle_retvals.get("converged", False):
        raise RuntimeError("O otimizador não convergiu: " + "; ".join(avisos))
    if not np.isfinite(ajuste.aic):
        raise RuntimeError("AIC não finito.")
    setattr(ajuste, "centro_log", centro)
    return ajuste, avisos


def prever(ajuste, passos):
    previsao = ajuste.get_forecast(steps=passos)
    mu = previsao.predicted_mean + ajuste.centro_log
    variancia = previsao.var_pred_mean
    limites = previsao.conf_int(alpha=0.05) + ajuste.centro_log
    return pd.DataFrame({"media": np.exp(mu + variancia / 2), "mediana": np.exp(mu),
                         "inferior_95": np.exp(limites.iloc[:, 0]),
                         "superior_95": np.exp(limites.iloc[:, 1])})


def metricas(observado, previsto, treino):
    erro = np.asarray(observado) - np.asarray(previsto)
    escala = np.mean(np.abs(np.asarray(treino)[12:] - np.asarray(treino)[:-12]))
    return {"RMSE": float(np.sqrt(np.mean(erro ** 2))), "MAE": float(np.mean(np.abs(erro))),
            "MAPE": float(100 * np.mean(np.abs(erro) / np.asarray(observado))),
            "MASE": float(np.mean(np.abs(erro)) / escala)}


def testar_estacionariedade(serie):
    transformacoes = {"original": serie, "log": np.log(serie),
                       "diff_log_1": np.log(serie).diff().dropna(),
                       "diff_log_12": np.log(serie).diff(12).dropna()}
    linhas = []
    for nome, valores in transformacoes.items():
        with warnings.catch_warnings(record=True) as capturados:
            warnings.simplefilter("always")
            a = adfuller(valores, regression="c", autolag="AIC")
            k = kpss(valores, regression="c", nlags="auto")
        linhas.append({"serie": nome, "n": len(valores), "ADF": a[0], "ADF_p": a[1],
                       "ADF_lags": a[2], "KPSS": k[0], "KPSS_p": k[1],
                       "avisos": " | ".join(sorted({str(w.message) for w in capturados}))})
    return pd.DataFrame(linhas)


def selecionar(serie):
    treino = serie.loc[:"2008-12-01"]
    specs = especificacoes()
    busca = []
    for i, spec in enumerate(specs, 1):
        registro = {**spec, "d": spec["order"][1], "D": spec["seasonal_order"][1]}
        try:
            ajuste, avisos = ajustar(treino, spec)
            registro.update(AIC=ajuste.aic, BIC=ajuste.bic, convergiu=True, avisos=" | ".join(avisos))
        except (ValueError, RuntimeError, np.linalg.LinAlgError) as exc:
            registro.update(AIC=np.nan, BIC=np.nan, convergiu=False, avisos=str(exc))
        busca.append(registro)
        print(f"Busca {i}/{len(specs)}: {spec['id']} - convergiu={registro['convergiu']}", flush=True)
    busca = pd.DataFrame(busca)
    busca.to_csv(ROOT / "output/tables/busca_modelos.csv", index=False)
    elegiveis = busca.loc[busca["convergiu"].eq(True), :].sort_values("AIC")
    shortlist = elegiveis.groupby(["familia", "d", "D"], sort=False).head(2)
    validacao = []
    for codigo in shortlist.id:
        spec = next(s for s in specs if s["id"] == codigo)
        for ano in range(2009, 2014):
            historico = serie.loc[:f"{ano - 1}-12-01"]
            alvo = serie.loc[f"{ano}-01-01":f"{ano}-12-01"]
            try:
                ajuste, avisos = ajustar(historico, spec)
                prev = prever(ajuste, 12)
                valores = metricas(alvo, prev.media, historico)
                validacao.append({"id": codigo, "familia": spec["familia"], "ano": ano,
                                  **valores, "avisos": " | ".join(avisos), "convergiu": True})
            except (ValueError, RuntimeError, np.linalg.LinAlgError) as exc:
                validacao.append({"id": codigo, "familia": spec["familia"], "ano": ano,
                                  "RMSE": np.nan, "avisos": str(exc), "convergiu": False})
        print(f"Validação: {codigo}", flush=True)
    validacao = pd.DataFrame(validacao)
    validacao.to_csv(ROOT / "output/tables/validacao_rolling.csv", index=False)
    completos = validacao.groupby("id").convergiu.sum()
    ranking = validacao[validacao.id.isin(completos[completos == 5].index)].groupby(
        ["familia", "id"])[["RMSE", "MAE", "MAPE", "MASE"]].mean().reset_index().sort_values("RMSE")
    ranking.to_csv(ROOT / "output/tables/ranking_validacao.csv", index=False)
    selecionados = {}
    for familia in ["ARIMA", "SARIMA"]:
        grupo = ranking[ranking.familia == familia]
        if grupo.empty:
            raise RuntimeError(f"Nenhum {familia} convergiu em todas as janelas de validação.")
        codigo = grupo.iloc[0].id
        selecionados[familia] = next(s for s in specs if s["id"] == codigo)
    return selecionados, ranking


def avaliar_e_prever(serie, selecionados):
    treino, teste = serie.loc[:"2013-12-01"], serie.loc["2014-01-01":]
    tabela = pd.DataFrame({"observado": teste})
    futuro = pd.DataFrame(index=pd.date_range("2017-01-01", periods=12, freq="MS"))
    scores, diagnosticos, ajustes = [], [], {}
    for familia, spec in selecionados.items():
        ajuste, avisos = ajustar(treino, spec)
        ajustes[familia] = ajuste
        prev = prever(ajuste, len(teste))
        if not prev.index.equals(teste.index):
            raise ValueError("Datas do teste e da previsão não coincidem.")
        for coluna in prev:
            tabela[f"{familia}_{coluna}"] = prev[coluna]
        scores.append({"modelo": familia, **metricas(teste, prev.media, treino),
                       "cobertura_95": float(((teste >= prev.inferior_95) & (teste <= prev.superior_95)).mean() * 100),
                       "largura_media_95": float((prev.superior_95 - prev.inferior_95).mean())})
        descarte = max(24, ajuste.loglikelihood_burn)
        resid = pd.Series(ajuste.filter_results.standardized_forecasts_error[0, descarte:],
                          index=treino.index[descarte:]).dropna()
        graus = sum([spec["order"][0], spec["order"][2], spec["seasonal_order"][0], spec["seasonal_order"][2]])
        lb = acorr_ljungbox(resid, lags=[12, 24], model_df=graus, return_df=True)
        _, jb_p = jarque_bera(resid)
        diagnosticos.append({"modelo": familia, "LB12_p": lb.lb_pvalue.iloc[0],
                             "LB24_p": lb.lb_pvalue.iloc[1], "JB_p": jb_p,
                             "media_residuo": resid.mean(), "descarte_inicial": descarte,
                             "model_df": graus, "avisos_teste": " | ".join(avisos)})
        resid.to_csv(ROOT / f"output/tables/residuos_{familia.lower()}.csv", header=["residuo_padronizado"])
        (ROOT / f"output/tables/ajuste_{familia.lower()}_teste.txt").write_text(ajuste.summary().as_text())
        total, avisos_total = ajustar(serie, spec)
        diagnosticos[-1]["avisos_final"] = " | ".join(avisos_total)
        for coluna, valores in prever(total, 12).items():
            futuro[f"{familia}_{coluna}"] = valores
        (ROOT / f"output/tables/ajuste_{familia.lower()}_final.txt").write_text(total.summary().as_text())
    baselines = {"Ingênuo sazonal": np.tile(treino.iloc[-12:].values, 3),
                 "Média por mês": treino.groupby(treino.index.month).mean().reindex(teste.index.month).values}
    for nome, valores in baselines.items():
        tabela[nome] = valores
        scores.append({"modelo": nome, **metricas(teste, valores, treino),
                       "cobertura_95": np.nan, "largura_media_95": np.nan})
    scores = pd.DataFrame(scores)
    tabela.to_csv(ROOT / "output/tables/previsoes_teste.csv", index_label="data")
    futuro.to_csv(ROOT / "output/tables/previsoes_2017.csv", index_label="data")
    scores.to_csv(ROOT / "output/tables/metricas_teste.csv", index=False)
    diagnosticos = pd.DataFrame(diagnosticos)
    diagnosticos.to_csv(ROOT / "output/tables/diagnosticos.csv", index=False)
    return scores, tabela, futuro, diagnosticos


def salvar_resumo(serie, selecionados, ranking, scores, diagnosticos):
    mensal = serie.groupby(serie.index.month).mean()
    resumo = {"n": len(serie), "inicio": str(serie.index.min().date()), "fim": str(serie.index.max().date()),
              "media": float(serie.mean()), "mediana": float(serie.median()), "desvio": float(serie.std()),
              "minimo": float(serie.min()), "data_minimo": str(serie.idxmin().date()),
              "maximo": float(serie.max()), "data_maximo": str(serie.idxmax().date()),
              "mes_maior_media": int(mensal.idxmax()), "mes_menor_media": int(mensal.idxmin()),
              "selecionados": selecionados, "ranking_validacao": ranking.to_dict(orient="records"),
              "metricas_teste": scores.replace({np.nan: None}).to_dict(orient="records"),
              "diagnosticos": diagnosticos.to_dict(orient="records"),
              "media_ate_2013": float(serie.loc[:"2013"].mean()),
              "media_2014_2016": float(serie.loc["2014":].mean()),
              "protocolo": {"treino_inicial": "1931-2008", "validacao": "2009-2013, cinco origens anuais de 12 meses",
                            "teste": "2014-2016, origem única em dez/2013, horizonte 36 meses",
                            "futuro": "2017, origem dez/2016, projeção histórica sem observações para conferir"}}
    (ROOT / "output/resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2))
    return resumo
