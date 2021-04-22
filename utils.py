import logging


def create_stdout_logger(level, *labels) -> logging.Logger:
    logger = logging.getLogger(" - ".join(labels))
    logger.setLevel(level)

    h = logging.StreamHandler()
    h.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    h.setFormatter(formatter)

    logger.addHandler(h)
    return logger
