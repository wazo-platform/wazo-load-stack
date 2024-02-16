# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
import asyncio

gateways = []
cluster = {}


def set_gateways(config):
    global gateways
    gateways = config['gateways']


def set_cluster(config):
    global cluster
    cluster = config['load_cluster']


def set_load_registry():
    global load_registry
    load_registry = LoadRegistry()


class LoadRegistry:
    def __init__(self) -> None:
        self.registry: dict = dict()
        self.lock = asyncio.Lock()

    async def add_load(self, uuid, payload, work_load_processor, start_time, label):
        async with self.lock:
            self.registry[str(uuid)] = {
                'payload': payload,
                'work_load_processor': work_load_processor,
                'start_time': start_time,
            }

    async def delete_work_load(self, uuid):
        async with self.lock:
            load_registry.registry[str(uuid)]['work_load_processor'] = None

    async def delete_load(self, uuid):
        async with self.lock:
            # get the instance of the orchestrator related to this uuid
            # work_load_processor = self.registry[str(uuid)]['work_load_processor']
            work_load_processor = self.registry.get(str(uuid), {}).get(
                'work_load_processor'
            )
            if work_load_processor:
                # cancel all jobs in progress
                await work_load_processor.cancel_jobs()
                # delete the entry
                del self.registry[str(uuid)]

    async def check_and_delete_invalid_entries(self):
        async with self.lock:
            for uuid, data in list(self.registry.items()):
                workload_processor = data.get('work_load_processor')
                if workload_processor is None:
                    print(
                        f"WorkloadProcessor not found for UUID: {uuid}. Removing entry."
                    )
                    del self.registry[uuid]

    async def get_registry(self):
        async with self.lock:
            return self.registry


global load_registry
load_registry = LoadRegistry()
