#!/usr/bin/python3
import time
from datetime import datetime

import common.http
from common.http import get, post
from constants.eama_ci_constants import *

TWO_MINUTES = 120
FOCUS_KEYWORDS = ['fdescribe', 'fit']


def get_open_merge_requests():
    return get(OPEN_MERGE_REQUESTS_URL)


def get_comments_for_merge_request(merge_request_iid):
    return get(COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request_iid)))


def get_merge_request_to_test():
    return list(filter(lambda mr: len(get_comments_for_merge_request(mr['iid'])) == 0 or
                                  not (get_comments_for_merge_request(mr['iid'])[0]['body'].startswith(AUTO_SCRIPT)),
                       get_open_merge_requests()))


def check_for_focus_keyword():
    for merge_request in get_merge_request_to_test():
        changes = common.http.get(GET_MR_CHANGES_URL.replace(':iid', str(merge_request['iid'])))['changes']
        for change in changes:
            for line in change['diff'].split('\n'):
                if line.startswith('+') and any(x in line for x in FOCUS_KEYWORDS):
                    comment = MESSAGES.get('forgot_focus')
                    post(f"{COMMENTS_FOR_MERGE_REQUEST_URL.replace(':iid', str(merge_request['iid']))}?body={comment}")
                    print(f'{datetime.now().strftime("%m-%dT%H:%M")}: fdescribe/fit was reported')
                    return


while True:
    check_for_focus_keyword()
    time.sleep(TWO_MINUTES)
