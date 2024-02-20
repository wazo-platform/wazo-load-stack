#!/usr/bin/env python3
# Copyright 2023-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

setup(
    name='wlctl',
    version='1.0.0',
    description='Wazo Load CLI',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    py_modules=['wlctl'],
    install_requires=[
        'Click',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wlctl = wlctl.main:cli',
        ],
    },
)
