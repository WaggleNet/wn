from .util import Registrar
from .shell import execute
from .config import get_source_dir

Action = Registrar()


def run_action(action, cwd=None, throw=True, **extras):
    cwd = cwd or get_source_dir()
    action.update(extras)
    atype = action['type']
    if 'message' in action:
        print('-->', action['message'])
    try:
        if atype == 'shell':  # Run shell command
            if 'pwd' in action:
                cwd /= action['pwd']
            execute('; '.join(action['commands']), False, cwd=cwd)
            return True
        elif atype == 'function':  # Run Python function hook
            fname = action['function']
            f = Action.get(fname)
            if f:
                result = f()
                if result is not None and not result:
                    raise OSError(
                        'Function {} indicates failure.'.format(fname))
            else:
                print(
                    'Function {} unimplemented, results may be affected'
                    .format(fname))
        elif atype == 'compose':
            service_name = action['service']
            if action.get('teardown'):
                cli_command = 'docker-compose rm -f ' + service_name
            else:
                cli_command = 'docker-compose up -d --build ' + service_name
            execute(cli_command, False, cwd=cwd)
    except Exception as e:
        if throw:
            print('-!> Exception', repr(e))
            raise
        return False
    return True
