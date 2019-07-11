from .util import Registrar
from .shell import execute
from .config import get_source_dir

Action = Registrar()


def run_action(action, cwd=None, **extras):
    counter = 0
    cwd = cwd or get_source_dir()
    for subaction in action:
        subaction.update(extras)
        atype = subaction['type']
        if 'message' in subaction:
            print('-->', subaction['message'])
        else:
            counter += 1
            print('--> Running step', counter)
        if atype == 'shell':  # Run shell command
            if 'pwd' in subaction:
                cwd /= subaction['pwd']
            execute('; '.join(subaction['commands']), False, cwd=cwd)
            return True
        elif atype == 'function':  # Run Python function hook
            f = Action.get(subaction['function'])
            if f:
                result = f()
                if result is not None and not result:
                    raise OSError('Execution of function has failed.')
            else:
                print('Function unimplemented, results may be affected')
        elif atype == 'compose':
            service_name = subaction['service']
            if subaction.get('teardown'):
                cli_command = 'docker-compose rm -f ' + service_name
            else:
                cli_command = 'docker-compose up -d --build ' + service_name
            execute(cli_command, False, cwd=cwd)
