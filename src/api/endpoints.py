from typing import Any

from src.api.client import HTTPClient
from src.config import config


class SocialListeningAPI:
    def __init__(self, client: HTTPClient) -> None:
        self._client = client

    def visao_geral(self, date_range: str) -> dict[str, Any]:
        return self._client.get("visao_geral", params={"date_range": date_range})

    def sentimento_grupos(self, date_range: str) -> dict[str, Any]:
        return self._client.get("sentimento_grupos", params={"date_range": date_range})

    def sentimento_temas(self, date_range: str, limit: int | None = None) -> dict[str, Any]:
        limit = limit or config.TEMAS_LIMIT
        return self._client.get(
            "sentimento_temas",
            params={"date_range": date_range, "limit": limit},
        )

    def linechart(self, date_range: str) -> dict[str, Any]:
        return self._client.get("linechart", params={"date_range": date_range})

    def publicacoes(
        self,
        date_range: str,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "date_desc",
    ) -> dict[str, Any]:
        return self._client.get(
            "publicacoes",
            params={
                "date_range": date_range,
                "limit": limit,
                "offset": offset,
                "order_by": order_by,
            },
        )

    def ranking_evolutivo(self, date_range: str) -> dict[str, Any]:
        return self._client.get("ranking_evolutivo", params={"date_range": date_range})
