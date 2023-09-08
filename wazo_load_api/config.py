# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy

_DEFAULT_HTTPS_PORT = 9900

_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-load-api/config.yml',
    'debug': False,
    'extra_config_files': '/etc/wazo-load-api/conf.d',
    'log_file': '/var/log/wazo-load-api.log',
    'log_level': 'info',
    'user': 'wazo-api',
    'rest_api': {
        'listen': '0.0.0.0',
        'port': _DEFAULT_HTTPS_PORT,
        'certificate': '/etc/wazo-load-api/certificate.pem',
        'private_key': '/etc/wazo-load-api/private.key',
        'cors': {
            'enabled': True,
            'allow_headers': ['Content-Type'],
        },
        'max_threads': 10,
    },
    'enabled_plugins': {
        'job': True,
        'status': True,
    },
    'certs': {
        'csr': '/etc/wazo-load-api/certificate.csr',
        'cert': '/etc/wazo-load-api/certificate.pem',
        'key': '/etc/wazo-load-api/private.key',
    },
}


def load_config(args):
    cli_config = _parse_cli_args(args)
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    return ChainMap(file_config, _DEFAULT_CONFIG)


def _parse_cli_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config-file', action='store', help='The path to the config file'
    )
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Log debug mesages. Override log_level',
    )
    parser.add_argument('-u', '--user', action='store', help='The owner of the process')
    parsed_args = parser.parse_args(argv)

    result = {}
    if parsed_args.config_file:
        result['config_file'] = parsed_args.config_file
    if parsed_args.debug:
        result['debug'] = parsed_args.debug
    if parsed_args.user:
        result['user'] = parsed_args.user

    return result
