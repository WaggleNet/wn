import click
from pathlib import Path
from services.config import read_conf, write_conf, recommend_project_folder
from services.shell import eprint
from os import system


@click.group(invoke_without_command=True)
@click.pass_context
def config_cmd(ctx):
    """Configure or reconfigure wn's settings"""
    if ctx.invoked_subcommand is None:
        conf = read_conf()
        proj_path = recommend_project_folder()
        eprint('I can automatically create a folder for your projects.')
        eprint('I think {} looks good.'.format(proj_path))
        if ctx and click.confirm('Do you want to change it?'):
            proj_path = click.prompt(
                'Location to store the source code',
                default=conf.get('source', ''),
                type=str
                ).strip().strip('\'').strip('"').rstrip('/')
            if not Path(proj_path).exists():
                eprint('Bummer. Your path is invalid or the folder does not exist.')
                eprint('Please first create it.')
                return
            else:
                conf['source'] = proj_path
        else:
            proj_path.mkdir(exist_ok=True)
            eprint('Okay, I created a folder at {}'.format(proj_path))
            conf['source'] = str(proj_path)
        conf['git_username'] = click.prompt('GitHub Username', type=str, default='optional')
        conf['git_password'] = click.prompt(
            'GitHub Password', type=str, hide_input=True, default='optional')
        write_conf(conf)
        click.echo('All set!')
