"""
Most of the tests for the application are in the ``deploy`` folder.
"""

import subprocess

import pytest

from . import helpers


def test_no_config():
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        helpers.run('depl deploy')
    assert excinfo.value.returncode == 1


@helpers.config_file('a wrong config file')
def test_wrong_config(tmpdir):
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        helpers.run('depl deploy')
    assert excinfo.value.returncode == 2
