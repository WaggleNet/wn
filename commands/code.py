import click

from services.config import check_config
from services.shell import eprint
from services.projects import query_projects, list_actions, run_op, \
    project_exists, checkout_project, print_project_list

ACTION_PRIORITY = ['git', 'env', 'conf', 'db']


@click.group(invoke_without_command=True)
@click.pass_context
def code_cmd(ctx):
    """Check out, update and configure source code"""
    if ctx.invoked_subcommand is None:
        print(code_cmd.get_help(ctx))
        print_project_list()
    else:
        pass


@code_cmd.command()
@click.argument('name')
@click.argument('actions', nargs=-1)
@click.pass_context
def init(ctx, name, actions):
    """Initializes source code projects.
    
    ACTION can be one of the following:
    - git: Clone the source code from git
    - env: Set up the environment for running the code
    """
    check_config(ctx)
    projects = query_projects(name)
    if not projects:
        eprint('I don\'t know which projects you\'re referring to...')
        exit(2)
    for i in projects:
        eprint('> Initializing project: {}'.format(i))
        available_actions = [
            a for a in list_actions(i).get('init', {})
            if a in actions or not actions]
        for actn in ACTION_PRIORITY:
            if actn in available_actions:
                try:
                    run_op(i, 'init', actn)
                except NotImplementedError:
                    eprint(
                        '--> Action {} not implemented, skipped'.format(actn))
        print('> Project {} initialized!'.format(i))
    print('> All set!')


@code_cmd.command()
@click.argument('name')
@click.argument('actions', nargs=-1)
@click.pass_context
def update(ctx, name, actions):
    """Update one or a group of projects."""
    check_config(ctx)
    projects = query_projects(name)
    if not projects:
        eprint('I don\'t know which projects you\'re referring to...')
        exit(2)
    for i in projects:
        if not project_exists(i):
            eprint('> Project %s does not exist, skipped' % i)
            continue
        eprint('> Updating project: {}'.format(i))
        available_actions = [
            a for a in list_actions(i).get('update', {})
            if a in actions or not actions]
        for actn in ACTION_PRIORITY:
            if actn in available_actions:
                try:
                    run_op(i, 'update', actn)
                except NotImplementedError:
                    eprint(
                        '--> Action {} not implemented, skipped'.format(actn))
        print('> Project {} updated!'.format(i))
    print('> All set!')


@code_cmd.command()
@click.argument('name')
@click.argument('branch')
@click.pass_context
def checkout(ctx, name, branch):
    """Switch a project or a group of them to the specified Git branch."""
    projects = query_projects(name)
    if not projects:
        eprint('I don\'t know which projects you\'re referring to...')
        exit(2)
    for i in projects:
        if not project_exists(i):
            eprint('> Project %s does not exist, skipped' % i)
            continue
        # Checkout the project
        if checkout_project(i, branch):
            eprint('> Project %s checked out to %s' % (i, branch))
    print('> All set!')
