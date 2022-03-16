import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GITLAB_TOKEN = "Bearer oKzXz4Ek1X1pfKfdWmkB"
ENABLE_SSL_VERIFICATION = False


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
