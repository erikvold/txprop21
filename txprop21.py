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
        url = '{}{}/'.format(URL, tx_hash)
    else:
        url = URL
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        data = dict(error_message=response.reason)
    return dict(status_code=response.status_code, data=data)


if __name__ == '__main__':
    tx_hash = None
    if len(sys.argv) > 1:
        tx_hash = sys.argv[1]
    response = txprop21(tx_hash)
    print(json.dumps(response, indent=4, sort_keys=True))
