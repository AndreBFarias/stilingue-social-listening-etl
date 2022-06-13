from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from src.config import config
from src.schemas import ENDPOINT_SCHEMAS, DEDUP_KEYS


def csv_ja_existe(endpoint: str, data_str: str) -> bool:
    arquivo = config.OUTPUT_DIR / endpoint / f"{data_str}.csv"
    return arquivo.exists() and arquivo.stat().st_size > 0


def _aplicar_schema(df: pd.DataFrame, endpoint: str) -> pd.DataFrame:
    colunas = ENDPOINT_SCHEMAS.get(endpoint)
    if not colunas:
        return df

    for col in colunas:
        if col not in df.columns:
            df[col] = ""

    return df[colunas]


def _deduplicar(df: pd.DataFrame, endpoint: str) -> pd.DataFrame:
    chaves = DEDUP_KEYS.get(endpoint)
    if chaves:
        return df.drop_duplicates(subset=chaves)
    return df.drop_duplicates()


def salvar_csv(registros: list[dict[str, Any]], endpoint: str, data_str: str) -> Path:
    pasta = config.OUTPUT_DIR / endpoint
    pasta.mkdir(parents=True, exist_ok=True)

    arquivo = pasta / f"{data_str}.csv"

    if arquivo.exists() and arquivo.stat().st_size > 0:
        logger.info(f"CSV ja existe, pulando: {arquivo}")
        return arquivo

    df = pd.DataFrame(registros)

    if df.empty:
        logger.warning(f"Nenhum registro para {endpoint} em {data_str}")
        return arquivo

    df = _deduplicar(df, endpoint)
    df = _aplicar_schema(df, endpoint)

    df.to_csv(arquivo, index=False, encoding="utf-8-sig")
    logger.info(f"CSV salvo: {arquivo} ({len(df)} linhas)")
    return arquivo
