import click


@click.command()
@click.argument('name')
def up_cmd(name):
    """Bring up and run projects locally from source code"""
    pass


@click.command()
@click.argument('name')
def down_cmd(name):
    """Tear down running components"""
    pass
