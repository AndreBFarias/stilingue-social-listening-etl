from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from src.config import config
from src.loaders.csv_writer import _deduplicar, _aplicar_schema
from src.schemas import ENDPOINT_SCHEMAS


def _parsear_data_arquivo(nome_arquivo: str) -> str | None:
    stem = Path(nome_arquivo).stem
    try:
        dt = datetime.strptime(stem, "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def consolidar_endpoint(endpoint: str) -> Path:
    saida = config.CONSOLIDADO_DIR / f"{endpoint}.csv"
    pasta_endpoint = config.OUTPUT_DIR / endpoint

    if not pasta_endpoint.exists():
        logger.warning(f"Pasta inexistente para {endpoint}: {pasta_endpoint}")
        return saida

    datas_existentes: set[str] = set()
    df_existente = pd.DataFrame()

    if saida.exists() and saida.stat().st_size > 0:
        df_existente = pd.read_csv(saida, encoding="utf-8-sig", dtype=str)
        if "data_referencia" in df_existente.columns:
            datas_existentes = set(df_existente["data_referencia"].unique())

    arquivos_csv = sorted(pasta_endpoint.glob("*.csv"))
    novos_dfs: list[pd.DataFrame] = []

    for arquivo in arquivos_csv:
        data_ref = _parsear_data_arquivo(arquivo.name)
        if data_ref is None:
            continue
        if data_ref in datas_existentes:
            continue

        df = pd.read_csv(arquivo, encoding="utf-8-sig", dtype=str)
        if not df.empty:
            novos_dfs.append(df)

    if not novos_dfs:
        logger.info(f"{endpoint}: consolidado atualizado, nenhum CSV novo")
        return saida

    df_novos = pd.concat(novos_dfs, ignore_index=True)
    linhas_novas = len(df_novos)

    if not df_existente.empty:
        df_final = pd.concat([df_existente, df_novos], ignore_index=True)
    else:
        df_final = df_novos

    df_final = _deduplicar(df_final, endpoint)
    df_final = _aplicar_schema(df_final, endpoint)

    df_final.to_csv(saida, index=False, encoding="utf-8-sig")
    logger.info(
        f"{endpoint}: consolidado salvo com {len(df_final)} linhas "
        f"({linhas_novas} novas) em {saida}"
    )
    return saida


def consolidar_todos() -> dict[str, Path]:
    resultados: dict[str, Path] = {}
    for endpoint in ENDPOINT_SCHEMAS:
        resultados[endpoint] = consolidar_endpoint(endpoint)
    return resultados
