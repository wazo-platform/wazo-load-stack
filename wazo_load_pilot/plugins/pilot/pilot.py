# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

from .commands import ShellCmdFactory
from .services import cluster

semaphore = asyncio.Semaphore(1000)


def get_command(node):
    if 'cmd' not in node:
        raise KeyError('Missing required key "cmd"')
    command = node['cmd']
    print(f"COMMAND TO SEND --------------- {command}")

    env = node.get('env')
    shell_factory: ShellCmdFactory = ShellCmdFactory(
        cmd=command, env=env, cluster=cluster
    )
    return shell_factory.new()


async def process_node(node, ttl):
    """
    Coroutine that connects, processes and disconnect from the remote host. Connection duration
    is based on the TTL
    """
    print(f"LOAD READY TO PROCESS +++++++++ {node}")

    try:
        cmd = get_command(node)
        print(f"URLS FROM process_node ======= {cmd.urls}")
        # print(cmd.send())
        responses = await cmd.send()
        print(f"SEND RETURNED ----------------- {responses}")

        # Await on the TTL
        await asyncio.sleep(ttl)

    except Exception as e:
        print(f"An error occurred in process_node: {str(e)}")


async def process_load(load):
    """
    Coroutine that processes a workload by creating a process_node coroutine for each node.
    This coroutine setup an additional queue that could be used for node coroutines
    to synchrinize.
    """

    coroutines = []

    nodes = load.get('load')
    # Loop for creating a coroutine for each node in the workload.
    for node in nodes:
        print(f"EXTRACTED NODES FROM process_load ====== {node}")
        ttl = 0
        print(f"TTL ============= {ttl}")
        async with semaphore:
            coroutine = asyncio.create_task(process_node(node, ttl))
            coroutines.append(coroutine)

    # The coroutine is waiting for all coroutines terminate
    try:
        await asyncio.gather(*coroutines)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


async def orchestrator(queue):
    """
    This coroutine consumes a queue containing the workload.
    When the orchestrator dequeue a load it sends it to the coroutine
    in charge of processing the load.
    """
    while True:
        try:
            load = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        else:
            await process_load(load)
            queue.task_done()


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
