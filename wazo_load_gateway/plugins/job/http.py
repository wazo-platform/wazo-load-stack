# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import uuid

from fastapi import APIRouter
from .services import run

router = APIRouter()

@router.post("/run")
async def run_load(payload: dict):
    try:
        command = payload["cmd"]
    except KeyError:
        return {"status": "internal_error", "error": str(e)}
    
    try:
        await run(command)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "internal_error", "error": str(e)}
