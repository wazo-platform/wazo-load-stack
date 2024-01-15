#!/usr/bin/env python3
# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

NAME = 'wlpd'
setup(
    name=NAME,
    version='1.0',
    author='Wazo Authors',
    description='Wazo Load Pilot',
    author_email='dev@wazo.io',
    url='https://wazo-platform.org',
    packages=find_packages(),
    package_data={'plugins': ['*/api.yml']},
    entry_points={
        'console_scripts': [
            f'{NAME}=main:main',
        ],
        'wlpd_plugins': [
            'cluster = plugins.cluster.plugin:Plugin',
            'pilot = plugins.pilot.plugin:Plugin',
            'status = plugins.status.plugin:Plugin',
        ],
    },
)
