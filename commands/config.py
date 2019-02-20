import click
from services.config import read_conf, write_conf


@click.group(invoke_without_command=True)
@click.pass_context
def config_cmd(ctx):
    if ctx.invoked_subcommand is None:
        conf = read_conf()
        conf['source'] = click.prompt(
            'Location to store the source code',
            default=conf.get('source', ''),
            type=str
            ).strip().strip('\'').strip('"')
        conf['git_username'] = click.prompt('GitHub Username', type=str)
        conf['git_password'] = click.prompt(
            'GitHub Password', type=str, hide_input=True)
        write_conf(conf)
        click.echo('All set!')
