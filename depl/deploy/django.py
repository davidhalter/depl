from depl.deploy import python


def load(settings, package):
    commands = []
    python.load(settings, package)
    return ['pip'], commands
