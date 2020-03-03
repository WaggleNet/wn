import requests
import psycopg2
from requests.exceptions import ConnectionError
from pathlib import Path

from services.actions import Action
from services.config import get_source_dir


@Action
def check_deploy_folder():
    src = Path(get_source_dir())
    return all((src/'data'/i).exists() for i in ['envs', 'postgres', 'keys'])


@Action
def check_iam_appkeys():
    apps = ['backplane', 'erp', 'wharf', 'wagglenet']
    src = Path(get_source_dir()) / 'data/keys'
    return all((src/'{}.pem'.format(i)).exists() for i in apps)


@Action
def check_db_connection():
    conn_str = 'postgres://wagglenet:WiggleWaggle@localhost:15001'
    try:
        psycopg2.connect(conn_str)
    except psycopg2.errors.OperationalError:
        return False
    return True


@Action
def check_redis_connection():
    import redis
    rs = redis.Redis(port=15043)
    try:
        rs.get(1)
    except (redis.exceptions.ConnectionError,
            redis.exceptions.BusyLoadingError):
        return False
    return True


def check_reachability(url):
    try:
        resp = requests.get(url)
        return resp.status_code < 500
    except (ConnectionError):
        return False


@Action
def check_iam():
    return check_reachability('http://localhost:15002/healthcheck')


@Action
def check_backplane():
    return check_reachability('http://localhost:15003/healthcheck')


@Action
def check_devportal():
    return check_reachability('http://localhost:15010/healthcheck')


@Action
def check_frontier():
    return check_reachability('http://localhost:15020/healthcheck')


@Action
def check_influx():
    return check_reachability('http://localhost:15044')
    

@Action
def check_broker():
    from paho.mqtt.client import Client
    try:
        client = Client()
        client.connect('localhost', 1883)
        return True
    except Exception as e:
        return False


@Action
def check_mockdata():
    return False


@Action
def check_rabbit():
    from pika import BlockingConnection, ConnectionParameters
    try:
        params = ConnectionParameters(host='localhost', port=15040)
        conn = BlockingConnection(params)
        assert conn.is_open
        return True
    except Exception:
        return False
