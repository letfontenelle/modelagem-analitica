import json
from pathlib import Path
from zipfile import ZipFile

import nbformat
import numpy as np
import pandas as pd
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def verificar():
    with pdfplumber.open(ROOT / "data/raw/ILHA_SOLTEIRA.pdf") as pdf:
        tabelas = [pagina.extract_tables()[0] for pagina in pdf.pages]
    registros = []
    for esquerda, direita in [(tabelas[0][2:], tabelas[1][2:]), (tabelas[2], tabelas[3])]:
        assert len(esquerda) == len(direita)
        for a, b in zip(esquerda, direita):
            registro = []
            for valor in a + b:
                assert isinstance(valor, str), "Célula vazia ou inválida no PDF original."
                registro.append(int(valor))
            registros.append(registro)
    valores_celulas = np.asarray(registros)[:, 1:].ravel()
    dados = pd.read_csv(ROOT / "data/processed/ilha_solteira_mensal.csv", parse_dates=["data"])
    np.testing.assert_array_equal(valores_celulas, dados.vazao.values)
    assert len(dados) == 1032
    assert pd.DatetimeIndex(dados.data).equals(pd.date_range("1931-01-01", "2016-12-01", freq="MS"))
    assert dados.vazao.gt(0).all() and not dados.isna().to_numpy().any()
    print("PASS: 1.032 valores conferidos por segunda extração, baseada nas células do PDF.")

    teste = pd.read_csv(ROOT / "output/tables/previsoes_teste.csv", parse_dates=["data"])
    futuro = pd.read_csv(ROOT / "output/tables/previsoes_2017.csv", parse_dates=["data"])
    scores = pd.read_csv(ROOT / "output/tables/metricas_teste.csv").set_index("modelo")
    for frame, inicio, fim in [(teste, "2014-01-01", "2016-12-01"), (futuro, "2017-01-01", "2017-12-01")]:
        assert pd.DatetimeIndex(frame.data).equals(pd.date_range(inicio, fim, freq="MS"))
        for modelo in ["ARIMA", "SARIMA"]:
            cols = [f"{modelo}_{c}" for c in ["media", "mediana", "inferior_95", "superior_95"]]
            assert np.isfinite(frame[cols].to_numpy()).all()
            assert (frame.loc[:, cols].to_numpy() > 0).all()
            assert (frame[f"{modelo}_inferior_95"] <= frame[f"{modelo}_mediana"]).all()
            assert (frame[f"{modelo}_mediana"] <= frame[f"{modelo}_superior_95"]).all()
            assert (frame[f"{modelo}_media"] >= frame[f"{modelo}_mediana"]).all()
    for modelo in scores.index:
        coluna = f"{modelo}_media" if modelo in ["ARIMA", "SARIMA"] else modelo
        erro = teste.observado - teste[coluna]
        np.testing.assert_allclose(np.sqrt(np.mean(erro**2)), scores.loc[modelo, "RMSE"])
        np.testing.assert_allclose(np.mean(np.abs(erro)), scores.loc[modelo, "MAE"])
        np.testing.assert_allclose(100*np.mean(np.abs(erro)/teste.observado), scores.loc[modelo, "MAPE"])
    for modelo in ["ARIMA", "SARIMA"]:
        cobertura = teste.observado.between(teste[f"{modelo}_inferior_95"], teste[f"{modelo}_superior_95"]).mean()*100
        np.testing.assert_allclose(cobertura, scores.loc[modelo, "cobertura_95"])
    validacao = pd.read_csv(ROOT / "output/tables/validacao_rolling.csv")
    assert set(validacao.ano) == set(range(2009, 2014))
    resumo = json.loads((ROOT / "output/resumo.json").read_text())
    ranking = pd.read_csv(ROOT / "output/tables/ranking_validacao.csv")
    for familia, spec in resumo["selecionados"].items():
        assert ranking.loc[ranking["familia"].eq(familia), :].sort_values("RMSE").iloc[0].id == spec["id"]
    print("PASS: datas, positividade, intervalos, métricas e seleção coincidem com os resultados publicados.")

    notebook = nbformat.read(ROOT / "notebooks/ilha_solteira.ipynb", as_version=4)
    nbformat.validate(notebook)
    celulas = [c for c in notebook.cells if c.cell_type == "code"]
    assert all(c.execution_count is not None for c in celulas)
    assert not any(o.output_type == "error" for c in celulas for o in c.outputs)
    print(f"PASS: notebook válido, {len(celulas)} células de código executadas, zero erros.")

    for nome in ["roteiro_ilha_solteira.pdf", "apresentacao_ilha_solteira.pdf"]:
        path = ROOT / "output/pdf" / nome
        assert path.is_file() and path.stat().st_size > 10000
        print(f"PASS: {nome}, {len(PdfReader(path).pages)} páginas.")
    with ZipFile(ROOT / "output/apresentacao_ilha_solteira.pptx") as pptx:
        nomes = pptx.namelist()
        import re
        slides = [n for n in nomes if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
        charts = [n for n in nomes if re.fullmatch(r"ppt/(slides/)?charts/chart\d+\.xml", n)]
        notes = [n for n in nomes if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)]
        assert len(slides) == len(notes) == 13 and len(charts) >= 7
        print(f"PASS: PPTX com {len(slides)} slides, {len(charts)} gráficos editáveis e {len(notes)} notas.")


if __name__ == "__main__":
    verificar()
