import logging
import sys

def setup_logging():
    log_format = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("STARHEALERS_UNIFIED")
    logger.info("STARHEALERS unified logging initialized.")
    return logger

logger = setup_logging()
