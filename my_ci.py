#!/usr/bin/python3

import os
import subprocess
import time
from datetime import datetime

import requests

from ci_constants import *

TWO_MINUTES = 120


def get(url):
    return requests.get(
        url,
        headers={
            "Authorization": GITLAB_TOKEN,
            "Content-Type": "application/json",
        },
        verify=ENABLE_SSL_VERIFICATION,
    ).json()


def post(url):
    return requests.post(
        url,
        headers={
            "Authorization": GITLAB_TOKEN,
            "Content-Type": "application/json",
        },
        verify=ENABLE_SSL_VERIFICATION,
    ).json()


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
        write_to_log_file(e)
        return False
    finally:
        # CLEANUP
        delete_folder(TEMP_TEST_FOLDER)


def delete_folder(folder_name):
    subprocess.run(f"rm -rf {folder_name}", shell=True)


def write_to_log_file(e):
    npm_output = e.output.decode("utf-8")
    with open(datetime.now().strftime("./logs/D%m_%dT%H_%M.txt"), "w") as f:
        f.write(npm_output)


def get_comment(test_was_successful):
    if test_was_successful:
        return MESSAGES.get('tests_passed')
    return MESSAGES.get('tests_failed')


def run_ci():
    count = 0
    test_successful = True
    for merge_request in get_open_merge_requests():
        latest_comment = get_comments_for_merge_request(merge_request['iid'])[0]
        if latest_comment['body'].startswith(RUN_COMMAND):
            count += 1
            test_successful = run_test(merge_request['source_branch'])
            comment = get_comment(test_successful)
            post(f"{COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request['iid']))}?body={comment}")

    print(f'{count} tests were run - {test_successful}')


while True:
    run_ci()
    time.sleep(TWO_MINUTES)
