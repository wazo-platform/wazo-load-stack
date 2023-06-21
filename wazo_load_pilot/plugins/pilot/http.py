# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import uuid

from fastapi.routing import APIRouter

router = APIRouter()

async def start_orchestrator(q):
    from .pilot import orchestrator
    await orchestrator(q)

@router.post("/process-load")
async def process_load(data: dict):
    from .pilot import parse_config
    q = parse_config(data)

    # load ID for tracking progress will be implemented in the next story.
    load_id = uuid.uuid4()

    loop = asyncio.get_event_loop()
    loop.create_task(start_orchestrator(q))

    return {"message": f"Load processing started. To get status, use the following endpoint: /status/{load_id}"}
