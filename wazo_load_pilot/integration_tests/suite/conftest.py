# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from .helpers import base as base_module


def pytest_collection_modifyitems(session, config, items):
    # item == test method
    # item.parent == test class
    # item.parent.own_markers == pytest markers of the test class
    # item.parent.own_markers[0].args[0] == name of the asset
    # It also remove the run-order pytest feature (--ff, --nf)
    items.sort(key=lambda item: item.parent.own_markers[0].args[0])


@pytest.fixture(scope='session')
def base():
    base_module.BaseAssetLaunchingTestCase.setUpClass()
    try:
        yield
    finally:
        base_module.BaseAssetLaunchingTestCase.tearDownClass()


@pytest.fixture(scope='session')
def vms():
    base_module.VmsAssetLaunchingTestCase.setUpClass()
    try:
        yield
    finally:
        base_module.VmsAssetLaunchingTestCase.tearDownClass()
