# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy

_DEFAULT_HTTPS_PORT = 9990

_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-load-pilot/config.yml',
    'debug': False,
    'extra_config_files': '/etc/wazo-load-pilot/conf.d',
    'log_file': '/var/log/wazo-load-pilot.log',
    'log_level': 'info',
    'user': 'wazo-pilot',
    'rest_api': {
        'listen': '0.0.0.0',
        'port': _DEFAULT_HTTPS_PORT,
        'certificate': None,
        'private_key': None,
        'cors': {
            'enabled': True,
            'allow_headers': ['Content-Type', 'X-Auth-Token'],
        },
        'max_threads': 10,
    },
    'load_cluster': {
        'protocol': 'http',
        'host': 'trafgen.load.wazo.io',
        'port': '9999',
    },
    'gateways': [
        'trafgen1.load.wazo.io',
        'trafgen2.load.wazo.io',
        'trafgen3.load.wazo.io',
        'trafgen4.load.wazo.io',
        'trafgen5.load.wazo.io',
        'trafgen6.load.wazo.io',
        'trafgen7.load.wazo.io',
        'trafgen8.load.wazo.io',
        'trafgen9.load.wazo.io',
        'trafgen10.load.wazo.io',
    ],
    'enabled_plugins': {
        'pilot': True,
        'status': True,
    },
    'certs': {
        'csr': '/etc/wazo-load-pilot/certificate.csr',
        'cert': '/etc/wazo-load-pilot/certificate.pem',
        'key': '/etc/wazo-load-pilot/private.key',
    },
    'docker':{
        'registry': 'registry.load.wazo.io',
        'registry_port': '5000',
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
