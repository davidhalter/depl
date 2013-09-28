from itertools import chain
from depl import deploy


def deploy_pool(pool):
    commands = chain.from_iterable(deploy.load(d.name, d.settings)
                                   for d in pool.deploy)

    run_in_pool(pool, commands)


def run_in_pool(pool, commands):
    pool.hosts
