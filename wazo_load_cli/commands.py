# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import click
import sys
import os

from yaml.parser import ParserError
from requests.exceptions import RequestException

from modules.load_generator import LoadGenerator, RandomizedTimer
from modules.utils import load_yaml_file, send_json


@click.group()
def load():
    """Subcommand that handles loads."""
    pass


@load.command()
@click.option(
    '--input',
    '-i',
    default="~/load.ini",
    help='Path to the configuration file used to creating load.',
)
@click.option(
    '--output',
    '-o',
    default="~/load.yml",
    help='Path for the output file where the load will be stored as a yaml file.',
)
def create(input, output):
    """Create a load file"""
    input_file_path = os.path.expanduser(input)
    output_file_path = os.path.expanduser(output)
    randomized_timer = RandomizedTimer()
    load = LoadGenerator(input_file_path, output_file_path, randomized_timer)
    load.generate_load_files()


@load.command()
@click.option(
    '--file',
    '-f',
    default=None,
    help='file is the yaml representation of the load to push.',
)
@click.pass_context
def push(ctx, file):
    """Push loads on a stack."""
    if file is None:
        click.echo("Load file is required.")
        sys.exit(1)

    config = ctx.obj
    pilot = config.get("DEFAULT", "pilot")

    try:
        data = load_yaml_file(file)
    except ParserError as e:
        print("Error while parsing the load file.")
        print(f"Check these error: {e}")

    try:
        send_json(data, pilot)
    except RequestException as e:
        print("An error occured while sending data")
        print("Error: ", str(e))
