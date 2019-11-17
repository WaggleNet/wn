import requests
import yaml
from pathlib import Path
from requests.exceptions import HTTPError

from iam import IAM
from backplane import Backplane, Node, Router, Site, \
                      DeviceLifecycle, AppCat

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
        'wagglenet': create_app('wagglenet', 'http://localhost:15020/callback')
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
    backplane = Backplane('http://localhost:15003')
    for user in data.get('users', {}).values():
        try:
            user_id = iam.user_register(user['name'], user['email'], user['password'])['result']
            user['user_id'] = user_id
            # Now it's a user. We'll start promoting it to other roles.
            if user.get('role') in ['dev', 'member', 'admin']:
                iam.set_user_profile(user_id, role='dev')
            if user.get('role') in ['member', 'admin']:
                iam.set_user_profile(user_id, role='member')
            if user.get('role') in ['admin']:
                iam.set_user_profile(user_id, role='admin')
        except HTTPError as e:
            if e.response.status_code == 403:
                print('\n-!> Skipping user [%s]: exists' % user['name'])

    for lcodename, lifecycle in data.get('devcats').items():
        # First we check if that is actually there
        lcfound = False
        try:
            lcfound = bool(DeviceLifecycle(backplane).get(lcodename))
        except: pass
        if lcfound:
            print('\n-!> Skipping lifecycle [%s]: exists' % lcodename)
            continue
        try:
            lifecycle['codename'] = lcodename
            lifecycle['status'] = 'SUPPORTED'
            l = DeviceLifecycle(backplane, True, **lifecycle)
            l.save()
        except Exception as e:
            print('\n-!> Failed to create lifecycle [%s]: %s' % (lcodename, e))

    for appcat_id, appcat in data.get('appcats').items():
        # First we check if that is actually there
        found = False
        try:
            found = bool(AppCat(backplane).get(appcat_id))
        except: pass
        if found:
            print('\n-!> Skipping appcat [%s]: exists' % appcat_id)
            continue
        try:
            appcat['_id'] = appcat_id
            a = AppCat(backplane, True, **appcat)
            a.save()
        except Exception as e:
            print('\n-!> Failed to create appcat [%s]: %s' % (lcodename, e))
            raise

    sites = {s.name: s._id for s in Site(backplane).list()}
    for site_name, site in data.get('sites', {}).items():
        # First we check if the site is actually there
        if site_name in sites:
            print('\n-!> Skipping site [%s]: exists' % site_name)
            site['site_id'] = sites[site_name]
            continue
        try:
            # Substitude the owner id
            owner = site.pop('owner', None)
            if owner:
                site['owner_id'] = data.get('users', {}).get(owner, {}).get('user_id')
            site['name'] = site_name
            s = Site(backplane, True, **site)
            s.save()
            site['site_id'] = s._id
        except Exception as e:
            print('\n-!> Failed to create site [%s]: %s' % (site_name, e))

    for device_id, node in data.get('nodes', {}).items():
        # First we check if the node is actually there
        if Node(backplane).list(device_id=device_id):
            print('\n-!> Skipping node [%s]: exists' % hex(device_id))
            continue
        try:
            node['owner_id'] = None
            node['site_id'] = None
            # Substitude the owner id
            owner = node.pop('owner', None)
            if owner:
                node['owner_id'] = data.get('users', {}).get(owner, {}).get('user_id')
            # Substitude the site id
            site = node.pop('site', None)
            if site:
                node['site_id'] = data.get('sites', {}).get(site, {}).get('site_id')
            node['device_id'] = device_id
            n = Node(backplane, True, **node)
            n.save()
            node['node_id'] = n._id
        except Exception as e:
            print('\n-!> Failed to create node [%s]: %s' % (hex(device_id), e))

    for device_id, router in data.get('routers', {}).items():
        # First we check if the router is actually there
        if Router(backplane).list(device_id=device_id):
            print('\n-!> Skipping router [%s]: exists' % hex(device_id))
            continue
        try:
            router['owner_id'] = None
            # Substitude the owner id
            owner = router.pop('owner', None)
            if owner:
                router['owner_id'] = data.get('users', {}).get(owner, {}).get('user_id')
            router['device_id'] = device_id
            n = Router(backplane, True, **router)
            n.save()
            router['router_id'] = n._id
        except Exception as e:
            print('\n-!> Failed to create router [%s]: %s' % (hex(device_id), e))
    dest = Path(get_source_dir()) / 'data' / 'mock_data.results.yaml'
    with open(dest, 'w') as fp:
        yaml.dump(data, fp)
