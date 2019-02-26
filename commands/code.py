import click

from services.config import check_config
from services.shell import eprint
from services.projects import query_projects, list_actions, run_action, \
    project_exists, checkout_project

ACTION_PRIORITY = ['git', 'env', 'conf', 'db']


@click.group(invoke_without_command=True)
@click.pass_context
def code_cmd(ctx):
    if ctx.invoked_subcommand is None:
        pass
    else:
        pass


@code_cmd.command()
@click.argument('name')
@click.argument('actions', nargs=-1)
@click.pass_context
def init(ctx, name, actions):
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
                    run_action(i, 'init', actn)
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
    check_config(ctx)
    projects = query_projects(name)
    if not projects:
        eprint('I don\'t know which projects you\'re referring to...')
        exit(2)
    for i in projects:
        if not project_exists(i):
            eprint('> Project %s does not exist, skipped' & i)
            continue
        eprint('> Updating project: {}'.format(i))
        available_actions = [
            a for a in list_actions(i).get('update', {})
            if a in actions or not actions]
        for actn in ACTION_PRIORITY:
            if actn in available_actions:
                try:
                    run_action(i, 'update', actn)
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
    projects = query_projects(name)
    if not projects:
        eprint('I don\'t know which projects you\'re referring to...')
        exit(2)
    for i in projects:
        if not project_exists(i):
            eprint('> Project %s does not exist, skipped' % i)
            continue
        # Checkout the project
        checkout_project(i, branch)
    print('> All set!')
