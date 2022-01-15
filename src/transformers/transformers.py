from typing import Any

import pandas as pd


def normalizar_registros(registros: list[dict[str, Any]]) -> pd.DataFrame:
    if not registros:
        return pd.DataFrame()

    df = pd.DataFrame(registros)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna("")

    for col in df.select_dtypes(include=["number"]).columns:
        df[col] = df[col].fillna(0)

    return df


def calcular_percentuais_sentimento(
    positivo: int, neutro: int, negativo: int, total: int
) -> dict[str, float]:
    if total == 0:
        return {"pct_positivo": 0.0, "pct_neutro": 0.0, "pct_negativo": 0.0}

    return {
        "pct_positivo": round(positivo / total * 100, 2),
        "pct_neutro": round(neutro / total * 100, 2),
        "pct_negativo": round(negativo / total * 100, 2),
    }


def calcular_saude_marca(positivo: int, negativo: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((positivo - negativo) / total * 100, 2)


def mapear_sentimento(valor: int) -> str:
    return {-1: "Negativo", 0: "Neutro", 1: "Positivo"}.get(valor, "Neutro")
