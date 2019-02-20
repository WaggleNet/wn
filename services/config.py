import yaml
import click
from os import environ
from pathlib import Path
from contextlib import contextmanager

from .shell import eprint

CONF_NAME = 'conf.yaml'


def read_conf():
    if not Path(CONF_NAME).exists():
        return {}
    with open(CONF_NAME) as fp:
        return yaml.load(fp)


def write_conf(conf):
    with open(CONF_NAME, 'w') as fp:
        return yaml.dump(conf, fp)


def get_source_dir():
    return read_conf().get('source')


def check_config(ctx=None):
    from commands.config import config_cmd
    if not get_source_dir():
        eprint('Sorry, you have not configured wn yet.')
        eprint('You can run the following command\n')
        eprint('wn config\n')
        if ctx and click.confirm('Shall I run it for you now?'):
            ctx.invoke(config_cmd)
        else:
            exit(10)


@contextmanager
def git_environ():
    conf = read_conf()
    username = conf.get('git_username') or \
        click.prompt('Enter your Git Username:', type=str)
    password = conf.get('git_password') or \
        click.prompt('Enter your Git Password', type=str)
    environ['GIT_USERNAME'] = username
    environ['GIT_PASSWORD'] = password
    yield
    environ.pop('GIT_USERNAME', None)
    environ.pop('GIT_PASSWORD', None)
