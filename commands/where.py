import click
from services.projects import get_project_dir, project_exists
from services.shell import eprint


@click.command()
@click.argument('name')
def where_cmd(name):
    """Finds where the project is, and returns the directory"""
    try:
        directory = get_project_dir(name)
        if not project_exists(name):
            eprint('Project is not initialized!')
            exit(1)
        print(directory, end='')
        exit(0)
    except IndexError:
        eprint('Project name invalid!')
        exit(1)
