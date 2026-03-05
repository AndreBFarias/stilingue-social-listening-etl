import time
from datetime import date, datetime
from typing import Any

from loguru import logger

from src.api.endpoints import StillingueAPI
from src.config import config
from src.extractors import validar_resposta

SENTIMENTO_MAP = {-1: "Negativo", 0: "Neutro", 1: "Positivo"}

FORMATOS_DATA = [
    "%d/%m/%Y %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%d/%m/%Y %H:%M:%S",
]


def _normalizar_data_publicacao(valor: str) -> str:
    for fmt in FORMATOS_DATA:
        try:
            return datetime.strptime(valor, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            continue
    return valor


def extrair_publicacoes(api: StillingueAPI, date_range: str, data_referencia: date) -> list[dict[str, Any]]:
    logger.info("Extraindo publicacoes (com paginacao)")

    offset = 0
    limit = config.PUBLICATIONS_LIMIT
    registros: list[dict[str, Any]] = []
    data_extracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    while True:
        response = api.publicacoes(date_range=date_range, limit=limit, offset=offset)
        validar_resposta(response, campo="posts")
        posts = response.get("posts", [])

        for post in posts:
            groups = post.get("groups", [])
            themes = post.get("themes", [])
            tags = post.get("tags", [])
            sentiment_num = post.get("sentiment", 0)

            registros.append({
                "data_referencia": data_referencia.isoformat(),
                "data_publicacao": _normalizar_data_publicacao(post.get("posted_at", "")),
                "data_extracao": data_extracao,
                "marca": groups[0] if groups else "",
                "todas_marcas": "|".join(groups) if isinstance(groups, list) else str(groups),
                "sentimento": SENTIMENTO_MAP.get(sentiment_num, "Neutro"),
                "sentimento_num": sentiment_num,
                "post_url": post.get("post_url", ""),
                "texto": post.get("text", ""),
                "canal": post.get("channel", ""),
                "interacoes": post.get("interactions", 0),
                "curtidas": post.get("likes", 0),
                "comentarios": post.get("comments", 0),
                "compartilhamentos": post.get("shares", 0),
                "temas": "|".join(themes) if isinstance(themes, list) else str(themes),
                "tags": "|".join(tags) if isinstance(tags, list) else str(tags),
                "pid": post.get("pid", ""),
                "seguidores_autor": post.get("followers", 0),
                "score_aaa": post.get("AAA_score", 0.0),
                "nivel_criticidade": post.get("critical_level", 0),
            })

        next_offset = response.get("next_offset", 0)
        if next_offset == 0 or not posts:
            break

        offset = next_offset
        time.sleep(config.REQUEST_SLEEP_BETWEEN)

    logger.info(f"publicacoes: {len(registros)} registros extraidos")
    return registros
