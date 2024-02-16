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


async def start_orchestrator(data, load_id, scheduler_settings):
    from .services import cluster

    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # setup default parameters for the scheduler
    batch = 1
    duration = 30
    rate = 0.0
    label = ""
    if scheduler_settings:
        batch = int(scheduler_settings.get("batch", batch))
        duration = int(scheduler_settings.get("duration", duration))
        rate = float(scheduler_settings.get("rate", rate))
        label = scheduler_settings.get("label", label)

    try:
        work_load_processor = WorkloadProcessor(
            cluster=cluster, uuid=load_id, schedule_batch=batch, duration=duration
        )
        await load_registry.add_load(
            load_id, data, work_load_processor, str(start_time), label
        )
    except Exception:
        traceback.print_exc()

    await work_load_processor.orchestrator(data)


@router.post("/process-load")
async def process_load(data: dict):
    print(f"RECEIVED THIS PAYLOAD ========= {data}")

    scheduler_settings = data.get("scheduler", None)
    print(f"SCHEDULER SETTINGS :::::::: {scheduler_settings}")
    load_id = uuid.uuid4()
    asyncio.create_task(start_orchestrator(data, load_id, scheduler_settings))

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


@router.delete("/delete-load/{load_uuid}")
async def delete_load(load_uuid):
    message = ""
    result = await load_registry.delete_load(load_uuid)
    if result:
        message = (
            f"load with uuid: {load_uuid} has been deleted"
            "jobs in progress will be completed by the way."
        )
    else:
        message = "No load with this uuid was found"
    return {"message": message}


@router.get("/clean-registry")
async def clean_registry():
    await load_registry.check_and_delete_invalid_entries()
    return {"message": "registry has been cleaned up"}
