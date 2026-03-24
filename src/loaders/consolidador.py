from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, ZIP_LZMA

import pandas as pd
from loguru import logger

from src.config import config
from src.loaders.csv_writer import _deduplicar, _aplicar_schema
from src.schemas import ENDPOINT_SCHEMAS, COLUNAS_DATA


def _parsear_data_arquivo(nome_arquivo: str) -> str | None:
    stem = Path(nome_arquivo).stem
    try:
        dt = datetime.strptime(stem, "%Y%m%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


def _remover_formato_oposto(saida: Path) -> None:
    if saida.suffix == ".parquet":
        oposto = saida.with_suffix(".csv")
    else:
        oposto = saida.with_suffix(".parquet")
    if oposto.exists():
        oposto.unlink()
        logger.info(f"Removido consolidado obsoleto: {oposto}")


def _formatar_datas_consolidado(df: pd.DataFrame, endpoint: str) -> pd.DataFrame:
    colunas = COLUNAS_DATA.get(endpoint, [])
    for col in colunas:
        if col not in df.columns:
            continue
        serie = pd.to_datetime(df[col], errors="coerce")
        if col == "data_referencia":
            df[col] = serie.dt.strftime("%d/%m/%Y").fillna("")
        else:
            df[col] = serie.dt.strftime("%d/%m/%Y %H:%M:%S").fillna("")
    return df


def consolidar_endpoint(endpoint: str) -> Path:
    fmt = config.CONSOLIDADO_FORMATO
    saida = config.CONSOLIDADO_DIR / f"{endpoint}.{fmt}"
    pasta_endpoint = config.OUTPUT_DIR / endpoint
    data_minima = config.CONSOLIDADO_DATA_MINIMA.isoformat()

    if not pasta_endpoint.exists():
        logger.warning(f"Pasta inexistente para {endpoint}: {pasta_endpoint}")
        return saida

    arquivos_csv = sorted(pasta_endpoint.glob("*.csv"))
    dfs: list[pd.DataFrame] = []

    for arquivo in arquivos_csv:
        data_ref = _parsear_data_arquivo(arquivo.name)
        if data_ref is None:
            continue
        if data_ref < data_minima:
            continue

        df = pd.read_csv(arquivo, encoding="utf-8-sig", dtype=str)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        logger.info(f"{endpoint}: nenhum CSV com data >= {data_minima}")
        return saida

    df_final = pd.concat(dfs, ignore_index=True)
    df_final = _deduplicar(df_final, endpoint)
    df_final = _aplicar_schema(df_final, endpoint)

    if saida.exists():
        saida.unlink()

    if fmt == "parquet":
        df_final.to_parquet(saida, index=False, engine="pyarrow")
    else:
        df_formatado = _formatar_datas_consolidado(df_final.copy(), endpoint)
        with open(saida, "w", encoding="utf-8", newline="") as f:
            df_formatado.to_csv(f, index=False, sep=";")

    _remover_formato_oposto(saida)

    logger.info(
        f"{endpoint}: consolidado recriado com {len(df_final)} linhas "
        f"(data >= {data_minima}, formato: {fmt}) em {saida}"
    )
    return saida


def _zipar_consolidados(caminhos: dict[str, Path]) -> Path:
    fmt = config.CONSOLIDADO_FORMATO
    zip_path = config.CONSOLIDADO_DIR / f"Consolidado_{fmt}.zip"

    if zip_path.exists():
        zip_path.unlink()

    arquivos = [p for p in caminhos.values() if p.exists()]
    if not arquivos:
        logger.warning("Nenhum consolidado para zipar")
        return zip_path

    with ZipFile(zip_path, "w", ZIP_LZMA) as zf:
        for arquivo in arquivos:
            zf.write(arquivo, arquivo.name)

    tamanho_mb = zip_path.stat().st_size / 1024 / 1024
    logger.info(f"ZIP criado: {zip_path} ({tamanho_mb:.1f} MB, {len(arquivos)} arquivos)")
    return zip_path


def consolidar_todos() -> dict[str, Path]:
    resultados: dict[str, Path] = {}
    for endpoint in ENDPOINT_SCHEMAS:
        resultados[endpoint] = consolidar_endpoint(endpoint)
    _zipar_consolidados(resultados)
    return resultados
