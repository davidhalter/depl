from depl.deploy._utils import lazy


def deploy(string):
    python_code = 'from fabric.api import *\n' + string
    return _run(python_code),


@lazy
def _run(python_code):
    # whatever - exec seems to need a separate function. Doesn't work with a
    # closure. I hope/think this is better in py3k.
    exec(python_code)
