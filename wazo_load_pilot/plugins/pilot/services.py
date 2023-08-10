# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

gateways = []


def set_gateways(config):
    global gateways
    gateways = config['gateways']
