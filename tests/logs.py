import logging

from backend.utils import (
    FORMAT,
    addLoggingLevel,
    get_debug_file_handler,
    get_info_console_handler,
    get_info_file_handler,
    get_trace_file_handler,
)
from definitions import TEST_LOGS_DIR


def setup_test_logging() -> None:
    addLoggingLevel("TRACE", logging.DEBUG - 5)
    handlers = [
        get_debug_file_handler(directory=TEST_LOGS_DIR),
        get_info_console_handler(),
        get_info_file_handler(directory=TEST_LOGS_DIR),
        get_trace_file_handler(directory=TEST_LOGS_DIR),
    ]
    logging.basicConfig(
        level=logging.TRACE,
        format=FORMAT,
        handlers=handlers,
    )
