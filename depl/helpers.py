from StringIO import StringIO

from fabric.api import get, put


def read_file(remote_path):
    """Wrapper around fabric's ``get``"""
    sio = StringIO()
    get(remote_path, sio)
    return sio.getvalue()


def write_file(text, remote_path, use_sudo=False):
    put(StringIO(text), remote_path, use_sudo)
