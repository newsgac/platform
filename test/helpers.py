from pprint import pformat

import requests

import logging

logger = logging.getLogger(__name__)


def is_valid_html(page):
    url = 'https://validator.w3.org/nu/?out=json'
    headers = {'Content-Type': 'text/html; charset=utf-8'}
    files = {'file': ('index.html', page)}
    r = requests.post(url, files=files, headers=headers)
    messages = r.json()['messages']
    errors = list(filter(lambda message: message['type'] == 'error', messages))
    warnings = list(filter(lambda message: message.get('subType', None) == 'warning', messages))
    others = list(filter(lambda message: message['type'] != 'error' and message.get('subType', None) != 'warning', messages))

    levels = [
        (errors, logger.error),
        (warnings, logger.warning),
        (others, logger.info)
    ]

    for collection, func in levels:
        func(pformat(collection))

    return False if errors else True
