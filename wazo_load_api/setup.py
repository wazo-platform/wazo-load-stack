#!/usr/bin/env python3
# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

NAME = 'wlapi'
setup(
    name=NAME,
    version='1.0',
    author='Wazo Authors',
    description='Wazo Load API',
    author_email='dev@wazo.io',
    url='https://wazo-platform.org',
    packages=find_packages(),
    package_data={'wlapi.plugins': ['*/api.yml']},
    entry_points={
        'console_scripts': [
            f'{NAME}=wlapi.main:main',
        ],
        'wlapi_plugins': [
            'job = wlapi.plugins.job.plugin:Plugin',
            'status = wlapi.plugins.status.plugin:Plugin',
        ],
    },
)
