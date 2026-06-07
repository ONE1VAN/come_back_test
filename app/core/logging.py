import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
MAX_BYTES = 10 * 1024 * 1024  # 10 мб
BACKUP_COUNT = 4

_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_DATE = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: str = "INFO") -> None:
    LOG_DIR.mkdir(exist_ok=True)
    formatter = logging.Formatter(_FORMAT, datefmt=_DATE)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [console, file_handler]
    root.setLevel(level)
