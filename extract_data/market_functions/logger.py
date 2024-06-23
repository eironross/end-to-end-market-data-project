import logging


def log_iemop():
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s: %(levelname)s - %(message)s")
    
    file_handler = logging.FileHandler("./logs/info.log")
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger


if __name__ == "__main__":
    log_iemop()