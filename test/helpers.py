import textwrap
import subprocess
import os
import shutil
import sys

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


def config_file(code, file_name="depl.yml"):
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
        path = os.path.join(from_path, file)
        if os.path.isdir(path):
            shutil.copytree(path, os.path.join(to_path, file))
        else:
            shutil.copy(path, to_path)
