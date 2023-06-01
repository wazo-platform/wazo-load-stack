#!/usr/bin/env python3
import click


from commands import load
from modules.utils import load_config


@click.group("cli")
@click.option(
    "--config", "-c", default="~/.wlctl/config", help="Path to the configuration file"
)
@click.pass_context
def cli(ctx, config):
    """wlctl is the Wazo Load cli, that alows to perform convenient operations
    in order to generate load and manage the load stack."""
    if config:
        ctx.obj = load_config(config)


cli.add_command(load)
