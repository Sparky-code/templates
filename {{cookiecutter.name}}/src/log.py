import logging

from .config import LOG_LEVEL


def setup_logger(name: str = "{{ cookiecutter.name }}", log_level: str = LOG_LEVEL) -> logging.Logger:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger(name)
