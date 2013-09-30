from itertools import chain

from fabric.api import settings, run
from fabric import tasks

from depl import deploy


def deploy_pool(pool):
    commands = chain.from_iterable(deploy.load(d.name, d.settings)
                                   for d in pool.deploy)

    run_in_pool(pool, commands)


def run_in_pool(pool, commands):
    # TODO think about adding the @parallel decorator here, but be careful,
    # @parallel doesn't allow password polling.
    def commands_run(commands):
        for command in commands:
            # command can be a string or a function
            if isinstance(command, (unicode, str)):
                run(command)
            else:
                command()

    hosts = [h.identifier for h in pool.hosts]
    passwords = dict((host.identifier, host.password) for host in pool.hosts
                                              if host.password is not None)
    with settings(hosts=hosts, passwords=passwords):
        tasks.execute(commands_run, commands)
