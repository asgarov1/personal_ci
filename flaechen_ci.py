#!/usr/bin/python3
import os
import subprocess
import time

from common.folder_util import delete_folder
from common.http import get, post
from common.log_util import write_to_log_file

from constants.flaechen_ci_constants import *

TWO_MINUTES = 120


def run_test(branch='develop'):
    try:
        if os.path.isdir(TEMP_TEST_FOLDER):
            delete_folder(TEMP_TEST_FOLDER)

        subprocess.run(f"git clone {GIT_URL} --branch {branch} --single-branch {TEMP_TEST_FOLDER}",
                       shell=True)
        subprocess.check_output(f"cd ./{TEMP_TEST_FOLDER} && mvn clean verify", shell=True)
        return True
    except subprocess.CalledProcessError as e:
        write_to_log_file(e, LOG_FOLDER)
        return False
    finally:
        # CLEANUP
        delete_folder(TEMP_TEST_FOLDER)


def get_comment(messages, test_was_successful):
    if test_was_successful:
        return messages.get('tests_passed')
    return messages.get('tests_failed')


def run_ci(run_command):
    count = 0
    test_successful = 'nothing to report'
    for merge_request in get(OPEN_MERGE_REQUESTS_URL):
        comments = get(COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request['iid'])))
        latest_comment = comments[0]
        if latest_comment['body'].startswith(run_command):
            count += 1
            test_successful = run_test(merge_request['source_branch'])
            comment = get_comment(MESSAGES, test_successful)
            post(f"{COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request['iid']))}?body={comment}")

    print(f'{count} tests were run - {test_successful}')


while True:
    run_ci(RUN_COMMAND)
    time.sleep(TWO_MINUTES)
