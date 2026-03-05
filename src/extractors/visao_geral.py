from datetime import date, datetime
from typing import Any

from loguru import logger

from src.api.endpoints import StillingueAPI
from src.extractors import validar_resposta


def extrair_visao_geral(api: StillingueAPI, date_range: str, data_referencia: date) -> list[dict[str, Any]]:
    logger.info("Extraindo visao_geral")
    response = api.visao_geral(date_range)
    validar_resposta(response, campo="collected_mentions")

    channels = response.get("channels", {})
    sentiment = response.get("general_sentiment", {})

    registro = {
        "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_referencia": data_referencia.isoformat(),
        "publicacoes_coletadas": int(response.get("collected_mentions", 0)),
        "variacao_publicacoes_pct": round(response.get("collected_mentions_variation", 0.0), 4),
        "total_usuarios": int(response.get("total_users", 0)),
        "variacao_usuarios_pct": round(response.get("total_users_variation", 0.0), 4),
        "alcance_potencial": int(response.get("potential_reach", 0)),
        "variacao_alcance_pct": round(response.get("potential_reach_variation", 0.0), 4),
        "indice_sentimento": round(response.get("net_promoter_score", 0.0), 4),
        "variacao_sentimento_pts": round(response.get("net_promoter_score_variation", 0.0), 4),
        "sentimento_negativo_qtd": int(sentiment.get("negative_value", 0)),
        "sentimento_neutro_qtd": int(sentiment.get("neutral_value", 0)),
        "sentimento_positivo_qtd": int(sentiment.get("positive_value", 0)),
        "canal_twitter": int(channels.get("Twitter", 0)),
        "canal_facebook": int(channels.get("Facebook", 0)),
        "canal_noticias": int(channels.get("News", 0)),
        "canal_instagram": int(channels.get("Instagram", 0)),
        "canal_youtube": int(channels.get("YouTube", 0)),
        "canal_blogs": int(channels.get("Blogs", 0)),
    }

    logger.info(f"visao_geral: {registro['publicacoes_coletadas']} publicacoes coletadas")
    return [registro]
