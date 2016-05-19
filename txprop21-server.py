#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import json
import os
import signal
import subprocess
import sys
import yaml

from flask import Flask, request

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
        return data, status_code


@payment.required(5)
def tx(data):
    return json.dumps(data, indent=4, sort_keys=True)


def is_running(pid_file):
    if os.path.exists(pid_file):
        pid = int(open(pid_file).read())
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            os.remove(pid_file)
    return False


@click.command()
@click.option(
    '-d',
    '--daemon',
    default=False,
    is_flag=True,
    help='Run in daemon mode.'
)
def run(daemon):
    filename = os.path.basename(__file__)
    if daemon:
        pid_file = './{}.pid'.format(filename)
        if is_running(pid_file):
            pid = int(open(pid_file).read())
            os.kill(pid, signal.SIGTERM)
        try:
            p = subprocess.Popen([sys.executable, filename])
        except subprocess.CalledProcessError as err:
            raise ValueError('Error starting {}: {}'.format(filename, err))
        else:
            open(pid_file, 'w').write(str(p.pid))
    else:
        print('Server running...')
        app.run(host='0.0.0.0', port=8008)


if __name__ == '__main__':
    run()
