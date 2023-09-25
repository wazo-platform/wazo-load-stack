# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

gateways = []
cluster = {}


def set_gateways(config):
    global gateways
    gateways = config['gateways']


def set_cluster(config):
    global cluster
    cluster = config['load_cluster']
