from fabric.api import local, run as run_fabric, env


def run(*args, **kwargs):
    """
    TODO This is very ugly! local/run don't have the same interfaces, but
    leave it for now - testing reasons. (btw: this should be done by fabric
    anyways, there's a ticket for it)
    """
    if len(env.hosts) and env.hosts[0] in ['localhost', '127.0.0.1']:
        return local(*args, **kwargs)
    else:
        return run_fabric(*args, **kwargs)
