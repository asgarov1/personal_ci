#!/usr/bin/python3
import os
import subprocess
import time

import urllib3

from common.folder_util import delete_folder
from common.http import get, post
from common.log_util import write_to_log_file

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from constants.eama_ci_constants import *

TWO_MINUTES = 120
FOCUS_KEYWORDS = ['fdescribe', 'fit']


def get_open_merge_requests():
    return get(OPEN_MERGE_REQUESTS_URL)


def get_comments_for_merge_request(merge_request_iid):
    return get(COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request_iid)))


def run_test(branch='develop'):
    try:
        if os.path.isdir(TEMP_TEST_FOLDER):
            delete_folder(TEMP_TEST_FOLDER)

        subprocess.run(f"git clone --no-checkout --depth 1 --no-single-branch {EAMA_GIT_URL} {TEMP_TEST_FOLDER}",
                       shell=True)

        command = f"cd ./{TEMP_TEST_FOLDER} && " \
                  f"git config core.sparseCheckout true && " \
                  f"echo {FE_FOLDER_PATH}/*> .git/info.sparse-checkout && " \
                  f"git checkout {branch} && " \
                  f"cd {FE_FOLDER_PATH} && " \
                  f"npm i && ng test --watch=false"
        subprocess.check_output(command, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        write_to_log_file(e, LOG_FOLDER)
        return False
    finally:
        # CLEANUP
        delete_folder(TEMP_TEST_FOLDER)


def get_comment(test_was_successful):
    if test_was_successful:
        return MESSAGES.get('tests_passed')
    return MESSAGES.get('tests_failed')


def get_merge_request_to_test():
    return list(filter(lambda mr: len(get_comments_for_merge_request(mr['iid'])) > 0 and
                                  get_comments_for_merge_request(mr['iid'])[0]['body'].startswith(RUN_COMMAND),
                       get_open_merge_requests()))


def run_eama_frontend_ci():
    count = 0
    test_successful = 'nothing to report'
    for merge_request in get_merge_request_to_test():
        count += 1
        test_successful = run_test(merge_request['source_branch'])
        comment = get_comment(test_successful)
        post(f"{COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request['iid']))}?body={comment}")

    print(f'{count} tests were run - {test_successful}')


while True:
    run_eama_frontend_ci()
    time.sleep(TWO_MINUTES)
