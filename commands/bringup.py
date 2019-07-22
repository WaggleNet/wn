import click

from services.projects import bringup_component


@click.command()
@click.argument('name')
def up_cmd(name):
    """Bring up and run projects locally from source code"""
    bringup_component(name, True)
    print('> Done bringing up.')


@click.command()
@click.argument('name')
def down_cmd(name):
    """Tear down running components"""
    pass
