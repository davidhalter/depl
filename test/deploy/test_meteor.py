import requests

from test_main import config_file, main_run


@config_file('''
    deploy:
        - meteor:
            port: 8880
    ''')
def test_simple(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])
    assert requests.get("http://localhost:8880/").status_code == 400
