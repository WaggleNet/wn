import shutil
import time
import yaml
from collections import defaultdict
from halo import Halo
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
if get_source_dir():
    for pp in Path('configs/copy_to_source').glob('*'):
        shutil.copy(pp, get_source_dir() + '/')

# Also expand default actions
for proj in PROJECTS.values():
    actions = proj.get('actions', {})
    for i in actions.keys():
        if actions[i] == 'default':
            actions[i] = DEFAULTS['actions'][i]

# Track components already brought up so recursion is cleaner
already_brought_up = set()


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


def print_project_list():
    """
    Print a list of all projects on the screen.
    """
    print('Choose NAME from the following components:\n')
    print('{:<15}DESCRIPTION'.format('NAME'))
    for name, component in PROJECTS.items():
        print('{:<15}{}'.format(name, component.get('description', 'N/A')))


def list_bringup_components():
    """
    Print a list of all components on the screen
    """
    print('Choose NAME from the following components:\n')
    print('{:<15}DESCRIPTION'.format('NAME'))
    print('='*14 + ' ' + '='*50)
    for name, component in BRINGUP['components'].items():
        print('{:<15}{}'.format(name, component.get('description', 'N/A')))


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
    if name in already_brought_up:
        return
    already_brought_up.add(name)
    print('> Starting component {}'.format(name))
    component = BRINGUP['components'].get(name)
    if not component:
        print('--> Component {} not defined, quitting.'.format(name))
        return
    # STEP 1: Check if pre-requisite has been met
    with Halo(text='Checking pre-requisites...', spinner='dots') as spin:
        if 'precheck' in component:
            precheck = component['precheck']
            if precheck == 'healthcheck':
                precheck = component['healthcheck']
            prereq_met = all(
                run_action(action, throw=False)
                for action in precheck)
        else:
            # Anything that does not have a prereq should always be run
            prereq_met = False
        if prereq_met:
            spin.succeed('Already running')
        else:
            spin.fail('Prerequisites not met!')
    # STEP 2: Propagate to downwards connections
    if not prereq_met or cascade_check:
        for prereq in component.get('requires', []):
            bringup_component(prereq, cascade_check, timeout, check_interval)
    # OK, if we don't need to execute, quit now
    if prereq_met:
        return
    # STEP 3: Execute the actions
    with Halo(
              text='Running the bringup actions for %s' % name,
              spinner='dots') as spin:
        bringup_actions = component.get('bringup')
        if bringup_actions:
            for action in bringup_actions:
                run_action(action, throw=True)
        spin.succeed('Successfully started %s' % name)
    # STEP 4: Run healthcheck until satisfied
    if 'healthcheck' in component:
        with Halo(
                  text='Wait for service to get ready...',
                  spinner='dots') as spin:
            healthcheck = component['healthcheck']
            start_time = time.time()
            while True:
                if all(
                       run_action(action, throw=False)
                       for action in healthcheck):
                    spin.succeed('Service %s is ready' % name)
                    return  # Done
                else:
                    if time.time() > start_time + timeout:
                        spin.fail('Timeout. Service may have failed.')
                        raise TimeoutError('-!> Bringup failed (timeout)')
                    time.sleep(check_interval)


def teardown_component(name: str):
    # STEP 1: Bring down dependents of the component
    for k, component in BRINGUP['components'].items():
        if name in component.get('requires', []):
            print('--> {} depends on {}.'.format(k, name))
            teardown_component(k)
    # STEP 2: Tear down the component itself
    with Halo(text='Tearing down component %s'%name, spinner='dots') as spin:
        actions = component.get('teardown')
        if not actions:
            action = {'teardown': True}
            action.update(component['bringup'][0])
            actions = [action]
        if run_action(action, throw=False):
            spin.succeed('{} is now down!'.format(name))
        else:
            spin.fail('Failed to bring down {}!'.format(name))
