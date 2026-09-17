import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import DATA_DIR


def setup_logging(level: str = "INFO") -> logging.Logger:
    log_dir = DATA_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("tanzania_problem_finder")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    file_handler = RotatingFileHandler(
        log_dir / "agent.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()
