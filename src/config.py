import sys
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
import os


def _resolve_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


_BASE_DIR = _resolve_base_dir()
load_dotenv(_BASE_DIR / ".env")


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


class Config:
    API_TOKEN: str = os.getenv("STILINGUE_API_TOKEN", "")
    BASE_URL: str = os.getenv("STILINGUE_BASE_URL", "https://api.stilingue.com.br")
    OUTPUT_DIR: Path = _BASE_DIR / os.getenv("OUTPUT_DIR", "./data/csv")
    CONSOLIDADO_DIR: Path = _BASE_DIR / os.getenv("CONSOLIDADO_DIR", "./consolidado")
    LOG_DIR: Path = _BASE_DIR / os.getenv("LOG_DIR", "./logs")
    DAYS_BACK: int = int(os.getenv("DAYS_BACK", "1"))
    PUBLICATIONS_LIMIT: int = int(os.getenv("PUBLICATIONS_LIMIT", "100"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))
    REQUEST_SLEEP_BETWEEN: int = int(os.getenv("REQUEST_SLEEP_BETWEEN", "1"))
    RANKING_EVOLUTIVO_DAYS: int = int(os.getenv("RANKING_EVOLUTIVO_DAYS", "30"))
    TEMAS_LIMIT: int = int(os.getenv("TEMAS_LIMIT", "50"))
    BACKFILL_DAYS: int = int(os.getenv("BACKFILL_DAYS", "90"))
    RETROATIVO_INICIO: date | None = _parse_date(os.getenv("RETROATIVO_INICIO", ""))
    RETROATIVO_FIM: date | None = _parse_date(os.getenv("RETROATIVO_FIM", ""))

    @classmethod
    def validate(cls) -> None:
        if not cls.API_TOKEN:
            raise ValueError("STILINGUE_API_TOKEN nao configurado no .env")
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CONSOLIDADO_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)


config = Config()
