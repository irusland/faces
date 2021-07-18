import logging

from pytest_mock_resources import create_redis_fixture

from backend.utils import addLoggingLevel


def _setup_test_logging() -> None:
    addLoggingLevel("TRACE", logging.DEBUG - 5)


_setup_test_logging()


def pytest_addoption(parser):
    parser.addoption("--silent", action="store_true", default=False)


def pytest_report_teststatus(report, config):
    category, short, verbose = "", "", ""
    if not config.getoption("--silent"):
        return None

    if hasattr(report, "wasxfail"):
        if report.skipped:
            category = "xfailed"
        elif report.passed:
            category = "xpassed"
        return category, short, verbose
    elif report.when in ("setup", "teardown"):
        if report.failed:
            category = "error"
        elif report.skipped:
            category = "skipped"
        return category, short, verbose
    category = report.outcome
    return category, short, verbose


redis = create_redis_fixture()
