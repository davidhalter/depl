from itertools import chain

from fabric.api import settings

from depl import deploy
from depl.utils import run


def deploy_pool(pool):
    commands = chain.from_iterable(deploy.load(d.name, d.settings)
                                   for d in pool.deploy)

    run_in_pool(pool, commands)


def run_in_pool(pool, commands):
    # TODO think about adding the @parallel decorator here, but be careful,
    # @parallel doesn't allow password polling.
    hosts = [h.identifier for h in pool.hosts]
    passwords = dict((host.identifier, host.password) for host in pool.hosts
                                                      if host.identifier)
    with settings(hosts=hosts, passwords=passwords):
        for command in commands:
            run(command)
