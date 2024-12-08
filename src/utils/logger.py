import logging
import os

def setup_logger(name="bintra", log_file=None, level=logging.INFO):
    """
    Sets up a logger with the specified name, log file, and log level.

    :param name: Name of the logger.
    :param log_file: File path to write logs. If None, logs only to console.
    :param level: Logging level. Default is logging.INFO.
    :return: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(file_handler)

    return logger
