import yaml
from collections import defaultdict
from pathlib import Path

from .config import get_source_dir
from .repo import git_clone, git_pull, git_checkout
from .shell import execute

# Initalize projects once and for all
with open('configs/defaults.yaml') as fp:
    DEFAULTS = yaml.load(fp)

with open('configs/groups.yaml') as fp:
    GROUPS = yaml.load(fp)

with open('configs/projects.yaml') as fp:
    PROJECTS = yaml.load(fp)

# Also expand default actions
for proj in PROJECTS.values():
    actions = proj.get('actions', {})
    for i in actions.keys():
        if actions[i] == 'default':
            actions[i] = DEFAULTS['actions'][i]


def list_all_projects():
    return [{
        'exists': project_exists(i),
        **i
    } for i in PROJECTS]


def get_project_dir(key: str) -> Path:
    if key not in PROJECTS:
        raise IndexError('Project %s does not exist' % key)
    return Path(get_source_dir()) / PROJECTS[key]['name']


def project_exists(key: str):
    return get_project_dir(key).exists()


def query_projects(key: str):
    if key in PROJECTS:
        return [key]
    if key in GROUPS:
        return GROUPS.get(key, [])
    return []


def list_actions(key: str):
    result = defaultdict(dict)
    actions = PROJECTS[key].get('actions', [])
    for k in actions:
        words = k.split('_')
        result[words[0]][words[1]] = actions[k]
    result['init']['git'] = None
    result['update']['git'] = None
    return result


def run_action(project: str, action_type: str, action_name: str):
    project_dir = get_project_dir(project)
    actions = list_actions(project).get(action_type, {})
    if action_name != 'git' and action_name not in actions:
        raise NotImplementedError()
    if action_name == 'git':
        if action_type == 'init':
            print('--> Cloning Git repository...')
            if not project_exists(project):
                git_clone(get_source_dir(), PROJECTS[project]['git'])
        elif action_type == 'update':
            if not project_exists(project):
                raise FileNotFoundError('Project {} does not exist'
                                        .format(project))
            print('--> Updating Git repository...')
            git_pull(project_dir)
    else:
        action = actions[action_name]
        counter = 0
        try:
            for subaction in action:
                if 'message' in subaction:
                    print('-->', subaction['message'])
                else:
                    counter += 1
                    print('--> Running action step', counter, 'of', action_name)
                if 'commands' in subaction:  # Run shell command
                    cwd = project_dir
                    if 'pwd' in subaction:
                        cwd /= subaction['pwd']
                    execute('; '.join(subaction['commands']), False, cwd=cwd)
                elif 'function' in subaction:  # Run Python function hook
                    # TODO: Implement custom function hook
                    print(
                        'Action {} not implemented, results may be affected'
                        .format(action_name))
        except Exception as e:
            print(
                'Action {} failed because:'.format(action_name),
                e.__repr__())


def checkout_project(project: str, branch: str):
    try:
        git_checkout(get_project_dir(project), branch)
    except Exception as e:
        print('Checkout failed because', e)
