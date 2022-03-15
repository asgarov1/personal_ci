#!/usr/bin/python3

import subprocess
import requests

from datetime import datetime
from ci_constants import *

queue_to_run_tests = []


def get_open_merge_requests():
    return requests.get(
        OPEN_MERGE_REQUESTS_URL,
        headers={
            "Authorization": GITLAB_TOKEN,
            "Content-Type": "application/json",
        },
        verify=ENABLE_SSL_VERIFICATION,
    ).json()


def get_comments_for_merge_request(merge_request_iid):
    return requests.get(
        COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request_iid)),
        headers={
            "Authorization": GITLAB_TOKEN,
            "Content-Type": "application/json",
        },
        verify=ENABLE_SSL_VERIFICATION,
    ).json()


def is_run_command(comment):
    return comment.body.startswith(RUN_COMMAND)


def run_test(branch='develop'):
    try:
        subprocess.run(f"git clone --no-checkout --depth 1 ${EAMA_GIT_URL} ${TEMP_TEST_FOLDER}",
                       capture_output=True,
                       shell=True,
                       check=True)

        # check if this works in this rheinfolge - might be that checkout has to happen before cd FE_FOLDER step
        command = f"cd ./${TEMP_TEST_FOLDER} && " \
                  f"git config core.sparseCheckout true" \
                  f"echo ${FE_FOLDER_PATH}*> .git/info.sparse-checkout" \
                  f"cd ${FE_FOLDER_PATH}" \
                  f"git checkout ${branch}" \
                  f"npm i && ng test --watch=false"
        subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError as e:
        write_to_log_file(e)
    finally:
        # CLEANUP
        subprocess.run(f"rm rf ${TEMP_TEST_FOLDER}", capture_output=True, shell=True)


def write_to_log_file(e):
    npm_output = e.output.decode("utf-8")
    with open(datetime.now().strftime("./logs/D%m_%dT%H_%M.txt"), "w") as f:
        f.write(npm_output)


print(get_comments_for_merge_request(272))

