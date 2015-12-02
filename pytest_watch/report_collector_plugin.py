""" Catch report for all test and save to tmpfile name provided"""

import os
import pytest
import json


test_reports = []


def pytest_addoption(parser):
    parser.addoption("--report_collector_filename", dest="report_collector_filename")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object

    outcome = yield
    report_obj = outcome.get_result()

    test_report = {}

    # copy stuff from report_obj

    test_report["duration"] = report_obj.duration
    test_report["failed"] = report_obj.failed
    test_report["fspath"] = report_obj.fspath
    test_report["keywords"] = report_obj.keywords
    test_report["location"] = report_obj.location

    # longrepr is pretty long, so maybe we should ignore this
    # if report_obj.longrepr:
    #     test_report["longrepr"] = str(report_obj.longrepr)
    # else:
    #     test_report["longrepr"] = None

    test_report["nodeid"] = report_obj.nodeid
    test_report["outcome"] = report_obj.outcome
    test_report["passed"] = report_obj.passed
    test_report["sections"] = report_obj.sections
    test_report["skipped"] = report_obj.skipped
    test_report["when"] = report_obj.when

    global test_reports
    test_reports.append(test_report)


def pytest_sessionfinish(session, exitstatus):
    config = pytest.config
    fname = config.getoption("report_collector_filename")

    with open(fname, mode="w") as f:
        f.write(json.dumps(test_reports))
