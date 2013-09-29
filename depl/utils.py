from fabric.api import local, run as run_fabric, env


def run(*args, **kwargs):
    if len(env.hosts) and env.hosts[0] in ['localhost', '127.0.0.1']:
        return local(*args, **kwargs)
    else:
        return run_fabric(*args, **kwargs)
