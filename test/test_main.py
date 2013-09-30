"""
Most of the tests for the application are in the ``deploy`` folder.
"""
import textwrap
import subprocess
import os
import shutil
import sys

import pytest

from depl import main
from depl import config


def main_run(args):
    config._recursion_paths = []
    old, sys.argv = sys.argv, args
    main()
    sys.argv = old


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
                return func(tmpdir)
            finally:
                os.chdir(path)
        return wrapper
    return decorator


def move_dir_content(from_path, to_path):
    for file in os.listdir(from_path):
        shutil.copy(os.path.join(from_path, file), to_path)


def test_no_config():
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        run('depl deploy')
    assert excinfo.value.returncode == 1


@config_file('a wrong config file')
def test_wrong_config(tmpdir):
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        run('depl deploy')
    assert excinfo.value.returncode == 2
