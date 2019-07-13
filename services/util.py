from Crypto.PublicKey import RSA
from .config import get_source_dir


def generate_keypairs(project):
    """
    Generates a pair of RSA keys for given project,
    then return the public key string for insertion into IAM.
    Privatekey is stored in ./data/keys/<project>.pem
    """
    private = RSA.generate(1024)
    publickeystr = private.publickey().export_key().decode()
    # In IAM, public key string is double-space separated, not \n
    publickeystr = '  '.join(publickeystr.split('\n'))
    privatekeystr = private.export_key().decode()
    with open('{}/data/keys/{}.pem'.format(
              get_source_dir(), project), 'w') as fp:
        fp.write(privatekeystr)
    return publickeystr


class Registrar:
    actions = {}

    def __call__(cls, f):
        cls.actions[f.__name__] = f
        return f

    @classmethod
    def get(cls, name):
        return cls.actions.get(name)
