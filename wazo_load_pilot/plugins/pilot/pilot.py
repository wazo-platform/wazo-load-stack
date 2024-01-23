# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

from .commands import ShellCmdFactory
from .services import cluster


def get_command(node):
    if 'cmd' not in node:
        raise KeyError('Missing required key "cmd"')
    command = node['cmd']
    env = node.get('env')
    shell_factory: ShellCmdFactory = ShellCmdFactory(
        cmd=command, env=env, cluster=cluster
    )
    return shell_factory.new()


async def process_node(node, ttl, channel):
    """
    Coroutine that connects, processes and disconnect from the remote host. Connection duration
    is based on the TTL
    """
    # channel not used yet

    cmd = get_command(node)
    print(cmd.send())

    # Await on the TTL
    await asyncio.sleep(ttl)


async def process_load(load):
    """
    Coroutine that processes a workload by creating a process_node coroutine for each node.
    This coroutine setup an additional queue that could be used for node coroutines
    to synchrinize.
    """

    coroutines = []

    # create a queue that will allow coroutine to send status.
    q: asyncio.Queue = asyncio.Queue()

    nodes = load.get('load')
    # Loop for creating a coroutine for each node in the workload.
    for node in nodes:
        ttl = load.get('ttl')
        coroutine = asyncio.create_task(process_node(node, ttl, q))
        coroutines.append(coroutine)

    # The coroutine is waiting for all coroutines terminate
    await asyncio.gather(*coroutines)


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
        await q.put(load)

    return q
