import urllib

from os.path import join, abspath, dirname
from test_main import config_file, main_run, move_dir_content


def django_basic_test(tempdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'django_test')
    move_dir_content(flask_path, str(tempdir))
    main_run(['depl', 'deploy', 'localhost'])
    assert urllib.urlopen("http://localhost:8887/").read() == "django rocks\n"

    txt = urllib.urlopen("http://localhost:8887/static/something.txt").read()
    assert txt == "static files\n"
    # django plays with the db
    assert urllib.urlopen("http://localhost:8887/db.html").read() == "django rocks\n"


@config_file('''
    deploy:
        - django:
            port: 8887
    ''')
def test_django(tempdir):
    django_basic_test(tempdir)


@config_file('''
    deploy:
        - postgres:
            database: depl
            user: depl
            password: depl
        - django:
            port: 8887
            settings: django_test.settings_with_db
    ''')
def test_django_with_db(tempdir):
    django_basic_test(tempdir)
