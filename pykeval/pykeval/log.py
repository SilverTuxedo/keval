import logging
import sys

_HANDLER = logging.StreamHandler(sys.stdout)


def setup_root_logger(level=logging.INFO):
    logger = logging.getLogger("pykeval")

    if _HANDLER in logger.handlers:
        return

    formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
    _HANDLER.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(_HANDLER)
