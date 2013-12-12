import pytest

from ..helpers import config_file, main_run


@config_file('''
    deploy:
        - sh: |
           set -e
           touch depl_sh
           rm depl_sh
    ''')
def test_no_error(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])


@config_file('''
    deploy:
        - sh: |
           set -e
           rm depl_a
           echo -n
    ''')
def test_raise_error(tmpdir):
    with pytest.raises(SystemExit):
        main_run(['depl', 'deploy', 'localhost'])


@config_file('''
    deploy:
        - sh: |
           rm depl_a
           echo -n
    ''')
def test_raise_error_but_quiet(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])
