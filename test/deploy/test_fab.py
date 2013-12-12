import pytest

from ..helpers import config_file, main_run


@config_file('''
    deploy:
        - fab: |
           run('touch depl_sh')
           sudo("rm depl_sh")
    ''')
def test_no_error(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])


@config_file('''
    deploy:
        - fab: |
           sudo("rm depl_sh")
    ''')
def test_raise_error(tmpdir):
    with pytest.raises(SystemExit):
        main_run(['depl', 'deploy', 'localhost'])


@config_file('''
    deploy:
        - fab: |
           with warn_only():
               result = sudo("rm depl_sh")
               assert result.failed
    ''')
def test_raise_error_but_quiet(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])
