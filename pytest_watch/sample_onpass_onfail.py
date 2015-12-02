import os
import json


def main():
    fname_report = os.environ["PYTEST_REPORT_FILEPATH"]

    with open(fname_report, "r") as f_report:
        list_report = json.load(f_report)

    count_pass = 0
    count_fail = 0

    for each_report in list_report:
        if each_report["when"] == "call":
            if each_report["passed"]:
                count_pass += 1
            else:
                count_fail += 1

    print("Passed: {count_pass}/{count_total}".format(
        count_pass=count_pass, count_total=count_fail + count_pass))

if __name__ == '__main__':
    main()
