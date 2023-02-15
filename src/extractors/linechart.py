from typing import Any

from loguru import logger

from src.api.endpoints import SocialListeningAPI
from src.extractors import validar_resposta


def extrair_linechart(api: SocialListeningAPI, date_range: str) -> list[dict[str, Any]]:
    logger.info("Extraindo linechart")
    response = api.linechart(date_range)
    validar_resposta(response)

    raw_data = response.get("data", [])
    registros: list[dict[str, Any]] = []

    if not raw_data or len(raw_data) < 2:
        logger.warning("linechart: raw_data vazio ou sem pontos de dados")
        return registros

    pontos = raw_data[1] if isinstance(raw_data[1], list) else []

    for ponto in pontos:
        if not isinstance(ponto, list) or len(ponto) < 2:
            continue

        timestamp_str = str(ponto[0])
        total = ponto[1]

        partes = timestamp_str.split(" ")
        data_ref = partes[0].replace("/", "-")
        hora = partes[1] if len(partes) > 1 else ""

        registros.append({
            "data_referencia": data_ref,
            "total_publicacoes": int(total),
            "hora": hora,
        })

    logger.info(f"linechart: {len(registros)} pontos extraidos")
    return registros
