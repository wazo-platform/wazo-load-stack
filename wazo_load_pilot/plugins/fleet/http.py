# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

import asyncssh
from fastapi import APIRouter, Depends, HTTPException

from .dependencies import get_config

router = APIRouter()


async def run_command(host, command: str) -> asyncssh.SSHCompletedProcess:
    async with asyncssh.connect(host, known_hosts=None) as conn:
        return await conn.run(command)


async def run_on_all_gateways(config: dict, command: str) -> dict:
    hostnames = config.get('gateways') or []
    tasks = (run_command(host, command) for host in hostnames)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print('Task %d failed: %s', i, str(result))
            raise HTTPException(status_code=500, detail=str(result))
        elif result.exit_status != 0:
            print('Task %d exited with status %s', i, result.exit_status)
            raise HTTPException(status_code=500, detail=str(result))
        else:
            print('Task %d succeeded', i)

    return {'message': 'success'}


@router.get('/fleet/start')
async def start(config: dict = Depends(get_config)):
    '''
    Connects to all trafgen VM and start the container fleet
    '''
    cmd = 'docker compose -f /etc/trafgen/docker-compose.yml up -d'
    result = await run_on_all_gateways(config, cmd)
    return result


@router.get('/fleet/stop')
async def stop(config: dict = Depends(get_config)):
    '''
    Connects to all trafgen VM and stops the container fleet
    '''
    cmd = 'docker compose -f /etc/trafgen/docker-compose.yml down'
    result = await run_on_all_gateways(config, cmd)
    return result
