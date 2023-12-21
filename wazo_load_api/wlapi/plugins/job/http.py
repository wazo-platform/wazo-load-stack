# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from fastapi import APIRouter, HTTPException

from .services import run

router = APIRouter()


@router.post("/run")
async def run_load(payload: dict):
    try:
        command = payload['cmd']
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )

    env = os.environ
    environ = payload.get('env')
    if environ:
        for key in environ:
            env[key] = str(environ[key])

    try:
        await run(command, env)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )

    return {"status": "ok"}
