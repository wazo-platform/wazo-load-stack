# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import sys

import click
from requests.exceptions import RequestException
from wlctl.modules.compose import ConfigParserIni, DockerComposeGenerator
from wlctl.modules.load_generator import Configuration, LoadGenerator, RandomizedTimer
from wlctl.modules.utils import load_yaml_file, send_json, send_query
from yaml.parser import ParserError

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    if not os.path.isfile(input_file_path):
        print(f"file {input_file_path} does not exist")
        sys.exit(2)
    output_file_path = os.path.expanduser(output)
    timer = RandomizedTimer()
    configuration = Configuration(input_file_path, timer)
    load_generator = LoadGenerator(output_file_path, configuration)
    load_generator.generate_load_files()


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
    pilot = f"{pilot}/process-load"

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

@load.command()
@click.pass_context
def list(ctx):
    """List current loads currently processed on a stack."""
    config = ctx.obj
    pilot = config.get("DEFAULT", "pilot")
    pilot = f"{pilot}/list-loads"
    response = send_query(pilot)
    response.raise_for_status()
    print(json.dumps(response.json()))

@click.group()
def cluster():
    """Subcommand that manages cluster."""
    pass


@cluster.command()
@click.option(
    '--input',
    '-i',
    default="compose.ini",
    help='Path to the configuration file used to creating docker compose file.',
)
@click.option(
    '--output',
    '-o',
    default="docker-compose.yml",
    help='Path for the output docker compose file.',
)
def compose(input, output):
    """Create a compose file"""
    parser = ConfigParserIni(input)
    config = parser.get_config_as_dict()

    try:
        cmp = DockerComposeGenerator(
            compose_file=output,
            image=config["image"],
            tag=config["tag"],
            start_exposed=int(config["start_exposed"]),
            sip_port=int(config["sip_port"]),
            media_port=int(config["media_port"]),
        )
    except KeyError as e:
        print(f"Malformed ini file: {e}")
        sys.exit(1)
    cmp.generate_compose_file()
