import shutil
import time
import yaml
from collections import defaultdict
from pathlib import Path
from progress.spinner import Spinner

from .actions import run_action
from .config import get_source_dir
from .repo import git_clone, git_pull, git_checkout

# Initalize projects once and for all
with open('configs/defaults.yaml') as fp:
    DEFAULTS = yaml.load(fp)

with open('configs/groups.yaml') as fp:
    GROUPS = yaml.load(fp)

with open('configs/projects.yaml') as fp:
    PROJECTS = yaml.load(fp)

with open('configs/bringup.yaml') as fp:
    BRINGUP = yaml.load(fp)

# Copy the content of copy_to_source over to source folder
for pp in Path('configs/copy_to_source').glob('*'):
    shutil.copy(pp, get_source_dir() + '/')

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


def run_op(project: str, action_type: str, action_name: str):
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
        actions = actions[action_name]
        project_dir = get_project_dir(project)
        try:
            counter = 0
            for action in actions:
                counter += 1
                print('--> Running step', counter)
                run_action(action, project_dir)
        except Exception as e:
            print(
                'Action {} failed because:'.format(action_name),
                repr(e))


def checkout_project(project: str, branch: str):
    try:
        git_checkout(get_project_dir(project), branch)
        return True
    except Exception as e:
        print('! Checkout failed because', e)
        return False


def bringup_component(name: str,
                      cascade_check=True,
                      timeout=60,
                      check_interval=1):
    """
    Bring up the named component.

    If a pre-check is defined, the bringup is only necessitated by the failure
    of the pre-check. If a healthcheck is defined, the bringup is failed if
    repeated healthcheck is timed out.

    :param name: Name of component.
    :param cascade_check: Cascade to depending tasks even if pre-check passes.
    :param timeout: Max duration of failed healthchecks before giving up.
    :param check_interval: Duration to wait before retrying healthcheck.
    """
    print('> Starting component {}'.format(name))
    component = BRINGUP['components'].get(name)
    if not component:
        print('--> Component {} not defined, quitting.'.format(name))
        return
    # STEP 1: Check if pre-requisite has been met
    print('--> Checking pre-requisites...', end='')
    if 'precheck' in component:
        precheck = component['precheck']
        if precheck == 'healthcheck':
            precheck = component['healthcheck']
        prereq_met = all(
            run_action(action, throw=False)
            for action in precheck)
    else:
        prereq_met = True
    print('Passed' if prereq_met else 'Not met.')
    # STEP 2: Propagate to downwards connections
    if not prereq_met or cascade_check:
        for prereq in component.get('requires', []):
            bringup_component(prereq, cascade_check, timeout, check_interval)
    # OK, if we don't need to execute, quit now
    if prereq_met:
        return
    # STEP 3: Execute the actions
    print('--> Running the bringup actions for %s ...' % name)
    bringup_actions = component.get('bringup')
    if bringup_actions:
        for action in bringup_actions:
            run_action(action, throw=True)
    # STEP 4: Run healthcheck until satisfied
    if 'healthcheck' in component:
        spinner = Spinner('--> Wait for service to come online...')
        healthcheck = component['healthcheck']
        start_time = time.time()
        while True:
            spinner.next()
            if all(run_action(action, throw=False) for action in healthcheck):
                return  # Done
            else:
                if time.time() > start_time + timeout:
                    raise TimeoutError('-!> Bringup failed, waited too long')
                time.sleep(check_interval)
        print('Done!')
