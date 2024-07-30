import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_red(message=None):
    """
    Logs the give message in red color
    """
    logger.error("\033[91m %s\033[0m", message)

def log_green(message=None):
    """
    Logs the give message in green color
    """
    logger.info("\033[92m %s\033[0m", message)

def log_purple(message=None):
    """
    Logs the give message in purple color
    """
    logger.info("\033[95m %s\033[0m", message)
