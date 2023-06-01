import click
import os

from modules.load_generator import LoadGenerator, RandomizedTimer


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
