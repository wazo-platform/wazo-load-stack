# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import unittest

import pytest
from wazo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase

use_asset = pytest.mark.usefixtures


class _WlpdAssetLaunchingTestCase(AssetLaunchingTestCase):
    assets_root = os.path.join(os.path.dirname(__file__), '../..', 'assets')
    service = 'wlpd'


class BaseAssetLaunchingTestCase(_WlpdAssetLaunchingTestCase):
    asset = 'base'


class VmsAssetLaunchingTestCase(_WlpdAssetLaunchingTestCase):
    asset = 'vms'


class BaseIntegrationTest(unittest.TestCase):
    asset_cls = BaseAssetLaunchingTestCase


class VmsIntegrationTest(unittest.TestCase):
    asset_cls = VmsAssetLaunchingTestCase
