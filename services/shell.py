import click
import subprocess
import sys


def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


def execute(command, permissive=True, **kwargs):
    process = subprocess.Popen(
        command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        **kwargs)
    stderr, stdout = process.communicate()
    retcode = process.returncode
    if retcode and not permissive:
        print('Command failed!')
        raise OSError(
            'STDERR:\n'+stderr.decode()+'STDOUT:\n'+stdout.decode())
                


def eprint(*args, **kwargs):
    """Prints to stderr like print()"""
    print(*args, **kwargs, file=sys.stderr)
