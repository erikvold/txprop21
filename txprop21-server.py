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
from flask import Response
from logging.handlers import RotatingFileHandler
from werkzeug.contrib.cache import MemcachedCache

from two1.bitserv.flask import Payment
from two1.wallet import Wallet

from txprop21 import mempool
from txprop21 import txprop21

app = Flask(__name__)
cache = MemcachedCache()
wallet = Wallet()
payment = Payment(app, wallet, zeroconf=True)

DEFAULT_PRICE = 5000
BULK_PRICE = 2000


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
    return jsonify(**data), status_code


@payment.required(DEFAULT_PRICE)
def tx(data):
    logger.debug('headers={}, data={}'.format(request.headers.to_list(), data))
    return jsonify(**data)


@app.route('/unconfirmed-txs')
@payment.required(get_bulk_price)
def unconfirmed_txs():
    """EXPERIMENTAL: Get transaction propagation data for unconfirmed txs."""
    limit = get_limit(request)

    def stream():
        txs = mempool()[:limit]
        for tx in txs:
            tx_hash = tx[0]
            response = txprop21(tx_hash)
            status_code = response.get('status_code')
            data = response.get('data')
            if status_code != 200:
                continue
            logger.debug('data={}'.format(data))
            yield json.dumps(data, indent=4, sort_keys=True) + '\n'

    return Response(stream(), mimetype='application/json')


def is_running(pid_file):
    if os.path.exists(pid_file):
        try:
            pid = int(open(pid_file).read())
        except ValueError:
            return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            os.remove(pid_file)
    return False


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--port', default=8008)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    program = os.path.basename(__file__)

    pid_file = './{}.pid'.format(program)
    if is_running(pid_file):
        pid = int(open(pid_file).read())
        os.kill(pid, signal.SIGTERM)
    open(pid_file, 'w').write(str(os.getpid()))

    handler = RotatingFileHandler(
        'access.log', maxBytes=2097152, backupCount=6)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(process)d.%(thread)d %(funcName)s >>> "
        "%(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    app.run(host='::', port=args.port, threaded=True)
