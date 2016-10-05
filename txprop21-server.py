#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import signal
import yaml
from argparse import ArgumentParser
from flask import Flask
from flask import jsonify
from flask import request
from werkzeug.contrib.cache import MemcachedCache

from two1.bitserv.flask import Payment
from two1.blockchain.twentyone_provider import TwentyOneProvider
from two1.wallet import Two1Wallet

from txprop21 import mempool
from txprop21 import txprop21

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

app = Flask(__name__)
cache = MemcachedCache()

data_provider = TwentyOneProvider(testnet=True)
wallet_path = os.path.join(
    os.path.expanduser('~'),
    '.two1',
    'wallet',
    'testnet_wallet_1.json')
wallet = Two1Wallet(wallet_path, data_provider)
# data_provider = TwentyOneProvider()
# wallet_path = os.path.join(
#     os.path.expanduser('~'),
#     '.two1',
#     'wallet',
#     'default_wallet.json')

wallet = Two1Wallet(wallet_path, data_provider)

payment = Payment(app, wallet, zeroconf=True)

DEFAULT_PRICE = 5000
BULK_PRICE = 10


def get_limit(request):
    limit = request.args.get('limit', 1)
    try:
        limit = int(limit)
    except ValueError:
        limit = 1
    limit = min(max(limit, 1), 100)  # Limit must be between 1 to 100
    return limit


def get_bulk_price(request):
    limit = get_limit(request)
    return limit * BULK_PRICE


@app.route('/manifest')
def manifest():
    with open('./manifest.yaml') as f:
        content = yaml.load(f)
    return json.dumps(content)


@app.route('/')
def root():
    tx_hash = request.args.get('tx', '')

    cache_key = 'txprop21:response:{}'.format(tx_hash)
    response = cache.get(cache_key)
    if response is None:
        response = txprop21(tx_hash)
        cache.set(cache_key, response, timeout=5)

    status_code = response.get('status_code')
    data = response.get('data')

    if status_code == 200:
        return tx(data)
    return jsonify(data), status_code


@payment.required(DEFAULT_PRICE)
def tx(data):
    logger.debug('headers={}, data={}'.format(request.headers.to_list(), data))
    return jsonify(data)


@app.route('/unconfirmed-txs')
@payment.required(get_bulk_price)
def unconfirmed_txs():
    limit = get_limit(request)
    txs = []
    for tx_hash in mempool()[:limit]:
        response = txprop21(tx_hash)
        status_code = response.get('status_code')
        data = response.get('data')
        if status_code != 200:
            continue
        logger.debug('data={}'.format(data))
        txs.append(data)
    return jsonify(txs)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--port', default=8008)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    program = os.path.basename(__file__)
    app.run(host='::', port=args.port, debug=True)
