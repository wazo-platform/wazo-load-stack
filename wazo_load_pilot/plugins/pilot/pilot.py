#!/usr/bin/env python3
import asyncio
import yaml
import queue
import sys
from .commands import DockerCmdFactory, ShellCmdFactory



def get_command(node):
    if 'host' not in node:
        raise KeyError('Missing required key "host"')
    host = node.get('host')

    if 'cmd' not in node:
        raise KeyError('Missing required key "cmd"')
    command = node['cmd']

    env = node.get("env")

    if 'container' in node:
        container = node['container']
        factory = DockerCmdFactory(container=container, cmd=command, env=env, server=host)
        return factory.new()
    else:
        factory = ShellCmdFactory(cmd=command, servers=[host])
        return factory.new()

async def process_node(node, ttl, channel):
    """
    Coroutine that connects, processes and disconnect from the remote host. Connection duration 
    is based on the TTL
    """
    node = node.get('node')
    host = node.get('host')
    if not host:
        raise KeyError('Missing required key "host"')
    if 'container' not in node:
        raise KeyError('Missing required key "container"')
    container = node['container']

    msg = "started"
    if container == "callee":
        msg = await channel.get()
    if msg != "started":
        print(f"quitting due to receiving: {msg}")
        return

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
    nodes = load.get('load')
    ttl = load.get('ttl')
    compose = load.get('compose')
    forever = load.get('forever')
    coroutines = []

    # create a queue that will allow coroutine to send status.
    q = asyncio.Queue()

    # Loop for creating a coroutine for each node in the workload.
    for node in nodes:
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
        # Waiting for a workload
        load = queue.get()
        print(load)

        # Workload processing
        await process_load(load)
        queue.task_done()

        # break when the queue is empty
        if queue.empty():
            break

def parse_config(yml):
    """
    parse_config takes the config yaml file as argument.
    It processes each load and put them into the queue.
    """
    q = queue.Queue()
    for load in yml["loads"]:
        q.put(load)

    return q
