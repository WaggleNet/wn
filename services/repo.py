from git import Git, Repo
from pathlib import Path
from .config import git_environ


def git_clone(path, url, branch='master'):
    with git_environ():
        Git(path).clone(url, branch=branch)


def git_pull(path):
    with git_environ():
        Repo(path).remotes.origin.pull()


def git_checkout(path, branch):
    Git(path).checkout(branch)
