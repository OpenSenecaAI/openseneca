import logging
import colorlog
import inspect
import os
import threading

class ThreadIDFilter(logging.Filter):
    """
    This is a filter which injects the thread id into the log.

    This because the Logger class is being instantiated in the main thread,
    so the thread ID (thid) is being set at the time of instantiation and
    doesn't change afterwards. This means that all log messages, even those
    from other threads, will have the same thread ID.

    To print the correct thread ID for each log message, you can use a
    logging.Filter to add the thread ID to the log record at the time the
    log message is processed.

    e.g: handler.addFilter(ThreadIDFilter())

    """
    def filter(self, record):
        record.threadid = threading.current_thread().ident
        return True

class Logger:
    """
    A Logger class for colored logging.
    """

    def __init__(self, name: str = None, level: str = 'DEBUG'):
        """
        Initialize the logger with a name and level.
        If no name is provided, it defaults to the name of the module where the Logger is instantiated.
        """

        if name is None:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            name = os.path.split(module.__file__)[-1]

        pid = os.getpid()
        thid = threading.current_thread().ident
        formatter = colorlog.ColoredFormatter(
            f"%(log_color)s%(asctime)s | 🚦 {pid}/%(threadid)s | 📁 \033[90m{name} %(log_color)s| "\
            "%(levelname)-4s | \033[37m%(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
            style='%'
        )

        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.addFilter(ThreadIDFilter())
        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, level))

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)