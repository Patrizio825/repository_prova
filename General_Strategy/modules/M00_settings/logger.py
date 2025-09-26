from AlgorithmImports import *
import logging
from functools import wraps

class ValidationError(Exception):
    """Eccezione personalizzata per errori di validazione."""
    pass

class Logger:
    LEVELS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET
    }

    @staticmethod
    def convert_level(level):
        """Converte un livello stringa in costante numerica logging."""
        if isinstance(level, str):
            return Logger.LEVELS.get(level.upper(), logging.INFO)
        return level

    def __init__(self, algorithm=None, name="Diagnostics", enabled=True, level=logging.INFO):
        self.algorithm = algorithm
        self.enabled = enabled
        self.level = Logger.convert_level(level)
        self.logger = self._setup_logger(name)

    def _setup_logger(self, name):
        """Setup logger Python con configurazione ottimizzata."""
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(name)s] %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(self.level)
        logger.disabled = not self.enabled
        self.info(f"Livello di log settato a {self.level}")
        return logger

    def set_level(self, level):
        """Aggiorna livello logging a runtime."""
        old_level = self.level
        self.level = Logger.convert_level(level)
        self.logger.setLevel(self.level)
        self.info(f"Livello di log cambiato da {logging.getLevelName(old_level)} a {level}")
    
    def set_enabled(self, enabled):
        """Abilita/disabilita logging a runtime."""
        old_enabled = self.enabled
        self.enabled = enabled
        self.logger.disabled = not enabled
        
        if enabled and not old_enabled:
            self.info("Logger riabilitato a runtime")
        elif not enabled and old_enabled:
            self.info("Logger disabilitato a runtime")

    def log(self, level, msg):
        """Metodo logging principale."""
        if not self.enabled or level < self.level:
            return
        
        self.logger.log(level, msg)
        
        if self.algorithm:
            if level >= logging.ERROR:
                self.algorithm.Error(msg)
            elif level >= logging.INFO:
                self.algorithm.Debug(msg)
            else:
                self.algorithm.Log(msg)

    def debug(self, msg): self.log(logging.DEBUG, msg)
    def info(self, msg): self.log(logging.INFO, msg)
    def warning(self, msg): self.log(logging.WARNING, msg)
    def error(self, msg): self.log(logging.ERROR, msg)
    def critical(self, msg): self.log(logging.CRITICAL, msg)

    def log_call(self, func):
        """Decoratore ottimizzato per logging chiamate funzioni."""
        if not self.enabled or not self.logger.isEnabledFor(logging.INFO):
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.info(f"→ Chiamata: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                result_str = (
                    f"[{', '.join(type(x).__name__ for x in result)}]"
                    if isinstance(result, list)
                    else (result if result is not None else 'OK')
                )
                self.info(f"← Uscita: {func.__name__} → {result_str}")
                return result
            except Exception as e:
                self.error(f"‼ Errore in {func.__name__}: {e}")
                raise
        return wrapper
    
    def error_validator(self, custom_exceptions=(ValidationError,), algorithm_attr="algorithm"):
        """Decoratore per gestione centralizzata errori."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except custom_exceptions as e:
                    if self.algorithm:
                        self.error(f"Errore personalizzato: {e}")
                    raise
                except Exception:
                    raise
            return wrapper
        return decorator

__all__ = ['Logger', 'ValidationError']
