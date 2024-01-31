#!/usr/bin/env python3
# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

NAME = 'voipctl'
setup(
    name=NAME,
    version='1.0',
    author='Wazo Authors',
    description='Wazo Load API',
    author_email='dev@wazo.io',
    url='https://wazo-platform.org',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            f'{NAME}=modules.baresip:main',
        ],
    },
)
