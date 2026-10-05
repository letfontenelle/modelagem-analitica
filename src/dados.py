"""Converte a tabela repartida em quatro páginas em uma série mensal auditável."""
import hashlib
import json
import re
from pathlib import Path

import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]


def extrair_pdf(caminho=ROOT / "data/raw/ILHA_SOLTEIRA.pdf"):
    """Une JAN-SET e OUT-DEZ por posição de linha, validando anos e contagens.

    O PDF não traz unidade, agência, nem definição de vazão natural/observada.
    Preservamos os inteiros como publicados; m³/s é uma hipótese de apresentação.
    """
    registros = []
    with pdfplumber.open(caminho) as pdf:
        if len(pdf.pages) != 4:
            raise ValueError("Esperadas quatro páginas na fonte fornecida.")
        for esquerda, direita in [(0, 1), (2, 3)]:
            linhas = pdf.pages[esquerda].extract_text(x_tolerance=2).splitlines()
            anos, nove_meses, pendente = [], [], None
            for linha in linhas:
                if not re.fullmatch(r"[\d\s]+", linha):
                    continue
                nums = [int(x) for x in linha.split()]
                if len(nums) == 1 and 1900 <= nums[0] <= 2100:
                    pendente = nums[0]
                elif len(nums) == 9 and pendente is not None:
                    anos.append(pendente)
                    nove_meses.append(nums)
                    pendente = None
                elif len(nums) == 10 and 1900 <= nums[0] <= 2100:
                    anos.append(nums[0])
                    nove_meses.append(nums[1:])
                else:
                    raise ValueError(f"Linha inesperada na página {esquerda + 1}: {linha}")
            ultimos = []
            for linha in pdf.pages[direita].extract_text(x_tolerance=2).splitlines():
                if re.fullmatch(r"[\d\s]+", linha):
                    nums = [int(x) for x in linha.split()]
                    if len(nums) != 3:
                        raise ValueError(f"Esperados três meses: {linha}")
                    ultimos.append(nums)
            if pendente is not None or len(anos) != len(ultimos):
                raise ValueError("As linhas das páginas não correspondem.")
            for linha, (ano, primeiros, finais) in enumerate(zip(anos, nove_meses, ultimos), 1):
                for mes, valor in enumerate(primeiros + finais, 1):
                    registros.append({"data": f"{ano}-{mes:02d}-01", "vazao": valor,
                                      "pagina_pdf": esquerda + 1 if mes <= 9 else direita + 1,
                                      "linha_tabela": linha})
    df = pd.DataFrame(registros)
    datas = pd.to_datetime(df.data)
    esperado = pd.date_range("1931-01-01", "2016-12-01", freq="MS")
    if not pd.DatetimeIndex(datas).equals(esperado):
        raise ValueError("A série deve conter todos os 1.032 meses de 1931 a 2016, na ordem.")
    if df.vazao.isna().any() or (df.vazao <= 0).any():
        raise ValueError("Valores ausentes ou não positivos encontrados.")
    return df


def salvar_dados():
    """Salva a série e sua procedência; não interpola nem remove extremos."""
    df = extrair_pdf()
    destino = ROOT / "data/processed"
    destino.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino / "ilha_solteira_mensal.csv", index=False)
    fonte = ROOT / "data/raw/ILHA_SOLTEIRA.pdf"
    meta = {"fonte": fonte.name, "sha256": hashlib.sha256(fonte.read_bytes()).hexdigest(),
            "n": len(df), "inicio": df.data.iloc[0], "fim": df.data.iloc[-1],
            "unidade": "m³/s (hipótese; não explicitada no PDF)",
            "tipo_vazao": "não especificado no PDF", "faltantes": 0, "duplicatas": 0,
            "transformacao_dados": "extração dos inteiros; sem imputação ou remoção de extremos",
            "paginas": "1/2: 1931-1979; 3/4: 1980-2016; JAN-SET à esquerda e OUT-DEZ à direita"}
    (destino / "metadados.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return df


def carregar_serie():
    df = pd.read_csv(ROOT / "data/processed/ilha_solteira_mensal.csv", parse_dates=["data"])
    return df.set_index("data").vazao.astype(float).asfreq("MS")


if __name__ == "__main__":
    print(salvar_dados().to_string(index=False, max_rows=12))
