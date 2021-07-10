import logging
import re
from functools import wraps
from time import perf_counter
from typing import Any

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
    **kwargs
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
                logger.__class__ = logger_class

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
    logger.debug(
        "%s | line %s\t:%s",
        message % args,
        lineno,
        executable,
        # extra={
        #     "filename": filename,
        #     "lineno": lineno,
        #     "funcName": funcname,
        # },
    )
