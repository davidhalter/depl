import urllib
from os.path import dirname, abspath, join

from test_main import config_file, move_dir_content, main_run


@config_file('''
    deploy:
        - python:
            port: 8888
            wsgi: hello
    ''')
def test_flask_simple(tempdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'flask')
    move_dir_content(flask_path, str(tempdir))
    main_run(['depl', 'deploy', 'localhost'])
    assert urllib.urlopen("http://localhost:8888/").getcode() == "Hello World!"
