""" Logging functionality. """

from ui import Colors


class Log:
    """
    All class methods are static methods.
    """

    @staticmethod
    def __init__(message=""):
        print(message)
   
    @staticmethod
    def critical(logger, message):
        if message:
            logger.critical(f"{Colors.RED}{message}{Colors.RESET}")

    @staticmethod
    def error(logger, message):
        if message:
            logger.error(f"{Colors.MAGENTA}{message}{Colors.RESET}")

    @staticmethod
    def warning(logger, message):
        if message:
            logger.warning(f"{Colors.YELLOW}{message}{Colors.RESET}")

    @staticmethod
    def info(logger, message):
        if message:
            logger.info(f"{Colors.GREY}{message}{Colors.RESET}")

    @staticmethod
    def debug(logger, message):
        if message:
            logger.debug(f"{Colors.BLUE}{message}{Colors.RESET}")
