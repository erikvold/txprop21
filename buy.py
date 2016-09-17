#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import requests as default_requests

from two1.bitrequests import BitTransferRequests
from two1.bitrequests import ChannelRequests
from two1.bitrequests import OnChainRequests
from two1.blockchain.twentyone_provider import TwentyOneProvider
from two1.wallet import Two1Wallet


def buy():
    default_wallet_path = os.path.join(
        os.path.expanduser('~'),
        '.two1',
        'wallet',
        'default_wallet.json')
    default_data_provider = TwentyOneProvider()
    default_wallet = Two1Wallet(default_wallet_path, default_data_provider)
    logger.debug('default_wallet.balances={}'.format(default_wallet.balances))

    testnet_wallet_path = os.path.join(
        os.path.expanduser('~'),
        '.two1',
        'wallet',
        'testnet_wallet.json')
    testnet_data_provider = TwentyOneProvider(testnet=True)
    if os.path.exists(testnet_wallet_path):
        testnet_wallet = Two1Wallet(testnet_wallet_path, testnet_data_provider)
    else:
        testnet_wallet_options = {
            'wallet_path': testnet_wallet_path,
            'data_provider': testnet_data_provider,
            'testnet': True,
        }
        configured = Two1Wallet.configure(testnet_wallet_options)
        if configured:
            testnet_wallet = Two1Wallet(
                testnet_wallet_path, testnet_data_provider)
        else:
            print('Cannot configure testnet wallet')
    logger.debug('testnet_wallet.balances={}'.format(testnet_wallet.balances))

    # requests = BitTransferRequests(default_wallet, username='addy21')
    # requests = OnChainRequests(testnet_wallet)
    requests = ChannelRequests(testnet_wallet)

    # Buy http://127.0.0.1:8008
    # response = requests.request('GET', 'http://127.0.0.1:8008')

    # Buy http://127.0.0.1:8008 via hub
    # response = requests.request('GET', 'http://127.0.0.1:8000/addy21/app')

    # Buy https://apps.21.co/klouttwitter/score
    # data = {'usernames': ['balajis', 'bhorowitz', 'pmarca']}
    # response = requests.request(
    #     'POST',
    #     'https://apps.21.co/klouttwitter/score',
    #     json=data)

    # Buy http://127.0.0.1:8008 via hub
    data = {'values': ['v5910', 'v7.1', 'v128']}
    response = requests.request(
        'POST',
        'http://127.0.0.1:8000/addy21/app',
        json=data)

    # Buy stage
    # requests = ChannelRequests(default_wallet)
    # response = requests.request(
    #     'GET',
    #     'https://mkt.21-stage.co/21dotco_stage/zip-code-data/zipdata/collect?zip_code=94109')

    # Buy prod
    # requests = ChannelRequests(default_wallet)
    # response = requests.request(
    #     'GET',
    #     'https://mkt.21.co/21dotco/zip_code_data/zipdata/collect?zip_code=94109')

    # Buy prod behind 21 sell
    # requests = BitTransferRequests(default_wallet, username='addy21')
    # response = requests.request(
    #     'GET',
    #     'https://mkt.21.co/jagra/ping21-tumbleweed/ping/?uri=21.co')

    # GET http://127.0.0.1:6002 via hub
    # response = default_requests.get('http://127.0.0.1:8000/addy21/app')

    # GET stage
    # response = default_requests.get(
    #     'https://mkt.21-stage.co/21dotco_stage/zip-code-data/zipdata/collect?zip_code=94109')

    # Buy prod
    # requests = OnChainRequests(default_wallet)
    # data = {'text': 'How are you?'}
    # response = requests.request(
    #     'POST',
    #     'https://mkt.21.co/21dotco/language_detection/detect_lang/text',
    #     json=data)

    logger.debug('response.status_code={}'.format(response.status_code))
    logger.debug('response.content={}'.format(response.content))


if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    buy()
