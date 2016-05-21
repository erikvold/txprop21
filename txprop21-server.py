#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import signal
import subprocess
import sys
import yaml
from flask import Flask, request
from logging.handlers import RotatingFileHandler

from two1.bitserv.flask import Payment
from two1.wallet import Wallet

from txprop21 import txprop21

app = Flask(__name__)
wallet = Wallet()
payment = Payment(app, wallet)


@app.route('/manifest')
def manifest():
    with open('./manifest.yaml', 'r') as f:
        content = yaml.load(f)
    return json.dumps(content)


@app.route('/')
def root():
    tx_hash = request.args.get('tx', '')
    (status_code, data) = txprop21(tx_hash)
    if status_code == 200:
        return tx(data)
    else:
        error = {'error_message': data}
        return json.dumps(error, indent=4), status_code


@payment.required(5)
def tx(data):
    return json.dumps(data, indent=4, sort_keys=True)


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


if __name__ == '__main__':
    program = os.path.basename(__file__)

    pid_file = './{}.pid'.format(program)
    if is_running(pid_file):
        pid = int(open(pid_file).read())
        os.kill(pid, signal.SIGTERM)
    open(pid_file, 'w').write(str(os.getpid()))

    # `werkzeug` is Flask's underlying module.
    logger = logging.getLogger('werkzeug')
    handler = RotatingFileHandler('access.log', maxBytes=2097152, backupCount=6)
    logger.addHandler(handler)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=8008, threaded=True)
