import requests
import yaml
from pathlib import Path

from iam import IAM
from backplane import Backplane

from services.actions import Action
from services.util import generate_keypairs
from services.config import get_source_dir


def create_app(name, url=''):
    iam_url = 'http://localhost:15002/dev/apps'
    pubkey = generate_keypairs(name)
    src = get_source_dir()
    resp = requests.put(iam_url, json={
        'name': name,
        'redirect_url': url,
        'public_key': pubkey
        })
    app_id = resp.json()['result']
    print('\n--> App ID of {} is {}'.format(name, app_id))
    # Now update the envfile
    with open('{}/data/envs/{}.env'.format(src, name), 'w') as f:
        f.write('IAM_APP_ID=%s' % app_id)
    return app_id


@Action
def create_iam_app_keys():
    appids = {
        'backplane': create_app('backplane'),
        'erp': create_app('erp', 'http://localhost:15010/callback'),
        'wharf': create_app('wharf'),
        'frontier': create_app('frontier', 'http://localhost:15020/callback')
    }
    src = get_source_dir()
    data = {
        'appids': appids
    }
    with open('{}/data/envs/env.yaml'.format(src), 'w') as f:
        yaml.dump(data, f)


@Action
def insert_mockdata():
    src = Path(get_source_dir()) / 'data' / 'mock_data.yaml'
    if not src.exists():
        raise FileNotFoundError('You need a mock_data.yaml placed under the data/ folder.')
    with open(src) as f:
        data = yaml.load(f)
    # Log into IAM as ERP
    envyaml_path = Path(get_source_dir()) / 'data/envs/env.yaml'
    with open(envyaml_path) as f:
        envs = yaml.load(f)
    appid = envs['appids']['erp']
    iam = IAM("http://localhost:15002", appid, None,
              str(Path(get_source_dir()) / 'data/keys/erp.pem'))
    for user in data.get('users', {}).values():
        user_id = iam.user_register(user['name'], user['email'], user['password'])['result']
        user['user_id'] = user_id
        # Now it's a user. We'll start promoting it to other roles.
        if user.get('role') in ['dev', 'member', 'admin']:
            iam.set_user_profile(user_id, rule='dev')
        if user.get('role') in ['member', 'admin']:
            iam.set_user_profile(user_id, rule='member')
        if user.get('role') in ['admin']:
            iam.set_user_profile(user_id, rule='admin')
