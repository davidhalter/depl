import textwrap
import subprocess

import pytest

def run(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    return stdout


def config_file(tmpdir, code, file_name = "default.yml"):
    p = tmpdir.join(file_name)
    p.write(textwrap.dedent(code))


def test_no_config():
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        run('depl deploy')
    assert excinfo.value.returncode == 1
