#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import requests as default_requests
import threading
import time
from collections import defaultdict

from two1.bitrequests import BitTransferRequests
from two1.bitrequests import ChannelRequests
from two1.bitrequests import OnChainRequests
from two1.blockchain.twentyone_provider import TwentyOneProvider
from two1.channels.paymentchannel import NotReadyError
from two1.server.rest_client import TwentyOneRestClient
from two1.wallet import Two1Wallet
from two1.wallet import Wallet

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class TestBuy(object):

    @classmethod
    def setup_class(cls):
        pass

    def setup_method(self):
        self.default_data_provider = TwentyOneProvider()
        self.testnet_data_provider = TwentyOneProvider(testnet=True)

        self.testnet = False

        # `21 login`
        self.username = os.environ.get('TWO1_USERNAME')
        self.password = os.environ.get('TWO1_PASSWORD')

    def create_new_wallet(self, filename):
        path = os.path.join(
            os.path.expanduser('~'), '.two1', 'wallet', filename)
        if os.path.exists(path):
            return False
        data_provider = self.default_data_provider
        if self.testnet:
            data_provider = self.testnet_data_provider
        options = {
            'wallet_path': path,
            'data_provider': data_provider,
            'testnet': self.testnet,
        }
        configured = Two1Wallet.configure(options)
        if configured:
            return True
        return False

    def load_wallet(self, filename=None, mnemonic=None):
        data_provider = self.default_data_provider
        account_type = Two1Wallet.DEFAULT_ACCOUNT_TYPE
        if self.testnet:
            data_provider = self.testnet_data_provider
            account_type = 'BIP44Testnet'
        if filename:
            path = os.path.join(
                os.path.expanduser('~'), '.two1', 'wallet', filename)
            return Two1Wallet(path, data_provider)
        else:
            return Two1Wallet.import_from_mnemonic(
                data_provider=data_provider,
                mnemonic=mnemonic,
                account_type=account_type)

    def spread_utxos(self, wallet, threshold=10000000):
        confirmed = wallet.balances['confirmed']
        if confirmed < threshold:
            return None
        num_addresses = min(100, int(confirmed / threshold))
        txids = wallet.spread_utxos(threshold, num_addresses)
        return txids

    def wallet_stats(self, wallet, verbose=False):
        logger.info('.'*30 + '   [wallet_stats]   ' + '.'*30)
        wallet.sync_accounts()
        total = wallet.balances['total']
        confirmed = wallet.balances['confirmed']
        logger.info('wallet.balances = {} (total - confirmed = {})'.format(
            wallet.balances, total - confirmed))
        if verbose:
            utxos_by_addr = wallet.get_utxos(include_unconfirmed=True)
            for addr, utxos in utxos_by_addr.items():
                logger.info('addr = {}'.format(addr))
                for utxo in utxos:
                    logger.info(
                        '\t'
                        'utxo.num_confirmations = {}, '
                        'utxo.transaction_hash = {}, '
                        'utxo.outpoint_index = {}, '
                        'utxo.value = {}'.format(
                            utxo.num_confirmations,
                            utxo.transaction_hash,
                            utxo.outpoint_index,
                            utxo.value))
        logger.info(
            'wallet.current_address = {}'.format(wallet.current_address))
        logger.info('.'*80 + '\n')

    def wallet_earnings(self, wallet):
        requests = BitTransferRequests(wallet, self.username)
        requests.client.login(wallet.current_address, self.password)
        earnings = requests.client.get_earnings()
        return earnings

    def validate_response(self, response):
        assert response is not None
        logger.info('\n')
        if response.status_code == 200:
            logger.info('status_code = {}'.format(response.status_code))
            logger.info('content = {}'.format(response.content))
        else:
            logger.info('!'*30 + '      [FAILED]      ' + '!'*30)
            logger.info('status_code = {}'.format(response.status_code))
            logger.info('content = {}'.format(response.content))
            logger.info('!'*30 + '      [FAILED]      ' + '!'*30)
        logger.info('\n')


class TestBuyTestnet(TestBuy):

    def setup_method(self):
        logger.info('*** TestBuyTestnet ***')
        super().setup_method()
        self.testnet = True

    def test_buy_channel(self):
        logger.info('#'*30 + '  test_buy_channel  ' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_4.json')
        self.wallet_stats(wallet)

        requests = ChannelRequests(wallet)
        response = requests.request('GET', 'http://127.0.0.1:8008')
        self.validate_response(response)

        self.wallet_stats(wallet)

    def test_buy_onchain(self):
        logger.info('#'*30 + '  test_buy_onchain  ' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_2.json')
        self.wallet_stats(wallet)

        requests = OnChainRequests(wallet)
        response = requests.request('GET', 'http://127.0.0.1:8000')
        self.validate_response(response)

        self.wallet_stats(wallet)

    def test_buy_hub_channel(self):
        logger.info('#'*30 + 'test_buy_hub_channel' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_4.json')
        self.wallet_stats(wallet)

        requests = ChannelRequests(wallet)
        response = requests.request(
            'GET', 'http://127.0.0.1:16000/21dotco/merchant')
        self.validate_response(response)

        self.wallet_stats(wallet)

    def test_buy_hub_file(self):
        logger.info('#'*30 + ' test_buy_hub_file  ' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_4.json')
        self.wallet_stats(wallet)

        requests = OnChainRequests(wallet)

        data = {'values': [12, 8]}
        files = {'file': open('access.log', 'rb')}
        response = requests.request(
            'POST',
            'http://127.0.0.1:16000/21dotco/merchant',
            json=data,
            files=files)

        self.validate_response(response)

        self.wallet_stats(wallet)

    def channels(self):
        logger.info('#'*30 + '      channels      ' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_4.json')
        requests = ChannelRequests(wallet)
        for channel_url in requests._channelclient.list():
            logger.info('channel_url: {}'.format(channel_url))

    def open_channel(self):
        logger.info('#'*30 + '    open_channel    ' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_4.json')

        requests = ChannelRequests(wallet)
        channel_url = requests._channelclient.open(
            'http://127.0.0.1:17000/payment',
            100000,
            86400 * 8,
            zeroconf=True,
            use_unconfirmed=True)
        logger.info('channel_url: {}'.format(channel_url))

        self.wallet_stats(wallet)

    def close_channel(self, channel_url=None):
        logger.info('#'*30 + '   close_channel    ' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_4.json')

        requests = ChannelRequests(wallet)
        if channel_url is None:
            channel_url = requests._channelclient.list()[0]
        requests._channelclient.close(channel_url)

        self.wallet_stats(wallet)

    def sync_channel(self, channel_url=None):
        logger.info('#'*30 + '    sync_channel    ' + '#'*30)
        wallet = self.load_wallet('testnet_wallet_4.json')

        requests = ChannelRequests(wallet)
        requests._channelclient.sync(url=channel_url)

        self.wallet_stats(wallet)


class TestBuyMainnet(TestBuy):

    def setup_method(self):
        logger.info('*** TestBuyMainnet ***')
        super().setup_method()
        self.testnet = False

    def test_buy_channel(self):
        logger.info('#'*30 + '  test_buy_channel  ' + '#'*30)
        wallet = self.load_wallet('default_wallet.json')
        self.wallet_stats(wallet, verbose=True)

        requests = ChannelRequests(wallet)
        url = 'https://mkt.21.co/21dotco/zip_code_data/zipdata/collect'
        info = requests.get_402_info(url)
        logger.info('info = {}'.format(info))

        payment_server = info.get('bitcoin-payment-channel-server')
        for zip_code in ['94109', '08015', '07728']:
            while True:
                try:
                    response = requests.request(
                        'GET', url, params=dict(zip_code=zip_code))
                except NotReadyError as e:
                    logging.info(str(e))
                    time.sleep(60)
                else:
                    channel_url = requests._channelclient \
                        .list(payment_server)[0]
                    channel_balance = requests._channelclient \
                        .status(channel_url).balance
                    self.validate_response(response)
                    logger.info('channel_balance = {}'.format(channel_balance))
                    break

        self.wallet_stats(wallet)

    def test_buy_onchain(self):
        logger.info('#'*30 + '  test_buy_onchain  ' + '#'*30)
        wallet = self.load_wallet('default_wallet.json')
        self.wallet_stats(wallet)

        requests = OnChainRequests(wallet)
        url = 'https://mkt.21.co/21dotco/expand_url/short_url/expand?short_url=http://bit.ly/1WNmMH7'
        info = requests.get_402_info(url)
        logger.info('info = {}'.format(info))
        response = requests.request('GET', url)
        self.validate_response(response)

        self.wallet_stats(wallet)

    def test_buy_offchain(self):
        logger.info('#'*30 + ' test_buy_offchain  ' + '#'*30)
        wallet = self.load_wallet('default_wallet.json')
        logger.info('earnings = {}'.format(self.wallet_earnings(wallet)))

        requests = BitTransferRequests(wallet)
        url = 'https://mkt.21.co/21dotco/zip_code_data/zipdata/collect?zip_code=94109'
        info = requests.get_402_info(url)
        logger.info('info = {}'.format(info))
        response = requests.request('GET', url)
        self.validate_response(response)

        logger.info('earnings = {}'.format(self.wallet_earnings(wallet)))

    def test_buy_stage_channel(self):
        logger.info('#'*25 + '    test_buy_stage_channel    ' + '#'*25)
        wallet = self.load_wallet('default_wallet.json')
        self.wallet_stats(wallet, verbose=True)

        requests = ChannelRequests(wallet)
        url = 'https://mkt.21-stage.co/21dotco_stage/zip-code-data/zipdata/collect'
        info = requests.get_402_info(url)
        logger.info('info = {}'.format(info))

        payment_server = info.get('bitcoin-payment-channel-server')
        for zip_code in ['94109', '08015', '07728']:
            while True:
                try:
                    response = requests.request(
                        'GET', url, params=dict(zip_code=zip_code))
                except NotReadyError as e:
                    logging.info(str(e))
                    time.sleep(60)
                else:
                    channel_url = requests._channelclient \
                        .list(payment_server)[0]
                    channel_balance = requests._channelclient \
                        .status(channel_url).balance
                    self.validate_response(response)
                    logger.info('channel_balance = {}'.format(channel_balance))
                    break

        self.wallet_stats(wallet)

    def open_prod_channel(self):
        logger.info('#'*30 + ' open_prod_channel  ' + '#'*30)
        wallet = self.load_wallet('default_wallet.json')

        requests = ChannelRequests(wallet)
        channel_url = requests._channelclient.open(
            'https://mkt.21.co/payment/', 100000, 86400 * 8)
        logger.info('channel_url: {}'.format(channel_url))

    def open_stage_channel(self):
        logger.info('#'*30 + ' open_stage_channel ' + '#'*30)
        wallet = self.load_wallet('default_wallet.json')

        requests = ChannelRequests(wallet)
        channel_url = requests._channelclient.open(
            'https://mkt.21-stage.co/payment/', 100000, 86400 * 8)
        logger.info('channel_url: {}'.format(channel_url))


if __name__ == '__main__':
    # testnet
    tc = TestBuyTestnet()
    tc.setup_method()
    tc.test_buy_channel()

    tc.setup_method()
    tc.test_buy_onchain()

    tc.setup_method()
    tc.test_buy_hub_channel()

    tc.setup_method()
    tc.test_buy_hub_file()

    # mainnet
    tc = TestBuyMainnet()
    tc.setup_method()
    tc.test_buy_channel()

    tc.setup_method()
    tc.test_buy_onchain()

    tc.setup_method()
    tc.test_buy_offchain()

    tc.setup_method()
    tc.test_buy_stage_channel()
