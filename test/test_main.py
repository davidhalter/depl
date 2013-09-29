import textwrap
import subprocess
import os

import pytest


def run(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    return stdout


def config_file(code, file_name = "depl.yml"):
    def decorator(func):
        def wrapper(tmpdir):
            p = tmpdir.join(file_name)
            p.write(textwrap.dedent(code))
            path = os.getcwd()
            try:
                print str(tmpdir)
                os.chdir(str(tmpdir))
                return func()
            finally:
                os.chdir(path)
        return wrapper
    return decorator


def test_no_config():
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        run('depl deploy')
    assert excinfo.value.returncode == 1


@config_file('a wrong config file')
def test_wrong_config():
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        run('depl deploy')
    assert excinfo.value.returncode == 2
