#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import json
import logging
import os
import requests
import time

logger = logging.getLogger(__name__)


class RpcError(Exception):
    pass


class BitcoinClient(object):

    def __init__(self, config=None):
        if config is None:
            conf_file = 'rpc_client.conf'
            if not os.path.isfile(conf_file):
                raise RpcError('{} does not exist'.format(conf_file))
            conf = configparser.ConfigParser()
            conf.read(conf_file)
            config = dict(
                HOST=conf.get('BITCOIN', 'HOST'),
                PORT=conf.get('BITCOIN', 'PORT'),
                COOKIE=conf.get('BITCOIN', 'COOKIE'),
            )

        cookie = config.get('COOKIE')
        if cookie:
            if cookie.startswith('~'):
                cookie = cookie.replace('~', os.path.expanduser('~'))
            if os.path.isfile(cookie):
                username, password = open(cookie).read().split(':')
            else:
                raise RpcError('{} does not exist'.format(cookie))
        else:
            raise RpcError('COOKIE not set')

        self.host = config.get('HOST')
        self.port = config.get('PORT')
        self.auth = (username, password)
        self.headers = {'content-type': 'application/json'}
        self.url = None
        self.session = None

    def _post(self, session, data, max_retries=10):
        if self.session is None:
            self.session = requests.Session()
            self.url = 'http://{}:{}/'.format(self.host, self.port)
            session = self.session

        retries = max_retries
        while retries > 0:
            try:
                return session.post(
                    self.url, auth=self.auth, headers=self.headers, data=data)
            except requests.exceptions.RequestException:
                logger.warn('retry data=%s', data)
                time.sleep(0.1)
            retries -= 1
        return None

    def rpc(self, cmd, **kwargs):
        params = kwargs.get('params', [])
        data = json.dumps({
            'id': str(int(time.time() * 1e6)),
            'jsonrpc': '1.0',
            'method': cmd,
            'params': params,
        })

        session = kwargs.get('session', self.session)
        response = self._post(session, data)
        if response is None:
            raise RpcError('No response')
        if response.status_code in (401, 403):
            raise RpcError('Unauthorized')
        json_data = response.json()

        logger.debug('[%s] cmd=%s, params=%s', self.url, cmd, params)
        error = json_data.get('error', None)
        if error:
            if isinstance(error, dict):
                error = error.get('message')
            raise RpcError(error)
        result = json_data.get('result', None)
        return result

    def getinfo(self, **kwargs):
        cmd = 'getinfo'
        info = self.rpc(cmd, **kwargs)
        return info

    def getblockcount(self, **kwargs):
        cmd = 'getblockcount'
        block_count = self.rpc(cmd, **kwargs)
        return block_count

    def getbestblockhash(self, **kwargs):
        cmd = 'getbestblockhash'
        block_hash = self.rpc(cmd, **kwargs)
        return block_hash

    def getblock(self, hash, **kwargs):
        cmd = 'getblock'
        kwargs.update(dict(params=[hash]))
        block = self.rpc(cmd, **kwargs)
        return block

    def getblockhash(self, index, **kwargs):
        cmd = 'getblockhash'
        kwargs.update(dict(params=[index]))
        block_hash = self.rpc(cmd, **kwargs)
        return block_hash

    def getrawtransaction(self, txid, **kwargs):
        cmd = 'getrawtransaction'
        kwargs.update(dict(params=[txid, 1]))
        try:
            transaction = self.rpc(cmd, **kwargs)
        except RpcError as err:
            if str(err) == 'No information available about transaction':
                return None
            raise
        return transaction

    def sendrawtransaction(self, hexstring, **kwargs):
        cmd = 'sendrawtransaction'
        kwargs.update(dict(params=[hexstring]))
        transaction = self.rpc(cmd, **kwargs)
        return transaction

    def getrawmempool(self, **kwargs):
        """Return txs in mempool with min. fees of 0.00001 BTC/kB and max. age
        of 1 hour."""
        cmd = 'getrawmempool'
        mempoolminfee = kwargs.pop('mempoolminfee', 0.00001)
        mempoolmaxage = kwargs.pop('mempoolmaxage', 3600)
        kwargs.update(dict(params=[True]))
        unconfirmed_txs = self.rpc(cmd, **kwargs)
        txs = []
        now = int(time.time())
        for txid, mem in unconfirmed_txs.items():
            if now - mem['time'] > mempoolmaxage:
                continue
            if mem['fee'] < mempoolminfee:
                continue
            txs.append((txid, mem))
        return txs


def main():
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    rpc = BitcoinClient()
    best_block_hash = rpc.getbestblockhash()
    print(best_block_hash)

    mempool = rpc.getrawmempool()
    print(mempool[:3])


if __name__ == '__main__':
    main()
