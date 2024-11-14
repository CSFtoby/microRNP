import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Crear el directorio de logs si no existe
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configuración del formato de logs
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Handler para archivo
    file_handler = RotatingFileHandler(
        filename=logs_dir / "app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger