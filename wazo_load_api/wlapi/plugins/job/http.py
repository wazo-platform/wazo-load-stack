# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import traceback

from fastapi import APIRouter, HTTPException

from .services import run

router = APIRouter()


@router.post("/run")
async def run_load(payload: dict):
    try:
        command = payload['cmd']
    except KeyError as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail={'status': 'internal_error', 'error': str(e)}
        )

    env = os.environ
    environ = payload.get('env')
    if environ:
        for key in environ:
            env[key] = str(environ[key])
    print(f"ENVIRON IS TYPE OF ============= {type(environ)}")
    try:
        print(f"COMMAND TO BE RUN ============ {command} with ENVIRONNMENT {environ}")
        result = await run(command, environ)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={'status': 'internal_error', 'output': result, 'error': str(e)},
        )

    return {"status": "ok"}
