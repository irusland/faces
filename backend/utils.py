import logging
import os
import re
import sys
from datetime import datetime
from functools import lru_cache, wraps
from time import perf_counter
from typing import Any

from definitions import LOGS_DIR

FORMAT = (
    "(%(asctime)s) %(levelname)-9s[%(thread)15d "
    "|%(filename)15s|%(funcName)15s:"
    "%(lineno)4s] %(message)s"
)


@lru_cache()
def _get_log_datetime() -> datetime:
    return datetime.now()


def _get_log_name(prefix: str) -> str:
    return f"{prefix}-{_get_log_datetime()}.log"


def _get_log_path(directory: str, filename: str) -> str:
    return os.path.join(directory, filename)


def get_log_path(directory: str, prefix: str) -> str:
    filename = _get_log_name(prefix)
    return _get_log_path(directory, filename)


class OnlyFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self._level = level

    def filter(self, log_record: logging.LogRecord):
        return log_record.levelno <= self._level


class ExcludeModuleFilter(logging.Filter):
    def __init__(self, *exclude_modules: str):
        super().__init__()
        self._exclude_modules = exclude_modules

    def filter(self, log_record: logging.LogRecord):
        return log_record.module not in self._exclude_modules


class ExcludeDirFilter(logging.Filter):
    def __init__(self, exclude_dir: str):
        super().__init__()
        self._exclude_dir = exclude_dir

    def filter(self, log_record: logging.LogRecord):
        return self._exclude_dir not in log_record.pathname


def _mkdir_by_path(path):
    os.makedirs(path, exist_ok=True)


class EnsureDirFileHandler(logging.FileHandler):
    def __init__(self, filename, mode="a", encoding=None, delay=0):
        _mkdir_by_path(os.path.dirname(filename))
        super().__init__(filename, mode, encoding, delay)


@lru_cache()
def get_debug_file_handler(directory: str = LOGS_DIR) -> logging.FileHandler:
    log_path = get_log_path(directory, "debug")
    handler = EnsureDirFileHandler(log_path)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    handler.addFilter(ExcludeDirFilter(".venv/"))
    handler.setLevel(logging.DEBUG)
    return handler


@lru_cache()
def get_trace_file_handler(directory: str = LOGS_DIR) -> logging.FileHandler:
    log_path = get_log_path(directory, "trace")
    handler = EnsureDirFileHandler(log_path)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    handler.addFilter(OnlyFilter(logging.TRACE))
    handler.setLevel(logging.TRACE)
    return handler


@lru_cache()
def get_info_file_handler(directory: str = LOGS_DIR) -> logging.FileHandler:
    log_path = get_log_path(directory, "info")
    handler = EnsureDirFileHandler(log_path)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    return handler


@lru_cache()
def get_info_console_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    return handler


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError(
            "{} already defined in logging module".format(levelName)
        )
    if hasattr(logging, methodName):
        raise AttributeError(
            "{} already defined in logging module".format(methodName)
        )
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError(
            "{} already defined in logger class".format(methodName)
        )

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def setup_global_logging() -> None:
    addLoggingLevel("TRACE", logging.DEBUG - 5)
    handlers = [
        get_debug_file_handler(),
        get_info_console_handler(),
        get_info_file_handler(),
        get_trace_file_handler(),
    ]
    logging.basicConfig(
        level=logging.TRACE,
        format=FORMAT,
        handlers=handlers,
    )


logger = logging.getLogger(__file__)


def makeRecord(
    self,
    name,
    level,
    fn,
    lno,
    msg,
    args,
    exc_info,
    func=None,
    extra=None,
    sinfo=None,
    **kwargs,
):
    """
    A factory method which can be overridden in subclasses to create
    specialized LogRecords.
    """
    rv = logging.LogRecord(
        name, level, fn, lno, msg, args, exc_info, func, sinfo
    )
    if extra is not None:
        rv.__dict__.update(extra)
    return rv


def log_args(logger: logging.Logger, level=logging.DEBUG, cache=dict()):
    """Decorator to log arguments passed to func."""
    logger_class = logger.__class__
    if logger_class in cache:
        UpdateableLogger = cache[logger_class]
    else:
        cache[logger_class] = UpdateableLogger = type(
            "UpdateableLogger", (logger_class,), dict(makeRecord=makeRecord)
        )

    def inner_func(func):
        @wraps(func)
        def return_func(*args, **kwargs):
            logger.__class__ = UpdateableLogger
            try:
                """
                Here you can override
                extra={
                    "filename": filename,
                    "lineno": lineno,
                    "funcName": funcname,
                }
                """
                return func(*args, **kwargs)
            finally:
                # todo fix for multithreading
                # logger.__class__ = logger_class
                pass

        return return_func

    return inner_func


def with_performance_profile(f):
    """
    Class method decorator for performance measuring
    """

    @wraps(f)
    def wrap(*args, **kw):
        ts = perf_counter()
        result = f(*args, **kw)
        te = perf_counter()
        autolog(3, "%2.4f sec", te - ts)
        return result

    return wrap


@log_args(logger)
def autolog(stack_shift: int, message: str, *args: Any):
    """Automatically log the current function details."""
    import inspect

    stack = inspect.stack()
    frame = stack[stack_shift]
    _, filename, lineno, funcname, code_context, *_ = frame

    callie = ""
    if code_context:
        (callie,) = code_context
    executable = re.sub(r"\n", "", callie)
    filename = filename.split("/")[-1]
    logger.trace(
        "%s | line %s\t:%s",
        message % args,
        lineno,
        executable,
        extra={
            "filename": filename,
            "lineno": lineno,
            "funcName": funcname,
        },
    )
