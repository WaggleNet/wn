import click
from commands.config import config_cmd
from commands.where import where_cmd
from commands.code import code_cmd
from commands.bringup import up_cmd, down_cmd
from services.shell import eprint

# Load up all the actions
import actions  # noqa


@click.group()
def cli():
    eprint("======= WaggleNet Ubercommand =======\n")
    pass


if __name__ == "__main__":
    cli.add_command(config_cmd, name='config')
    cli.add_command(where_cmd, name='where')
    cli.add_command(code_cmd, name='code')
    cli.add_command(up_cmd, name='up')
    cli.add_command(down_cmd, name='down')
    cli()
