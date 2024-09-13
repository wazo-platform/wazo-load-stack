# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fabric import ThreadingGroup
from fastapi import APIRouter, Depends

from .dependencies import get_config

router = APIRouter()


@router.get('/fleet/start')
async def start(config: dict = Depends(get_config)):
    '''
    Connects to all trafgen VM and start the container fleet
    '''
    hostnames = config.get('gateways') or []

    cmd = 'docker compose -f /etc/trafgen/docker-compose.yml up -d'
    results = ThreadingGroup(*hostnames).run(cmd)  # Not async do something
    for hostname, result in results.items():
        print(f'ran {result.command} on {hostname}')

    return {'message': 'success'}
