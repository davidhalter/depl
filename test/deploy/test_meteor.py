import requests
from os.path import dirname, abspath, join

from test_main import config_file, move_dir_content, main_run


@config_file('''
    deploy:
        - meteor:
            port: 8880
    ''')
def test_simple(tmpdir):
    main_run(['depl', 'deploy', 'localhost'])
    meteor_path = join(dirname(abspath(__file__)), 'sample', 'meteor')
    move_dir_content(meteor_path, str(tmpdir))
    assert requests.get("http://localhost:8880/").status_code == 400
