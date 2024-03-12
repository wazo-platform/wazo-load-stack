# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import time
import traceback

from .commands import ShellCmdFactory
from .services import cluster, load_registry


class WorkloadProcessor:
    def __init__(
        self, cluster=cluster, uuid=None, schedule_batch=1, duration=30, delay=0.0
    ):
        self.uuid = uuid
        self.semaphore = asyncio.Semaphore()
        self.cluster = cluster
        self.cancel_event = asyncio.Event()
        self.scheduler_batch = schedule_batch
        self.start_time = int(time.time())
        self.scheduler_duration = duration
        self.scheduler_delay = delay

    async def cancel_jobs(self):
        self.cancel_event.set()

    async def get_command(self, node):
        if 'cmd' not in node:
            raise KeyError('Missing required key "cmd"')
        command = node['cmd']
        print(f"COMMAND TO SEND --------------- {command}")

        env = node.get('env')
        shell_factory = ShellCmdFactory(cmd=command, env=env, cluster=self.cluster)
        return shell_factory.new()

    async def process_node(self, node, ttl):
        print(f"LOAD READY TO PROCESS +++++++++ {node}")

        try:
            cmd = await self.get_command(node)
            print(f"URLS FROM process_node ======= {cmd.urls}")

            responses = await cmd.send()
            print(f"SEND RETURNED ----------------- {responses}")

            # Await on the TTL
            await asyncio.sleep(ttl)

        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred in process_node: {str(e)}")

    async def process_load(self, load):
        coroutines = []

        nodes = load.get('load')
        for node in nodes:
            print(f"EXTRACTED NODES FROM process_load ====== {node}")
            ttl = 0
            print(f"TTL ============= {ttl}")
            async with self.semaphore:
                coroutine = asyncio.create_task(self.process_node(node, ttl))
                coroutines.append(coroutine)

            if self.cancel_event.is_set():
                break
            await asyncio.sleep(0.2)

        try:
            await asyncio.gather(*coroutines)
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred: {str(e)}")

    async def orchestrator(self, data):
        print("******STARTING SCHEDULE*********")
        coroutines = []
        for x in range(self.scheduler_batch):
            if self.start_time + self.scheduler_duration < int(time.time()):
                print("This load has reached its deadline, it is about to terminate")
                break
            print(f"----- ITERATION #{x}")
            queue = await parse_config(data)
            print(f"PROCESSING QUEUE {queue.__str__}")
            while not queue.empty():
                if self.start_time + self.scheduler_duration < int(time.time()):
                    # This load has reached its deadline, it about to terminate
                    break
                async with self.semaphore:
                    load = queue.get_nowait()
                    queue.task_done()
                    coroutine = asyncio.create_task(self.process_load(load))
                    coroutines.append(coroutine)
                if self.cancel_event.is_set():
                    break

                await asyncio.sleep(self.scheduler_delay)

            if self.cancel_event.is_set():
                break

        try:
            await asyncio.gather(*coroutines)
            print(f"============ CLEANING entry: {self.uuid} in the load registry")
            await load_registry.delete_load(self.uuid)
            print(f"Current load registry status: {await load_registry.get_registry()}")
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred: {str(e)}")


async def parse_config(yml):
    """
    parse_config takes the config yaml file as argument.
    It processes each load and put them into the queue.
    """
    q: asyncio.Queue = asyncio.Queue()
    for load in yml["loads"]:
        print(f"LOAD  to PROCESS===== {load}")
        await q.put(load)

    return q
