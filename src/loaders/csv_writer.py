from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from src.config import config


def salvar_csv(registros: list[dict[str, Any]], endpoint: str, data_str: str) -> Path:
    pasta = config.OUTPUT_DIR / endpoint
    pasta.mkdir(parents=True, exist_ok=True)

    arquivo = pasta / f"{data_str}.csv"
    df = pd.DataFrame(registros)

    if df.empty:
        logger.warning(f"Nenhum registro para {endpoint} em {data_str}")
        return arquivo

    df.to_csv(arquivo, index=False, encoding="utf-8-sig")
    logger.info(f"CSV salvo: {arquivo} ({len(df)} linhas)")
    return arquivo
