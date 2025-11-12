#!/usr/bin/env python3
# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
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
    package_data={'wlpd.plugins': ['*/api.yml']},
    entry_points={
        'console_scripts': [
            f'{NAME}=wlpd.main:main',
        ],
        'wlpd_plugins': [
            'fleet = wlpd.plugins.fleet.plugin:Plugin',
            'pilot = wlpd.plugins.pilot.plugin:Plugin',
            'status = wlpd.plugins.status.plugin:Plugin',
        ],
    },
)
