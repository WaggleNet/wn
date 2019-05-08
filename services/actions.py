from .util import Registrar

Action = Registrar()

@Action
def configure_iam():
    pass


@Action
def configure_backplane():
    pass


@Action
def configure_devportal():
    pass


@Action
def configure_frontier():
    pass


@Action
def deploy_iam():
    pass


@Action
def deploy_backplane():
    pass


@Action
def deploy_devportal():
    pass


@Action
def deploy_frontier():
    pass
