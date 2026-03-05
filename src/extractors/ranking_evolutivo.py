from datetime import datetime
from typing import Any

from loguru import logger

from src.api.endpoints import StillingueAPI
from src.extractors import validar_resposta


def extrair_ranking_evolutivo(api: StillingueAPI, date_range: str) -> list[dict[str, Any]]:
    logger.info("Extraindo ranking_evolutivo")
    response = api.ranking_evolutivo(date_range)
    validar_resposta(response, campo="themes")

    themes = response.get("themes", [])
    registros: list[dict[str, Any]] = []

    for theme in themes:
        marca = theme.get("theme_title", "")
        pontos = theme.get("data", [])

        for ponto in pontos:
            data_str_raw = ponto.get("date", "")
            try:
                dt = datetime.strptime(data_str_raw, "%Y/%m/%d %H:%M")
                data_referencia = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                logger.warning(f"Data invalida no ranking_evolutivo: {data_str_raw}")
                continue

            descritores_raw = ponto.get("themes_descriptors", [])
            if isinstance(descritores_raw, list):
                descritores = "|".join(str(d) for d in descritores_raw)
            else:
                descritores = str(descritores_raw)

            valor = ponto.get("value", "0")
            try:
                total_mencoes = int(valor)
            except (ValueError, TypeError):
                total_mencoes = 0

            registros.append({
                "data_referencia": data_referencia,
                "marca": marca,
                "posicao_ranking": ponto.get("position", 0),
                "total_mencoes": total_mencoes,
                "descritores": descritores,
            })

    logger.info(f"ranking_evolutivo: {len(registros)} registros extraidos")
    return registros
