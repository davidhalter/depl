from fabric.api import sudo, run


def deploy(string):
    cmd = sudo if 'sudo ' in string else run

    return lambda: cmd(string),
