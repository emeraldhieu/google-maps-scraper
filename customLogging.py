import logging
from colorama import init as colorama_init, Fore, Style
colorama_init()

class ColoredLog(logging.Formatter):
    format = "%(asctime)s  %(name)-12.12s L%(lineno)-4.4d  %(levelname)-7.7s: %(message)s"

    FORMATS = {
        logging.DEBUG: Fore.LIGHTBLACK_EX + format + Style.RESET_ALL,
        logging.INFO: Fore.WHITE + format + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format + Style.RESET_ALL,
        logging.CRITICAL: Fore.LIGHTRED_EX + format + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
class CallCounted:
    """Decorator to determine number of calls for a method"""

    def __init__(self,method):
        self.method=method
        self.counter=0

    def __call__(self,*args,**kwargs):
        self.counter+=1
        return self.method(*args,**kwargs)