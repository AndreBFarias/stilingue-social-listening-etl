from datetime import date
from typing import Any

from loguru import logger

from src.api.endpoints import StillingueAPI
from src.extractors import validar_resposta


def extrair_sentimento_grupos(api: StillingueAPI, date_range: str, data_referencia: date) -> list[dict[str, Any]]:
    logger.info("Extraindo sentimento_grupos")
    response = api.sentimento_grupos(date_range)
    validar_resposta(response)

    data = response.get("data", {})
    registros: list[dict[str, Any]] = []

    for canal, grupos in data.items():
        if not isinstance(grupos, list):
            continue
        for grupo in grupos:
            total = grupo.get("total", 0)
            positivo = grupo.get("positive", 0)
            neutro = grupo.get("neutral", 0)
            negativo = grupo.get("negative", 0)

            pct_pos = round(positivo / total * 100, 2) if total > 0 else 0.0
            pct_neu = round(neutro / total * 100, 2) if total > 0 else 0.0
            pct_neg = round(negativo / total * 100, 2) if total > 0 else 0.0
            saude = round((positivo - negativo) / total * 100, 2) if total > 0 else 0.0

            registros.append({
                "data_referencia": data_referencia.isoformat(),
                "marca": grupo.get("name", ""),
                "canal": canal,
                "qtd_positivo": positivo,
                "qtd_neutro": neutro,
                "qtd_negativo": negativo,
                "total_mencoes": total,
                "pct_positivo": pct_pos,
                "pct_neutro": pct_neu,
                "pct_negativo": pct_neg,
                "saude_marca_score": saude,
            })

    logger.info(f"sentimento_grupos: {len(registros)} registros extraidos")
    return registros
