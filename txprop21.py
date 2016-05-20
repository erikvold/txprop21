#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import sys

__all__ = [
    'txprop21',
]

URL = 'https://bitnodes.21.co/api/v1/bitcoind/gettransactionpropagation/'


def txprop21(tx_hash):
    if tx_hash:
        url = '{}{}'.format(URL, tx_hash)
    else:
        url = URL
    response = requests.get(url)
    if response.status_code == 200:
        return (response.status_code, response.json())
    # e.g. (404, 'Not Found'), (500, 'Internal Server Error')
    return (response.status_code, response.reason)


if __name__ == '__main__':
    tx_hash = None
    if len(sys.argv) > 1:
        tx_hash = sys.argv[1]
    (status_code, data) = txprop21(tx_hash)
    if status_code == 200:
        print(json.dumps(data, indent=4, sort_keys=True))
    else:
        print('{}: {}'.format(status_code, data))
