import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(name: str = "app") -> logging.Logger:

    logger = logging.getLogger(name)

    # Prevent adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    # JSON formatter — every log line is a parseable JSON object
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent logs from bubbling up to the root logger and printing twice
    logger.propagate = False

    return logger


# Single shared logger instance for the whole app
logger = setup_logger("customer_segmentation_api")