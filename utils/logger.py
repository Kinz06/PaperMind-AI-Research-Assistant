import logging
import sys
from pathlib import Path
from colorlog import ColoredFormatter

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(name='papermind', level=logging.INFO):

    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)
    
    logger_instance.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if sys.platform == 'win32':
        try:
            # Reconfigure stdout to use UTF-8
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7 fallback
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    console_format = ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(white)s%(name)s%(reset)s - %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    
    file_handler = logging.FileHandler(
        LOG_DIR / "papermind.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    logger_instance.addHandler(console_handler)
    logger_instance.addHandler(file_handler)
    
    logger_instance.propagate = False
    
    return logger_instance

class SafeLogger:
    
    def __init__(self, logger_instance):
        self._logger = logger_instance
    
    def _sanitize(self, msg):
        """Remove problematic Unicode characters for Windows console"""
        if sys.platform == 'win32':
            replacements = {
                '→': '->',
                '←': '<-',
                '↔': '<->',
                '✓': '[OK]',
                '✗': '[X]',
                '•': '*',
                '…': '...',
                'α': 'alpha',
                'β': 'beta',
                'γ': 'gamma',
                'δ': 'delta',
                'ε': 'epsilon',
                'θ': 'theta',
                'λ': 'lambda',
                'μ': 'mu',
                'π': 'pi',
                'σ': 'sigma',
                'φ': 'phi',
                'ω': 'omega',
            }
            
            msg_str = str(msg)
            for char, replacement in replacements.items():
                msg_str = msg_str.replace(char, replacement)
            
            try:
                msg_str.encode('cp1252')
                return msg_str
            except UnicodeEncodeError:
                return msg_str.encode('ascii', errors='replace').decode('ascii')
        
        return msg
    
    def debug(self, msg, *args, **kwargs):
        self._logger.debug(self._sanitize(msg), *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self._logger.info(self._sanitize(msg), *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self._logger.warning(self._sanitize(msg), *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        self._logger.error(self._sanitize(msg), *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self._logger.critical(self._sanitize(msg), *args, **kwargs)

_default_logger = setup_logger('papermind')
logger = SafeLogger(_default_logger)