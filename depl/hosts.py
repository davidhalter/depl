from itertools import chain

from fabric.api import settings, run
from fabric import tasks

from depl import deploy


def execute_pool(pool, action):
    commands = chain.from_iterable(
        deploy.load_commands(d.name, d.settings, action) for d in pool.deploy
    )

    run_in_pool(pool, commands)


def run_in_pool(pool, commands):
    # TODO think about adding the @parallel decorator here, but be careful,
    # @parallel doesn't allow password polling.
    def commands_run(commands):
        for command in commands:
            if isinstance(command, (unicode, str)):
                run(command)
            else:
                command()

    hosts = [h.identifier for h in pool.hosts]
    passwords = dict((host.identifier, host.password) for host in pool.hosts
                     if host.password is not None)
    with settings(hosts=hosts, passwords=passwords):
        tasks.execute(commands_run, commands)
