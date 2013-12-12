from os.path import dirname, abspath, join
import time

import requests

from ..helpers import config_file, move_dir_content, main_run


@config_file('''
    deploy:
        - meteor:
            port: 8880
            ssl:
                # disable
                port: 0
    ''')
def test_simple(tmpdir):
    meteor_path = join(dirname(abspath(__file__)), 'sample', 'meteor')
    move_dir_content(meteor_path, str(tmpdir))
    main_run(['depl', 'deploy', 'localhost'])
    # http request on hosts with preinstalled meteor only works after a timeout
    # of some seconds - probably some weird restart issue (most probably meteor
    # itself).
    time.sleep(5)
    assert requests.get("http://localhost:8880/").status_code == 200
