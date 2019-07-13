import requests

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
    # Now update the envfile
    with open('{}/data/envs/{}.env'.format(src, name), 'w') as f:
        f.write('IAM_APP_ID=%s' % app_id)


@Action
def create_iam_app_keys():
    create_app('backplane')
    create_app('devportal', 'http://localhost:15010/callback')
    create_app('wharf')
    create_app('frontier', 'http://localhost:15020/callback')
