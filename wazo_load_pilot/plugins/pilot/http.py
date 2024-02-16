# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import datetime
import traceback
import uuid

from fastapi.routing import APIRouter

from .pilot import WorkloadProcessor
from .services import load_registry

router = APIRouter()


async def start_orchestrator(data, load_id):
    from .services import cluster

    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        work_load_processor = WorkloadProcessor(cluster=cluster, uuid=load_id)
        await load_registry.add_load(
            load_id, data, work_load_processor, str(start_time)
        )
    except Exception:
        traceback.print_exc()

    await work_load_processor.orchestrator(data)


@router.post("/process-load")
async def process_load(data: dict):
    print(f"RECEIVED THIS PAYLOAD ========= {data}")

    load_id = uuid.uuid4()
    asyncio.create_task(start_orchestrator(data, load_id))

    message = (
        f"Load processing started. To get status, "
        f"use the following endpoint: /status/{load_id}"
    )
    return {"message": message}


@router.get("/list-loads")
async def list_loads():
    print(f"REGISTRY OBJECT = {load_registry}")
    registry = await load_registry.get_registry()
    print(f"=======   {registry}")
    return {"loads_in_registry": registry}


@router.post("/delete-load")
async def delete_load(data):
    await load_registry.delete_load(data['uuid'])
    message = (
        f"load with uuid: {data['uuid']} has been deleted"
        "jobs in progress will be completed by the way."
    )
    return {"message": message}


@router.get("/clean-registry")
async def clean_registry():
    await load_registry.check_and_delete_invalid_entries()
    return {"message": "registry has been cleaned up"}
