import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class Config:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_SEARCH_ENGINE_ID: str = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    BING_API_KEY: str = os.getenv("BING_API_KEY", "")
    BRAVE_API_KEY: str = os.getenv("BRAVE_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(DATA_DIR / "problems.db"))

    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    REPORT_RECIPIENT: str = os.getenv("REPORT_RECIPIENT", "")

    MIN_PROBLEMS_TO_DISCOVER: int = int(os.getenv("MIN_PROBLEMS_TO_DISCOVER", "50"))
    TOP_OPPORTUNITIES: int = int(os.getenv("TOP_OPPORTUNITIES", "5"))
    SEARCH_RESULTS_PER_QUERY: int = int(os.getenv("SEARCH_RESULTS_PER_QUERY", "10"))
    MAX_QUERIES_PER_RUN: int = int(os.getenv("MAX_QUERIES_PER_RUN", "30"))
    DUPLICATE_THRESHOLD: float = float(os.getenv("DUPLICATE_THRESHOLD", "0.75"))
    SCHEDULER_INTERVAL_HOURS: int = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "3"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> list[str]:
        errors = []
        if not cls.SMTP_USER:
            errors.append("SMTP_USER is not set")
        if not cls.SMTP_PASSWORD:
            errors.append("SMTP_PASSWORD is not set")
        if not cls.REPORT_RECIPIENT:
            errors.append("REPORT_RECIPIENT is not set")
        return errors

    @classmethod
    def validate_warn(cls) -> list[str]:
        warnings = []
        if not cls.GOOGLE_API_KEY:
            warnings.append("GOOGLE_API_KEY haijewekwa - utafutaji wa Google umekatwa")
        if not cls.BING_API_KEY:
            warnings.append("BING_API_KEY haijewekwa - Bing Search haifanyi kazi")
        if not cls.BRAVE_API_KEY:
            warnings.append("BRAVE_API_KEY haijewekwa - Brave Search haifanyi kazi")
        if not cls.TAVILY_API_KEY:
            warnings.append("TAVILY_API_KEY haijewekwa - Tavily Search haifanyi kazi")
        active = [cls.GOOGLE_API_KEY, cls.BING_API_KEY, cls.BRAVE_API_KEY, cls.TAVILY_API_KEY]
        if not any(active):
            warnings.append("DuckDuckGo peke yake inatumika")
        return warnings
