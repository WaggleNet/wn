import click

from services.projects import bringup_component, list_bringup_components, \
                              teardown_component


@click.command()
@click.argument('name', default='')
@click.pass_context
def up_cmd(ctx, name):
    """Bring up and run component (under NAME) locally from source code."""
    if not name:
        print(up_cmd.get_help(ctx))
        list_bringup_components()
        return
    bringup_component(name, True)
    print('> Done bringing up.')


@click.command()
@click.argument('name', default='')
@click.pass_context
def down_cmd(ctx, name):
    """Tear down running components"""
    if not name:
        print(up_cmd.get_help(ctx))
        list_bringup_components()
        return
    teardown_component(name)
    print('> Done tearing down.')
