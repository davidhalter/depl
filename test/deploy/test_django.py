import urllib

from os.path import join, abspath, dirname
from test_main import config_file, main_run, move_dir_content


@config_file('''
    deploy:
        - django:
            port: 8887
    ''')
def test_django(tempdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'django_test')
    move_dir_content(flask_path, str(tempdir))
    main_run(['depl', 'deploy', 'localhost'])
    assert urllib.urlopen("http://localhost:8887/").read() == "django rocks\n"
